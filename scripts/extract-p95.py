#!/usr/bin/env python3
"""k6 summary текстээс p(95)-ийг олж миллисекундээр хэвлэнэ."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Хэрэглээ: python3 scripts/extract-p95.py results/run-local-baseline.txt", file=sys.stderr)
        return 2

    summary_path = Path(sys.argv[1])
    if not summary_path.is_file():
        print(f"Файл олдсонгүй: {summary_path}", file=sys.stderr)
        return 2

    content = summary_path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"p\(95\)\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*(ns|µs|μs|us|ms|s)?", content)
    if not match:
        print("Summary дотроос p(95) олдсонгүй. k6-ийн бүрэн гаралтыг шалгана уу.", file=sys.stderr)
        return 1

    value = float(match.group(1))
    unit = match.group(2) or "ms"
    to_ms = {"ns": 1e-6, "µs": 1e-3, "μs": 1e-3, "us": 1e-3, "ms": 1.0, "s": 1000.0}
    print(f"{value * to_ms[unit]:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
