# Exercise: Comprehensive Metrics Dashboard (DORA • SPACE • PVM)

## What this Lesson2 demo does

This expanded exercise demonstrates how **multiple metric frameworks are derived from raw platform events**. It shows the complete picture of platform health by synthesizing:

1. **DORA Metrics** - Deployment Frequency, MTTR (delivery & reliability)
2. **SPACE Framework** - Activity, Communication, Satisfaction, Efficiency, Performance (team health)
3. **Platform Value Metrics (PVM)** - VCR, IAR, DTR (business impact & ROI)

A Python script generates synthetic event streams with realistic correlations, then automatically computes and visualizes all three frameworks in an interactive tabbed dashboard.

### Key Point

Metrics don't exist in isolation. This demo shows how:
- **DORA** measures *what you ship*
- **SPACE** measures *how your team feels while shipping*
- **PVM** measures *the value generated from platform investments*

Together, they tell the complete story of platform engineering success.

## Event Generation & Data Flow

### Synthetic but Realistic Event Streams

The demo generates synthetic events with realistic correlations:

**DORA Events:**
- `deploy` - Deployments happen 2-10 times per day across services
- `incident_start` / `incident_resolved` - Incidents occur on ~20% of days with MTTR 8-120 minutes

**SPACE Events:**
- `pr_created` / `pr_reviewed` / `pr_merged` - PR cycles tied to deployments (2-6 PRs/day)
- `satisfaction_survey` - Monthly surveys (1-5 scale, lower after incidents)
- Code review metrics derived from timestamp deltas

**PVM Events:**
- `platform_investment_hour` - Constant platform investment (2-8 hours/day at $150/hr)
- `incident_response` - Time spent responding to incidents (operationaltoil)
- `onboarding_complete` - Developer ramp-up events

All events are **chronologically ordered** with UTC timestamps.

### Production Equivalence

The metric computation pipeline is **identical to real systems**:

- **DORA**: Derives from CI/CD logs (GitHub Actions, GitLab, Argo, Spinnaker)
- **SPACE**: Derives from git activity, PR systems, surveys, and observability
- **PVM**: Derives from investment tracking, deployment counts, and incident costs

Only the **event source** changes—not the metric logic. This demo proves the methodology works with synthetic data.

## The Three Metric Frameworks

### DORA Metrics (Delivery & Reliability)

