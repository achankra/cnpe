#!/usr/bin/env python3
import json, time, urllib.request, urllib.parse

IDP = "http://127.0.0.1:8081"
API = "http://127.0.0.1:8082"

def post(url, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return r.getcode(), json.loads(r.read().decode("utf-8"))

def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req) as r:
        return r.getcode(), json.loads(r.read().decode("utf-8"))

def main():
    _, device = post(f"{IDP}/device/code", {})
    print("\n== Device Login ==")
    print(f"1) Open: {device['verification_uri']}")
    print(f"2) Enter code: {device['user_code']}")
    print("3) Approve in browser\n")

    token = None
    while True:
        try:
            code, resp = post(f"{IDP}/oauth/token", {"device_code": device["device_code"]})
            token = resp["access_token"]
            break
        except urllib.error.HTTPError as e:
            payload = json.loads(e.read().decode("utf-8"))
            if payload.get("error") == "authorization_pending":
                time.sleep(device["interval"])
                continue
            raise

    print("✅ Token issued. Calling protected API...\n")
    code, resp = get(f"{API}/platform/resource", headers={"Authorization": f"Bearer {token}"})
    print(json.dumps(resp, indent=2))

if __name__ == "__main__":
    main()
