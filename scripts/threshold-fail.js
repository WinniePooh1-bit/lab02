import http from 'k6/http';
import { check, sleep } from 'k6';

const target = __ENV.BASE_URL || 'http://127.0.0.1:3000/slow';

// Санаатайгаар хатуу босго тавина. /slow endpoint ~100ms сааталтай тул
// p95 < 50ms нөхцөл биелэхгүй, тест FAIL болох ёстой.
export const options = {
  vus: 5,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<50'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const response = http.get(target);
  check(response, {
    'удаашруулсан endpoint HTTP 200 буцаав': (res) => res.status === 200,
  });
  sleep(1);
}
