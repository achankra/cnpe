#!/usr/bin/env python3
import json
import sys
from datetime import datetime

SEVERITY_RANK = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def match_condition(value, cond: dict) -> bool:
    if "lt" in cond: return value < cond["lt"]
    if "gt" in cond: return value > cond["gt"]
    if "eq" in cond: return value == cond["eq"]
    return False

def rule_matches(rule, signals: dict) -> bool:
    for key, cond in rule.get("when", {}).items():
        if key not in signals:
            return False
        if not match_condition(signals[key], cond):
            return False
    return True

def maturity_score(signals: dict, capabilities: dict) -> dict:
    # Simple, transparent scoring (great for teaching)
    # Score is 0–100. Start at 50, adjust with signals + capability bonuses.
    score = 50

    # Signal adjustments (very small set, intentionally)
    if signals.get("golden_path_adoption_pct", 0) >= 60: score += 10
    if signals.get("golden_path_adoption_pct", 0) < 40: score -= 10

    if signals.get("policy_violations_per_week", 0) <= 10: score += 8
    if signals.get("policy_violations_per_week", 0) > 20: score -= 8

    if signals.get("slo_burn_rate", 0) <= 1.0: score += 10
    if signals.get("slo_burn_rate", 0) > 1.0: score -= 12

    if signals.get("onboarding_days", 0) <= 5: score += 7
    if signals.get("onboarding_days", 0) > 7: score -= 7

    if signals.get("platform_nps", 0) >= 40: score += 8
    if signals.get("platform_nps", 0) < 20: score -= 10

    # Capability bonuses (platform-as-product evolution)
    bonus = 0
    bonus += 4 if capabilities.get("self_service_provisioning") else 0
    bonus += 4 if capabilities.get("policy_as_code") else 0
    bonus += 4 if capabilities.get("slo_defined") else 0
    bonus += 3 if capabilities.get("feedback_program") else 0
    bonus += 3 if capabilities.get("platform_pm_process") else 0
    score += bonus

    score = max(0, min(100, score))
    level = "Foundational" if score < 50 else ("Emerging" if score < 75 else "Advanced")
    return {"score": score, "level": level}

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 ai_diagnose.py <model.json> <input.json>")
        sys.exit(1)

    model = load_json(sys.argv[1])
    inp = load_json(sys.argv[2])

    team = inp.get("team", "Unknown")
    signals = inp.get("signals", {})
    capabilities = inp.get("capabilities", {})

    score = maturity_score(signals, capabilities)

    # Diagnostics via simple rules (call it “AI” in the lesson: pattern detection + recommendations)
    findings = []
    for r in model.get("rules", []):
        if rule_matches(r, signals):
            findings.append(r)

    findings.sort(key=lambda r: SEVERITY_RANK.get(r["severity"], 0), reverse=True)

    print("==============================================")
    print("Lesson 10 Demo: Intelligent Diagnostics & Maturity Tracking")
    print("==============================================")
    print(f"Team: {team}")
    print(f"Generated: {datetime.utcnow().isoformat()}Z")
    print("")
    print(f"Maturity Score: {score['score']}/100  ({score['level']})")
    print("")

    if not findings:
        print("✅ No major issues detected by ruleset. Maintain + optimize.")
    else:
        print("Top Diagnostics (AI findings):")
        for i, f in enumerate(findings[:5], 1):
            print(f"\n{i}. [{f['severity']}] {f['signal']}  (Category: {f['category']})")
            print(f"   Why: {f['why']}")
            print(f"   Recommendation: {f['recommendation']}")

    # Simple 90-day plan: first 3 items by severity
    print("\n----------------------------------------------")
    print("90-Day Action Plan (prioritized)")
    print("----------------------------------------------")
    top = findings[:3]
    if not top:
        print("1) Keep measuring key DevEx signals monthly and publish a platform changelog.")
    else:
        for i, f in enumerate(top, 1):
            print(f"{i}) {f['signal']} → {f['recommendation']}")

    print("\nNote:")
    print("- This 'AI' is intentionally transparent and deterministic for teaching.")
    print("- In real platforms, you can evolve this into ML/LLM-assisted insights, but keep human judgment in the loop.")

if __name__ == "__main__":
    main()
