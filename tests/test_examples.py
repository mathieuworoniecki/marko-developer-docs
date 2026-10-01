"""Exercise the three HTTP examples against a local protocol fixture.

This verifies client behavior, not MARKO business behavior or real credentials.
"""
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
KEY_ID = "documentation01"
SECRET = "synthetic-documentation-fixture"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def reply(self, status, value):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-Request-ID", "fixture-request")
        self.end_headers()
        self.wfile.write(json.dumps(value).encode())

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path == "/v1/auth/token":
            message = f"MARKO-EXTERNAL-API-TOKEN-V1\n{KEY_ID}\n{body['timestamp']}\n{body['nonce']}"
            expected = hmac.new(SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()
            assert body["key_id"] == KEY_ID
            assert body["signature"] == expected
            assert body["nonce"] not in self.server.nonces
            self.server.nonces.add(body["nonce"])
            self.server.tokens += 1
            self.reply(200, {"access_token": f"fixture-token-{self.server.tokens}", "expires_in": 300})
        else:
            raise AssertionError("Unexpected POST " + self.path)

    def do_GET(self):
        assert self.headers.get("Authorization", "").startswith("Bearer fixture-token-")
        assert SECRET not in str(self.headers)
        self.server.reads += 1
        if self.server.reject_first_read and self.server.reads == 1:
            self.reply(401, {"status": 401, "request_id": "fixture-401"})
        else:
            self.reply(200, {"items": [], "total": 0, "limit": 1, "offset": 0})

    def do_PUT(self):
        self.server.writes += 1
        assert self.path == "/v1/operations/external/example-001"
        assert self.headers.get("Idempotency-Key") == "example-001-r1"
        assert self.headers.get("Authorization", "").startswith("Bearer fixture-token-")
        assert json.loads(self.rfile.read(int(self.headers["Content-Length"]))) == {"name": "Exemple MARKO"}
        self.reply(409, {"status": 409, "reason_code": "fixture-conflict", "request_id": "fixture-409"})


class ExampleTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.tokens = self.server.reads = self.server.writes = 0
        self.server.nonces = set()
        self.server.reject_first_read = False
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.env = {**os.environ, "MARKO_KEY_ID": KEY_ID, "MARKO_API_SECRET": SECRET,
                    "MARKO_API_BASE_URL": f"http://127.0.0.1:{self.server.server_port}/v1"}

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def run_example(self, command):
        result = subprocess.run(command, cwd=ROOT, env=self.env, text=True, capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(SECRET, result.stdout + result.stderr)
        return result.stdout

    def test_first_call_and_one_read_renewal_in_each_language(self):
        for command in (["python3", "examples/python/marko_client.py"],
                        ["node", "examples/node/marko-client.mjs"],
                        ["php", "examples/php/marko-client.php"]):
            with self.subTest(language=command[0]):
                self.server.tokens = self.server.reads = 0
                self.server.reject_first_read = True
                result = json.loads(self.run_example(command))
                self.assertEqual(result["items"], [])
                self.assertEqual(self.server.tokens, 2)
                self.assertEqual(self.server.reads, 2)

    def test_write_conflict_is_not_retried_and_token_is_cached(self):
        programs = [
            ["python3", "-c", "import sys; sys.path.insert(0,'examples/python'); from marko_client import MarkoClient,ApiError; c=MarkoClient(); c.request('GET','/operations?limit=1');\ntry: c.request('PUT','/operations/external/example-001',{'name':'Exemple MARKO'},idempotency_key='example-001-r1')\nexcept ApiError as e: assert e.status==409 and e.request_id=='fixture-409'; print('409')"],
            ["node", "--input-type=module", "-e", "import {MarkoClient,ApiError} from './examples/node/marko-client.mjs'; const c=new MarkoClient(); await c.request('GET','/operations?limit=1'); try {await c.request('PUT','/operations/external/example-001',{name:'Exemple MARKO'},{idempotencyKey:'example-001-r1'}); throw new Error('Expected conflict');} catch(e) {if(!(e instanceof ApiError)||e.status!==409||e.requestId!=='fixture-409') throw e; console.log('409');}"],
            ["php", "-r", "require 'examples/php/marko-client.php'; $c=new MarkoClient(); $c->request('GET','/operations?limit=1'); try {$c->request('PUT','/operations/external/example-001',['name'=>'Exemple MARKO'],'example-001-r1'); throw new RuntimeException('Expected conflict');} catch(MarkoApiError $e) {if($e->status!==409||$e->requestId!=='fixture-409') throw $e; echo '409';}"],
        ]
        for program in programs:
            with self.subTest(language=program[0]):
                self.server.tokens = self.server.reads = self.server.writes = 0
                self.assertEqual(self.run_example(program).strip(), "409")
                self.assertEqual(self.server.tokens, 1)
                self.assertEqual(self.server.writes, 1)

    def test_signatures_match_fixed_vector(self):
        # Fixed ASCII inputs catch LF vs literal backslash-n and a trailing LF.
        message = b"MARKO-EXTERNAL-API-TOKEN-V1\ndocumentation01\n1790848800\nexample_nonce_001"
        expected = hmac.new(SECRET.encode(), message, hashlib.sha256).hexdigest()
        programs = [
            ["python3", "-c", "import sys,os;sys.path.insert(0,'examples/python');from marko_client import sign;print(sign(os.environ['MARKO_API_SECRET'],'documentation01',1790848800,'example_nonce_001'))"],
            ["node", "--input-type=module", "-e", "import {sign} from './examples/node/marko-client.mjs';console.log(sign(process.env.MARKO_API_SECRET,'documentation01',1790848800,'example_nonce_001'));"],
            ["php", "-r", "require 'examples/php/marko-client.php';echo marko_signature(getenv('MARKO_API_SECRET'),'documentation01',1790848800,'example_nonce_001');"],
        ]
        for program in programs:
            with self.subTest(language=program[0]):
                self.assertEqual(self.run_example(program).strip(), expected)


if __name__ == "__main__":
    unittest.main()
