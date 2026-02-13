# Lesson 4 – Identity demo: secure cluster access with SSO

This lesson explains how **platform teams should design identity for cloud-native platforms**: decoupled from cloud providers, centralized, token-based, and aligned with team ownership.

The included demo shows how modern CLIs and platforms securely authenticate developers
**without ever handling passwords**.

## Learning Objectives

By the end of this lesson, students will understand:

- What a **control plane** is and why identity belongs there
- Why platform identity must be **abstracted from cloud IAM**
- The role of an **Identity Provider (IdP)** as an authentication broker
- How **OIDC-style tokens (JWTs)** are used in practice
- Why **team-based authorization** scales better than user-based permissions
- The “last mile” problem of securing developer terminals

## Demo Overview

This demo simulates:

- A **central IdP** issuing short-lived tokens
- A **CLI using OAuth Device Authorization Flow**
- A **platform API** validating tokens and enforcing team-based access

No cloud accounts, Kubernetes, or real IdP are required.

This is about **architecture and flow**, not vendor tooling.

## Folder Structure
```
lesson4/
├── idp_server.py # Simulated Identity Provider (Device Flow + JWT)
├── api_server.py # Protected platform API
├── cli_login.py # Developer CLI using device auth
└── README.md
```

## Prerequisites

- Python 3.9+
- A browser

## Running the Demo (2 Terminals + Browser)

### Terminal 1 – Start the Identity Provider
```
python3 idp_server.py
```
This represents Okta, Azure AD, Auth0, etc.  

### Terminal 2 – Start the API and run the CLI
```
python3 api_server.py &
python3 cli_login.py
```
The CLI will print:

-A URL  
-A short numeric code  

### Browser – Approve Access

- Open the URL shown in the CLI  
- Enter the code
- Choose a team (try platform-team and a non-platform team)
- Approve
- Return to the terminal to see the result.

## Expected Outcomes

-platform-team	  Access granted
-payments-team	  Forbidden
-guest	          Forbidden

## Takeaways

-Notice that the CLI never asked me for a password.  
-The browser handled authentication through the Identity Provider.  
-The CLI only received a short-lived token.  
-That token represents who I am and which team I belong to.  
-The platform API validates the token and makes an authorization decision.  
-Access isn’t granted because I'm a specific named user  
-It’s granted because I’m a member of the platform team.  


## Why This Matters for Platform Engineering

-Developers should never manage cloud credentials directly
-Identity must survive:cloud migrations, mergers and acquisitions, org restructuring
-Platform teams need:centralized audit, fast revocation, consistent access patterns
-This is how kubectl, gcloud, az, and internal platform CLIs work.
-Credentials never live in terminals. Tokens expire automatically.
-Identity here is not cloud IAM. It's a platform capability, owned by the platform team.

## Code Deep Dive

### 1. IdP Server (idp_server.py) – JWT Token Generation

The Identity Provider uses **Device Authorization Flow** and issues JWTs:

```python
def jwt_encode(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h = b64url_json(header)
    p = b64url_json(payload)
    to_sign = f"{h}.{p}".encode("utf-8")
    s = sign_hs256(to_sign)
    return f"{h}.{p}.{s}"
```

The JWT includes:
- **iss**: Token issuer (the IdP)
- **aud**: Audience (the API that will validate it)
- **sub**: Subject (the user)
- **team**: Team membership (for authorization)
- **exp**: Expiration time (5 minutes in this demo)

When a user approves in the browser, the IdP stores their team membership and issues a signed token:

```python
access_token = jwt_encode({
    "iss": f"http://{HOST}:{PORT}",
    "aud": "cnpe-platform-api",
    "sub": d["sub"],
    "team": d["team"],
    "iat": now,
    "exp": now + 300,  # 5-minute expiration
})
```

### 2. API Server (api_server.py) – Token Validation & Team-Based Authorization

The protected API validates the JWT signature and enforces team-based access control:

```python
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
```

Note the **three security checks**:
1. **Signature verification** – Ensures token wasn't tampered with
2. **Expiration check** – Rejects expired tokens (no need for revocation list)
3. **Audience validation** – Ensures token is intended for this API

After validation, authorization is decided by **team membership**:

```python
# Team-based authorization (simple demo rule)
if claims.get("team") != "platform-team":
    self._send(403, {"error": "forbidden", "needed_team": "platform-team", "your_team": claims.get("team")})
    return

self._send(200, {
    "message": "✅ Access granted to platform resource",
    "sub": claims.get("sub"),
    "team": claims.get("team"),
})
```

This is **much simpler** than checking individual user names. One rule covers all team members.

### 3. CLI (cli_login.py) – Device Authorization Flow

The CLI never handles passwords. Instead, it uses **Device Authorization Flow**:

```python
def main():
    _, device = post(f"{IDP}/device/code", {})
    print("\n== Device Login ==")
    print(f"1) Open: {device['verification_uri']}")
    print(f"2) Enter code: {device['user_code']}")
    print("3) Approve in browser\n")
```

The CLI receives a **device_code** and **user_code**. The device_code is stored locally; the user_code is a 6-digit number they enter in their browser.

Then the CLI **polls** the IdP until the user approves:

```python
token = None
while True:
    try:
        code, resp = post(f"{IDP}/oauth/token", {"device_code": device["device_code"]})
        token = resp["access_token"]
        break
    except urllib.error.HTTPError as e:
        payload = json.loads(e.read().decode("utf-8"))
        if payload.get("error") == "authorization_pending":
            time.sleep(device["interval"])  # Poll every 2 seconds
            continue
        raise
```

Once approved, the CLI receives a **Bearer token** and can authenticate to the API:

```python
print("✅ Token issued. Calling protected API...\n")
code, resp = get(f"{API}/platform/resource", headers={"Authorization": f"Bearer {token}"})
print(json.dumps(resp, indent=2))
```

### Key Insights

1. **No passwords in the CLI** – Device Flow moves authentication to the browser
2. **Short-lived tokens** – Expire in 5 minutes; no need for revocation lists
3. **Team-based rules** – One authorization rule (`team == "platform-team"`) scales to hundreds of users
4. **HMAC-SHA256 signing** – Validates token integrity without a database lookup
5. **Stateless validation** – The API doesn't need to talk to the IdP to check tokens
