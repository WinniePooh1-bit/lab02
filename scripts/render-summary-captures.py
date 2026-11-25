#!/usr/bin/env python3
"""Render selected lines from actual k6 summary output files as readable PNG captures."""

from __future__ import annotations

import re
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

SUMMARY_RE = re.compile(
    r"^\\s*(?:checks_total|checks_succeeded|checks_failed|http_req_duration|"
    r"http_req_failed|http_reqs|http_req_waiting|http_req_connecting|"
    r"http_req_tls_handshaking|iteration_duration|iterations|vus_max|vus|"
    r"data_received|data_sent)\\b"
)
HEADER_RE = re.compile(
    r"^\\s*(?:█\\s*TOTAL RESULTS|HTTP$|EXECUTION$|NETWORK$|"
    r"thresholds on metrics|time=|Тестийн үр дүн:|[✓✗]\\s*')"
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
    selected = [
        line.rstrip()
        for line in raw
        if SUMMARY_RE.search(line) or HEADER_RE.search(line)
    ]
    output: list[str] = []
    for line in selected:
        output.extend(textwrap.wrap(line, width=112, subsequent_indent="    ") or [""])
    return output


def render(source: Path, destination: Path) -> None:
    lines = selected_lines(source)
    title_font = load_font(23)
    body_font = load_font(18)
    footer_font = load_font(14)
    line_height = 31
    width = 1600
    height = 100 + max(1, len(lines)) * line_height + 38

    image = Image.new("RGB", (width, height), "#101820")
    draw = ImageDraw.Draw(image)
    draw.text((36, 24), f"k6 measured summary  |  {source.name}", font=title_font, fill="#f4f7fb")
    draw.line((36, 70, width - 36, 70), fill="#567080", width=2)

    y = 91
    for line in lines:
        draw.text((38, y), line, font=body_font, fill="#b9e6d3")
        y += line_height

    draw.text(
        (38, height - 28),
        "Extracted from the corresponding complete k6 text output.",
        font=footer_font,
        fill="#9aaab5",
    )

    # Reduce the PNG size without removing the metric text.
    image = image.quantize(colors=64, method=Image.Quantize.FASTOCTREE)
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, optimize=True)


def main() -> int:
    missing = [name for name in CAPTURES if not (RESULTS / name).is_file()]
    if missing:
        raise SystemExit("PNG capture үүсгэхэд дараах k6 output дутуу байна: " + ", ".join(missing))

    for source_name, image_name in CAPTURES.items():
        destination = OUTPUT / image_name
        render(RESULTS / source_name, destination)
        print(f"PNG summary capture үүслээ: screenshots/{image_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
