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

**Одоогоор бодит k6 хэмжилт хийгдээгүй.** k6 CLI суулгасан Ubuntu/WSL2 орчинд скриптийг ажиллуулсны дараа хүснэгт, дүгнэлт автоматаар үүснэ. Хэмжилтийн тоог таамгаар бөглөөгүй.

<!-- AUTO-RESULTS-END -->

## Дэлгэцийн зургууд

k6 summary бүрийн screenshot-ийг screenshots/ хавсанд нэмнэ. Файлын нэрийн загвар болон жагсаалт screenshots/README.md дотор бий. Screenshot нь текстэн гаралтыг орлохгүй; results/ доторх .txt файлуудыг заавал хамт хадгална.

## Git-д хадгалах

Хэмжилт, screenshot-уудыг өөрийн компьютерт үүсгэсний дараа дараах байдлаар commit болон push хийнэ:

~~~bash
git add README.md results/ screenshots/
git commit -m "test: add measured k6 results and screenshots"
git push origin main
~~~

Ингэснээр README-ийн хүснэгтийн утга болон хавсаргасан k6 текст гаралт хоорондоо таарч байх боломжтой. Эцэст нь GitHub репозиторийн линкийг MS Teams Assignment-д оруулаад **Turn in** дарна.

## Одоогийн гүйцэтгэлийн тэмдэглэл

Скриптүүд болон локал туршилтын серверийг бэлтгэж, Node.js синтакс болон локал endpoint-ийн /health, /slow, /error, 404 хариуг шалгасан. Харин энэ репозиторыг бэлтгэсэн орчинд k6 CLI байгаагүй, гадаад DNS холболт ажиллаагүй тул k6-ийн бодит хэмжилт, k6 version гаралт, screenshot-ууд хараахан үүсээгүй. Тиймээс эдгээр үр дүнг зохиомлоор нөхөөгүй; өөрийн WSL2/Ubuntu орчинд дээрх командыг ажиллуулж бодит нотолгоог нэмэх шаардлагатай.
