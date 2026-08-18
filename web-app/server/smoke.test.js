const assert = require('node:assert/strict');
const http = require('node:http');
const app = require('./index');

function request(port, path) {
  return new Promise((resolve, reject) => {
    const req = http.get({ hostname: '127.0.0.1', port, path }, (res) => {
      let body = '';
      res.setEncoding('utf8');
      res.on('data', (chunk) => { body += chunk; });
      res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body }));
    });
    req.on('error', reject);
  });
}

(async () => {
  const server = app.listen(0);
  try {
    const { port } = server.address();
    const api = await request(port, '/api/hello');
    assert.equal(api.status, 200);
    assert.deepEqual(JSON.parse(api.body), { message: 'Hello gamer!' });

    const fallback = await request(port, '/');
    assert.equal(fallback.status, 200);
    assert.match(fallback.headers['content-type'] || '', /text\/html/);
    assert.match(fallback.body, /<html/i);

    console.log('server smoke test passed');
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
