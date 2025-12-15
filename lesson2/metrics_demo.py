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

import pandas as pd
import matplotlib.pyplot as plt


@dataclass(frozen=True)
class Event:
    ts: datetime
    kind: str  # "deploy" | "incident_start" | "incident_resolved"
    service: str
    deploy_id: str | None = None
    incident_id: str | None = None


SERVICES = ["payments-api", "orders", "web-frontend"]


def _utc(dt: datetime) -> datetime:
    return dt.astimezone(timezone.utc).replace(tzinfo=timezone.utc)


def generate_events(days: int, seed: int) -> list[Event]:
    """
    Generate a plausible stream:
    - deployments happen multiple times/day across services
    - incidents occur occasionally; each incident has start+resolved
    """
    random.seed(seed)
    now = _utc(datetime.now())
    start = now - timedelta(days=days)

    events: list[Event] = []
    deploy_counter = 0
    incident_counter = 0

    # Deployments
    for d in range(days):
        day = start + timedelta(days=d)
        deploys_today = random.randint(2, 10)  # tweak to show "before/after" later
        for _ in range(deploys_today):
            deploy_counter += 1
            svc = random.choice(SERVICES)
            ts = day + timedelta(hours=random.randint(8, 18), minutes=random.randint(0, 59))
            events.append(Event(ts=_utc(ts), kind="deploy", service=svc, deploy_id=f"d{deploy_counter:04d}"))

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


def plot_dashboard(deploys_per_day: pd.DataFrame, mttr: pd.DataFrame, df: pd.DataFrame) -> None:
    # Figure with 3 vertically stacked charts
    fig = plt.figure(figsize=(11, 8))

    # 1) Deployments/day
    ax1 = plt.subplot(3, 1, 1)
    ax1.plot(deploys_per_day["day"], deploys_per_day["deployments"], marker="o")
    ax1.set_title("Deployment Frequency (deployments/day)")
    ax1.set_ylabel("deployments")
    ax1.grid(True, alpha=0.3)

    # 2) MTTR per incident
    ax2 = plt.subplot(3, 1, 2, sharex=ax1)
    if len(mttr) > 0:
        ax2.plot(mttr["start"], mttr["mttr_minutes"], marker="o")
    ax2.set_title("Recovery (MTTR minutes per incident)")
    ax2.set_ylabel("minutes")
    ax2.grid(True, alpha=0.3)

    # 3) Timeline overlay: deployments + incident windows
    ax3 = plt.subplot(3, 1, 3, sharex=ax1)
    deploy_ts = df[df["kind"] == "deploy"]["ts"]
    ax3.scatter(deploy_ts, [1] * len(deploy_ts), marker="|")
    for _, row in mttr.iterrows():
        ax3.plot([row["start"], row["resolved"]], [0.5, 0.5], linewidth=4)
    ax3.set_title("Timeline overlay (deploys as ticks, incidents as recovery bars)")
    ax3.set_yticks([0.5, 1])
    ax3.set_yticklabels(["incidents", "deploys"])
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    events = generate_events(days=args.days, seed=args.seed)
    df = to_dataframe(events)

    deploys_per_day = compute_deployments_per_day(df)
    mttr = compute_mttr(df)

    # Quick “exec summary” for narration
    avg_deploys = deploys_per_day["deployments"].mean() if len(deploys_per_day) else 0
    avg_mttr = mttr["mttr_minutes"].mean() if len(mttr) else float("nan")
    p95_mttr = mttr["mttr_minutes"].quantile(0.95) if len(mttr) else float("nan")

    print("\n--- Quick readout ---")
    print(f"Days observed: {args.days}")
    print(f"Avg deployments/day: {avg_deploys:.2f}")
    if len(mttr):
        print(f"Incidents: {len(mttr)} | Avg MTTR: {avg_mttr:.1f} min | P95 MTTR: {p95_mttr:.1f} min")
    else:
        print("Incidents: 0")

    plot_dashboard(deploys_per_day, mttr, df)


if __name__ == "__main__":
    main()
