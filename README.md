# Лабораторийн ажил №2 — k6-аар гүйцэтгэлийн хэмжүүр хэмжих

**Оюутан:** М.Наранбат  
**Оюутны код:** B242270801  
**Хичээл:** F.CSA313 — Программ хангамжийн чанарын баталгаа ба тест (2026)

## Зорилго

Энэ лабораторид Grafana k6 ашиглан HTTP серверт ачааллын тест хийж, latency (p90, p95), throughput болон error rate хэмжинэ. Ачааллыг 5, 30, 100 зэрэгцээ хэрэглэгч (VU) болгон тус тусад нь туршиж, дараа нь stages ашиглан өсгөж буулгана. Мөн хэмжсэн baseline-д тулгуурласан SLO threshold-ийн PASS болон зориудын FAIL үр дүнг шалгана.

## Аюулгүй ажиллагаа

Гадаад тестийг зөвхөн зааварт зөвшөөрсөн https://test.k6.io/ хаяг руу явуулна. Бусдын болон сургуулийн бодит вебсайт руу load test хийхгүй. Нэмэлт threshold туршилтууд зөвхөн өөрийн компьютерт ажиллах 127.0.0.1:3000 локал сервер рүү чиглэнэ.

## Орчны тохиргоо

Зааварт Ubuntu Linux орчин санал болгосон. Windows ашиглаж байгаа бол WSL2 дотор Ubuntu нээгээд k6 суулгана:

~~~bash
sudo apt-get install -y ca-certificates curl gnupg
curl -fsSL https://dl.k6.io/key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/k6-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update && sudo apt-get install -y k6
k6 version
~~~

Локал сервер ажиллуулахад Node.js, гаралтыг боловсруулахад Python 3, серверийн бэлэн эсэхийг шалгахад curl хэрэгтэй. Сервер нь нэмэлт сан ашиглахгүй, Node.js-ийн http модулийг хэрэглэнэ.

## Тест ажиллуулах

Репозиторыг өөрийн компьютерт clone хийгээд төслийн хавтас руу орно:

~~~bash
git clone https://github.com/WinniePooh1-bit/lab02.git
cd lab02
~~~

Бүх туршилтыг дарааллаар нь ажиллуулж, k6-ийн бүтэн текст гаралтыг results/ хавсанд хадгалах:

~~~bash
bash scripts/run-lab.sh
~~~

Скрипт дараах туршилтуудыг тус тусад нь гүйцэтгэнэ.

| Файл | Туршилт |
|---|---|
| results/k6-version.txt | Ашигласан k6 хувилбар |
| results/run-baseline.txt | Алхам 2 — test.k6.io, 5 VU, 30 секунд baseline |
| results/run-05vu.txt | 5 VU, 1 минут |
| results/run-30vu.txt | 30 VU, 1 минут |
| results/run-100vu.txt | 100 VU, 1 минут |
| results/run-stages.txt | 5 → 30 → 100 → 0 VU шаталсан ачаалал |
| results/run-local-baseline.txt | Локал /health endpoint-ийн 5 VU baseline |
| results/run-threshold-pass.txt | Локал baseline-д үндэслэсэн SLO threshold |
| results/run-threshold-fail.txt | /slow endpoint дээрх санаатай хатуу босгын FAIL |
| results/report-summary.md | Хэмжилтээс автоматаар гаргасан хүснэгт, дүгнэлт |

5, 30, 100 VU туршилтуудыг нэг stages ажиллуулалтын summary-гаас салгаж тооцохгүй. Гурван түвшин тус бүрд тусдаа ажиллуулсан үр дүнг README-ийн хүснэгтэд оруулна. scripts/generate-report.py нь бодит summary текстээс p90, p95, throughput, error rate-ийг уншаад хүснэгт болон 9 өгүүлбэртэй дүгнэлтийг энэ README-д автоматаар оруулна.

## Хэмжүүрүүд

- **Latency:** http_req_duration хэмжүүрийн p(90) болон p(95) утга. Эдгээр нь хүсэлтүүдийн 90%, 95% нь тухайн хугацаанаас бага хугацаанд хариу авсныг харуулна.
- **Throughput:** http_reqs мөрийн секундэд ногдох хүсэлтийн тоо (/s).
- **Error rate:** http_req_failed хэмжүүрийн хувь. Энэ лабораторид лекцэд үзсэн POFOD ойлголттой харьцуулан тайлбарлана.
- **VU:** зэрэг ажиллаж буй виртуал хэрэглэгчийн тоо.

## SLO ба threshold

threshold-pass.js нь локал /health endpoint дээр 5 VU-ээр хэмжсэн өөрийн baseline-ийн p95 утгыг BASELINE_P95 хувьсагчаар авна. p95 босгыг тухайн baseline × 1.5, http_req_failed босгыг 1%-иас бага байхаар тогтооно. Ийнхүү дурын 300ms зэрэг жишээ тоог шууд хуулалгүй, ижил target дээрх бодит baseline-д тулгуурлана. /slow endpoint нь ойролцоогоор 100ms саатал үүсгэдэг тул түүнд p(95)<50 босго тавьсан threshold-fail.js санаатайгаар FAIL болох ёстой.

