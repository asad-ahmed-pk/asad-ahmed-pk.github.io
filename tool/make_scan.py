#!/usr/bin/env python3
"""Generate site/assets/img/scan.svg: a stylised lidar sweep for the hero (stdlib only).

Ground returns are concentric rings around the sensor, drawn in perspective (ellipses).
A few obstacles block the rings behind them and show up as vertical "walls" of returns,
coloured by height like a typical point-cloud viewer. Deterministic: same output every run.
Colours match the tokens in src/input.css (an <img> cannot read CSS variables).

Usage: python3 tool/make_scan.py
"""
from __future__ import annotations

import math
import random
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "site" / "assets" / "img" / "scan.svg"

W, H = 1200, 640
CX, CY = 600, 380          # sensor position
SQUASH = 0.36              # ellipse ry / rx: viewing angle
RINGS = [34 + i * 34 * (1 + i * 0.07) for i in range(15)]

GROUND = "#5fd4e6"         # --color-cyan
HEIGHT = ["#ffb03b", "#ff8a3d", "#ff6b6b"]  # --color-amber -> --color-axis-x by height

# Obstacles: (start angle deg, end angle deg, range px, height in beams). Angle 0 = right, 90 = towards viewer.
OBSTACLES = [
    (200, 232, 210, 5),    # car, back left
    (300, 318, 330, 7),    # van, back right
    (338, 352, 150, 4),    # post / pedestrian, right
    (118, 140, 260, 4),    # kerb object, front left
    (20, 44, 420, 6),      # building corner, far right front
]

def blocked(angle: float, r: float) -> tuple[float, int] | None:
    for a1, a2, d, h in OBSTACLES:
        if a1 <= angle <= a2 and r > d:
            return d, h
    return None

def point(angle: float, r: float) -> tuple[float, float]:
    a = math.radians(angle)
    return CX + r * math.cos(a), CY + r * math.sin(a) * SQUASH

def main() -> None:
    rnd = random.Random(7)
    groups: dict[tuple[str, float, float], list[str]] = defaultdict(list)

    def dot(x: float, y: float, rad: float, col: str, op: float) -> None:
        if -4 < x < W + 4 and -4 < y < H + 4:
            groups[(col, round(op, 1), round(rad * 2) / 2)].append(f'<circle cx="{x:.0f}" cy="{y:.0f}"/>')

    # Ground rings
    for i, r in enumerate(RINGS):
        n = max(24, int(2 * math.pi * r / 13))
        for k in range(n):
            ang = k * 360 / n + rnd.uniform(-.4, .4)
            if blocked(ang, r):
                continue
            x, y = point(ang, r + rnd.uniform(-1.2, 1.2))
            far = math.sin(math.radians(ang)) < 0     # back half of the ellipse
            fade = 1 - i / len(RINGS)
            op = (0.22 + 0.6 * fade) * (0.62 if far else 1)
            rad = 1.25 + 0.9 * fade
            dot(x, y, rad, GROUND, op)

    # Obstacle walls: vertical stacks of returns at the obstacle range
    for a1, a2, d, h in OBSTACLES:
        steps = max(4, int((a2 - a1) * d / 260))
        for s in range(steps + 1):
            ang = a1 + (a2 - a1) * s / steps
            x, y = point(ang, d + rnd.uniform(-2, 2))
            for b in range(h):
                if rnd.random() < 0.12:
                    continue
                col = HEIGHT[min(len(HEIGHT) - 1, b * len(HEIGHT) // h)]
                op = 0.95 - b * 0.07
                dot(x, y - b * 7.5, 2, col, op)

    # Sensor at the origin: a small coordinate frame (ROS TF colours: x red, y green, z blue)
    frame = (
        f'<g stroke-width="2.5" stroke-linecap="round">'
        f'<line x1="{CX}" y1="{CY}" x2="{CX + 34}" y2="{CY + 8}" stroke="#ff6b6b"/>'
        f'<line x1="{CX}" y1="{CY}" x2="{CX - 22}" y2="{CY + 12}" stroke="#5ee08a"/>'
        f'<line x1="{CX}" y1="{CY}" x2="{CX}" y2="{CY - 34}" stroke="#6aa8ff"/>'
        f'</g><circle cx="{CX}" cy="{CY}" r="4" fill="#e9eef0"/>'
    )

    body = "".join(
        f'<g fill="{c}" opacity="{o}">' + "".join(d.replace("/>", f' r="{r:g}"/>') for d in ds) + "</g>"
        for (c, o, r), ds in sorted(groups.items())
    )
    count = sum(len(ds) for ds in groups.values())
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{body}{frame}</svg>\n'
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT.relative_to(OUT.parents[3])} ({count} points, {len(svg) // 1024} KB)")

if __name__ == "__main__":
    main()
