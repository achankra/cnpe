#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import json, time, secrets, base64, hmac, hashlib

HOST = "127.0.0.1"
PORT = 8081

SIGNING_SECRET = b"demo-secret-change-me"
DEVICES = {}  # device_code -> device record

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

def b64url_json(obj: dict) -> str:
    return b64url(json.dumps(obj, separators=(",", ":")).encode("utf-8"))

def sign_hs256(message: bytes) -> str:
    sig = hmac.new(SIGNING_SECRET, message, hashlib.sha256).digest()
    return b64url(sig)

def jwt_encode(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h = b64url_json(header)
    p = b64url_json(payload)
    to_sign = f"{h}.{p}".encode("utf-8")
    s = sign_hs256(to_sign)
    return f"{h}.{p}.{s}"

class Handler(BaseHTTPRequestHandler):
    def _send(self, code=200, content_type="application/json", body=b"{}"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(length).decode("utf-8")

    def do_GET(self):
        u = urlparse(self.path)
        if u.path != "/activate":
            self._send(404, body=b'{"error":"not_found"}')
            return

        html = f"""
        <html><body style="font-family: sans-serif; max-width: 720px; margin: 40px auto;">
          <h2>CNPE Demo IdP Device Activation</h2>
          <p>Enter the <b>User Code</b> shown in your terminal.</p>
          <form method="POST" action="/activate">
            <label>User Code:</label><br/>
            <input name="user_code" style="font-size: 18px; padding: 6px;" /><br/><br/>
            <label>Username (sub):</label><br/>
            <input name="sub" value="ajay" style="font-size: 18px; padding: 6px;" /><br/><br/>
            <label>Team:</label><br/>
            <select name="team" style="font-size: 18px; padding: 6px;">
              <option value="platform-team">platform-team</option>
              <option value="payments-team">payments-team</option>
              <option value="guest">guest</option>
            </select><br/><br/>
            <button type="submit" style="font-size: 18px; padding: 8px 14px;">Approve</button>
          </form>
          <p style="color:#666;">Demo only. Real IdPs do SSO/MFA here.</p>
        </body></html>
        """
        self._send(200, content_type="text/html", body=html.encode("utf-8"))

    def do_POST(self):
        # /device/code  (CLI requests a device_code + user_code)
        if self.path == "/device/code":
            device_code = secrets.token_urlsafe(16)
            user_code = f"{secrets.randbelow(999999):06d}"
            DEVICES[device_code] = {
                "user_code": user_code,
                "approved": False,
                "sub": None,
                "team": None,
                "expires_at": int(time.time()) + 600,
            }
            resp = {
                "device_code": device_code,
                "user_code": user_code,
                "verification_uri": f"http://{HOST}:{PORT}/activate",
                "interval": 2,
                "expires_in": 600,
            }
            self._send(200, body=json.dumps(resp).encode("utf-8"))
            return

        # /oauth/token (CLI polls until approved; then gets JWT)
        if self.path == "/oauth/token":
            raw = self._read_body()
            ctype = self.headers.get("Content-Type", "")
            data = json.loads(raw or "{}") if "application/json" in ctype else {k: v[0] for k, v in parse_qs(raw).items()}

            device_code = data.get("device_code")
            if not device_code or device_code not in DEVICES:
                self._send(400, body=b'{"error":"invalid_device_code"}')
                return

            d = DEVICES[device_code]
            now = int(time.time())
            if now > d["expires_at"]:
                self._send(400, body=b'{"error":"expired_token"}')
                return

            if not d["approved"]:
                self._send(428, body=b'{"error":"authorization_pending"}')
                return

            access_token = jwt_encode({
                "iss": f"http://{HOST}:{PORT}",
                "aud": "cnpe-platform-api",
                "sub": d["sub"],
                "team": d["team"],
                "iat": now,
                "exp": now + 300,
            })
            resp = {"access_token": access_token, "token_type": "Bearer", "expires_in": 300}
            self._send(200, body=json.dumps(resp).encode("utf-8"))
            return

        # /activate (browser form approves the device_code via user_code)
        if self.path == "/activate":
            raw = self._read_body()
            form = {k: v[0] for k, v in parse_qs(raw).items()}
            user_code = form.get("user_code", "")
            sub = form.get("sub", "user")
            team = form.get("team", "guest")

            for dc, d in DEVICES.items():
                if d["user_code"] == user_code and int(time.time()) <= d["expires_at"]:
                    d["approved"] = True
                    d["sub"] = sub
                    d["team"] = team
                    ok = "<html><body><h3>Approved</h3><p>You may return to your terminal.</p></body></html>"
                    self._send(200, content_type="text/html", body=ok.encode("utf-8"))
                    return

            bad = "<html><body><h3>Invalid code ❌</h3><p>Try again.</p></body></html>"
            self._send(400, content_type="text/html", body=bad.encode("utf-8"))
            return

        self._send(404, body=b'{"error":"not_found"}')

if __name__ == "__main__":
    print(f"IdP running at http://{HOST}:{PORT}")
    HTTPServer((HOST, PORT), Handler).serve_forever()
