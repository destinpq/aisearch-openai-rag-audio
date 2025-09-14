# Frontend changes — summary

This file summarizes recent frontend changes for maintainers.

- Replaced a global `globals.css` with per-component CSS Modules.
- Added `app/tw-input.css` as Tailwind input and a `prebuild` script to compile
  `public/tw.css` so the app has a fallback CSS file when started via PM2.
- Implemented a controlled `SearchForm` and a `SearchClient` wrapper that
  supports a "Start Conversation" button and a microphone button that uses
  browser SpeechRecognition (webkitSpeechRecognition/SpeechRecognition).
- Hardened SpeechRecognition handling (interim/final results, onend/onerror,
  stop on unmount). Final transcripts auto-trigger a search.
- Added a smoke-test script `scripts/smoke-test.sh` and an npm script
  `npm run smoke-test` to verify the frontend serves expected content.
- Removed the experimental `appDir` key from `next.config.js` to silence
  noisy Next warnings in PM2 logs.

How to smoke-test locally

1. Ensure the frontend is running (PM2 or `npm start`).
2. Run `npm run smoke-test` inside `frontend-next`.
