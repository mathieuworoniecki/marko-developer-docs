<?php
// PHP 8.1+. HTTP JSON example, not an official SDK. No dependency required.
declare(strict_types=1);

function marko_signature(string $secret, string $keyId, int $timestamp, string $nonce): string {
    $message = "MARKO-EXTERNAL-API-TOKEN-V1\n{$keyId}\n{$timestamp}\n{$nonce}";
    return hash_hmac('sha256', $message, $secret);
}

final class MarkoApiError extends RuntimeException {
    public function __construct(public int $status, public mixed $problem, public ?string $requestId) {
        parent::__construct('HTTP ' . $status . '; request_id=' . ($requestId ?? 'absent'));
    }
}

final class MarkoClient {
    private string $baseUrl;
    private string $keyId;
    private string $secret;
    private ?string $accessToken = null;
    private float $refreshAt = 0;

    public function __construct(?string $baseUrl = null, ?string $keyId = null, ?string $secret = null) {
        $this->baseUrl = rtrim($baseUrl ?? (getenv('MARKO_API_BASE_URL') ?: 'https://partner-api.marko.fr/v1'), '/');
        $this->keyId = $keyId ?? (getenv('MARKO_KEY_ID') ?: '');
        $this->secret = $secret ?? (getenv('MARKO_API_SECRET') ?: '');
        if ($this->keyId === '' || $this->secret === '') throw new RuntimeException('Define MARKO_KEY_ID and MARKO_API_SECRET');
    }

    private function http(string $method, string $path, mixed $body = null, array $headers = []): mixed {
        if (!str_starts_with($path, '/') || str_starts_with($path, '//')) throw new InvalidArgumentException('Use a path relative to /v1');
        $headers[] = 'Accept: application/json';
        $options = ['method' => $method, 'header' => implode("\r\n", $headers), 'timeout' => 30, 'ignore_errors' => true, 'follow_location' => 0];
        if ($body !== null) {
            $options['header'] .= "\r\nContent-Type: application/json";
            $options['content'] = json_encode($body, JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE);
        }
        $raw = @file_get_contents($this->baseUrl . $path, false, stream_context_create(['http' => $options]));
        if ($raw === false) throw new RuntimeException('Network failure; verify the result before repeating a write');
        $status = 0;
        $requestId = null;
        foreach ($http_response_header ?? [] as $line) {
            if (preg_match('/^HTTP\/\S+\s+(\d{3})/', $line, $match)) $status = (int) $match[1];
            if (stripos($line, 'X-Request-ID:') === 0) $requestId = trim(substr($line, 13));
        }
        try { $parsed = $raw === '' ? null : json_decode($raw, true, 512, JSON_THROW_ON_ERROR); }
        catch (JsonException $error) {
            if ($status >= 200 && $status < 300) throw new RuntimeException('Expected a JSON response; use a binary client for file exports');
            $parsed = null;
        }
        if ($status < 200 || $status >= 300) throw new MarkoApiError($status, $parsed, $parsed['request_id'] ?? $requestId);
        return $parsed;
    }

    public function token(): string {
        $now = hrtime(true) / 1e9;
        if ($this->accessToken === null || $now >= $this->refreshAt) {
            $timestamp = time();
            $nonce = rtrim(strtr(base64_encode(random_bytes(24)), '+/', '-_'), '=');
            $result = $this->http('POST', '/auth/token', [
                'key_id' => $this->keyId, 'timestamp' => $timestamp, 'nonce' => $nonce,
                'signature' => marko_signature($this->secret, $this->keyId, $timestamp, $nonce),
            ]);
            $this->accessToken = $result['access_token'];
            $this->refreshAt = hrtime(true) / 1e9 + max(0, (int) $result['expires_in'] - 30);
        }
        return $this->accessToken;
    }

    public function request(string $method, string $path, mixed $body = null, ?string $idempotencyKey = null): mixed {
        $method = strtoupper($method);
        if (!in_array($method, ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], true)) throw new InvalidArgumentException('Unsupported method');
        if ($method !== 'GET' && ($idempotencyKey === null || $idempotencyKey === '')) throw new InvalidArgumentException('An explicit idempotency key is required for this example\'s writes');
        if ($idempotencyKey !== null && !preg_match('/^[!-~]{1,255}$/D', $idempotencyKey)) throw new InvalidArgumentException('Idempotency key: 1 to 255 visible ASCII characters, without spaces');
        $headers = ['Authorization: Bearer ' . $this->token(), 'X-Request-ID: ' . bin2hex(random_bytes(16))];
        if ($idempotencyKey !== null) $headers[] = 'Idempotency-Key: ' . $idempotencyKey;
        try { return $this->http($method, $path, $body, $headers); }
        catch (MarkoApiError $error) {
            if ($error->status !== 401 || $method !== 'GET') throw $error;
            $this->accessToken = null;
            $headers[0] = 'Authorization: Bearer ' . $this->token();
            return $this->http($method, $path, $body, $headers);
        }
    }
}

if (realpath($_SERVER['SCRIPT_FILENAME'] ?? '') === __FILE__) {
    try { echo json_encode((new MarkoClient())->request('GET', '/operations?limit=1'), JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR) . "\n"; }
    catch (Throwable $error) { fwrite(STDERR, $error->getMessage() . "\n"); exit(1); }
}
