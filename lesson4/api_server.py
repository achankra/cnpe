#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, base64, hmac, hashlib, time

HOST = "127.0.0.1"
PORT = 8082
SIGNING_SECRET = b"demo-secret-change-me"

def b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)

def verify_jwt(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("bad token format")
    h_b64, p_b64, sig_b64 = parts
    msg = f"{h_b64}.{p_b64}".encode("utf-8")
    expected = hmac.new(SIGNING_SECRET, msg, hashlib.sha256).digest()
    if not hmac.compare_digest(expected, b64url_decode(sig_b64)):
        raise ValueError("bad signature")

    payload = json.loads(b64url_decode(p_b64).decode("utf-8"))

    now = int(time.time())
    if payload.get("exp", 0) < now:
        raise ValueError("token expired")
    if payload.get("aud") != "cnpe-platform-api":
        raise ValueError("bad audience")

    return payload

class Handler(BaseHTTPRequestHandler):
    def _send(self, code=200, body=None):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body or {}).encode("utf-8"))

    def do_GET(self):
        if self.path != "/platform/resource":
            self._send(404, {"error": "not_found"})
            return

        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            self._send(401, {"error": "missing_bearer_token"})
            return

        token = auth[len("Bearer "):].strip()
        try:
            claims = verify_jwt(token)
        except Exception as e:
            self._send(401, {"error": "invalid_token", "detail": str(e)})
            return

        # Team-based authorization (simple demo rule)
        if claims.get("team") != "platform-team":
            self._send(403, {"error": "forbidden", "needed_team": "platform-team", "your_team": claims.get("team")})
            return

        self._send(200, {
            "message": "✅ Access granted to platform resource",
            "sub": claims.get("sub"),
            "team": claims.get("team"),
            "iss": claims.get("iss"),
        })

if __name__ == "__main__":
    print(f"API running at http://{HOST}:{PORT}")
    HTTPServer((HOST, PORT), Handler).serve_forever()
