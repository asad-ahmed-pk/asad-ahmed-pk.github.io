#!/usr/bin/env python3
"""Site checks (stdlib only). Run from anywhere: python3 tool/check.py

- internal links, assets and #fragments resolve (clean URLs: /support -> support.html)
- no third-party resources (scripts, styles, images, fonts, media, iframes)
- every <img> has alt, width and height; exactly one <h1> per page
- shared <header> / <footer> markup is identical on every page that has one
- site/assets/css/site.css matches a fresh Tailwind build
- no inline style attributes (styles live in src/input.css)
- no unfilled placeholders (RATE-TODO and other *-TODO markers)
Exit code 1 on any failure. Set SKIP_CSS=1 to skip the Tailwind freshness check (CI without Tailwind).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
CSS_OUT = SITE / "assets" / "css" / "site.css"
RESOURCE_ATTRS = {
    ("script", "src"), ("img", "src"), ("img", "srcset"), ("source", "src"),
    ("source", "srcset"), ("video", "src"), ("video", "poster"), ("audio", "src"),
    ("iframe", "src"), ("embed", "src"), ("object", "data"),
}
LINK_RESOURCE_RELS = {"stylesheet", "preload", "modulepreload", "icon", "apple-touch-icon", "manifest"}

errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[tuple[str, str, bool]] = []  # (tag, url, is_resource)
        self.ids: set[str] = set()
        self.h1 = 0
        self.imgs: list[dict[str, str | None]] = []
        self.inline_styles = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "style" in a:
            self.inline_styles += 1
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "h1":
            self.h1 += 1
        if tag == "img":
            self.imgs.append(a)
        if tag == "a" and a.get("href"):
            self.refs.append((tag, a["href"], False))
        if tag == "link" and a.get("href"):
            rels = set((a.get("rel") or "").lower().split())
            self.refs.append((tag, a["href"], bool(rels & LINK_RESOURCE_RELS)))
        for t, attr in RESOURCE_ATTRS:
            if tag == t and a.get(attr):
                if attr.endswith("srcset"):
                    for part in a[attr].split(","):
                        url = part.strip().split(" ")[0]
                        if url:
                            self.refs.append((tag, url, True))
                else:
                    self.refs.append((tag, a[attr], True))

    handle_startendtag = handle_starttag


def resolve(page: Path, path: str) -> Path | None:
    base = SITE if path.startswith("/") else page.parent
    target = (base / path.lstrip("/")).resolve()
    candidates = [target, target.with_name(target.name + ".html"), target / "index.html"]
    if path in ("", "/"):
        candidates = [SITE / "index.html"]
    for c in candidates:
        if c.is_file() and SITE.resolve() in c.parents:
            return c
    return None


def block(html: str, tag: str) -> str | None:
    m = re.search(rf"<{tag}\b.*?</{tag}>", html, re.S)
    if not m:
        return None
    text = re.sub(r'\s+aria-current="[^"]*"', "", m.group(0))
    return re.sub(r"\s+", " ", text).strip()


def check_pages() -> None:
    pages = sorted(SITE.rglob("*.html"))
    if not pages:
        fail("no HTML pages in site/")
        return
    parsed: dict[Path, Page] = {}
    sources: dict[Path, str] = {}
    for p in pages:
        src = p.read_text(encoding="utf-8")
        sources[p] = src
        parser = Page()
        parser.feed(src)
        parsed[p] = parser

    for p, pg in parsed.items():
        rel = p.relative_to(ROOT)
        if pg.h1 != 1:
            fail(f"{rel}: {pg.h1} <h1> elements (want exactly 1)")
        for m in sorted(set(re.findall(r"\b[A-Z]+-TODO\b", sources[p]))):
            fail(f"{rel}: unfilled placeholder {m}")
        if pg.inline_styles:
            fail(f"{rel}: {pg.inline_styles} inline style attribute(s); use classes")
        for img in pg.imgs:
            name = img.get("src", "?")
            for attr in ("alt", "width", "height"):
                if img.get(attr) is None:
                    fail(f"{rel}: <img src={name}> missing {attr}")
        for tag, url, is_resource in pg.refs:
            parts = urlsplit(url)
            if parts.scheme in ("mailto", "tel", "data"):
                continue
            if parts.scheme or url.startswith("//"):
                if is_resource:
                    fail(f"{rel}: third-party resource <{tag}> {url}")
                continue
            target = p if not parts.path else resolve(p, parts.path)
            if target is None:
                fail(f"{rel}: broken link <{tag}> {url}")
                continue
            if parts.fragment and target.suffix == ".html":
                if parts.fragment not in parsed[target].ids:
                    fail(f"{rel}: missing #{parts.fragment} in {target.relative_to(ROOT)}")

    for tag in ("header", "footer"):
        blocks = {p: block(src, tag) for p, src in sources.items()}
        present = {p: b for p, b in blocks.items() if b is not None}
        if len(set(present.values())) > 1:
            names = ", ".join(str(p.relative_to(SITE)) for p in present)
            fail(f"<{tag}> markup differs between pages ({names}); keep it identical")


def check_css() -> None:
    if os.environ.get("SKIP_CSS"):
        return
    exe = shutil.which("tailwindcss")
    if not exe:
        fail("tailwindcss not installed (brew install tailwindcss); cannot verify site.css")
        return
    if not CSS_OUT.is_file():
        fail("site/assets/css/site.css missing: run tool/build.sh")
        return
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "site.css"
        r = subprocess.run([exe, "-i", "src/input.css", "-o", str(out), "--minify"],
                           cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            fail(f"tailwind build failed:\n{r.stderr.strip()}")
            return
        if out.read_bytes() != CSS_OUT.read_bytes():
            fail("site/assets/css/site.css is stale: run tool/build.sh and commit it")


def main() -> int:
    check_pages()
    check_css()
    if errors:
        print(f"check: {len(errors)} problem(s)")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"check: ok ({len(list(SITE.rglob('*.html')))} pages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
