import http from 'k6/http';
import { check, sleep } from 'k6';

const target = __ENV.BASE_URL || 'http://127.0.0.1:3000/health';

// Локал сервер дээр SLO тооцоход ашиглах baseline хэмжилт.
export const options = {
  vus: 5,
  duration: '30s',
};

export default function () {
  const response = http.get(target);
  check(response, {
    'локал сервер HTTP 200 буцаав': (res) => res.status === 200,
  });
  sleep(1);
}
