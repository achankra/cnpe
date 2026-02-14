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

### Blue/Green configuration (configs/bluegreen.yaml)
```yaml
service: orders
host: orders.api.platform.local

security:
  tls: true

traffic:
  strategy: bluegreen
  active_color: blue
  allow_header_override: true
```

### Developers do not configure:

- certificates  
- ingress controllers  
- routing rules  
- retries or load balancing  

They only declare what they want.

## Platform Guardrails (policy.py)

Before any automation runs, the platform validates intent:

- TLS must be enabled  
- Host must be under *.platform.local  
- Traffic strategy must be canary or bluegreen  
- Canary percentage must be 1–99  
- Blue/green active_color must be blue or green  
- Invalid configurations are rejected immediately.  

### This is a Golden Path:

-opinionated  
-predictable  
-safe by default  

## Running the Demo

From lesson8/ingress-demo:

```
pip install pyyaml
python3 run_demo.py
```

### This runs two demos back-to-back:

- Canary traffic control  
- Blue/green traffic control  

### Demo Output Explained

#### BEFORE (no platform automation)

- Request → orders-v1  
- Request → orders-v1  
- Request → orders-v1  
- All traffic goes to a single version
- Releases are risky
- Rollbacks require redeploys

#### AFTER – Canary

- Request → orders-v1  
- Request → orders-v2  
- Request → orders-v1  
- Small percentage routed to v2  
- Risk reduced gradually
- Header override allows safe testing

#### AFTER – Blue/Green

- Request → orders-blue
- Request → orders-blue
- All traffic routed to active environment
- One-line flip switches environments
- Instant rollback by changing intent

#### SAFE TEST (Header Override)

- Canary: X-Canary: true  
- Blue/Green: X-Force-Color: green  
- Allows testing without impacting users.  

