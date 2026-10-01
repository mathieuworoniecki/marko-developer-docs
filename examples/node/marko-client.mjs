// Node.js 22+. HTTP JSON example, not an official SDK.
import { createHmac, randomBytes } from 'node:crypto';
import { pathToFileURL } from 'node:url';

export function sign(secret, keyId, timestamp, nonce) {
  const message = `MARKO-EXTERNAL-API-TOKEN-V1\n${keyId}\n${timestamp}\n${nonce}`;
  return createHmac('sha256', secret).update(message, 'utf8').digest('hex');
}

export class ApiError extends Error {
  constructor(status, problem, requestId) {
    super(`HTTP ${status}; request_id=${requestId ?? 'absent'}`);
    this.status = status;
    this.problem = problem;
    this.requestId = requestId;
  }
}

export class MarkoClient {
  constructor({ baseUrl, keyId, secret } = {}) {
    this.baseUrl = (baseUrl ?? process.env.MARKO_API_BASE_URL ?? 'https://partner-api.marko.fr/v1').replace(/\/$/, '');
    this.keyId = keyId ?? process.env.MARKO_KEY_ID;
    this.secret = secret ?? process.env.MARKO_API_SECRET;
    if (!this.keyId || !this.secret) throw new Error('Define MARKO_KEY_ID and MARKO_API_SECRET');
    this.accessToken = null;
    this.refreshAt = 0;
  }

  async http(method, path, body, headers = {}) {
    if (!path.startsWith('/') || path.startsWith('//')) throw new Error('Use a path relative to /v1');
    const response = await fetch(this.baseUrl + path, {
      method, redirect: 'error', signal: AbortSignal.timeout(30_000),
      headers: { Accept: 'application/json', ...(body === undefined ? {} : { 'Content-Type': 'application/json' }), ...headers },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const raw = await response.text();
    let parsed;
    try { parsed = raw ? JSON.parse(raw) : null; } catch {
      if (response.ok) throw new Error('Expected a JSON response; use a binary client for file exports');
      parsed = null;
    }
    if (!response.ok) throw new ApiError(response.status, parsed, parsed?.request_id ?? response.headers.get('X-Request-ID'));
    return parsed;
  }

  async token() {
    if (!this.accessToken || performance.now() >= this.refreshAt) {
      const timestamp = Math.floor(Date.now() / 1000);
      const nonce = randomBytes(24).toString('base64url');
      const result = await this.http('POST', '/auth/token', {
        key_id: this.keyId, timestamp, nonce,
        signature: sign(this.secret, this.keyId, timestamp, nonce),
      });
      this.accessToken = result.access_token;
      this.refreshAt = performance.now() + Math.max(0, result.expires_in - 30) * 1000;
    }
    return this.accessToken;
  }

  async request(method, path, body, { idempotencyKey } = {}) {
    method = method.toUpperCase();
    if (!['GET', 'POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) throw new Error('Unsupported method');
    if (method !== 'GET' && !idempotencyKey) throw new Error('An explicit idempotency key is required for this example’s writes');
    if (idempotencyKey && !/^[!-~]{1,255}$/.test(idempotencyKey)) throw new Error('Idempotency key: 1 to 255 visible ASCII characters, without spaces');
    const headers = { Authorization: `Bearer ${await this.token()}`, 'X-Request-ID': randomBytes(16).toString('hex') };
    if (idempotencyKey) headers['Idempotency-Key'] = idempotencyKey;
    try { return await this.http(method, path, body, headers); } catch (error) {
      if (!(error instanceof ApiError) || error.status !== 401 || method !== 'GET') throw error;
      this.accessToken = null;
      headers.Authorization = `Bearer ${await this.token()}`;
      return this.http(method, path, body, headers);
    }
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try { console.log(JSON.stringify(await new MarkoClient().request('GET', '/operations?limit=1'), null, 2)); }
  catch (error) { console.error(error.message); process.exitCode = 1; }
}
