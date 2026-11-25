import http from 'k6/http';
import { check, sleep } from 'k6';

// Алхам 2: зааварт заасан test.k6.io руу хийх үндсэн тест.
// BASE_URL өгвөл зөвшөөрөгдсөн локал сервер рүү чиглүүлж болно.
const target = __ENV.BASE_URL || 'https://test.k6.io/';

export const options = {
  vus: 5,
  duration: '30s',
};

export default function () {
  const response = http.get(target);
  check(response, {
    'HTTP статус 200 байна': (res) => res.status === 200,
  });
  sleep(1);
}
