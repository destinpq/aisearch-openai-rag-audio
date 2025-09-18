"""Main backend app moved from nested project."""
from aiohttp import web
import asyncio
import os
import logging
from dotenv import load_dotenv
from ragtools import stream_query
import httpx
import json
from io import BytesIO
import sqlite3
try:
    # gTTS provides a simple server-side TTS fallback for development
    from gtts import gTTS
except Exception:
    gTTS = None

# Load environment variables from .env file
load_dotenv()

# Basic logging so we can see which TTS backend is used
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('backend')

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

# Read configurable ports/origins from environment so they can be overridden in .env
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:2357")
# BACKEND_PORT can be set in the environment; default to 2355 per request
try:
    BACKEND_PORT = int(os.environ.get("BACKEND_PORT", "2355"))
except ValueError:
    BACKEND_PORT = 2355


def get_voice_for_language(language_code):
    """Query the Azure voices database for an appropriate voice for the given language.

    Args:
        language_code: ISO language code (e.g., 'mr', 'hi', 'en-IN')

    Returns:
        Voice short_name string, or None if no suitable voice found
    """
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'azure_voices.db')
        if not os.path.exists(db_path):
            logger.warning("Azure voices database not found")
            return None

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Try exact locale match first (e.g., 'mr-IN' for 'mr')
        lang_lower = language_code.lower()
        if '-' not in lang_lower:
            # If just language code like 'mr', try to find locale variants
            cur.execute("SELECT short_name, gender FROM voices WHERE locale LIKE ? ORDER BY gender DESC, short_name", (f"{lang_lower}-%",))
        else:
            # Exact locale match
            cur.execute("SELECT short_name, gender FROM voices WHERE locale = ? ORDER BY gender DESC, short_name", (lang_lower,))

        voices = cur.fetchall()
        conn.close()

        if voices:
            # Prefer female voices, then first available
            female_voices = [v[0] for v in voices if v[1] and v[1].lower() == 'female']
            if female_voices:
                return female_voices[0]
            return voices[0][0]

        logger.info("No voices found in database for language: %s", language_code)
        return None

    except Exception as e:
        logger.exception("Error querying voices database: %s", e)
        return None


async def hello(request):
    return web.Response(text="Hello from backend")


async def search(request):
    try:
        data = await request.json()
        query = data.get("query", "")
    except Exception:
        query = ""

    # non-streaming JSON response (kept for compatibility)
    resp = web.json_response({
        "results": [
            {"text": f"You searched for: {query}"}
        ]
    })
    # ensure CORS headers present for fetch POST
    resp.headers['Access-Control-Allow-Origin'] = FRONTEND_ORIGIN
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp


async def search_sse(request):
    """Stream Server-Sent Events for a query.

    Uses `stream_query(query)` from `ragtools` which yields strings (tokens/chunks).
    """
    query = request.query.get("query", "")

    headers = {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': FRONTEND_ORIGIN,
        'Access-Control-Allow-Credentials': 'true',
    }

    resp = web.StreamResponse(status=200, reason='OK', headers=headers)
    await resp.prepare(request)

    # Server-side framing: batch small chunks and flush periodically to reduce SSE frequency.
    buffer = []
    buffer_chars = 0
    FLUSH_INTERVAL = 0.15  # seconds
    FLUSH_CHARS = 200

    async def flush_buffer():
        nonlocal buffer, buffer_chars
        if not buffer:
            return
        text = "".join(buffer)
        payload = {"text": text}
        try:
            await resp.write(f"data: {web.json_response(payload).text}\n\n".encode())
        except ConnectionResetError:
            return False
        buffer = []
        buffer_chars = 0
        return True

    # flush loop runs in background
    stop_event = asyncio.Event()

    async def flusher():
        while not stop_event.is_set():
            await asyncio.sleep(FLUSH_INTERVAL)
            ok = await flush_buffer()
            if ok is False:
                break

    flusher_task = asyncio.create_task(flusher())
    try:
        async for chunk in stream_query(query):
            buffer.append(chunk)
            buffer_chars += len(chunk)
            if buffer_chars >= FLUSH_CHARS:
                ok = await flush_buffer()
                if ok is False:
                    break
    except ConnectionResetError:
        pass
    finally:
        stop_event.set()
        try:
            await flusher_task
        except Exception:
            pass
    try:
        await resp.write_eof()
    except Exception:
        pass
    return resp