Measures how fast and stable you ship (from [DORA Research](https://dora.dev)).

- **Deployment Frequency**: How many times per day does code reach production?
- **MTTR (Mean Time to Recovery)**: How quickly can you resolve incidents?
- **Dashboard Tab**: Shows deployment trends over time + incident recovery windows

### SPACE Framework (Team & Developer Health)

Measures the human side of productivity (from [Forsgren et al., 2021](https://getdx.com/blog/space-metrics/).

| Dimension | What It Measures | Example Metric |
|-----------|-----------------|-----------------|
| **S** - Satisfaction & Well-being | How fulfilled developers are | Monthly survey scores (1-5) |
| **P** - Performance | Delivery quality and reliability | Incident rate per deployment |
| **A** - Activity | Observable work contributions | PRs created, code reviews completed |
| **C** - Communication & Collaboration | Team coordination effectiveness | Code review turnaround time |
| **E** - Efficiency & Flow | Ability to work uninterrupted | Time from PR creation to merge |

**Why SPACE matters**: You can hit elite DORA metrics while burning out your team. SPACE captures the sustainability of your delivery.

### Platform Value Metrics (PVM)

Measures ROI of platform investments (from [Chankramath & Kotagiri, 2023](https://itrevolution.com/product/value-internal-developer-platform-investments/)).

| Metric | Formula | Default | Target | Meaning |
|--------|---------|---------|--------|---------|
| **VCR** - Value to Cost Ratio | (Total Value / Total Cost) × 100 | 200% | 1000% | Platform value per $1 spent |
| **IAR** - Innovation Adoption Rate | ((Adoption_now - Adoption_prev) / Adoption_prev) × 100 | 10% | 30% | Year-over-year adoption growth |
| **DTR** - Developer Toil Ratio | (Toil Time / Feature Time) × 100 | <30% | <10% | % of time on repetitive work (lower is better) |

**Why PVM matters**: Boards ask "What's the ROI?" PVM connects platform investment to measurable business outcomes.

## Seeds & Scenario Exploration

The script uses a **seeded random number generator** to create repeatable, realistic scenarios.

### Command Line Seeds (Initial Load)

```bash
python3 metrics_demo.py --seed 42   # Load with seed 42
python3 metrics_demo.py --seed 7    # Load with seed 7
```

### What Seeds Control

Same seed = identical dataset (reproducible for demos)
Different seed = different "delivery universe" (varies incidents, PRs, satisfaction, etc.)

This demonstrates how metrics respond to **operational variance** while keeping the methodology constant.

## Why This Matters

**Core Principle**: Metrics don't magically exist—they are computed from events your platform already emits.

By synthesizing DORA, SPACE, and PVM together:

- **Teams** see the relationship between delivery velocity and team health
- **Leaders** understand why platform investments matter (not just cost)
- **Platform engineers** can reason about impact, not just tooling

## Setup & Usage

### Install Dependencies

```bash
pip install pandas matplotlib
```

### Run with Defaults (14 days, seed 42)

```bash
python3 metrics_demo.py
```

The dashboard will launch with **fully interactive seed controls**—no need to restart to try different scenarios!

### Start with Different Observation Windows

```bash
# 30-day observation (shows more trends)
python3 metrics_demo.py --days 30

# Extended observation period (60 days)
python3 metrics_demo.py --days 60

# Quick demo (7 days)
python3 metrics_demo.py --days 7
```

Once the dashboard opens, use the **Seed input field** to explore any scenario dynamically without restarting.

### Interactive Dashboard

The dashboard is **fully interactive**. Once running:

**Navigation Buttons:**
- **DORA** (blue) - Deployment frequency, MTTR, timeline (using calendar dates)
- **SPACE** (green) - Activity, collaboration, satisfaction, efficiency (using relative days from start)
- **PVM** (purple) - VCR, IAR, DTR ratios

**Dynamic Seed Exploration:**
- Type a new seed number in the **Seed field** (left side)
- Press **Enter** or click **Refresh** to reload metrics instantly
- Dashboard updates while staying on the current tab

**Close:**
- Click **Quit** (red) to close gracefully

### Demo Scenarios: Recommended Seeds

Try these seeds to explore different operational scenarios:

| Seed | Scenario | What to Notice |
|------|----------|-----------------|
| **42** | Balanced baseline | Moderate DORA metrics, stable SPACE scores |
| **7** | High incidents | Higher MTTR, lower satisfaction on SPACE tab, lower VCR on PVM |
| **99** | Efficient delivery | High deployment frequency, good satisfaction, high IAR growth |
| **1** | Early stage | Lower metrics across all frameworks, room for improvement |
| **100** | Mature platform | Elite DORA (5+ deploys/day), strong SPACE, healthy PVM ratios |


## Output & Visualization

The script produces a **tabbed dashboard** with three interactive tabs:

### Tab 1: DORA Metrics
- **Deployment Frequency**: Line chart of deployments per day
- **Recovery (MTTR)**: Line chart of incident recovery times
- **Timeline Overlay**: Unified view showing deploys as ticks + incidents as recovery bars

### Tab 2: SPACE Framework
- **Activity**: PR creation and code review velocity over time
- **Collaboration**: Code review turnaround time trend (weekly)
- **Satisfaction & Well-being**: Monthly survey scores with trend
- **Efficiency & Flow**: Time from PR creation to merge (with variance)

### Tab 3: Platform Value (PVM)
- **VCR (Value to Cost Ratio)**: Bar chart with target lines (200% default, 1000% target)
- **IAR (Innovation Adoption Rate)**: Month-over-month growth visualization
- **DTR (Developer Toil Ratio)**: Percentage of time on toil vs. features (lower is better)
- **Impact Summary**: Platform hours invested vs. deployments generated

### Console Output

Each run prints a comprehensive summary:

```
--- DORA METRICS (Delivery & Reliability) ---
Avg deployments/day: 5.29
Incidents: 2 | Avg MTTR: 8.0 min | P95 MTTR: 8.0 min

--- SPACE METRICS (Team & Developer Health) ---
Activity: Avg PRs/day: 4.29 | Avg reviews/day: 3.86
Collaboration: Avg code review turnaround: 23.8 hours
Satisfaction: Avg satisfaction score: 3.0/5.0
Efficiency: Avg PR→merge time: 28.1 hours
Performance: Incident rate: 2.70% per deployment

--- PLATFORM VALUE METRICS (PVM) ---
VCR: 129% | Platform hours invested: 77
IAR: -15.0% | First period: 40 deploys | Second period: 34 deploys
DTR: 0.0% | Toil: 16 min | Feature: 95040 min
```

## Code Functions Overview

### Event Generation & Data Processing

| Function | Purpose |
|----------|---------|
| `generate_events(days, seed)` | Creates synthetic event stream (deploys, incidents, PRs, surveys) with realistic correlations |
| `to_dataframe(events)` | Converts event list to pandas DataFrame with UTC timestamps |

### DORA Metrics

| Function | Purpose |
|----------|---------|
| `compute_deployments_per_day(df)` | Counts daily deployments, returns deployment frequency |
| `compute_mttr(df)` | Pairs incident start/end events, calculates recovery time |

### SPACE Framework

| Function | Purpose |
|----------|---------|
| `compute_activity_metrics(df)` | Daily PR creation and code review counts |
| `compute_collaboration_metrics(df)` | Weekly code review turnaround time (created → reviewed) |
| `compute_satisfaction_metrics(df)` | Weekly average developer satisfaction survey scores (1-5) |
| `compute_efficiency_metrics(df)` | Weekly PR merge time (created → merged) with variance |
| `compute_performance_metrics(df, mttr)` | Incident rate per deployment and reliability metrics |

### Platform Value Metrics (PVM)

| Function | Purpose |
|----------|---------|
| `compute_pvm_vcr(df)` | Value to Cost Ratio: platform value / investment cost |
| `compute_pvm_iar(df, days)` | Innovation Adoption Rate: period-over-period deployment growth |
| `compute_pvm_dtr(df)` | Developer Toil Ratio: incident response time vs. feature work time |

### Visualization

| Function | Purpose |
|----------|---------|
| `plot_dashboard(days)` | Creates interactive 3-tab dashboard (DORA, SPACE, PVM) with live seed controls |

## Customization & Extension Guide

### Modifying Synthetic Data Generation

To change how synthetic events are generated, edit the `generate_events()` function:

**Adjust deployment frequency:**
```python
# Line ~50: Change deployment count per day
deploys_today = random.randint(2, 10)  # Change to (3, 15) for more deployments
```

**Adjust incident rate:**
```python
# Line ~95: Change incident frequency
incident_days = sorted(random.sample(range(days), k=max(2, days // 5)))  # days // 5 = ~20% of days
# Change to: k=max(2, days // 3)  for more incidents (33%), or k=max(1, days // 10) for fewer (10%)
```

**Adjust PR/review cycle:**
```python
# Line ~66: Change daily PR count
prs_today = random.randint(2, 6)  # Change to (1, 3) for fewer PRs, (5, 10) for more
```

**Adjust satisfaction scores:**
```python
# Line ~94: Modify satisfaction baseline
satisfaction = random.choice([1, 2, 3, 4, 5])  # Change weights: [1, 1, 2, 4, 5] for higher baseline
```

### Integrating Real Data Sources

To use actual metrics instead of synthetic data, replace the event generation:

#### From GitHub API (PRs, Code Reviews)
```python
# Replace generate_events() logic with:
import requests
from github import Github

def fetch_github_events(repo_owner, repo_name, days):
    """Fetch real PR and review data from GitHub."""
    g = Github(os.getenv('GITHUB_TOKEN'))
    repo = g.get_user(repo_owner).get_repo(repo_name)

    events = []
    for pull in repo.get_pulls(state='closed'):
        if (datetime.now(timezone.utc) - pull.created_at).days <= days:
            events.append(Event(
                ts=pull.created_at,
                kind='pr_created',
                service=repo_name,
                pr_id=f"pr{pull.number}"
            ))
            # Add review events...
    return events
```

#### From Incident Management (PagerDuty, OpsGenie)
```python
# Replace incident generation with API calls:
import pdpyras  # PagerDuty Python REST API Session

def fetch_pagerduty_incidents(api_token, days):
    """Fetch real incidents from PagerDuty."""
    session = pdpyras.APISession(api_token)
    incidents = session.list_all('incidents', params={'statuses': ['resolved']})

    events = []
    for incident in incidents:
        if (datetime.now(timezone.utc) - incident['created_at']).days <= days:
            events.append(Event(ts=incident['created_at'], kind='incident_start', ...))
            events.append(Event(ts=incident['last_status_change_at'], kind='incident_resolved', ...))
    return events
```

#### From CI/CD Pipeline (GitHub Actions, GitLab)
```python
# Replace deployment tracking:
def fetch_deployments(ci_provider='github'):
    """Fetch real deployment data from CI/CD."""
    if ci_provider == 'github':
        # Use GitHub API to fetch workflow runs
        runs = repo.get_workflow('deploy.yml').get_runs(status='completed')
        for run in runs:
            events.append(Event(ts=run.updated_at, kind='deploy', ...))
    elif ci_provider == 'gitlab':
        # Use GitLab API for deployments
        deployments = project.deployments.list()
        for deploy in deployments:
            events.append(Event(ts=deploy.updated_at, kind='deploy', ...))
```

#### From Developer Surveys (Google Forms, Typeform)
```python
# Fetch satisfaction survey responses:
def fetch_satisfaction_surveys(form_id, api_key):
    """Fetch real satisfaction data from survey platform."""
    # Using Typeform API as example
    url = f"https://api.typeform.com/responses?form_id={form_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(url, headers=headers)
    for answer in response.json()['items']:
        # Extract satisfaction score
        events.append(Event(
            ts=answer['submitted_at'],
            kind='satisfaction_survey',
            service='team',
            metric_value=float(answer['answers'][0]['number'])
        ))
```

### Extending with Custom Metrics

Add new metrics by creating computation functions following the pattern:

```python
def compute_custom_metric(df: pd.DataFrame) -> pd.DataFrame:
    """Compute your custom metric from event data."""
    # Filter events relevant to your metric
    custom_events = df[df["kind"] == "your_event_type"].copy()

    if len(custom_events) == 0:
        return pd.DataFrame()

    # Group by time period
    custom_events["period"] = custom_events["ts"].dt.floor("1D")

    # Aggregate
    result = custom_events.groupby("period").agg({
        "metric_value": ["mean", "sum", "count"]
    }).reset_index()

    return result
```

Then add to the dashboard:
```python
# In plot_dashboard() function:
custom = metrics["custom_metric"]
ax_custom = fig.add_subplot(2, 2, 1)
ax_custom.plot(custom["period"], custom["metric_value"], marker="o")
ax_custom.set_title("Your Custom Metric", fontweight="bold")
```

### Modifying Dashboard Appearance

**Change colors:**
```python
# In plot_dashboard(), modify button colors:
btn_dora = Button(ax_btn_dora, "DORA", color="your_color", hovercolor="darker_shade")
```

**Add more detail to plots:**
```python
# Add confidence intervals, annotations, or additional data series
ax.fill_between(dates, lower, upper, alpha=0.2)  # Confidence bands
ax.annotate("Peak", xy=(date, value), xytext=(10, 10), arrowprops=dict(...))
```

**Change observation window:**
```bash
# Adjust default days in main():
python3 metrics_demo.py --days 90  # 3-month view
python3 metrics_demo.py --days 365 # Annual view
```

### Performance Tuning

**For large datasets (>10,000 events):**
```python
# Use event filtering to reduce memory:
df = df[df["ts"] > start_date]  # Filter old events
df = df[df["kind"].isin(["deploy", "incident_start"])]  # Focus on key events
```

**Improve plot rendering:**
```python
# Reduce plot resolution in plot_dashboard()
plt.rcParams['figure.dpi'] = 80  # Lower DPI for faster rendering
```

### Testing Your Customizations

```bash
# Test with small dataset
python3 metrics_demo.py --days 7 --seed 1

# Verify metrics are computed
python3 -c "from metrics_demo import *; events = generate_events(7, 1); df = to_dataframe(events); print(compute_activity_metrics(df))"

# Check for errors in custom functions
python3 -c "from metrics_demo import *; df = to_dataframe(generate_events(14, 42)); compute_custom_metric(df)"
```

### Common Extension Patterns

| Use Case | Modification |
|----------|--------------|
| Add team size tracking | Add `team_size` field to Event, compute `deployments_per_person` |
| Track deployment success rate | Add `success` boolean field, compute pass rate per day |
| Monitor on-call burden | Add `on_call_hours` events, track DTR impact |
| Measure code quality | Parse code review comments, compute quality score |
| Track infrastructure costs | Add cost metrics to PVM calculations |
| Monitor SLA compliance | Correlate MTTR with SLA targets, compute compliance % |
