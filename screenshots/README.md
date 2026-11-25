# k6 summary captures

`bash scripts/run-lab.sh` ажиллуулахад k6-ийн тухайн удаагийн бодит текстэн summary мөрүүдийг PNG зураг болгон автоматаар дүрсэлнэ. Зураг бүр эх `results/*.txt` файлын тодорхойлогч нэрийг харуулна. Эдгээр PNG нь summary мөрүүдийн уншихад хялбар визуал capture бөгөөд эх текстэн гаралтыг орлохгүй.

Үүсэх зургууд:

- `summary-05vu.png`
- `summary-30vu.png`
- `summary-100vu.png`
- `summary-threshold-pass.png`
- `summary-threshold-fail.png`

Эх k6-ийн бүрэн гаралт `results/` хавсанд байна.
