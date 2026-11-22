#!/usr/bin/env python3
"""Render the link-preview (Open Graph) images with headless Chrome (stdlib only).

Source: og/card.html (one template, variant by URL hash). Output: site/assets/img/og-<variant>.jpg,
1200x630 JPEG, referenced by og:image on each page. Re-run after changing the card, the name,
the role or the services rate.

Needs Google Chrome (/Applications/Google Chrome.app) and macOS sips.
Usage: python3 tool/make_og.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARD = ROOT / "og" / "card.html"
OUT = ROOT / "site" / "assets" / "img"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
VARIANTS = ["cv", "services"]
W, H = 1200, 630


def render(variant: str, tmp: Path) -> Path:
    png = tmp / f"og-{variant}.png"
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
         "--allow-file-access-from-files", f"--window-size={W},{H}", "--virtual-time-budget=2000",
         f"--screenshot={png}", f"{CARD.as_uri()}#{variant}"],
        check=True, capture_output=True,
    )
    jpg = OUT / f"og-{variant}.jpg"
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "86", str(png), "--out", str(jpg)],
                   check=True, capture_output=True)
    return jpg


def main() -> int:
    if not Path(CHROME).exists():
        print(f"Chrome not found at {CHROME}", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as t:
        for v in VARIANTS:
            jpg = render(v, Path(t))
            print(f"wrote {jpg.relative_to(ROOT)} ({jpg.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
