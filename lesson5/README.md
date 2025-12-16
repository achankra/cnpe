# Lesson 5 – Governance, Trust & Compliance  
**Automated Policy Enforcement at the Point of Change**

This lesson demonstrates how modern platform teams replace manual governance with **automated, version-controlled guardrails** that provide instant feedback
to developers — without slowing delivery.

The live demo focuses on **OPA (Open Policy Agent)** for preventive controls. Runtime detection with **Falco** is introduced conceptually and provided as
a take-home exercise.

## Learning Objectives

By the end of this lesson, students will understand:

- Why automated governance is a **business imperative**
- How to escape the “development triangle” tradeoff
- The idea of **Compliance at the Point of Change**
- How **Policy-as-Code** replaces manual stage gates
- The difference between **prevention** and **detection**
- How platforms balance **autonomy and control**


## The Four Layers of Modern Governance

1. **Identity (Zero Trust)**  
   Never trust, always verify (SPIFFE / SPIRE)

2. **Provenance (Supply Chain Security)**  
   Signed commits, SBOMs, and container images

3. **Prevention (Policy-as-Code)** ← *Live demo focus*  
   Automated checks that block non-compliant changes

4. **Detection (Runtime Security)** ← *Take-home*  
   Detect unexpected behavior in running systems

## Demo Overview (Live)

The live demo shows:

- A deployment request represented as JSON  
- A compliance policy written as code (Rego)  
- An automated decision: **allow or deny**  
- Clear, actionable feedback for developers  

This simulates what happens in:  
- Kubernetes admission control (OPA / Gatekeeper)  
- CI policy checks  
- Platform APIs enforcing governance  

## Folder Structure
```
lesson5/
├── compliance-demo/
│ ├── policies/
│ │ └── k8s.rego
│ ├── inputs/
│ │ ├── bad-deploy.json
│ │ └── good-deploy.json
│ ├── scripts/
│ │ └── check.sh
│ └── README.md
└── README.md
```

## Prerequisites (for Live Demo)
```
- macOS / Linux
- OPA CLI
```
### Install OPA (macOS)
```
brew install opa
```
### Verify:
```
./scripts/check.sh inputs/bad-deploy.json
````
#### Expected result:

❌ DENY  

List of policy violations (missing labels, insecure config, etc.)

```
./scripts/check.sh inputs/good-deploy.json
```
#### Expected result:

✅ PASS


## Summary

- I’m not managing developer workflows. I’m verifying compliance automatically.  
- This policy runs at the point of change — not weeks later in an audit.  
- There’s no ticket, no approval board, no checklist. Just fast, deterministic feedback.  
- The policy is version-controlled code, just like application logic.  
- This protects junior engineers by default, and it doesn’t slow experts who already know what they’re doing.  

### Why This Matters
- Traditional governance finds problems late, relies on manual reviews, creates pipeline bottlenecks, and frustrates developers  
- Policy-as-Code: Provides instant feedback, is consistent across environments, is auditable and testable, enables high velocity and compliance  

This is how platforms balance autonomy and control. 

## Where Falco Fits (Conceptual)

OPA answers: “Should this be allowed?”  
Falco answers: “Something unexpected just happened.”  

**OPA is the shield. Falco is the alarm.**

Prevention is necessary — but not sufficient. We must assume breach is possible.  

### Take-Home Exercise (Optional)  

For those who want to explore runtime detection:  

- Install Falco in a Linux-based Kubernetes cluster  
- Trigger a simple rule (e.g., shell spawned in a container)  
- Observe the real-time alert

### Falco detects:  

- Privilege escalation attempts  
- Unauthorized file access  
- Suspicious network activity  
- Interactive shells in containers  
- This complements OPA’s preventive controls.  

#### Key Takeaways  

- Replace manual stage gates with automated guardrails  
- Verify compliance at the point of change  
- Use Policy-as-Code for fast, consistent enforcement  
- Separate compliance work from compliance verification  
- Combine prevention (OPA) with detection (Falco)  
- Platforms embed governance transparently via golden paths  
