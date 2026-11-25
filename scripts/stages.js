import http from 'k6/http';
import { check, sleep } from 'k6';

const target = __ENV.BASE_URL || 'https://test.k6.io/';

// Алхам 3: ачааллыг 5 -> 30 -> 100 VU болгон өсгөөд буулгана.
export const options = {
  stages: [
    { duration: '30s', target: 5 },
    { duration: '1m', target: 30 },
    { duration: '30s', target: 100 },
    { duration: '30s', target: 0 },
  ],
};

export default function () {
  const response = http.get(target);
  check(response, {
    'HTTP статус 200 байна': (res) => res.status === 200,
  });
  sleep(1);
}
