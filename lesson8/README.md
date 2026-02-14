# Lesson 8 – Golden Path Automation  
**Secure Ingress & Traffic Control**

This lesson demonstrates how platform teams provide **secure-by-default ingress**
and **safe traffic management** as a *Golden Path*, without requiring developers
to understand certificates, ingress controllers, or service meshes.

The demo is intentionally **simple and Python-based**, focusing on **intent,
guardrails, and automation** rather than infrastructure plumbing.

---

## Learning Objectives

By the end of this lesson, students will understand:

- What a **Golden Path** really means in practice  
- Why ingress and traffic control belong to the **platform**, not individual teams  
- How platforms enforce **secure defaults** (TLS, DNS boundaries)  
- The difference between **canary** and **blue/green** traffic strategies  
- How guardrails prevent invalid configurations before runtime  
- How “before vs after” automation changes delivery behavior  

---

## Core Idea

Developers should declare **intent**:  

> “Expose my service securely and manage traffic safely.”  

Platforms should handle **everything else**:  
- TLS   
- host routing  
- traffic strategies  
- validation and guardrails  

This demo simulates that contract.

---

## Folder Structure 

lesson8/  
├── ingress-demo/  
│ ├── gateway.py # Secure ingress + traffic control simulation  
│ ├── policy.py # Platform guardrails (validation)  
│ ├── run_demo.py # Runs canary + blue/green demos back-to-back  
│ ├── configs/  
│ │ ├── canary.yaml  
│ │ └── bluegreen.yaml  
│ └── README.md  
└── README.md  


---

## Developer Intent (Declarative Config)  

### Canary configuration (`configs/canary.yaml`)  

```yaml
service: orders
host: orders.api.platform.local

security:
  tls: true

traffic:
  strategy: canary
  canary_percentage: 20
```
Blue/Green configuration (configs/bluegreen.yaml)

service: orders
host: orders.api.platform.local

security:
  tls: true

traffic:
  strategy: bluegreen
  active_color: blue
  allow_header_override: true
Developers do not configure:

certificates

ingress controllers

routing rules

retries or load balancing

They only declare what they want.

Platform Guardrails (policy.py)
Before any automation runs, the platform validates intent:

TLS must be enabled

Host must be under *.platform.local

Traffic strategy must be canary or bluegreen

Canary percentage must be 1–99

Blue/green active_color must be blue or green

Invalid configurations are rejected immediately.

This is a Golden Path:

opinionated

predictable

safe by default

Running the Demo
From lesson8/ingress-demo:

bash
Copy code
pip install pyyaml
python3 run_demo.py
This runs two demos back-to-back:

Canary traffic control

Blue/green traffic control

No files need to be edited live.

Demo Output Explained
BEFORE (no platform automation)
nginx
Copy code
Request → orders-v1
Request → orders-v1
Request → orders-v1
All traffic goes to a single version

Releases are risky

Rollbacks require redeploys

AFTER – Canary
nginx
Copy code
Request → orders-v1
Request → orders-v2
Request → orders-v1
Small percentage routed to v2

Risk reduced gradually

Header override allows safe testing

AFTER – Blue/Green
nginx
Copy code
Request → orders-blue
Request → orders-blue
All traffic routed to active environment

One-line flip switches environments

Instant rollback by changing intent

SAFE TEST (Header Override)
Canary: X-Canary: true

Blue/Green: X-Force-Color: green

Allows testing without impacting users.

What to Say During the Demo (Key Teaching Script)
Use this while running run_demo.py:

“Before automation, every request goes to one version.
Deployments are high-risk.”

“After automation, the platform controls traffic centrally.”

“Developers don’t touch ingress, TLS, or routing logic.
They declare intent — the platform enforces it.”

“Canary reduces risk gradually.
Blue/green flips risk instantly.”

“This is what a Golden Path looks like:
secure-by-default, opinionated, and automated.”

About the Hostname
The hostname shown:

arduino
Copy code
https://orders.api.platform.local
is illustrative.

It represents:

platform-owned DNS

enforced TLS

centralized ingress ownership

No DNS, certificates, or servers are required for this demo.

Mapping to Real Platforms
Demo Concept	Real-World Equivalent
config.yaml	Kubernetes Ingress / Gateway API
policy.py	OPA / admission control
gateway.py	Envoy / Istio ingress gateway
Canary routing	Service mesh traffic rules
Blue/green	Argo Rollouts / deployment strategies
Header overrides	A/B testing & safe validation

Key Takeaways
Golden Paths remove cognitive load

Security should be automatic, not optional

Traffic control belongs to the platform

Guardrails prevent invalid intent early

Platforms scale by reducing choices, not increasing them

Automation turns best practices into defaults

