#!/usr/bin/env python3
"""Render selected lines from actual k6 output files as readable PNG captures."""

from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUTPUT = ROOT / "screenshots"

CAPTURES = {
    "run-05vu.txt": "summary-05vu.png",
    "run-30vu.txt": "summary-30vu.png",
    "run-100vu.txt": "summary-100vu.png",
    "run-threshold-pass.txt": "summary-threshold-pass.png",
    "run-threshold-fail.txt": "summary-threshold-fail.png",
}

KEYS = (
    "execution:",
    "data_received",
    "data_sent",
    "http_req_duration",
    "http_req_failed",
    "http_reqs",
    "http_req_waiting",
    "http_req_connecting",
    "http_req_tls_handshaking",
    "iterations",
    "checks",
    "vus",
    "Тестийн үр дүн:",
    "thresholds on metrics",
    "ERRO[",
    "WARN[",
)


def load_font(size: int) -> ImageFont.ImageFont:
    candidates = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def selected_lines(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8", errors="replace").splitlines()
    selected = [line.rstrip() for line in raw if any(key in line for key in KEYS)]
    if not selected:
        selected = raw[-35:]
    # Keep a concise capture while preserving the requested percentile and rate rows.
    output: list[str] = []
    for line in selected:
        output.extend(textwrap.wrap(line, width=100, subsequent_indent="    ") or [""])
    return output[:45]


def render(source: Path, destination: Path) -> None:
    lines = selected_lines(source)
    title = f"k6 result capture  |  {source.name}"
    font = load_font(18)
    title_font = load_font(23)
    line_height = 29
    width = 1680
    height = 88 + max(1, len(lines)) * line_height + 35
    image = Image.new("RGB", (width, height), "#101820")
    draw = ImageDraw.Draw(image)
    draw.text((34, 22), title, font=title_font, fill="#f4f7fb")
    draw.line((34, 62, width - 34, 62), fill="#567080", width=2)
    y = 82
    for line in lines:
        draw.text((36, y), line, font=font, fill="#b9e6d3")
        y += line_height
    draw.text((36, height - 31), "Rendered from the matching raw k6 output file in results/.", font=load_font(14), fill="#9aaab5")
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination)


def main() -> int:
    missing = [name for name in CAPTURES if not (RESULTS / name).is_file()]
    if missing:
        raise SystemExit("PNG capture үүсгэхэд дараах k6 output дутуу байна: " + ", ".join(missing))
    for source_name, image_name in CAPTURES.items():
        render(RESULTS / source_name, OUTPUT / image_name)
        print(f"PNG capture үүслээ: screenshots/{image_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
