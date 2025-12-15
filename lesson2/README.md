# Exercise: Metrics demo: visualizing deployment & recovery


## What this demo does

This exercise demonstrates how **deployment and reliability metrics are derived from raw platform events**, not manually tracked or guessed. It translates raw events → DORA view in 90 seconds with synthetic data

A small Python script generates (or can later ingest) an event stream consisting of:

- `deploy`
- `incident_start`
- `incident_resolved`

From these raw events, the script automatically:

- Plots **deployments per day** (Deployment Frequency)
- Computes and plots **MTTR per incident** (Recovery Time)
- Overlays deployments and incidents on a **single timeline**, making the relationship between delivery and recovery visible

The goal is to show how platform teams can move from *events → metrics → insight* in minutes.

## How the data works

### Synthetic but realistic data

The demo uses **synthetic data generated at runtime**. This allows the exercise to be:

- Fast to run
- Repeatable
- Safe to demo live
- Free from external dependencies

Even though the data is synthetic, the **metric pipeline is identical to real systems**. In production, the same logic would apply to:

- CI/CD logs (GitHub Actions, GitLab, Argo, Spinnaker)
- Incident systems (PagerDuty, OpsGenie, ServiceNow)
- Observability pipelines (logs, events, traces)

Only the **event source** changes — not the metric logic.

## What does `--seed` do?

The script uses a random number generator to simulate deployments and incidents.

```bash
python metrics_demo.py --seed 42
python metrics_demo.py --seed 7
```
seed controls the random data generation. The same seed always produces the same dataset. Changing the seed produces a different but still repeatable scenario. This demonstrates ow metrics shift under different operating conditions Think of the seed as selecting a different delivery universe.

## Why this matters

This exercise reinforces a core platform engineering principle:

Metrics don’t magically exist — they are computed from events your platform already emits. By visualizing deployment frequency and MTTR together:

-- Teams see how delivery and recovery interact
-- Leaders understand why platform investments matter
-- Platform teams can reason about impact, not just tooling

## Setup

```
pip install pandas matplotlib
python metrics_demo.py
```

## Optional:

```
python metrics_demo.py --days 21 --seed 7
```

## Output

The script renders three charts:

1. Deployment Frequency
2. Deployments per day over time
2. Recovery (MTTR)

### Timeline Overlay

1. Each dot represents the recovery time of an incident  
2. Deployments shown as ticks  
3. Incidents shown as recovery bars  
4. A single view of deploys vs recoveries  

Together, these charts tell the full deployment & recovery story at a glance.
