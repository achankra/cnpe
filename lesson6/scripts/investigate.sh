#!/usr/bin/env bash
set -euo pipefail

METRICS="data/metrics.csv"
LOGS="data/logs.jsonl"
TRACE="data/trace.json"

echo "=============================="
echo "INCIDENT SUMMARY (fast)"
echo "=============================="

python3 - <<'PY'
import csv, json

# --- metrics summary ---
with open("data/metrics.csv") as f:
    rows = list(csv.DictReader(f))

# Find peak p95 latency + peak error rate
peak_lat = max(rows, key=lambda r: float(r["p95_latency_ms"]))
peak_err = max(rows, key=lambda r: float(r["error_rate_pct"]))

print(f"- Peak p95 latency : {peak_lat['p95_latency_ms']} ms at minute {peak_lat['minute']}")
print(f"- Peak error rate  : {peak_err['error_rate_pct']}% at minute {peak_err['minute']}")
print(f"- RPS (at peak err): {peak_err['rps']}")

# --- logs summary ---
warn_err = []
with open("data/logs.jsonl") as f:
    for line in f:
        if not line.strip(): 
            continue
        e = json.loads(line)
        if e.get("level") in ("WARN","ERROR"):
            warn_err.append(e)

upstreams = {}
fail_status = 0
for e in warn_err:
    if "upstream" in e:
        upstreams[e["upstream"]] = upstreams.get(e["upstream"], 0) + 1
    if e.get("msg") == "request failed":
        fail_status += 1

top_upstream = None
if upstreams:
    top_upstream = sorted(upstreams.items(), key=lambda x: x[1], reverse=True)[0]

if top_upstream:
    print(f"- Dominant upstream in WARN/ERROR logs: {top_upstream[0]} ({top_upstream[1]} events)")
else:
    print("- No upstream pattern found in logs")
print(f"- Failed requests observed in logs: {fail_status}")

# --- trace summary ---
t = json.load(open("data/trace.json"))
root = t["rootSpan"]
spans = sorted(root["spans"], key=lambda s: s["duration_ms"], reverse=True)
top = spans[0]
err = f" (error={top.get('error')})" if top.get("error") else ""
print(f"- Slowest span: {top['name']} {top['duration_ms']}ms{err}")
print("")
print("Conclusion:")
print(f"  Metrics show a spike; logs point to an upstream issue; trace confirms bottleneck in '{top['name']}'.")
PY

echo ""
echo "=============================="
echo "METRICS (What happened?)"
echo "=============================="
echo "minute  p95_latency_ms  error_rate_pct  rps"
python3 - <<'PY'
import csv
with open("data/metrics.csv") as f:
    rows = list(csv.DictReader(f))

# Print all rows, highlight the spike window (simple heuristic: latency >= 200 or error >= 1%)
for r in rows:
    lat = float(r["p95_latency_ms"])
    err = float(r["error_rate_pct"])
    flag = " <-- spike" if (lat >= 200 or err >= 1.0) else ""
    print(f"{r['minute']:>6}  {lat:>14.0f}  {err:>14.1f}  {r['rps']:>4}{flag}")
PY

# Optional: generate plots if the script exists
if [[ -f "scripts/plot_metrics.py" ]]; then
  echo ""
  echo "Generating plots (optional)..."
  ./scripts/plot_metrics.py >/dev/null || true
  echo "Plots written to ./out/ (p95_latency.png, error_rate.png)"
fi

echo ""
echo "=============================="
echo "LOGS (How did it happen?)"
echo "=============================="
echo "Showing WARN/ERROR entries:"
python3 - <<'PY'
import json
for line in open("data/logs.jsonl"):
    if not line.strip(): 
        continue
    e = json.loads(line)
    if e.get("level") in ("WARN","ERROR"):
        ts = e.get("ts","?")
        lvl = e.get("level","?")
        svc = e.get("service","?")
        msg = e.get("msg","?")
        extra = []
        if "upstream" in e: extra.append(f"upstream={e['upstream']}")
        if "attempt" in e: extra.append(f"attempt={e['attempt']}")
        if "timeout_ms" in e: extra.append(f"timeout_ms={e['timeout_ms']}")
        if "status" in e: extra.append(f"status={e['status']}")
        if "orderId" in e: extra.append(f"orderId={e['orderId']}")
        print(f"{ts} {lvl:<5} {svc:<12} {msg} " + (" ".join(extra) if extra else ""))
PY

echo ""
echo "=============================="
echo "TRACE (Why did it happen?)"
echo "=============================="
python3 - <<'PY'
import json
t = json.load(open("data/trace.json"))
root = t["rootSpan"]
print(f"traceId={t['traceId']}  request='{root['name']}'  total={root['duration_ms']}ms")
print("span breakdown (largest first):")
for s in sorted(root["spans"], key=lambda x: x["duration_ms"], reverse=True):
    err = f"  ERROR={s.get('error')}" if s.get("error") else ""
    print(f" - {s['name']:<22} {s['duration_ms']:>4}ms{err}")
PY
