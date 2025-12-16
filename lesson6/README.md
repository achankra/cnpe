# Lesson 6 – Observability & Reliability  
**From Signals to Decisions**

This lesson shows how observability is not about dashboards or tools, but about
**making reliable engineering decisions using signals**.

Instead of setting up Prometheus or Grafana, this lesson uses **small, local artifacts**
to make the core ideas of SLIs, SLOs, error budgets, and the three pillars of observability
clear and teachable.

---

## Learning Objectives

By the end of this lesson, students will understand:

- The difference between **metrics, logs, and traces**
- What **SLIs, SLOs, and error budgets** actually mean
- How reliability becomes a **control signal**, not an ops metric
- Why observability is a **design concern**, not an afterthought
- How teams use observability data to decide *when to ship vs when to stop*

---

## Folder Structure

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

yaml
Copy code

---

## Part 1 – SLOs as a Control Signal

### SLO definition (`slo.yaml`)
The SLO defines *what “good enough” means* for the service.

```yaml
service: payments-api
sli:
  description: "Percentage of successful requests"
slo:
  target: 99.9
  window: 30d
Calculate reliability (calculate_slo.py)
bash
Copy code
python3 calculate_slo.py
This computes:

SLI (actual reliability)

SLO target

Error budget

A clear decision: ship or stop and fix

What to say (SLO demo)
“We’re not arguing about how bad an incident felt.
We’re measuring whether the service met its reliability objective.”

“Error budgets turn observability into behavior.
When the budget is healthy, we move faster.
When it’s burned, we stop and fix reliability.”

Part 2 – Metrics: What Happened?
Generate plots
bash
Copy code
python3 plot_metrics.py
This generates:

out/p95_latency.png

out/error_rate.png

These plots answer:

What happened to the system over time?

They clearly show:

A latency spike

An error-rate spike

A recovery period

What to say (metrics)
“Metrics are about symptoms.
They tell us that something is wrong, not why.”

“This is what alerts should be based on — user impact.”

Part 3 – Logs & Traces: How and Why?
Run the investigation script
bash
Copy code
./scripts/investigate.sh
This script produces:

Incident summary

Peak latency

Peak error rate

Dominant upstream

Slowest span

Metrics view – confirms the spike

Logs view – shows retries, timeouts, failures

Trace view – pinpoints the bottleneck

What to say (tri-pillar demo)
“Metrics tell me what happened: latency and errors spiked.”

“Logs tell me how it happened: retries and upstream timeouts.”

“Traces tell me why it happened: one downstream call dominated the request.”

“You need all three — but for different questions.”

Why This Matters for Platform Engineering
Observability is not owned by ops

It is a product design requirement

Platforms must make the right signals easy to produce

Developers should not guess during incidents

This is observability-driven development.

Key Takeaways
Metrics, logs, and traces answer different questions

SLOs define acceptable reliability

Error budgets align product and engineering

Observability data should drive decisions, not dashboards

Reliability is managed, not hoped for

Platforms make good behavior the default

