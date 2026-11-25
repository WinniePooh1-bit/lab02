'use strict';

const http = require('node:http');

const host = process.env.HOST || '127.0.0.1';
const port = Number(process.env.PORT || 3000);

const server = http.createServer((request, response) => {
  const url = new URL(request.url, `http://${request.headers.host || `${host}:${port}`}`);

  if (request.method !== 'GET') {
    response.writeHead(405, { 'content-type': 'application/json; charset=utf-8' });
    response.end(JSON.stringify({ error: 'Method not allowed' }));
    return;
  }

  if (url.pathname === '/' || url.pathname === '/health') {
    response.writeHead(200, { 'content-type': 'application/json; charset=utf-8' });
    response.end(JSON.stringify({ status: 'ok', message: 'Local k6 test server is ready' }));
    return;
  }

  if (url.pathname === '/slow') {
    setTimeout(() => {
      response.writeHead(200, { 'content-type': 'application/json; charset=utf-8' });
      response.end(JSON.stringify({ status: 'ok', delay_ms: 100 }));
    }, 100);
    return;
  }

  if (url.pathname === '/error') {
    response.writeHead(500, { 'content-type': 'application/json; charset=utf-8' });
    response.end(JSON.stringify({ status: 'error' }));
    return;
  }

  response.writeHead(404, { 'content-type': 'application/json; charset=utf-8' });
  response.end(JSON.stringify({ error: 'Not found' }));
});

server.listen(port, host, () => {
  console.log(`Local k6 test server listening at http://${host}:${port}`);
});

function shutdown() {
  server.close(() => process.exit(0));
}

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
