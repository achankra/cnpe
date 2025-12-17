# lesson8/ingress-demo/run_demo.py

import yaml
import time
from gateway import (
    validate_config,
    secure_ingress_check,
    print_banner,
    demo_before_after,
)

def load(path):
    with open(path) as f:
        return yaml.safe_load(f)

def run(label, cfg):
    print("\n\n")
    print("##################################################")
    print(f"### {label}")
    print("##################################################\n")

    errors = validate_config(cfg)
    if errors:
        print("❌ CONFIG REJECTED")
        for e in errors:
            print(" -", e)
        return

    secure_ingress_check(cfg["host"], cfg["security"]["tls"])

    print("✅ CONFIG ACCEPTED")
    print_banner(cfg)

    print("Automating ingress setup...")
    time.sleep(0.4)
    print(" - TLS termination: enabled")
    time.sleep(0.2)
    print(" - Host routing: configured")
    time.sleep(0.2)
    print(" - Traffic rules: applied\n")

    demo_before_after(cfg)

def main():
    canary = load("configs/canary.yaml")
    bluegreen = load("configs/bluegreen.yaml")

    run("DEMO 1 — CANARY TRAFFIC CONTROL", canary)
    run("DEMO 2 — BLUE/GREEN TRAFFIC CONTROL", bluegreen)

    print("\n🎯 Demo complete.")
    print("Notice how the *developer intent* changed,")
    print("but the platform behavior stayed secure-by-default.")

if __name__ == "__main__":
    main()
