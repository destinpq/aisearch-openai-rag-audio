# aisearch-openai-rag-audio

This repository implements a small backend and frontend for multilingual TTS and speech features. The system automatically detects input language using OpenAI, selects the best Azure Neural voice from a local voice database (600+ voices), optionally transliterates romanized Indic text to Devanagari, and uses Azure Neural TTS (with gTTS fallback) to produce MP3 audio.

## Architecture Overview

- Backend (Python, aiohttp)

  - `backend/app.py` is the main server.
  - Responsibilities:
    - Receive API requests (TTS, detect-dialect, transliterate, transcribe, streaming TTS)
    - Call OpenAI to detect language/dialect (`detect_language`) and transliterate (`transliterate_text`)
    - Select voice from local SQLite database `azure_voices.db` (600+ Azure voices)
    - Call Azure Cognitive Services TTS to synthesize audio (SSML)
    - Fallback to `gTTS` when Azure TTS is not configured or fails
  - Key functions and endpoints:
    - `detect_language(text)` — core detection logic (returns `{language, dialect}`)
    - `transliterate_text(text, target)` — transliteration helper using OpenAI
    - `get_voice_for_language(lang)` — queries local voice DB
    - `tts_endpoint` — POST `/tts` accepts `{text, lang, voice}` and returns `audio/mpeg`
    - `detect_dialect` — POST `/detect-dialect` accepts `{text}` and returns `{language, dialect}`
    - `transliterate` — POST `/transliterate` accepts `{text, target}` and returns `{transliteration}`
    - `transcribe` — POST `/transcribe` accepts audio file and returns transcript (uses OpenAI Whisper if configured)
    - `tts_stream` — GET `/tts-stream` websocket streaming endpoint for chunked client-side TTS

- Frontend (Next.js)

  - `frontend-next/` contains a minimal UI that calls backend endpoints.
  - `frontend-next/components/SearchClient.tsx` includes `readAloud` and `playServerTTS` flows which call `/tts` with `lang: "auto"` to let the server detect language and return MP3 audio.

- Data
  - `backend/azure_voices.db` — local SQLite DB with Azure voices metadata used to pick matching `short_name`/voice name.

## API Endpoints

Base URL: `http://<host>:2355` (default when running locally)

1. POST /detect-dialect

   - Request: `{ "text": "..." }`
   - Response: `{ "language": "en", "dialect": "en-US" }`
   - Notes: Uses `detect_language` which calls OpenAI to classify short text. Falls back to `en/en-US` on error.

2. POST /transliterate

   - Request: `{ "text": "...", "target": "devanagari" }`
   - Response: `{ "transliteration": "..." }`
   - Notes: Uses `transliterate_text` (OpenAI) to convert romanized Indic text to Devanagari. Strict instruction to return Devanagari only when `target==devanagari`.

3. POST /tts

   - Request: `{ "text": "...", "lang": "auto" | "en" | "hi" | ..., "voice": "<azure voice short name>" }
   - Response: binary MP3 audio with `Content-Type: audio/mpeg`
   - Behavior:
     - If `lang` is `auto`, server calls `detect_language` internally (direct function call) to get `{language, dialect}` quickly.
     - Server chooses a voice from `azure_voices.db` via `get_voice_for_language(lang)`; falls back to sensible defaults.
     - For Indic languages (hi/mr) the server attempts transliteration to Devanagari to improve pronunciation.
     - Synthesis done by Azure Cognitive Services TTS API; falls back to `gTTS` if Azure is not configured or fails.

4. POST /transcribe

   - Request: multipart/form-data with `file` audio
   - Response: `{ "text": "transcript..." }`
   - Notes: Uses OpenAI Whisper (if configured) or other configured transcription service.

5. GET /tts-stream
   - WebSocket endpoint to stream text chunks for client-side TTS playback.

## Environment Variables

- `OPENAI_API_KEY` — OpenAI API key (required for language detection & transliteration features)
- `OPENAI_MODEL` — optional, default used in code (e.g., `gpt-4o-mini` or configured model)
- `AZURE_TTS_KEY` — Azure Cognitive Services key
- `AZURE_TTS_REGION` — Azure region (e.g., `eastus`)
- `AZURE_TTS_VOICE` — optional default voice name
- `BACKEND_PORT` — defaults to `2355` in `app.py`
- `FRONTEND_ORIGIN` — allowed origin for CORS (set by the app)

## How it Works (flow)

TTS request with `lang: "auto"`:

1. Client POSTs `{text, lang: 'auto'}` to `/tts`.
2. Server calls `detect_language(text)` (direct function call). This sends a small message to OpenAI and expects a JSON response like `{language: 'hi', dialect: 'hi'}`.
3. Server queries `azure_voices.db` for a good voice match via `get_voice_for_language`. If none found, it falls back to well-chosen default voices (en-US, hi-IN, mr-IN, etc.).
4. For Indic languages, if the input appears romanized, server transliterates with `transliterate_text(text, 'devanagari')` to ensure correct pronunciation.
5. Server constructs SSML with `xml:lang` and the chosen voice and sends it to Azure TTS API. If Azure is not configured, server falls back to `gTTS`.
6. Synthesized MP3 is returned directly to the client as `audio/mpeg`.

## Running Locally

Backend (Python 3.12+ recommended):

1. Create virtualenv and install requirements

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Set environment variables (example):

```bash
export OPENAI_API_KEY=sk_...
export AZURE_TTS_KEY=<your-azure-key>
export AZURE_TTS_REGION=eastus
export BACKEND_PORT=2355
```

3. Start backend

```bash
python3 app.py
```

Frontend (Next.js):

```bash
cd frontend-next
npm install
npm run dev
```

Open the frontend UI and use the Read Aloud / Play Server TTS buttons. They call `/tts` with `lang: 'auto'`.

## Testing

- Quick test script included: `test_detect.py` (calls `/detect-dialect` and `/tts` with `lang:auto` and saves sample MP3s under `/tmp`).

## Next Steps / Improvements

- Add unit tests and integration tests for detection/transliteration flows
- Add caching for recent detection results to reduce OpenAI calls and cost
- Add logging/metrics (request latencies, OpenAI errors, Azure TTS errors)
- Add a simple admin UI to preview voice samples from the `azure_voices.db`
- Add CI to validate basic endpoints and ensure no regressions

---

If you want, I can:

- Add a `README` section showing example responses and cURL snippets (I can append them now),
- Add a small script to sample and compare multiple Azure voices for a given language, or
- Implement caching for detection results and show a benchmark of latency improvements.

Tell me which follow-up you'd like and I'll add it next.
