# Lesson 7 – Demo: Self-service resource provisioning

**From Tickets to APIs**

This lesson demonstrates how platform teams enable **self-service infrastructure** using **well-designed Platform APIs**, instead of ticket-driven workflows. The demo shows how developers can provision resources in seconds using a **contract-first API**, while the platform hides complexity and enforces guardrails.

## Learning Objectives

By the end of this lesson, students will understand:

- Why **APIs are the primary interface** of a modern platform
- How platform APIs replace ticket queues
- The idea of **self-service resource provisioning**
- How platforms hide implementation complexity
- The **80/20 rule** in platform API design
- Why OpenAPI is critical for platform products

## What This Demo Shows?

This demo simulates a **Platform Provisioning API** that allows developers to:

- Request resources (e.g., Kubernetes namespaces, storage)
- Receive immediate, structured feedback
- Check status without waiting for humans
- Avoid dealing with Terraform, kubectl, or cloud IAM directly

This is **not** about infrastructure automation tools.  It’s about **how platforms present capabilities**.

## Folder Structure
```
lesson7/
│ ├── main.py # Platform API (FastAPI)
│ └── README.md
```

## Core Idea: Platform API as Product

### In a ticket-driven world: Developer → Ticket → Waiting → Manual Work → Days/Weeks  
### In a platform-driven world: Developer → API Call → Instant Feedback → Self-Service

The API is the **product interface**.

## How to Run the Demo?

```
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn pydantic
uvicorn main:app --reload --port 8080
```

- Explore the API Contract (Design-First)  
- Open in your browser:  
  -- Swagger UI :  http://127.0.0.1:8080/docs  
  -- OpenAPI spec: http://127.0.0.1:8080/openapi.json  
  
**This contract is what**

- Developers depend on  
- Docs are generated from  
- SDKs can be created from  

## Demo Calls

**1. Simple self-service request (80% path)** 
```
curl http://127.0.0.1:8080/provision-requests \
  -H "Content-Type: application/json" \
  -d '{
    "team": "payments-team",
    "env": "dev",
    "resource_type": "k8s-namespace"
  }'
```
### What this shows?

- Safe defaults  
- Minimal input  
- Immediate success  
- No infrastructure knowledge required (DevEx improvement!)  

**2. Advanced controls (20% path)**
```
curl http://127.0.0.1:8080/provision-requests \
  -H "Content-Type: application/json" \
  -d '{
    "team": "payments-team",
    "env": "staging",
    "resource_type": "k8s-namespace",
    "advanced": {
      "annotations": {
        "owner": "platform-team",
        "cost-center": "cc-102"
      }
    }
  }'
```

### What this shows?

- Power-user flexibility  
- Controlled extensibility  
- No raw Terraform or kubectl exposure  
- Platform remains opinionated  

**3. Intentional failure (actionable error messaging)**
```
curl http://127.0.0.1:8080/provision-requests \
  -H "Content-Type: application/json" \
  -d '{
    "team": "failme",
    "env": "dev",
    "resource_type": "s3-bucket"
  }'
```

### What this shows?

- Guardrails enforced at the API  
- Clear, actionable error messages  
- No silent failures or tickets  

**4. List provisioning requests (visibility without tickets)**
   
```
curl http://127.0.0.1:8080/provision-requests
```

### What this shows?

- Transparency  
- Async-friendly workflows  
- Status visibility without human intervention  

## Summary

- The platform is not Terraform or Kubernetes. The platform is the API.  
- Developers don’t want to learn infrastructure internals. They want outcomes.  
- This API hides complexity and exposes value: a resource name, a status, and what to do next.  
- Notice the 80/20 rule: simple defaults for most teams, optional advanced controls for power users.  
- This is how we go from weeks of waiting to seconds of self-service.

### Why This Matters

**Without platform APIs** 

-- Platform teams become ticket bottlenecks  
-- Knowledge becomes tribal  
-- Velocity stalls as scale increases  

**With platform APIs**

-- Self-service becomes the default  
-- Guardrails are enforced automatically  
-- Platform teams scale impact without scaling headcount  



