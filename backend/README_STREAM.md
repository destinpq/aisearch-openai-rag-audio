Local streaming README

Required env vars for streaming:

- OPENAI_API_KEY (optional): set to enable real streaming from OpenAI Responses API.
- OPENAI_MODEL (optional): model id to use for streaming (default: gpt-4o-mini).
- FRONTEND_ORIGIN (optional): origin allowed for CORS (default: http://localhost:45533)

Install deps and run:

```bash
. .venv/bin/activate
pip install -r backend/requirements.txt
# optional: export OPENAI_API_KEY="sk-..."
export FRONTEND_ORIGIN="http://localhost:45533"
python backend/app.py
```

Smoke test (no API key required):

```bash
python backend/test_stream.py
```

Notes:

- The streaming implementation attempts the Responses API (stream=true). If your provider uses a different format, update `backend/ragtools.py` parsing accordingly.
