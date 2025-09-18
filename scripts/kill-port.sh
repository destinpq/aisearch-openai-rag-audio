#!/usr/bin/env bash
# Kill any process listening on the given port (first arg)
PORT=${1:-}
if [ -z "$PORT" ]; then
  echo "Usage: $0 <port>" >&2
  exit 1
fi
# macOS and Linux compatible using lsof
PIDS=$(lsof -iTCP:"$PORT" -sTCP:LISTEN -t || true)
if [ -n "$PIDS" ]; then
  echo "Killing processes on port $PORT: $PIDS"
  kill -9 $PIDS || true
else
  echo "No process listening on port $PORT"
fi
