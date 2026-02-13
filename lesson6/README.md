# Lesson 6 – SLO demo: automated error budget monitoring

**From Signals to Decisions**

This lesson shows how observability is not about dashboards or tools, but about **making reliable engineering decisions using signals**.

Instead of setting up Prometheus or Grafana, this lesson uses **small, local artifacts** to make the core ideas of SLIs, SLOs, error budgets, and the three pillars of observability
clear and teachable.

## Learning Objectives

By the end of this lesson, students will understand:

- The difference between **metrics, logs, and traces**
- What **SLIs, SLOs, and error budgets** actually mean
- How reliability becomes a **control signal**, not an ops metric
- Why observability is a **design concern**, not an afterthought
- How teams use observability data to decide *when to ship vs when to stop*

## How This Demo Works: A Coherent Picture of Observability

This lesson uses **three small, interconnected demos** to show how observability works as a complete system:

### The Problem
A service (payments-api) experiences an incident. Teams need to:
1. **Know** if reliability is good enough (SLO check) → Decide shipping velocity
2. **See** what happened (metrics) → Understand the scope of the incident
3. **Understand** why it happened (logs + traces) → Fix the root cause

### The Three Pillars in Action

**Demo 1: SLOs as Control** (`calculate_slo.py`)
- Shows error budget **before** and **after** the incident
- Proves that observability drives behavior
- When budget is healthy → move fast
- When budget is burned → stop and stabilize

**Demo 2: Metrics Answer "What?"** (`plot_metrics.py`)
- Shows **symptom detection** (latency spike, error spike)
- Proves that dashboards answer "did something go wrong?"
- Metrics are the first signal that an incident occurred
- They define the **scope** (how bad, how long)

**Demo 3: Logs & Traces Answer "How?" & "Why?"** (`investigate.sh`)
- Shows **root cause analysis** (retries, timeouts, bottlenecks)
- Logs explain the **mechanism** (what failed)
- Traces pinpoint the **culprit** (which dependency, which span)
- Together they explain why metrics spiked

### The Coherent Flow

```
        [Incident Occurs]
              ↓
   [Metrics detect it]  ← Do we have a problem?
              ↓
   [SLO check impact]   ← Is it serious enough to stop shipping?
              ↓
   [Logs explain it]    ← How did the failure propagate?
              ↓
   [Traces pinpoint it] ← Which exact dependency is the culprit?
              ↓
   [Fix deployed]       ← Error budget recovered
              ↓
   [Back to shipping]   ← Observability enabled the decision
```

### Why This Matters

- **SLOs** = reliability as code (not opinion)
- **Metrics** = symptoms (tell you something is wrong)
- **Logs** = mechanisms (show how failures flow)
- **Traces** = causality (prove which component caused it)
- **Together** = complete incident lifecycle from detection to resolution

Students will see that observability is **not about tools** (no Prometheus, no Grafana needed). It's about having the right signals at each decision point in the incident response process.

## Folder Structure
```
lesson6/
├── slo.yaml # SLO defined as code
├── traffic.log # Simulated request outcomes
├── calculate_slo.py # Computes SLI, SLO, error budget
├── plot_metrics.py # Generates simple latency & error plots
├── data/
│ ├── metrics.csv # Time-series metrics
│ ├── logs.jsonl # Structured logs
│ └── trace.json # Single representative trace
├── scripts/
│ └── investigate.sh # Incident summary + tri-pillar investigation
├── out/
│ ├── p95_latency.png
│ └── error_rate.png
└── README.md
```

## Part 1 – SLOs as a Control Signal

### SLO definition (`slo.yaml`)
The SLO defines *what “good enough” means* for the service.

```
service: payments-api
sli:
  description: "Percentage of successful requests"
slo:
  target: 99.9
  window: 30d
```

### Calculate reliability (calculate_slo.py)
```
python3 calculate_slo.py
```

This computes:  

- SLI (actual reliability)
- SLO target
- Error budget

### Summary

- We’re not arguing about how bad an incident felt  
- We’re measuring whether the service met its reliability objective.  
- Error budgets turn observability into behavior. 
- When the budget is healthy, we move faster.  
- When it’s burned, we stop and fix reliability.  

## Part 2 – Metrics: What Happened?

Generate plots
```
python3 plot_metrics.py
```

### This generates:

- out/p95_latency.png  
- out/error_rate.png  

These plots answer what happened to the system over time by showing:

- A latency spike  
- An error-rate spike  
- A recovery period  

### Summary
- Metrics are about symptoms.  
- They tell us that something is wrong, not why.  
- This is what alerts should be based on — user impact.  

## Part 3 – Logs & Traces: How and Why?

Run the investigation script  
```
./scripts/investigate.sh
```

This script produces:  

- Incident summary  
- Peak latency  
- Peak error rate  
- Dominant upstream  
- Slowest span  
- Metrics view – confirms the spike  
- Logs view – shows retries, timeouts, failures  
- Trace view – pinpoints the bottleneck  

### Summary

- Metrics tell me what happened: latency and errors spiked.  
- Logs tell me how it happened: retries and upstream timeouts.  
- Traces tell me why it happened: one downstream call dominated the request.  
- You need all three — but for different questions.  

## Why This Matters for Platform Engineering

- Observability is not owned by ops  
- It is a product design requirement  
- Platforms must make the right signals easy to produce  
- Developers should not guess during incidents  
- This is observability-driven development  
- Metrics, logs, and traces answer different questions  
- SLOs define acceptable reliability  
- Error budgets align product and engineering  
- Observability data should drive decisions, not dashboards  
- Reliability is managed, not hoped for  
- Platforms make good behavior the default  

