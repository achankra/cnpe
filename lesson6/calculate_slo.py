import yaml

# Load SLO definition
with open("slo.yaml") as f:
    slo = yaml.safe_load(f)

TARGET = slo["slo"]["target"]

# Load traffic log
with open("traffic.log") as f:
    statuses = [int(line.strip()) for line in f if line.strip()]

total = len(statuses)
good = len([s for s in statuses if s < 500])

sli = (good / total) * 100
error_budget = 100 - TARGET
burn = TARGET - sli

print(f"Service: {slo['service']}")
print(f"Total requests: {total}")
print(f"Good requests: {good}")
print(f"SLI: {sli:.2f}%")
print(f"SLO Target: {TARGET}%")
print(f"Error Budget: {error_budget:.2f}%")

if sli >= TARGET:
    print("SUCCESS: SLO met — safe to deploy")
else:
    print("ERROR: SLO violated — freeze features, fix reliability")
    print(f"Error budget burned: {burn:.2f}%")
