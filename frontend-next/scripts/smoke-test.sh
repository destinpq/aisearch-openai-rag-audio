#!/usr/bin/env bash
# Simple smoke test for the frontend
set -euo pipefail
URL=${1:-http://127.0.0.1:45533/}
OUT=$(curl -sS "$URL" || true)
if echo "$OUT" | grep -q "AISearch Next" || echo "$OUT" | grep -q "Start Conversation"; then
  echo "SMOKE-PASS: Found expected content on $URL"
  exit 0
else
  echo "SMOKE-FAIL: expected content not found on $URL"
  echo "--- HTML (truncated) ---"
  echo "$OUT" | sed -n '1,200p'
  exit 2
fi
