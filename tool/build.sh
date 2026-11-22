#!/bin/sh
# Build the minified site CSS. Commit site/assets/css/site.css afterwards.
set -eu
cd "$(dirname "$0")/.."
command -v tailwindcss >/dev/null || { echo "tailwindcss not found: brew install tailwindcss" >&2; exit 1; }
tailwindcss -i src/input.css -o site/assets/css/site.css --minify