async def transcribe_audio(request):
    """Accept multipart form data with a file field named 'file' and return a transcript.

    This forwards the audio to OpenAI's transcription endpoint if OPENAI_API_KEY is set.
    """
    if not OPENAI_API_KEY:
        return web.json_response({"error": "OPENAI_API_KEY not configured"}, status=400)

    reader = await request.multipart()
    file_field = None
    async for part in reader:
        if part.name == 'file':
            file_field = part
            break

    if file_field is None:
        return web.json_response({"error": "missing file field"}, status=400)

    # read content into memory (acceptable for small dev uploads)
    data = await file_field.read(decode=False)

    url = 'https://api.openai.com/v1/audio/transcriptions'
    headers = {'Authorization': f'Bearer {OPENAI_API_KEY}'}

    files = {'file': ('upload.wav', data)}
    # optionally add model param
    params = {'model': 'whisper-1'}

    async with httpx.AsyncClient(timeout=60) as client:
        try:
            resp = await client.post(url, headers=headers, files=files, data=params)
            resp.raise_for_status()
            obj = resp.json()
            text = obj.get('text') or obj.get('transcript') or None
            return web.json_response({'text': text})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)


async def transliterate_text(text, target='latin'):
    """Transliterate text to a target script using OpenAI.

    Returns the transliterated text or None if failed.
    """
    if not text or not OPENAI_API_KEY:
        return None

    # Strong instruction to force output in the requested script. When target is
    # 'devanagari' we explicitly instruct the model to return ONLY Devanagari
    # characters and nothing else so the frontend can safely apply the text.
    if str(target).lower() == 'devanagari' or str(target).lower() == 'devanagari-only':
        prompt = (
            "You are a transliteration assistant. Respond ONLY with the text "
            "transliterated into Devanagari script. Do not translate the meaning, "
            "do not add any commentary, and preserve punctuation. Return exactly "
            "the Devanagari text and nothing else. Use natural Devanagari spellings "
            "for names (for example, 'pratik' -> 'प्रतीक' not 'प्रातिक').\n\n" + text + "\n\n"
        )
    else:
        prompt = (
            f"Transliterate the following text to {target} (preserve punctuation, do NOT translate):\n\n{text}\n\n")

    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': OPENAI_MODEL,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 512,
        'temperature': 0.0
    }

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            obj = resp.json()
            # try to extract content
            translit = ''
            if 'choices' in obj and obj['choices']:
                c = obj['choices'][0]
                if 'message' in c and isinstance(c['message'], dict):
                    translit = c['message'].get('content', '')
                elif 'text' in c:
                    translit = c.get('text', '')
            # Post-process common name mappings for Devanagari
            if str(target).lower() == 'devanagari':
                try:
                    name_map = {
                        'pratik': 'प्रतीक',
                        'pratikr': 'प्रतीक',
                        'rahul': 'राहुल',
                    }
                    orig_words = text.split()
                    trans_words = translit.split()
                    for i, ow in enumerate(orig_words):
                        low = ow.lower()
                        for nk, dv in name_map.items():
                            if nk in low:
                                if i < len(trans_words):
                                    trans_words[i] = dv
                    translit = " ".join(trans_words)
                except Exception:
                    # if postprocessing fails, fall back to raw transliteration
                    pass
            return translit
        except Exception:
            return None


async def transliterate(request):
    """Transliterate short text to a target script (default: latin).

    Expects JSON { text: string, target?: 'latin' }
    Uses OpenAI by sending a small prompt to transliterate/romanize the text.
    """
    try:
        data = await request.json()
        text = data.get('text', '')
        target = data.get('target', 'latin')
    except Exception:
        return web.json_response({'error': 'invalid json'}, status=400)

    if not text:
        return web.json_response({'transliteration': ''})

    translit = await transliterate_text(text, target)
    if translit is None:
        # fallback: return original if no key or failed
        translit = text

    body = json.dumps({'transliteration': translit}, ensure_ascii=False)
    return web.Response(text=body, content_type='application/json')


