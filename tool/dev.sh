#!/bin/sh
# Local dev: Tailwind watch (minified, same output as build.sh) + static server on :8126.
set -eu
cd "$(dirname "$0")/.."
command -v tailwindcss >/dev/null || { echo "tailwindcss not found: brew install tailwindcss" >&2; exit 1; }
PORT="${PORT:-8126}"
if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port $PORT is already in use (another dev server or preview?)." >&2
  echo "Stop it, or run on another port: PORT=8127 tool/dev.sh" >&2
  exit 1
fi
tailwindcss -i src/input.css -o site/assets/css/site.css --minify --watch=always &
WATCH=$!
trap 'kill $WATCH 2>/dev/null' EXIT INT TERM
python3 tool/serve.py "$PORT"
