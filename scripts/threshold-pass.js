import http from 'k6/http';
import { check, sleep } from 'k6';

const baselineP95 = Number(__ENV.BASELINE_P95);
if (!Number.isFinite(baselineP95) || baselineP95 <= 0) {
  throw new Error('BASELINE_P95 утгыг local-baseline хэмжилтийн p(95)-ээс миллисекундээр өгнө.');
}

// SLO-г өөрийн хэмжсэн локал baseline p95-ийн 1.5 дахин ихээр тогтооно.
const p95Slo = Number((baselineP95 * 1.5).toFixed(2));
const target = __ENV.BASE_URL || 'http://127.0.0.1:3000/health';

export const options = {
  vus: 30,
  duration: '1m',
  thresholds: {
    http_req_duration: [`p(95)<${p95Slo}`],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const response = http.get(target);
  check(response, {
    'локал сервер HTTP 200 буцаав': (res) => res.status === 200,
  });
  sleep(1);
}
