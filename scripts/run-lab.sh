#!/usr/bin/env bash
set -Eeuo pipefail
# Run the complete k6 lab and render the real summary captures.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
mkdir -p results screenshots

if ! command -v k6 >/dev/null 2>&1; then
  echo "Алдаа: k6 олдсонгүй. README.md дэх Ubuntu/WSL2 суулгах зааврыг дагана уу." >&2
  exit 127
fi
if ! command -v node >/dev/null 2>&1; then
  echo "Алдаа: Node.js олдсонгүй. Локал серверийн тестэд Node.js хэрэгтэй." >&2
  exit 127
fi

k6 version 2>&1 | tee results/k6-version.txt

run_k6() {
  local output_file="$1"
  shift
  echo "\n===== $output_file ====="
  "$@" 2>&1 | tee "results/$output_file"
}

# Алхам 2: 5 VU / 30 секунд — baseline.
run_k6 run-baseline.txt k6 run scripts/smoke.js

# Алхам 3: хүснэгтийн гурван түвшинг тус тусад нь ажиллуулна.
run_k6 run-05vu.txt k6 run --vus 5 --duration 1m scripts/smoke.js
run_k6 run-30vu.txt k6 run --vus 30 --duration 1m scripts/smoke.js
run_k6 run-100vu.txt k6 run --vus 100 --duration 1m scripts/smoke.js

# Stages тестийн summary тусдаа хадгалагдана.
run_k6 run-stages.txt k6 run scripts/stages.js

# Алхам 5: зөвхөн өөрийн локал сервер рүү тест хийнэ.
node server/server.js > results/local-server.log 2>&1 &
SERVER_PID=$!
cleanup() {
  kill "$SERVER_PID" >/dev/null 2>&1 || true
  wait "$SERVER_PID" 2>/dev/null || true
}
trap cleanup EXIT

server_ready=0
for attempt in $(seq 1 30); do
  if curl --silent --fail http://127.0.0.1:3000/health >/dev/null; then
    server_ready=1
    break
  fi
  sleep 0.2
done
if [[ "$server_ready" -ne 1 ]]; then
  echo "Локал сервер ассангүй. results/local-server.log файлыг шалгана уу." >&2
  exit 1
fi

run_k6 run-local-baseline.txt k6 run scripts/local-baseline.js
BASELINE_P95="$(python3 scripts/extract-p95.py results/run-local-baseline.txt)"
echo "Локал baseline p95: ${BASELINE_P95} ms"

run_k6 run-threshold-pass.txt env BASELINE_P95="$BASELINE_P95" k6 run scripts/threshold-pass.js
echo "Тестийн үр дүн: PASS" | tee -a results/run-threshold-pass.txt

# Энэ тест FAIL болох нь зориудын: /slow ойролцоогоор 100ms, харин босго 50ms.
echo "\n===== run-threshold-fail.txt (expected FAIL) ====="
set +e
k6 run scripts/threshold-fail.js 2>&1 | tee results/run-threshold-fail.txt
fail_status=${PIPESTATUS[0]}
set -e
if [[ "$fail_status" -eq 0 ]]; then
  echo "АНХААР: threshold-fail.js амжилттай дууслаа. /slow endpoint болон threshold-ийг шалгана уу." | tee -a results/run-threshold-fail.txt
  exit 1
fi
echo "Тестийн үр дүн: FAIL (хүлээгдсэн, exit code $fail_status)." | tee -a results/run-threshold-fail.txt

python3 scripts/generate-report.py
python3 scripts/render-summary-captures.py
echo "\nБүх хэмжилтийн текст results/ хавтсанд хадгалагдлаа. Screenshot-уудыг screenshots/ хавтсанд нэмнэ үү."