async def detect_language(text):
    """Detect language and dialect for a short text.

    Returns { language: str, dialect: str }
    Uses OpenAI chat completions to classify; falls back to 'en'.
    """
    if not text:
        return {'language': 'en', 'dialect': 'en-US'}

    if not OPENAI_API_KEY:
        return {'language': 'en', 'dialect': 'en-US'}

    prompt = (
        "You are a short-text language and dialect classifier. Given a short piece of text, "
        "detect the primary language (ISO 639-1 code, e.g., 'en' for English, 'hi' for Hindi, 'mr' for Marathi) "
        "and, if the language is English, also return the most likely English variant/dialect from this set: "
        "['en-US','en-GB','en-AU','en-IN','en-CA']. Respond with a single JSON object and nothing else, for example:\n"
        "{""language"": ""en"", ""dialect"": ""en-GB""}\n\n"
        "If the language is not English, set 'dialect' to the language code (for example {\"language\": \"hi\", \"dialect\": \"hi\"}).\n"
        "Now classify the following text exactly and output only JSON:\n\n"
        + text
    )

    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': OPENAI_MODEL,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 16,
        'temperature': 0.0
    }

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            obj = resp.json()
            if 'choices' in obj and obj['choices']:
                c = obj['choices'][0]
                text_out = ''
                if 'message' in c and isinstance(c['message'], dict):
                    text_out = c['message'].get('content', '')
                elif 'text' in c:
                    text_out = c.get('text', '')
                # try to parse JSON from the model output
                try:
                    parsed = json.loads(text_out.strip())
                    lang = parsed.get('language') or parsed.get('lang')
                    dialect_out = parsed.get('dialect') or None
                    if lang:
                        return {'language': lang, 'dialect': dialect_out or lang}
                except Exception:
                    # fallback: attempt to extract a token
                    token = text_out.strip().split('\n')[0].strip()
                    if token in ('en-US', 'en-GB', 'en-AU', 'en-IN', 'en-CA'):
                        return {'language': 'en', 'dialect': token}
            return {'language': 'en', 'dialect': 'en-US'}
        except Exception as e:
            logger.exception('Language detection failed: %s', e)
            return {'language': 'en', 'dialect': 'en-US'}


async def detect_dialect(request):
    """HTTP endpoint wrapper for detect_language function."""
    try:
        data = await request.json()
        text = data.get('text', '')
    except Exception:
        return web.json_response({'error': 'invalid json'}, status=400)

    if not text:
        return web.json_response({'error': 'missing text'}, status=400)

    result = await detect_language(text)
    return web.json_response(result)


