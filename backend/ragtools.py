"""RAG tools: minimal streaming interface.

Provides `stream_query(query)` which yields strings (tokens/chunks).
If OPENAI_API_KEY is set, uses OpenAI's streaming HTTP API; otherwise falls back to a dummy generator.
"""
import os
import time
import json
import asyncio
from typing import AsyncIterator

import openai
import httpx
from concurrent.futures import ThreadPoolExecutor


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def _parse_event_for_text(obj) -> str | None:
    try:
        if isinstance(obj, str):
            return obj
        if isinstance(obj, dict):
            # direct fields
            if 'text' in obj and isinstance(obj['text'], str):
                return obj['text']
            if 'content' in obj and isinstance(obj['content'], str):
                return obj['content']
            # choices/delta style
            if 'choices' in obj and isinstance(obj['choices'], list):
                parts = []
                for choice in obj['choices']:
                    if isinstance(choice, dict) and 'delta' in choice and isinstance(choice['delta'], dict):
                        d = choice['delta']
                        if 'content' in d:
                            parts.append(str(d['content']))
                        elif 'text' in d:
                            parts.append(str(d['text']))
                if parts:
                    return ''.join(parts)
            # responses output
            if 'output' in obj and isinstance(obj['output'], list):
                parts = []
                for out in obj['output']:
                    if isinstance(out, dict):
                        if 'content' in out:
                            parts.append(str(out['content']))
                        elif 'text' in out:
                            parts.append(str(out['text']))
                if parts:
                    return ''.join(parts)
    except Exception:
        return None
    return None


async def stream_query(q: str) -> AsyncIterator[str]:
    """Yield chunks for a query using OpenAI's chat completions streaming API."""
    if OPENAI_API_KEY:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": OPENAI_MODEL,
            "messages": [{"role": "user", "content": q}],
            "stream": True
        }
        async with httpx.AsyncClient(timeout=None) as client:
            try:
                async with client.stream("POST", url, json=payload, headers=headers) as resp:
                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        if line.startswith("data: "):
                            chunk = line[len("data: "):]
                        else:
                            chunk = line
                        if chunk.strip() == "[DONE]":
                            return
                        try:
                            obj = json.loads(chunk)
                            if "choices" in obj and obj["choices"]:
                                choice = obj["choices"][0]
                                if "delta" in choice and "content" in choice["delta"]:
                                    yield choice["delta"]["content"]
                        except Exception:
                            pass
                return
            except Exception as e:
                print(f"OpenAI API error: {e}")
                pass

    # Final fallback: simulated chunks for dev
    i = 1
    while True:
        yield f"Simulated answer for '{q}' (chunk {i})"
        i += 1
        await asyncio.sleep(0.5)
