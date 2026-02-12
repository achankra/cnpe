#!/usr/bin/env python3
"""
Metrics demo: visualizing deployment frequency + MTTR (recovery).
Run:
  pip install pandas matplotlib
  python metrics_demo.py
Optional:
  python metrics_demo.py --days 21 --seed 7
"""

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import random
import math

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button


@dataclass(frozen=True)
class Event:
    ts: datetime
    kind: str  # "deploy" | "incident_start" | "incident_resolved" |
               # "pr_created" | "pr_reviewed" | "pr_merged" |
               # "satisfaction_survey" | "platform_investment_hour" |
               # "incident_response" | "onboarding_complete"
    service: str
    deploy_id: str | None = None
    incident_id: str | None = None
    pr_id: str | None = None
    metric_value: float | None = None  # for surveys (1-5), velocity, cost, etc.


SERVICES = ["payments-api", "orders", "web-frontend"]


def _utc(dt: datetime) -> datetime:
    return dt.astimezone(timezone.utc).replace(tzinfo=timezone.utc)


def generate_events(days: int, seed: int) -> list[Event]:
    """
    Generate a plausible stream:
    - deployments happen multiple times/day across services
    - incidents occur occasionally; each incident has start+resolved
    - PRs and code reviews correlate with deployments
    - Satisfaction surveys monthly
    - Platform investment hours constant
    - Developer onboarding events occasional
    """
    random.seed(seed)
    now = _utc(datetime.now())
    start = now - timedelta(days=days)

    events: list[Event] = []
    deploy_counter = 0
    incident_counter = 0
    pr_counter = 0

    # Deployments + correlated PRs and code reviews
    for d in range(days):
        day = start + timedelta(days=d)
        deploys_today = random.randint(2, 10)
        for _ in range(deploys_today):
            deploy_counter += 1
            svc = random.choice(SERVICES)
            ts = day + timedelta(hours=random.randint(8, 18), minutes=random.randint(0, 59))
            events.append(Event(ts=_utc(ts), kind="deploy", service=svc, deploy_id=f"d{deploy_counter:04d}"))

        # PRs and code reviews (loosely tied to deployments)
        prs_today = random.randint(2, 6)
        for _ in range(prs_today):
            pr_counter += 1
            pr_id = f"pr{pr_counter:04d}"
            svc = random.choice(SERVICES)

            # PR creation
            pr_creation = day + timedelta(hours=random.randint(8, 16), minutes=random.randint(0, 59))
            events.append(Event(ts=_utc(pr_creation), kind="pr_created", service=svc, pr_id=pr_id))

            # Code review (6-48 hours after PR creation)
            review_hours = random.randint(6, 48)
            pr_review = pr_creation + timedelta(hours=review_hours)
            events.append(Event(ts=_utc(pr_review), kind="pr_reviewed", service=svc, pr_id=pr_id))

            # Merge (if reviewed)
            if random.random() > 0.1:  # 90% merge rate
                pr_merge = pr_review + timedelta(hours=random.randint(1, 8))
                events.append(Event(ts=_utc(pr_merge), kind="pr_merged", service=svc, pr_id=pr_id))

        # Platform investment hours (steady baseline)
        platform_hours = random.uniform(2, 8)  # 2-8 hours per day
        events.append(Event(
            ts=_utc(day + timedelta(hours=12)),
            kind="platform_investment_hour",
            service="platform",
            metric_value=platform_hours
        ))

    # Incidents (some tied to deploy bursts)
    incident_days = sorted(random.sample(range(days), k=max(2, days // 5)))
    for d in incident_days:
        incident_counter += 1
        svc = random.choice(SERVICES)
        start_ts = start + timedelta(days=d, hours=random.randint(10, 22), minutes=random.randint(0, 59))
        # MTTR between 8 and 120 minutes
        mttr_min = random.choice([8, 12, 18, 25, 40, 60, 90, 120])
        resolved_ts = start_ts + timedelta(minutes=mttr_min)
        inc_id = f"i{incident_counter:03d}"
        events.append(Event(ts=_utc(start_ts), kind="incident_start", service=svc, incident_id=inc_id))
        events.append(Event(ts=_utc(resolved_ts), kind="incident_resolved", service=svc, incident_id=inc_id))

        # Incident response time (toil): proportional to MTTR
        events.append(Event(
            ts=_utc(start_ts),
            kind="incident_response",
            service=svc,
            metric_value=mttr_min * random.uniform(0.8, 1.2)  # slightly varied
        ))

    # Monthly satisfaction surveys (1-5 scale)
    for month in range((days // 30) + 1):
        survey_day = start + timedelta(days=month * 30 + random.randint(0, 5))
        if survey_day <= now:
            satisfaction = random.choice([1, 2, 3, 4, 5])
            # Lower satisfaction after incidents
            incident_count = sum(1 for d in incident_days if abs(d - (month * 30)) < 7)
            if incident_count > 0:
                satisfaction = max(1, satisfaction - random.randint(0, 2))
            events.append(Event(
                ts=_utc(survey_day),
                kind="satisfaction_survey",
                service="team",
                metric_value=float(satisfaction)
            ))

    # Occasional onboarding events (one every 10 days on average)
    onboarding_days = sorted(random.sample(range(days), k=max(1, days // 10)))
    for d in onboarding_days:
        onboarding_day = start + timedelta(days=d)
        events.append(Event(
            ts=_utc(onboarding_day + timedelta(hours=14)),
            kind="onboarding_complete",
            service="platform",
            metric_value=random.uniform(0.5, 2.0)  # weeks to productivity
        ))

    return sorted(events, key=lambda e: e.ts)


def to_dataframe(events: list[Event]) -> pd.DataFrame:
    df = pd.DataFrame([e.__dict__ for e in events])
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    return df


def compute_deployments_per_day(df: pd.DataFrame) -> pd.DataFrame:
    deploys = df[df["kind"] == "deploy"].copy()
    deploys["day"] = deploys["ts"].dt.floor("D")
    out = deploys.groupby("day").size().reset_index(name="deployments")
    return out


def compute_mttr(df: pd.DataFrame) -> pd.DataFrame:
    starts = df[df["kind"] == "incident_start"][["incident_id", "service", "ts"]].rename(columns={"ts": "start"})
    ends = df[df["kind"] == "incident_resolved"][["incident_id", "ts"]].rename(columns={"ts": "resolved"})
    mttr = starts.merge(ends, on="incident_id", how="inner")
    mttr["mttr_minutes"] = (mttr["resolved"] - mttr["start"]).dt.total_seconds() / 60.0
    return mttr.sort_values("start")


def compute_activity_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute SPACE Activity dimension: PR creation and code review velocity."""
    prs = df[df["kind"] == "pr_created"].copy()
    if len(prs) == 0:
        return pd.DataFrame(columns=["day", "prs", "reviews"])

    prs["day"] = prs["ts"].dt.floor("D")
    pr_counts = prs.groupby("day").size().reset_index(name="prs")

    # Code review counts per day
    reviews = df[df["kind"] == "pr_reviewed"].copy()
    if len(reviews) > 0:
        reviews["day"] = reviews["ts"].dt.floor("D")
        review_counts = reviews.groupby("day").size().reset_index(name="reviews")
        activity = pr_counts.merge(review_counts, on="day", how="left").fillna(0)
    else:
        activity = pr_counts.copy()
        activity["reviews"] = 0

    return activity


def compute_collaboration_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute SPACE Communication & Collaboration: code review turnaround time."""
    prs_created = df[df["kind"] == "pr_created"][["pr_id", "ts"]].rename(columns={"ts": "created"})
    prs_reviewed = df[df["kind"] == "pr_reviewed"][["pr_id", "ts"]].rename(columns={"ts": "reviewed"})

    if len(prs_created) == 0 or len(prs_reviewed) == 0:
        return pd.DataFrame(columns=["created", "turnaround_hours"])

    merged = prs_created.merge(prs_reviewed, on="pr_id", how="inner")
    merged["turnaround_hours"] = (merged["reviewed"] - merged["created"]).dt.total_seconds() / 3600.0

    # Weekly aggregation (7 day periods)
    merged["week"] = merged["created"].dt.floor("7D")
    weekly = merged.groupby("week")["turnaround_hours"].mean().reset_index()
    weekly.columns = ["week", "avg_turnaround_hours"]
    return weekly


def compute_satisfaction_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute SPACE Satisfaction & Well-being: survey scores over time."""
    surveys = df[df["kind"] == "satisfaction_survey"].copy()
    if len(surveys) == 0:
        return pd.DataFrame(columns=["date", "satisfaction"])

    surveys = surveys[["ts", "metric_value"]].rename(columns={"ts": "date", "metric_value": "satisfaction"})
    surveys["week"] = surveys["date"].dt.floor("7D")
    weekly = surveys.groupby("week")["satisfaction"].mean().reset_index()
    weekly.columns = ["week", "avg_satisfaction"]
    return weekly


def compute_efficiency_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute SPACE Efficiency & Flow: time from PR creation to merge."""
    prs_created = df[df["kind"] == "pr_created"][["pr_id", "ts"]].rename(columns={"ts": "created"})
    prs_merged = df[df["kind"] == "pr_merged"][["pr_id", "ts"]].rename(columns={"ts": "merged"})

    if len(prs_created) == 0 or len(prs_merged) == 0:
        return pd.DataFrame(columns=["created", "merge_time_hours"])

    merged = prs_created.merge(prs_merged, on="pr_id", how="inner")
    merged["merge_time_hours"] = (merged["merged"] - merged["created"]).dt.total_seconds() / 3600.0

    # Weekly trend (7 day periods)
    merged["week"] = merged["created"].dt.floor("7D")
    weekly = merged.groupby("week")["merge_time_hours"].agg(["mean", "std"]).reset_index()
    weekly.columns = ["week", "avg_merge_time", "std_merge_time"]
    return weekly


def compute_performance_metrics(df: pd.DataFrame, mttr: pd.DataFrame) -> dict:
    """Compute SPACE Performance: deployment success and incident correlation."""
    deploys = df[df["kind"] == "deploy"]
    incidents = df[df["kind"] == "incident_start"]

    if len(deploys) == 0:
        return {"incident_rate_per_deploy": 0.0}

    total_deploys = len(deploys)
    total_incidents = len(incidents)
    incident_rate = (total_incidents / total_deploys) * 100 if total_deploys > 0 else 0.0

    return {
        "incident_rate_per_deploy": incident_rate,
        "total_deploys": total_deploys,
        "total_incidents": total_incidents,
        "avg_mttr_minutes": mttr["mttr_minutes"].mean() if len(mttr) > 0 else 0.0
    }


def compute_pvm_vcr(df: pd.DataFrame) -> dict:
    """Compute PVM Value to Cost Ratio (VCR)."""
    # Value = deployments × $200 assumed value per deploy
    deploying_value = len(df[df["kind"] == "deploy"]) * 200

    # Costs = platform investment hours × $150/hour assumed cost
    platform_hours = df[df["kind"] == "platform_investment_hour"]["metric_value"].sum()
    platform_cost = platform_hours * 150

    vcr = (deploying_value / platform_cost * 100) if platform_cost > 0 else 0.0

    return {
        "vcr_percentage": vcr,
        "total_value": deploying_value,
        "total_cost": platform_cost,
        "platform_hours": platform_hours
    }


def compute_pvm_iar(df: pd.DataFrame, days: int) -> dict:
    """Compute PVM Innovation Adoption Rate (IAR)."""
    # Use deployments as proxy for adoption (more platform features adopted = more deployments)
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days)

    # Split data into first half and second half of observation period
    mid_point = start + timedelta(days=days // 2)
    df["ts"] = pd.to_datetime(df["ts"], utc=True)

    first_half_deploys = len(df[(df["kind"] == "deploy") & (df["ts"] < mid_point)])
    second_half_deploys = len(df[(df["kind"] == "deploy") & (df["ts"] >= mid_point)])

    iar = ((second_half_deploys - first_half_deploys) / max(first_half_deploys, 1)) * 100

    return {
        "iar_percentage": iar,
        "first_period_deploys": first_half_deploys,
        "second_period_deploys": second_half_deploys
    }


def compute_pvm_dtr(df: pd.DataFrame) -> dict:
    """Compute PVM Developer Toil Ratio (DTR)."""
    # Toil = incident response time (operational work)
    # Feature work = PR review time + merge time (development work)

    toil_events = df[df["kind"] == "incident_response"]
    toil_minutes = toil_events["metric_value"].sum() if len(toil_events) > 0 else 0

    pr_created = df[df["kind"] == "pr_created"][["pr_id", "ts"]].rename(columns={"ts": "created"})
    pr_merged = df[df["kind"] == "pr_merged"][["pr_id", "ts"]].rename(columns={"ts": "merged"})

    feature_work_data = pr_created.merge(pr_merged, on="pr_id", how="inner")
    feature_minutes = (feature_work_data["merged"] - feature_work_data["created"]).dt.total_seconds().sum() / 60
    feature_minutes += len(df[df["kind"] == "pr_reviewed"]) * 30  # assume 30 min per review

    dtr = (toil_minutes / max(toil_minutes + feature_minutes, 1)) * 100

    return {
        "dtr_percentage": dtr,
        "toil_minutes": toil_minutes,
        "feature_minutes": feature_minutes
    }


def plot_dashboard(days: int = 14) -> None:
    """Create interactive dashboard with DORA, SPACE, and PVM metrics using button-based navigation.

    Allows dynamic seed selection to explore different scenarios without restarting.
    """
    # Initial data generation with default seed
    current_seed = {"value": 42}

    def compute_all_metrics(seed):
        """Generate events and compute all metrics for a given seed."""
        events = generate_events(days=days, seed=seed)
        df = to_dataframe(events)

        deploys_per_day = compute_deployments_per_day(df)
        mttr = compute_mttr(df)
        activity = compute_activity_metrics(df)
        collaboration = compute_collaboration_metrics(df)
        satisfaction = compute_satisfaction_metrics(df)
        efficiency = compute_efficiency_metrics(df)
        performance = compute_performance_metrics(df, mttr)

        vcr = compute_pvm_vcr(df)
        iar = compute_pvm_iar(df, days)
        dtr = compute_pvm_dtr(df)

        return {
            "deploys_per_day": deploys_per_day,
            "mttr": mttr,
            "df": df,
            "activity": activity,
            "collaboration": collaboration,
            "satisfaction": satisfaction,
            "efficiency": efficiency,
            "performance": performance,
            "vcr": vcr,
            "iar": iar,
            "dtr": dtr
        }

    metrics = compute_all_metrics(current_seed["value"])

    fig = plt.figure(figsize=(14, 10))
    fig.suptitle(f"Comprehensive Metrics Dashboard (DORA • SPACE • PVM) | Seed: {current_seed['value']}",
                 fontsize=14, fontweight="bold", y=0.98)

    # Initialize all subplots (will be shown/hidden based on active tab)
    fig.subplots_adjust(left=0.1, right=0.95, top=0.88, bottom=0.18)

    # ===== TAB 1: DORA =====
    ax_dora = [fig.add_subplot(3, 1, i+1) for i in range(3)]

    def update_dora_plots():
        """Update DORA plots with current metrics."""
        for ax in ax_dora:
            ax.clear()

        deploys_per_day = metrics["deploys_per_day"]
        mttr = metrics["mttr"]
        df = metrics["df"]

        # 1a) Deployments/day
        ax_dora[0].plot(deploys_per_day["day"], deploys_per_day["deployments"], marker="o", color="steelblue")
        ax_dora[0].set_title("Deployment Frequency (deployments/day)", fontweight="bold")
        ax_dora[0].set_ylabel("deployments")
        ax_dora[0].grid(True, alpha=0.3)

        # 1b) MTTR per incident
        if len(mttr) > 0:
            ax_dora[1].plot(mttr["start"], mttr["mttr_minutes"], marker="o", color="coral")
        ax_dora[1].set_title("Recovery (MTTR minutes per incident)", fontweight="bold")
        ax_dora[1].set_ylabel("minutes")
        ax_dora[1].grid(True, alpha=0.3)

        # 1c) Timeline overlay
        deploy_ts = df[df["kind"] == "deploy"]["ts"]
        ax_dora[2].scatter(deploy_ts, [1] * len(deploy_ts), marker="|", s=100, color="steelblue")
        for _, row in mttr.iterrows():
            ax_dora[2].plot([row["start"], row["resolved"]], [0.5, 0.5], linewidth=4, color="coral")
        ax_dora[2].set_title("Timeline overlay (deploys as ticks, incidents as recovery bars)", fontweight="bold")
        ax_dora[2].set_yticks([0.5, 1])
        ax_dora[2].set_yticklabels(["incidents", "deploys"])
        ax_dora[2].grid(True, alpha=0.3)

    update_dora_plots()

    # ===== TAB 2: SPACE =====
    ax_space = [fig.add_subplot(2, 2, i+1) for i in range(4)]

    def update_space_plots():
        """Update SPACE plots with current metrics."""
        for ax in ax_space:
            ax.clear()

        activity = metrics["activity"]
        collaboration = metrics["collaboration"]
        satisfaction = metrics["satisfaction"]
        efficiency = metrics["efficiency"]

        # Get the start date for relative time axis
        if len(metrics["df"]) > 0:
            start_date = metrics["df"]["ts"].min()
        else:
            start_date = pd.Timestamp.now(tz="UTC")

        # 2a) Activity: PRs and reviews per day
        if len(activity) > 0:
            # Convert days to relative days from start
            activity_days = (activity["day"] - start_date).dt.days
            ax_space[0].plot(activity_days, activity["prs"], marker="o", label="PRs created", color="mediumseagreen")
            ax_space[0].plot(activity_days, activity["reviews"], marker="s", label="Reviews", color="orange", alpha=0.7)
            ax_space[0].legend()
            ax_space[0].set_xlabel("days from start")
        ax_space[0].set_title("SPACE: Activity (PRs & Code Reviews)", fontweight="bold")
        ax_space[0].set_ylabel("count/day")
        ax_space[0].grid(True, alpha=0.3)

        # 2b) Collaboration: Code review turnaround
        if len(collaboration) > 0:
            collab_days = (collaboration["week"] - start_date).dt.days
            ax_space[1].plot(collab_days, collaboration["avg_turnaround_hours"], marker="o", color="mediumpurple")
            ax_space[1].fill_between(collab_days, 0, collaboration["avg_turnaround_hours"], alpha=0.3, color="mediumpurple")
            ax_space[1].set_xlabel("days from start")
        ax_space[1].set_title("SPACE: Collaboration (Code Review Turnaround)", fontweight="bold")
        ax_space[1].set_ylabel("hours")
        ax_space[1].grid(True, alpha=0.3)

        # 2c) Satisfaction & Well-being
        if len(satisfaction) > 0:
            sat_days = (satisfaction["week"] - start_date).dt.days
            ax_space[2].plot(sat_days, satisfaction["avg_satisfaction"], marker="D", color="gold", linewidth=2)
            ax_space[2].fill_between(sat_days, 1, satisfaction["avg_satisfaction"], alpha=0.3, color="gold")
            ax_space[2].set_ylim(0.5, 5.5)
            ax_space[2].set_xlabel("days from start")
        ax_space[2].set_title("SPACE: Satisfaction & Well-being (Survey Score)", fontweight="bold")
        ax_space[2].set_ylabel("score (1-5)")
        ax_space[2].grid(True, alpha=0.3)

        # 2d) Efficiency: Merge time
        if len(efficiency) > 0:
            eff_days = (efficiency["week"] - start_date).dt.days
            ax_space[3].plot(eff_days, efficiency["avg_merge_time"], marker="o", label="Avg merge time", color="lightcoral")
            if not efficiency["std_merge_time"].isna().all():
                ax_space[3].fill_between(eff_days,
                                         efficiency["avg_merge_time"] - efficiency["std_merge_time"],
                                         efficiency["avg_merge_time"] + efficiency["std_merge_time"],
                                         alpha=0.2, color="lightcoral")
            ax_space[3].set_xlabel("days from start")
        ax_space[3].set_title("SPACE: Efficiency & Flow (Merge Time)", fontweight="bold")
        ax_space[3].set_ylabel("hours")
        ax_space[3].grid(True, alpha=0.3)

    update_space_plots()

    # ===== TAB 3: PVM =====
    ax_pvm = [fig.add_subplot(2, 2, i+1) for i in range(4)]

    def update_pvm_plots():
        """Update PVM plots with current metrics."""
        for ax in ax_pvm:
            ax.clear()

        vcr = metrics["vcr"]
        iar = metrics["iar"]
        dtr = metrics["dtr"]
        performance = metrics["performance"]

        # 3a) Value to Cost Ratio (VCR)
        vcr_val = vcr.get("vcr_percentage", 0)
        colors_vcr = "green" if vcr_val >= 1000 else "orange" if vcr_val >= 200 else "red"
        ax_pvm[0].bar(["VCR"], [vcr_val], color=colors_vcr, alpha=0.7)
        ax_pvm[0].axhline(y=1000, color="green", linestyle="--", label="Target (1000%)", linewidth=2)
        ax_pvm[0].axhline(y=200, color="orange", linestyle="--", label="Default (200%)", linewidth=1)
        ax_pvm[0].set_title("PVM: Value to Cost Ratio (VCR)", fontweight="bold")
        ax_pvm[0].set_ylabel("percentage")
        ax_pvm[0].legend(fontsize=8)
        ax_pvm[0].grid(True, alpha=0.3, axis="y")
        ax_pvm[0].text(0, vcr_val + 50, f"{vcr_val:.0f}%", ha="center", fontweight="bold")

        # 3b) Innovation Adoption Rate (IAR)
        iar_val = iar.get("iar_percentage", 0)
        colors_iar = "green" if iar_val >= 30 else "orange" if iar_val >= 10 else "red"
        ax_pvm[1].bar(["IAR"], [iar_val], color=colors_iar, alpha=0.7)
        ax_pvm[1].axhline(y=30, color="green", linestyle="--", label="Target (30%)", linewidth=2)
        ax_pvm[1].axhline(y=10, color="orange", linestyle="--", label="Default (10%)", linewidth=1)
        ax_pvm[1].set_title("PVM: Innovation Adoption Rate (IAR)", fontweight="bold")
        ax_pvm[1].set_ylabel("percentage")
        ax_pvm[1].legend(fontsize=8)
        ax_pvm[1].grid(True, alpha=0.3, axis="y")
        ax_pvm[1].text(0, iar_val + 1, f"{iar_val:.1f}%", ha="center", fontweight="bold")

        # 3c) Developer Toil Ratio (DTR)
        dtr_val = dtr.get("dtr_percentage", 0)
        colors_dtr = "green" if dtr_val <= 10 else "orange" if dtr_val <= 30 else "red"
        ax_pvm[2].bar(["DTR"], [dtr_val], color=colors_dtr, alpha=0.7)
        ax_pvm[2].axhline(y=10, color="green", linestyle="--", label="Target (<10%)", linewidth=2)
        ax_pvm[2].axhline(y=30, color="orange", linestyle="--", label="Default (<30%)", linewidth=1)
        ax_pvm[2].set_title("PVM: Developer Toil Ratio (DTR) - Lower is Better", fontweight="bold")
        ax_pvm[2].set_ylabel("percentage")
        ax_pvm[2].legend(fontsize=8)
        ax_pvm[2].grid(True, alpha=0.3, axis="y")
        ax_pvm[2].text(0, dtr_val + 1, f"{dtr_val:.1f}%", ha="center", fontweight="bold")

        # 3d) Platform Investment vs Deployment Impact
        ax_pvm[3].text(0.5, 0.7, f"Platform Hours: {vcr.get('platform_hours', 0):.0f}",
                       ha="center", fontsize=11, transform=ax_pvm[3].transAxes, bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.7))
        ax_pvm[3].text(0.5, 0.5, f"Deployments: {performance.get('total_deploys', 0)}",
                       ha="center", fontsize=11, transform=ax_pvm[3].transAxes, bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.7))
        ax_pvm[3].text(0.5, 0.3, f"Efficiency: {performance.get('total_deploys', 0) / max(vcr.get('platform_hours', 1), 1):.2f} deploys/platform-hour",
                       ha="center", fontsize=10, transform=ax_pvm[3].transAxes, bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.7))
        ax_pvm[3].set_title("PVM: Platform Impact Summary", fontweight="bold")
        ax_pvm[3].axis("off")

    update_pvm_plots()

    # Hide all initially and show first tab
    all_axes = ax_dora + ax_space + ax_pvm
    for ax in all_axes:
        ax.set_visible(False)
    for ax in ax_dora:
        ax.set_visible(True)

    # Create button navigation
    ax_btn_dora = plt.axes([0.05, 0.05, 0.10, 0.04])
    ax_btn_space = plt.axes([0.18, 0.05, 0.10, 0.04])
    ax_btn_pvm = plt.axes([0.31, 0.05, 0.10, 0.04])
    ax_btn_refresh = plt.axes([0.64, 0.05, 0.10, 0.04])
    ax_btn_quit = plt.axes([0.77, 0.05, 0.10, 0.04])

    btn_dora = Button(ax_btn_dora, "DORA", color="steelblue", hovercolor="navy")
    btn_space = Button(ax_btn_space, "SPACE", color="mediumseagreen", hovercolor="darkgreen")
    btn_pvm = Button(ax_btn_pvm, "PVM", color="mediumpurple", hovercolor="indigo")
    btn_refresh = Button(ax_btn_refresh, "Refresh", color="lightyellow", hovercolor="gold")
    btn_quit = Button(ax_btn_quit, "Quit", color="lightcoral", hovercolor="darkred")

    # Seed input area (for user to type new seed)
    from matplotlib.widgets import TextBox
    ax_seed_input = plt.axes([0.44, 0.055, 0.15, 0.03])
    text_seed = TextBox(ax_seed_input, "Seed: ", initial=str(current_seed["value"]))

    current_tab = {"index": 0}  # Track which tab is active

    def show_tab(tab_index):
        """Helper to show/hide axes based on tab index."""
        for ax in all_axes:
            ax.set_visible(False)
        if tab_index == 0:
            for ax in ax_dora:
                ax.set_visible(True)
            btn_dora.ax.set_facecolor("steelblue")
            btn_space.ax.set_facecolor("lightgray")
            btn_pvm.ax.set_facecolor("lightgray")
        elif tab_index == 1:
            for ax in ax_space:
                ax.set_visible(True)
            btn_dora.ax.set_facecolor("lightgray")
            btn_space.ax.set_facecolor("mediumseagreen")
            btn_pvm.ax.set_facecolor("lightgray")
        elif tab_index == 2:
            for ax in ax_pvm:
                ax.set_visible(True)
            btn_dora.ax.set_facecolor("lightgray")
            btn_space.ax.set_facecolor("lightgray")
            btn_pvm.ax.set_facecolor("mediumpurple")
        current_tab["index"] = tab_index
        fig.canvas.draw_idle()

    def on_refresh(_):
        """Refresh metrics with new seed from text box."""
        try:
            new_seed = int(text_seed.text)
            current_seed["value"] = new_seed
            nonlocal metrics
            metrics = compute_all_metrics(new_seed)

            # Update title with new seed
            fig.suptitle(f"Comprehensive Metrics Dashboard (DORA • SPACE • PVM) | Seed: {new_seed}",
                        fontsize=14, fontweight="bold", y=0.98)

            # Refresh all plot types
            update_dora_plots()
            update_space_plots()
            update_pvm_plots()

            show_tab(current_tab["index"])  # Redraw current tab
            print(f"✓ Refreshed metrics with seed {new_seed}")
        except ValueError:
            print("✗ Invalid seed value. Please enter an integer.")
        fig.canvas.draw_idle()

    def on_quit(_):
        """Close the dashboard gracefully."""
        plt.close(fig)
        print("\n✓ Dashboard closed. Thanks for reviewing the metrics!")

    btn_dora.on_clicked(lambda _: show_tab(0))
    btn_space.on_clicked(lambda _: show_tab(1))
    btn_pvm.on_clicked(lambda _: show_tab(2))
    btn_refresh.on_clicked(on_refresh)
    btn_quit.on_clicked(on_quit)
    text_seed.on_submit(lambda text: on_refresh(None))  # Allow Enter key to refresh

    plt.subplots_adjust(left=0.1, right=0.95, top=0.88, bottom=0.12)
    plt.show()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    events = generate_events(days=args.days, seed=args.seed)
    df = to_dataframe(events)

    # === DORA Metrics ===
    deploys_per_day = compute_deployments_per_day(df)
    mttr = compute_mttr(df)

    # === SPACE Metrics ===
    activity = compute_activity_metrics(df)
    collaboration = compute_collaboration_metrics(df)
    satisfaction = compute_satisfaction_metrics(df)
    efficiency = compute_efficiency_metrics(df)
    performance = compute_performance_metrics(df, mttr)

    # === PVM Metrics ===
    vcr = compute_pvm_vcr(df)
    iar = compute_pvm_iar(df, args.days)
    dtr = compute_pvm_dtr(df)

    # === Summary Statistics ===
    print("\n" + "="*60)
    print("COMPREHENSIVE METRICS DASHBOARD SUMMARY")
    print("="*60)

    print("\n--- DORA METRICS (Delivery & Reliability) ---")
    avg_deploys = deploys_per_day["deployments"].mean() if len(deploys_per_day) else 0
    print(f"Days observed: {args.days}")
    print(f"Avg deployments/day: {avg_deploys:.2f}")
    if len(mttr):
        avg_mttr = mttr["mttr_minutes"].mean()
        p95_mttr = mttr["mttr_minutes"].quantile(0.95)
        print(f"Incidents: {len(mttr)} | Avg MTTR: {avg_mttr:.1f} min | P95 MTTR: {p95_mttr:.1f} min")
    else:
        print("Incidents: 0")

    print("\n--- SPACE METRICS (Team & Developer Health) ---")
    print("Activity:")
    if len(activity) > 0:
        print(f"  Avg PRs/day: {activity['prs'].mean():.2f}")
        print(f"  Avg reviews/day: {activity['reviews'].mean():.2f}")
    else:
        print("  No activity data")

    print("Collaboration:")
    if len(collaboration) > 0:
        print(f"  Avg code review turnaround: {collaboration['avg_turnaround_hours'].mean():.1f} hours")
    else:
        print("  No collaboration data")

    print("Satisfaction & Well-being:")
    if len(satisfaction) > 0:
        avg_satisfaction = satisfaction["avg_satisfaction"].mean()
        print(f"  Avg satisfaction score: {avg_satisfaction:.1f}/5.0")
    else:
        print("  No satisfaction surveys")

    print("Efficiency & Flow:")
    if len(efficiency) > 0:
        print(f"  Avg PR→merge time: {efficiency['avg_merge_time'].mean():.1f} hours")
    else:
        print("  No PR merge data")

    print("Performance:")
    print(f"  Incident rate: {performance.get('incident_rate_per_deploy', 0):.2f}% per deployment")
    print(f"  Total deployments: {performance.get('total_deploys', 0)}")
    print(f"  Total incidents: {performance.get('total_incidents', 0)}")

    print("\n--- PLATFORM VALUE METRICS (PVM) ---")
    print("Value to Cost Ratio (VCR):")
    print(f"  VCR: {vcr['vcr_percentage']:.0f}% (Target: 1000%, Default: 200%)")
    print(f"  Platform hours invested: {vcr['platform_hours']:.0f}")
    print(f"  Estimated value: ${vcr['total_value']:.0f}")

    print("Innovation Adoption Rate (IAR):")
    print(f"  IAR: {iar['iar_percentage']:.1f}% (Target: 30%)")
    print(f"  First period deployments: {iar['first_period_deploys']}")
    print(f"  Second period deployments: {iar['second_period_deploys']}")

    print("Developer Toil Ratio (DTR):")
    print(f"  DTR: {dtr['dtr_percentage']:.1f}% (Target: <10%)")
    print(f"  Toil time: {dtr['toil_minutes']:.0f} minutes")
    print(f"  Feature time: {dtr['feature_minutes']:.0f} minutes")

    print("\n" + "="*60)
    print("Launching interactive dashboard...")
    print("Tip: Use the seed input field to explore different scenarios!")
    print("="*60 + "\n")

    plot_dashboard(days=args.days)


if __name__ == "__main__":
    main()