async def tts_endpoint(request):
    """Simple TTS endpoint.

    Accepts JSON: { text: string, lang?: 'en'|'hi'|'auto', voice?: string }
    Returns audio/mpeg (mp3) generated via gTTS if available. If gTTS is not
    installed, returns 501.
    """
    try:
        data = await request.json()
        text = data.get('text', '')
        lang = data.get('lang', 'en')
        voice_param = data.get('voice')
    except Exception:
        return web.json_response({'error': 'invalid json'}, status=400)

    if not text:
        return web.json_response({'error': 'missing text'}, status=400)

    # Prefer Azure Neural TTS if configured
    AZURE_KEY = os.environ.get('AZURE_TTS_KEY')
    AZURE_REGION = os.environ.get('AZURE_TTS_REGION')
    AZURE_VOICE = os.environ.get('AZURE_TTS_VOICE')

    # If caller asked for automatic detection, call our detect_language function directly
    # so we can pick a voice that matches the detected language/dialect.
    if str(lang).lower() in ('auto', 'auto-detect', 'detect'):
        logger.info('Starting language detection for text: %s', text[:50])
        try:
            # Call detect_language function directly instead of making HTTP request
            detection_result = await detect_language(text)
            logger.info('Language detection result: %s', detection_result)
            # prefer explicit dialect if provided, else language
            detected = detection_result.get('dialect') or detection_result.get('language')
            if detected:
                lang = detected
                logger.info('Set language to: %s', lang)
            else:
                logger.warning('No language detected, falling back to en')
                lang = 'en'
        except Exception as e:
            logger.exception('Language detection exception: %s, falling back to en', e)
            lang = 'en'

    async def _use_gtts():
        if gTTS is None:
            logger.error('gTTS not available in environment')
            return web.json_response({'error': 'no-tts-backend-available'}, status=501)
        try:
            logger.info('Using gTTS fallback for text (lang=%s)', lang)
            tts = gTTS(text=text, lang=(lang if lang else 'en'))
            buf = BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            return web.Response(body=buf.read(), content_type='audio/mpeg')
        except Exception as e:
            logger.exception('gTTS generation failed: %s', e)
            return web.json_response({'error': str(e)}, status=500)

    if AZURE_KEY and AZURE_REGION:
        # If caller provided an explicit voice, use it. Otherwise map the
        # detected language/dialect to a sensible Azure neural voice.
        if voice_param:
            voice = voice_param
        else:
            # First try to get voice from database based on detected language
            db_voice = get_voice_for_language(lang)
            if db_voice:
                voice = db_voice
                logger.info("Selected voice from database: %s for language: %s", voice, lang)
            else:
                # Fall back to hardcoded voices if database query fails
                lang_l = str(lang).lower()
                # map common languages/dialects -> Azure voices; fallback to en-US
                if lang_l.startswith('hi'):
                    voice = AZURE_VOICE or 'hi-IN-SwaraNeural'
                elif lang_l.startswith('mr'):
                    # Prefer a Marathi Azure voice when the language is Marathi.
                    # Fall back to a Hindi voice only if a Marathi voice is not available.
                    voice = AZURE_VOICE or 'mr-IN-AarohiNeural'
                elif lang_l.startswith('en-in') or lang_l == 'en-in' or lang_l == 'en_in':
                    voice = AZURE_VOICE or 'en-IN-NeerjaNeural'
                elif lang_l.startswith('en-gb') or lang_l.startswith('en-uk'):
                    voice = AZURE_VOICE or 'en-GB-LibbyNeural'
                elif lang_l.startswith('en-au'):
                    voice = AZURE_VOICE or 'en-AU-NatashaNeural'
                elif lang_l.startswith('en'):
                    voice = AZURE_VOICE or 'en-US-AriaNeural'
                else:
                    # For other language codes, attempt to pick a regional voice if possible,
                    # otherwise fall back to the default English voice above.
                    voice = AZURE_VOICE or 'en-US-AriaNeural'

        # Determine SSML language tag to inform the TTS engine about pronunciation.
        lang_tag = 'en-US'
        try:
            ll = str(lang).lower()
            if ll.startswith('hi'):
                lang_tag = 'hi-IN'
            elif ll.startswith('mr'):
                lang_tag = 'mr-IN'
            elif ll.startswith('en-in'):
                lang_tag = 'en-IN'
            elif ll.startswith('en-gb') or ll.startswith('en-uk'):
                lang_tag = 'en-GB'
            elif ll.startswith('en-au'):
                lang_tag = 'en-AU'
            elif ll.startswith('en'):
                lang_tag = 'en-US'
            else:
                # default to provided short lang code if possible (e.g., 'fr' -> 'fr-FR')
                if len(ll) == 2:
                    lang_tag = f"{ll}-{ll.upper()}"
        except Exception:
            pass

        # If the caller provided text in Latin script for Hindi/Marathi, try transliterating
        # to Devanagari first (via the existing transliterate function) so Azure pronounces
        # it more naturally for those languages.
        try:
            ll = str(lang).lower()
            if OPENAI_API_KEY and (ll.startswith('hi') or ll.startswith('mr')):
                # call transliterate function directly instead of making HTTP request
                try:
                    transliteration_result = await transliterate_text(text, 'devanagari')
                    if transliteration_result:
                        text = transliteration_result
                except Exception:
                    # if transliteration fails, continue with original text
                    pass
        except Exception:
            pass

        # Include xml:lang on the voice element as well to more strongly
        # indicate the intended language (helps force regional pronunciation).
        # Wrap the spoken text in a <lang> tag to more explicitly indicate
        # the intended language; some TTS voices respond better when the
        # text is wrapped in <lang xml:lang='...'>.
        ssml_text = (
            "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' "
            "xmlns:mstts='https://www.w3.org/2001/mstts' "
            f"xml:lang='{lang_tag}'>"
            f"<voice name='{voice}' xml:lang='{lang_tag}'><lang xml:lang='{lang_tag}'>{text}</lang></voice></speak>"
        )

        url = f"https://{AZURE_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
        headers = {
            'Ocp-Apim-Subscription-Key': AZURE_KEY,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-24khz-160kbitrate-mono-mp3',
            'User-Agent': 'aisearch-tts/1.0'
        }
        logger.info('Attempting Azure TTS with voice=%s region=%s', voice, AZURE_REGION)
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(url, headers=headers, content=ssml_text.encode('utf-8'))
                resp.raise_for_status()
                # If Azure returns an empty body (some languages/inputs may not be supported),
                # fall back to the local gTTS backend instead of returning an empty file.
                if not resp.content or len(resp.content) == 0:
                    logger.warning('Azure TTS returned empty content (status=%s); falling back to gTTS', resp.status_code)
                    return await _use_gtts()
                logger.info('Azure TTS succeeded (status=%s, bytes=%s)', resp.status_code, len(resp.content))
                return web.Response(body=resp.content, content_type='audio/mpeg')
            except Exception:
                logger.exception('Azure TTS failed, falling back to gTTS')
                # Azure failed, fall back to gTTS if present
                return await _use_gtts()

    # If Azure not configured, use gTTS fallback
    return await _use_gtts()