test.k6.io-ийн baseline болон локал серверийн baseline нь өөр target тул latency-ийн тоонуудыг хооронд нь шууд харьцуулахгүй. Тайланд аль хэмжилт ямар target дээр хийгдсэнийг тодорхой бичнэ.

## Хэмжилтийн үр дүн

bash scripts/run-lab.sh амжилттай дууссаны дараа доорх хэсэг автоматаар шинэчлэгдэнэ. README-д оруулах тоонуудыг results/*.txt доторх k6-ийн бүрэн гаралттай тулгаж шалгана.

<!-- AUTO-RESULTS-START -->

| VU | p90 latency | p95 latency | Throughput | Error rate |
|---:|---:|---:|---:|---:|
| 5 | 62.3ms | 62.45ms | 9.357544/s | 0.00% |
| 30 | 62.72ms | 63.24ms | 56.037821/s | 0.00% |
| 100 | 62.43ms | 63.18ms | 186.773504/s | 0.00% |

## Дүгнэлт

1. 5 VU үед p90 62.3ms, p95 62.45ms, throughput 9.357544/s, error rate 0.00% байв.
2. 30 VU үед p90 62.72ms, p95 63.24ms, throughput 56.037821/s, error rate 0.00% байв.
3. 100 VU үед p90 62.43ms, p95 63.18ms, throughput 186.773504/s, error rate 0.00% байв.
4. 5-аас 100 VU хүртэл өсгөхөд p95 latency 62.45ms-ээс 63.18ms болж өөрчлөгдсөн.
5. Энэ хугацаанд throughput 9.357544/s-ээс 186.773504/s болсон нь серверийн нийт хүсэлт боловсруулах хурдыг харуулж байна.
6. Гурван түвшинд http_req_failed error rate 0.00%, 0.00%, 0.00% байсан нь хэмжилтийн хугацаанд хүсэлтийн алдаа илрээгүйг харууллаа.
7. 100 VU дээр p95 latency 63.18ms болж бага өөрчлөгдсөн ч хамгийн их latency 263.89ms хүрсэн нь ачааллын оргил үед цөөн хүсэлт илт удааширсныг харуулж байна.
8. Локал /health endpoint-ийн 5 VU baseline p95 1.13ms байсан бөгөөд PASS тестийн босгыг энэ хэмжилтийн 1.5 дахин ихээр тогтоосон.
9. Threshold PASS туршилтын бүртгэгдсэн төлөв: PASS.
10. 100 ms орчим сааталтай /slow endpoint-д p95 < 50 ms босго тавьсан зориудын туршилтын төлөв: FAIL (хүлээгдсэн); энэ нь SLO quality gate FAIL-ийг илрүүлэх ёстойг харуулна.

## Анхаарах нь

Энэ хураангуй нь results/ хавтас дахь k6-ийн текст гаралтаас автоматаар үүссэн. README-д оруулахын өмнө эх файлуудтай нь тулгаж шалгана.

<!-- AUTO-RESULTS-END -->

## Дэлгэцийн зургууд

5/30/100 VU болон threshold-ийн k6 summary capture-ууд PNG хэлбэрээр screenshots/ хавтаст үүсэж, репозиторид хадгалагдсан. Эдгээр зураг нь бодит k6 текстэн гаралтын сонгосон мөрүүдийг уншихад хялбар харуулна. Бүтэн k6 гаралт results/ хавтас дахь .txt файлуудад байна.

## Git-д хадгалах

Хэмжилт, screenshot-уудыг өөрийн компьютерт үүсгэсний дараа дараах байдлаар commit болон push хийнэ:

~~~bash
git add README.md results/ screenshots/
git commit -m "test: add measured k6 results and screenshots"
git push origin main
~~~

Ингэснээр README-ийн хүснэгтийн утга болон хавсаргасан k6 текст гаралт хоорондоо таарч байх боломжтой. Эцэст нь GitHub репозиторийн линкийг MS Teams Assignment-д оруулаад **Turn in** дарна.

## Туршилтын гүйцэтгэлийн тэмдэглэл

Бүх тестийг GitHub Actions-ийн Ubuntu орчинд k6 v2.4.0 ашиглан бодитоор ажиллуулсан. Алхам 2-ын test.k6.io baseline p95 нь 62.38ms, error rate нь 0.00% байв. 5, 30, 100 VU хэмжилтийн p95 нь тус тус 62.45ms, 63.24ms, 63.18ms гарсан тул энэ хэмжилтээр 100 VU хүртэл p95-д огцом доройтол ажиглагдаагүй. Харин 100 VU үед хамгийн их latency 263.89ms хүрсэн нь цөөн хүсэлт удааширсан tail latency-ийн анхааруулах дохио юм. Локал /health baseline-ийн p95 1.13ms байсан; үүнээс гаргасан p95 < 1.69ms SLO туршилт 0.93249ms үр дүнтэйгээр PASS болсон. /slow endpoint дээрх p95 < 50ms хатуу босго 101.15ms бодит p95 дээр биелээгүй бөгөөд хүлээгдсэн FAIL гарсан. Бүх k6-ийн бүтэн текст гаралт results/ хавтаст, summary capture PNG-ууд screenshots/ хавтаст хадгалагдсан.
