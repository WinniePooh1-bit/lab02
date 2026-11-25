#!/usr/bin/env python3
"""k6 summary файлуудаас харьцуулсан хүснэгт, 9 өгүүлбэртэй дүгнэлт үүсгэнэ."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def find_metric_line(text: str, metric: str) -> str:
    for line in text.splitlines():
        if re.match(rf"^\s*{re.escape(metric)}\s*\.+\s*:", line):
            return line
    raise ValueError(f"{metric} мөр олдсонгүй")


def parse_summary(filename: str) -> dict[str, str]:
    path = RESULTS / filename
    if not path.is_file():
        raise FileNotFoundError(f"Үр дүнгийн файл алга: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    duration_line = find_metric_line(text, "http_req_duration")
    requests_line = find_metric_line(text, "http_reqs")
    failed_line = find_metric_line(text, "http_req_failed")

    p90 = re.search(r"p\(90\)=([0-9.]+\s*[A-Za-zµμ]*)", duration_line)
    p95 = re.search(r"p\(95\)=([0-9.]+\s*[A-Za-zµμ]*)", duration_line)
    throughput = re.search(r"([0-9]+(?:\.[0-9]+)?)/s", requests_line)
    error_rate = re.search(r"([0-9]+(?:\.[0-9]+)?)%", failed_line)
    if not all((p90, p95, throughput, error_rate)):
        raise ValueError(f"{filename}: p90/p95/throughput/error rate-ийг бүрэн уншиж чадсангүй")

    return {
        "p90": p90.group(1).strip(),
        "p95": p95.group(1).strip(),
        "throughput": f"{throughput.group(1)}/s",
        "error_rate": f"{error_rate.group(1)}%",
    }


def threshold_status(filename: str) -> str:
    path = RESULTS / filename
    if not path.is_file():
        return "Үр дүн алга"
    text = path.read_text(encoding="utf-8", errors="replace")
    if "Тестийн үр дүн: PASS" in text:
        return "PASS"
    if "Тестийн үр дүн: FAIL" in text:
        return "FAIL (хүлээгдсэн)" if "threshold-fail" in filename else "FAIL"
    return "Гаралтыг шалгана уу"


def main() -> int:
    try:
        rows = {level: parse_summary(f"run-{level}vu.txt") for level in ("05", "30", "100")}
        local_baseline = parse_summary("run-local-baseline.txt")
        pass_result = threshold_status("run-threshold-pass.txt")
        fail_result = threshold_status("run-threshold-fail.txt")
    except (FileNotFoundError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1

    sentences = [
        f"5 VU үед p90 {rows['05']['p90']}, p95 {rows['05']['p95']}, throughput {rows['05']['throughput']}, error rate {rows['05']['error_rate']} байв.",
        f"30 VU үед p90 {rows['30']['p90']}, p95 {rows['30']['p95']}, throughput {rows['30']['throughput']}, error rate {rows['30']['error_rate']} байв.",
        f"100 VU үед p90 {rows['100']['p90']}, p95 {rows['100']['p95']}, throughput {rows['100']['throughput']}, error rate {rows['100']['error_rate']} байв.",
        f"5-аас 100 VU хүртэл өсгөхөд p95 latency {rows['05']['p95']}-ээс {rows['100']['p95']} болж өөрчлөгдсөн.",
        f"Энэ хугацаанд throughput {rows['05']['throughput']}-ээс {rows['100']['throughput']} болсон нь серверийн нийт хүсэлт боловсруулах хурдыг харуулж байна.",
        f"100 VU үеийн error rate {rows['100']['error_rate']} байсан тул хүсэлтүүдийн алдааны түвшнийг мөн latency-тай хамт үнэлэх шаардлагатай.",
        f"Локал /health endpoint-ийн 5 VU baseline p95 {local_baseline['p95']} байсан бөгөөд PASS тестийн босгыг энэ хэмжилтийн 1.5 дахин ихээр тогтоосон.",
        f"Threshold PASS туршилтын бүртгэгдсэн төлөв: {pass_result}.",
        f"100 ms орчим сааталтай /slow endpoint-д p95 < 50 ms босго тавьсан зориудын туршилтын төлөв: {fail_result}; энэ нь SLO quality gate FAIL-ийг илрүүлэх ёстойг харуулна.",
    ]

    output = [
        "# Хэмжилтийн тайлангийн хураангуй",
        "",
        "| VU | p90 latency | p95 latency | Throughput | Error rate |",
        "|---:|---:|---:|---:|---:|",
    ]
    for level, label in (("05", "5"), ("30", "30"), ("100", "100")):
        data = rows[level]
        output.append(f"| {label} | {data['p90']} | {data['p95']} | {data['throughput']} | {data['error_rate']} |")
    output += ["", "## Дүгнэлт", ""]
    output.extend(f"{index}. {sentence}" for index, sentence in enumerate(sentences, start=1))
    output += ["", "## Анхаарах нь", "", "Энэ хураангуй нь results/ хавтас дахь k6-ийн текст гаралтаас автоматаар үүссэн. README-д оруулахын өмнө эх файлуудтай нь тулгаж шалгана.", ""]

    report_text = "\n".join(output)
    destination = RESULTS / "report-summary.md"
    destination.write_text(report_text, encoding="utf-8")

    readme_path = ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    start_marker = "<!-- AUTO-RESULTS-START -->"
    end_marker = "<!-- AUTO-RESULTS-END -->"
    if start_marker in readme and end_marker in readme:
        before, remaining = readme.split(start_marker, 1)
        _, after = remaining.split(end_marker, 1)
        embedded_report = report_text.split("\n", 2)[2].strip()
        readme_path.write_text(
            before + start_marker + "\n\n" + embedded_report + "\n\n" + end_marker + after,
            encoding="utf-8",
        )

    print(f"Тайлангийн хураангуй үүслээ: {destination.relative_to(ROOT)}; README.md-ийн хүснэгт шинэчлэгдлээ.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
