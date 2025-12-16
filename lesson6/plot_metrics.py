#!/usr/bin/env python3
import csv
from pathlib import Path
import matplotlib.pyplot as plt

DATA = Path("data/metrics.csv")
OUTDIR = Path("out")
OUTDIR.mkdir(exist_ok=True)

minutes = []
p95 = []
err = []
rps = []

with DATA.open() as f:
    reader = csv.DictReader(f)
    for row in reader:
        minutes.append(int(row["minute"]))
        p95.append(float(row["p95_latency_ms"]))
        err.append(float(row["error_rate_pct"]))
        rps.append(float(row["rps"]))

# Plot 1: p95 latency
plt.figure()
plt.plot(minutes, p95, marker="o")
plt.title("p95 Latency (ms)")
plt.xlabel("Minute")
plt.ylabel("ms")
plt.xticks(minutes)
plt.grid(True)
plt.tight_layout()
plt.savefig(OUTDIR / "p95_latency.png", dpi=160)
plt.close()

# Plot 2: error rate
plt.figure()
plt.plot(minutes, err, marker="o")
plt.title("Error Rate (%)")
plt.xlabel("Minute")
plt.ylabel("%")
plt.xticks(minutes)
plt.grid(True)
plt.tight_layout()
plt.savefig(OUTDIR / "error_rate.png", dpi=160)
plt.close()

print("Wrote:")
print(f" - {OUTDIR/'p95_latency.png'}")
print(f" - {OUTDIR/'error_rate.png'}")
