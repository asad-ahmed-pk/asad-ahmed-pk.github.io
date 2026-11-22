#!/usr/bin/env python3
"""Local static server for site/ that behaves like GitHub Pages (stdlib only).

- clean URLs: /support serves support.html
- unknown paths get 404.html with status 404
Usage: python3 tool/serve.py [port]   (default 8126, bound to 127.0.0.1)
"""
from __future__ import annotations

import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

SITE = Path(__file__).resolve().parent.parent / "site"


class Handler(SimpleHTTPRequestHandler):
    def send_head(self):
        parts = urlsplit(self.path)
        path = unquote(parts.path)
        target = SITE / path.lstrip("/")
        if not target.exists() and not path.endswith("/") and (SITE / (path.lstrip("/") + ".html")).is_file():
            self.path = path + ".html" + (f"?{parts.query}" if parts.query else "")
        elif not target.exists():
            return self.not_found()
        return super().send_head()

    def not_found(self):
        page = SITE / "404.html"
        if not page.is_file():
            self.send_error(404)
            return None
        body = page.read_bytes()
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)
        return None


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8126
    server = ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=str(SITE)))
    print(f"Serving site/ on http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
