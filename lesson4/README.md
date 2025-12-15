# Lesson 4 – Control Plane & Identity

This lesson explains how **platform teams should design identity for cloud-native platforms**:
decoupled from cloud providers, centralized, token-based, and aligned with team ownership.

The included demo shows how modern CLIs and platforms securely authenticate developers
**without ever handling passwords**.

---

## Learning Objectives

By the end of this lesson, students will understand:

- What a **control plane** is and why identity belongs there
- Why platform identity must be **abstracted from cloud IAM**
- The role of an **Identity Provider (IdP)** as an authentication broker
- How **OIDC-style tokens (JWTs)** are used in practice
- Why **team-based authorization** scales better than user-based permissions
- The “last mile” problem of securing developer terminals

---

## Demo Overview

This demo simulates:

- A **central IdP** issuing short-lived tokens
- A **CLI using OAuth Device Authorization Flow**
- A **platform API** validating tokens and enforcing team-based access

No cloud accounts, Kubernetes, or real IdP are required.

This is about **architecture and flow**, not vendor tooling.

---

## Folder Structure

lesson4/
├── idp_server.py # Simulated Identity Provider (Device Flow + JWT)
├── api_server.py # Protected platform API
├── cli_login.py # Developer CLI using device auth
└── README.md

yaml
Copy code

---

## Prerequisites

- Python 3.9+
- A browser

No external dependencies required.

---

## Running the Demo (2 Terminals + Browser)

### Terminal 1 – Start the Identity Provider
```bash
python3 idp_server.py
This represents Okta, Azure AD, Auth0, etc.

Terminal 2 – Start the API and run the CLI
bash
Copy code
python3 api_server.py &
python3 cli_login.py
The CLI will print:

A URL

A short numeric code

Browser – Approve Access
Open the URL shown in the CLI

Enter the code

Choose a team (try platform-team and a non-platform team)

Approve

Return to the terminal to see the result.

Expected Outcomes
Team Selected	Result
platform-team	✅ Access granted
payments-team	❌ Forbidden
guest	❌ Forbidden

What To Say During the Demo (Key Teaching Script)
Use this script while running the demo live:

“Notice that the CLI never asked me for a password.
The browser handled authentication through the Identity Provider.
The CLI only received a short-lived token.”

“That token represents who I am and which team I belong to.
The platform API validates the token and makes an authorization decision.”

“Access isn’t granted because I’m Ajay.
It’s granted because I’m a member of the platform team.”

“This is how kubectl, gcloud, az, and internal platform CLIs work.
Credentials never live in terminals. Tokens expire automatically.”

“Identity here is not cloud IAM.
It’s a platform capability, owned by the platform team.”

Why This Matters for Platform Engineering
Developers should never manage cloud credentials directly

Identity must survive:

cloud migrations

mergers and acquisitions

org restructuring

Platform teams need:

centralized audit

fast revocation

consistent access patterns

This is why identity belongs in the control plane.

Core Concepts Reinforced
Abstract identity from infrastructure

Centralize authentication with an IdP

Standardize on OIDC-style tokens

Authorize via teams, not individuals

Secure the “last mile” (developer terminals)

What This Lesson Is Not
Not an IdP implementation guide

Not Kubernetes RBAC training

Not OAuth spec deep-dive

This lesson is about platform architecture and intent.

Key Takeaways
Treat identity as a platform product

Never expose raw cloud IAM to developers

Use tokens, not passwords

Scale authorization via team membership

Build identity into the control plane

