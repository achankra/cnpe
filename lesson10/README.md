# Lesson 10 – Future of DevEx: intelligent diagnostics & maturity tracking

This lesson demonstrates how platform teams can use **intelligent diagnostics** to continuously assess platform maturity, detect friction, and prioritize
improvements.

## Learning Objectives

By the end of this lesson, students will understand:

- What “intelligent diagnostics” means in platform engineering
- How maturity tracking differs from dashboards
- Why explainability matters more than accuracy at first
- How rules and signals create feedback loops
- How this model evolves toward AI and RAG systems
- Why AI should **augment**, not replace, human judgment

## Core Idea

Instead of asking:

> “What metric is red?”

Platform teams should ask:

> “What does this say about platform maturity, and what should we do next?”

This demo converts **signals → diagnostics → actions**.

## Folder Structure
```

lesson10/
 ├── ai_diagnose.py
 ├── model.json
 ├── sample_team_a.json
 └── sample_team_b.json
 └── README.md

```

## Demo Overview

The demo takes:

1. Quantitative signals    (onboarding time, golden path adoption, policy violations, SLO burn rate)
2. Qualitative signals    (platform NPS, feedback maturity)
3. Capability flags    (self-service, policy as code, SLOs)

And produces:

1. A **maturity score** (0–100)
2. A **maturity level** (Foundational / Emerging / Advanced)
3. A ranked list of **diagnostic findings**
4. A **90-day prioritized action plan**

No machine learning models are required.

## Running the Demo

```
python3 ai_diagnose.py model.json sample_team_a.json
```

## Demo Calls (Run These Live)

**1. Diagnose a struggling team** 

```
python3 ai_diagnose.py model.json sample_team_a.json
```

You will see:

- Low maturity score
- Multiple HIGH-severity findings
- Clear explanations and recommendations

 **2. Diagnose a healthier team**
```
python3 ai_diagnose.py model.json sample_team_b.json
```
You will see:
- Higher maturity score
- Fewer or no diagnostics
- Reinforcement of good practices

**3. Improve a signal and re-run**

Edit sample_team_a.json:

```
"golden_path_adoption_pct": 25
```

Change to:
```
"golden_path_adoption_pct": 55

python3 ai_diagnose.py model.json sample_team_a.json
```
You will see:

- Maturity score increases
- Related diagnostics disappear
- This demonstrates a tight feedback loop.

**4. Add a new diagnostic rule from rule-based-diagnostics.json (show evolution)** 
Add the new rule to model.json (for example, alert on slow onboarding):

```
{
  "id": "R6",
  "when": { "onboarding_days": { "gt": 10 } },
  "severity": "MEDIUM",
  "category": "SelfService",
  "signal": "Very slow developer onboarding",
  "why": "Long onboarding time indicates missing automation or unclear documentation.",
  "recommendation": "Create a single golden onboarding path with templates and scripts."
}
```
Re-run the same command:
```
python3 ai_diagnose.py model.json sample_team_a.json
```

- No code changes
- Diagnostics adapt automatically
- This demo uses rule-based diagnostics, not Retrieval-Augmented Generation (RAG).
- These Rules like R6 are RAG-ready building blocks — the decision layer that future LLM and RAG systems plug into.


## Summary 
- This is a maturity scorecard, not a dashboard.
- The intelligence is transparent. If it flags something, we can explain exactly why.
- Notice that we evolve the diagnostic model without changing code.
- This is how platforms continuously improve without rewriting pipelines.

### Why This Matters for DevEx

- Developer experience improves through feedback loops
- Mature platforms measure and adapt continuously
- AI accelerates insight, not decision-making
- Explainability builds trust
- This is the future of platforms as products.

## Key Takeaways

- Intelligent diagnostics turn signals into action
- Rules provide explainable, trustworthy intelligence
- Maturity tracking guides investment decisions
- Feedback loops drive continuous improvement
- Rule-based systems are the foundation for future RAG
