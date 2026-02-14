# Lesson 9 – Automation Demo: Scaling Platforms
This lesson demonstrates how modern platform teams use **event-driven pipelines** to decouple systems, scale automation, and avoid tight integrations between tools.

The demo shows how a **single deployment event** can trigger multiple independent automations — including **automated issue creation** — without modifying the original producer.

## Learning Objectives

By the end of this lesson, students will understand:

- Why event-driven architecture matters at scale
- The difference between **direct integrations** and **event-based decoupling**
- What an **adapter** is and why platforms normalize events
- How a single event can **fan out** to multiple consumers
- How automation naturally emerges from events
- Why event streams are a core platform capability

## Core Idea

### Tightly coupled pipelines (does not scale)

CI → Slack
CI → Jira
CI → Observability
CI → Custom scripts

Each new integration increases coupling and fragility.

### Event-driven pipelines (scales cleanly)

Producer → Adapter → Normalized Event → Consumers

- Producers do not know who consumes events
- Consumers do not know who produced events
- The **platform owns the event contract**

## Folder Structure

```
lesson9/
├── bus.py
├── schemas.py
├── run_demo.py
├── adapters/
│ └── github_adapter.py
├── consumers/
│ ├── issue_consumer.py
│ ├── notify_consumer.py
│ └── deploy_marker_consumer.py
├── events/
│ ├── github_deploy_completed.json
│ └── github_deploy_failed.json
└── README.md
```

## Demo Overview

The demo simulates:

1. A CI/CD system emitting a deployment event
2. An **adapter** converting it into a platform-standard event
3. An **event bus** publishing the event
4. Multiple **consumers** reacting independently:
   - Notification
   - Observability marker
   - Automated issue creation
5. Optional addition of a **new consumer** without touching the producer
6. No Kafka, No Docker, No infrastructure setup!

The goal is to make **decoupling visible**.

## Running the Demo

From the `lesson9/` directory:

```
python3 run_demo.py events/github_deploy_completed.json
```

## Demo Calls (Run These Live)

**1. Successful deployment (fan-out automation)** 

```
python3 run_demo.py events/github_deploy_completed.json
```

### What happens

- Adapter normalizes the event
- Notification consumer reacts
- Observability consumer emits a deploy marker
- No issues are created

 **2. Failed deployment → automated issue creation** 
 
```
python3 run_demo.py events/github_deploy_failed.json
```

### What happens

- Same producer event
- Same adapter
- Issue consumer automatically creates an issue
- Other consumers still run independently

**3. Add a new consumer (no producer changes)** 
```
python3 run_demo.py events/github_deploy_failed.json --enable new_consumer
```

### What this proves

- Producers are unaware of consumers
- New automation can be added safely
- No refactoring or redeploying producers

**4. Explicit fan-out demonstration** 

```
python3 run_demo.py events/github_deploy_completed.json --fanout
```

### What this shows

- One event
- Multiple independent reactions
- No orchestration logic in the producer

## Summary

- At small scale, teams integrate tools directly.
- At scale, that becomes a fragile dependency web.
- Instead, platforms standardize on events.
- Adapters normalize inbound signals into a shared schema.
- Consumers react independently — including automated issue creation.
- You can add new automation without changing the system that emitted the event.

### Why This Matters

**Without event-driven pipelines:** 

1. CI systems become integration hubs
2. Changes require cross-team coordination
3. Automation becomes brittle

**With event-driven pipelines:** 

1. Systems are loosely coupled
2. Automation scales naturally
3. Platforms evolve without breaking producers

This is how platforms scale coordination without becoming bottlenecks.

## Mapping to Real Platforms

| Demo Concept         | Real-World Equivalent                   |
|---------------------|-----------------------------------------|
| In-memory event bus | Kafka / PubSub / EventBridge             |
| Adapter             | Webhooks / Connectors                    |
| Normalized schema   | CloudEvents / Internal event standards   |
| Consumers           | Automation services / Workers / Lambdas |
| Issue consumer      | Jira / GitHub Issues automation          |
| Deploy marker       | Observability deploy annotations         |


### Key Takeaways

- Events decouple producers from consumers
- Adapters protect platforms from vendor lock-in
- One event can drive many automations
- New automation does not require producer changes
- Event-driven pipelines scale coordination cleanly

