"""HTTP JSON example for MARKO. Standard library only; not an official SDK."""
import hashlib
import hmac
import json
import os
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request


class ApiError(RuntimeError):
    def __init__(self, status, problem, request_id=None):
        self.status = status
        self.problem = problem
        self.request_id = request_id
        super().__init__(f"HTTP {status}; request_id={request_id or 'absent'}")


def sign(secret, key_id, timestamp, nonce):
    message = f"MARKO-EXTERNAL-API-TOKEN-V1\n{key_id}\n{timestamp}\n{nonce}"
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        return None


class MarkoClient:
    def __init__(self, base_url=None, key_id=None, secret=None):
        self.base_url = (base_url or os.getenv(
            "MARKO_API_BASE_URL", "https://partner-api.marko.fr/v1"
        )).rstrip("/")
        self.key_id = key_id or os.environ["MARKO_KEY_ID"]
        self.secret = secret or os.environ["MARKO_API_SECRET"]
        self.access_token = None
        self.refresh_at = 0
        self.opener = urllib.request.build_opener(NoRedirect())

    def _http(self, method, path, body=None, headers=None):
        if not path.startswith("/") or path.startswith("//"):
            raise ValueError("Use a path relative to /v1, starting with one slash")
        data = None if body is None else json.dumps(body, ensure_ascii=False).encode()
        request_headers = {"Accept": "application/json", **(headers or {})}
        if data is not None:
            request_headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            self.base_url + path, data=data, headers=request_headers, method=method,
        )
        try:
            with self.opener.open(request, timeout=30) as response:
                raw = response.read()
                return None if not raw else json.loads(raw)
        except urllib.error.HTTPError as error:
            raw = error.read()
            try:
                problem = json.loads(raw)
            except (ValueError, UnicodeDecodeError):
                problem = None
            request_id = error.headers.get("X-Request-ID")
            if isinstance(problem, dict):
                request_id = problem.get("request_id") or request_id
            raise ApiError(error.code, problem, request_id) from None

    def token(self):
        if self.access_token is None or time.monotonic() >= self.refresh_at:
            timestamp = int(time.time())
            nonce = secrets.token_urlsafe(24)
            result = self._http("POST", "/auth/token", {
                "key_id": self.key_id, "timestamp": timestamp, "nonce": nonce,
                "signature": sign(self.secret, self.key_id, timestamp, nonce),
            })
            self.access_token = result["access_token"]
            self.refresh_at = time.monotonic() + max(0, int(result["expires_in"]) - 30)
        return self.access_token

    def request(self, method, path, body=None, *, idempotency_key=None):
        method = method.upper()
        if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
            raise ValueError("Unsupported method")
        if method != "GET" and not idempotency_key:
            raise ValueError("An explicit idempotency key is required for this example's writes")
        if idempotency_key and (len(idempotency_key) > 255 or any(not 33 <= ord(c) <= 126 for c in idempotency_key)):
            raise ValueError("Idempotency key: 1 to 255 visible ASCII characters, without spaces")
        headers = {"Authorization": "Bearer " + self.token(), "X-Request-ID": secrets.token_hex(16)}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        try:
            return self._http(method, path, body, headers)
        except ApiError as error:
            # Only repeat a read. Writes and ambiguous network failures remain
            # explicit at the caller, with their original idempotency key.
            if error.status != 401 or method != "GET":
                raise
            self.access_token = None
            headers["Authorization"] = "Bearer " + self.token()
            return self._http(method, path, body, headers)


if __name__ == "__main__":
    try:
        print(json.dumps(MarkoClient().request("GET", "/operations?limit=1"), indent=2, ensure_ascii=False))
    except (ApiError, urllib.error.URLError) as error:
        raise SystemExit(str(error)) from None