async def tts_stream(request):
    """Websocket endpoint that streams text chunks for client-side TTS.

    Usage: connect to ws://host:port/tts-stream and send a single JSON message
    { "text": "..." }. The server will run dialect detection/transliteration
    as needed and then stream back JSON messages: { "chunk": "..." }
    until the full text is sent. This allows the frontend to speak as chunks
    arrive using the browser SpeechSynthesis API.
    """
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    try:
        msg = await ws.receive_json(timeout=10)
    except Exception:
        await ws.send_json({"error": "no input received"})
        await ws.close()
        return ws

    text = msg.get('text', '') if isinstance(msg, dict) else ''
    if not text:
        await ws.send_json({"error": "missing text"})
        await ws.close()
        return ws

    # detect language/dialect using the same logic as detect_dialect
    detected = 'en'
    dialect = 'en-US'
    if OPENAI_API_KEY:
        # reuse detect_dialect prompt via OpenAI
        prompt = (
            "You are a short-text language and dialect classifier. Given a short piece of text, "
            "detect the primary language (ISO 639-1 code) and if English return a dialect code. "
            "Respond with a single JSON object like {\"language\": \"en\", \"dialect\": \"en-IN\"}.\n\n"
            + text
        )
        url = 'https://api.openai.com/v1/chat/completions'
        headers = {'Authorization': f'Bearer {OPENAI_API_KEY}', 'Content-Type': 'application/json'}
        payload = {
            'model': OPENAI_MODEL,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 16,
            'temperature': 0.0
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                obj = resp.json()
                if 'choices' in obj and obj['choices']:
                    c = obj['choices'][0]
                    txt = ''
                    if 'message' in c and isinstance(c['message'], dict):
                        txt = c['message'].get('content', '')
                    elif 'text' in c:
                        txt = c.get('text', '')
                    try:
                        parsed = json.loads(txt.strip())
                        detected = parsed.get('language') or detected
                        dialect = parsed.get('dialect') or detected
                    except Exception:
                        pass
        except Exception:
            # ignore detection failures and continue with defaults
            pass

    # if hindi/marathi, transliterate to Devanagari for client display/speaking
    out_text = text
    if OPENAI_API_KEY and (str(detected).lower().startswith('hi') or str(detected).lower().startswith('mr')):
        # call transliterate endpoint programmatically
        try:
            prompt = (
                "You are a transliteration assistant. Respond ONLY with the text "
                "transliterated into Devanagari script. Do not translate the meaning, "
                "do not add any commentary. Return exactly the Devanagari text and nothing else.\n\n" + text + "\n\n"
            )
            url = 'https://api.openai.com/v1/chat/completions'
            headers = {'Authorization': f'Bearer {OPENAI_API_KEY}', 'Content-Type': 'application/json'}
            payload = {
                'model': OPENAI_MODEL,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 512,
                'temperature': 0.0
            }
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                obj = resp.json()
                if 'choices' in obj and obj['choices']:
                    c = obj['choices'][0]
                    if 'message' in c and isinstance(c['message'], dict):
                        out_text = c['message'].get('content', out_text)
                    elif 'text' in c:
                        out_text = c.get('text', out_text)
        except Exception:
            pass

    # stream back chunks: simple split by whitespace and send words gradually
    words = out_text.split()
    # send an initial ack
    await ws.send_json({"status": "ok", "estimated_words": len(words)})
    for i in range(len(words)):
        chunk = words[i]
        try:
            await ws.send_json({"chunk": chunk, "index": i, "total": len(words)})
        except Exception:
            break
        await asyncio.sleep(0.12)

    # final message
    try:
        await ws.send_json({"done": True})
    except Exception:
        pass
    await ws.close()
    return ws


@web.middleware
async def cors_middleware(request, handler):
    # Handle preflight
    if request.method == 'OPTIONS':
        resp = web.Response(status=204)
        resp.headers['Access-Control-Allow-Origin'] = FRONTEND_ORIGIN
        resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp

    resp = await handler(request)
    # Add CORS headers to normal responses
    resp.headers['Access-Control-Allow-Origin'] = FRONTEND_ORIGIN
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp


def create_app():
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_get('/', hello)
    app.router.add_post('/search', search)
    app.router.add_get('/search-sse', search_sse)
    app.router.add_post('/transcribe', transcribe_audio)
    app.router.add_post('/transliterate', transliterate)
    app.router.add_post('/detect-dialect', detect_dialect)
    app.router.add_post('/tts', tts_endpoint)
    app.router.add_get('/tts-stream', tts_stream)
    return app


if __name__ == '__main__':
    web.run_app(create_app(), host='0.0.0.0', port=BACKEND_PORT)
