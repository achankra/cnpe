# Lesson 10 – Future of Developer Experience  
**AI Demo: Intelligent Diagnostics & Maturity Tracking**

This lesson demonstrates how platform teams can use **intelligent diagnostics**
to continuously assess platform maturity, detect friction, and prioritize
improvements.

The demo is intentionally **simple, transparent, and deterministic**.  
It shows how *rule-based intelligence* forms the foundation for future
AI and RAG-based systems — without hiding logic behind a black box.

---

## Learning Objectives

By the end of this lesson, students will understand:

- What “intelligent diagnostics” means in platform engineering
- How maturity tracking differs from dashboards
- Why explainability matters more than accuracy at first
- How rules and signals create feedback loops
- How this model evolves toward AI and RAG systems
- Why AI should **augment**, not replace, human judgment

---

## Core Idea

Instead of asking:

> “What metric is red?”

Platform teams should ask:

> “What does this say about platform maturity, and what should we do next?”

This demo converts **signals → diagnostics → actions**.

---

## Folder Structure

lesson10/
├── maturity_demo/
│ ├── ai_diagnose.py
│ ├── model.json
│ ├── sample_team_a.json
│ └── sample_team_b.json
└── README.md

yaml
Copy code

---

## Demo Overview

The demo takes:

- Quantitative signals  
  (onboarding time, golden path adoption, policy violations, SLO burn rate)
- Qualitative signals  
  (platform NPS, feedback maturity)
- Capability flags  
  (self-service, policy as code, SLOs)

And produces:

1. A **maturity score** (0–100)
2. A **maturity level** (Foundational / Emerging / Advanced)
3. A ranked list of **diagnostic findings**
4. A **90-day prioritized action plan**

No machine learning models are required.

---

## Running the Demo

From `lesson10/maturity_demo`:

```bash
python3 ai_diagnose.py model.json sample_team_a.json
Demo Calls (Run These Live)
1️⃣ Diagnose a struggling team
bash
Copy code
python3 ai_diagnose.py model.json sample_team_a.json
You will see:

Low maturity score

Multiple HIGH-severity findings

Clear explanations and recommendations

2️⃣ Diagnose a healthier team
bash
Copy code
python3 ai_diagnose.py model.json sample_team_b.json
You will see:

Higher maturity score

Fewer or no diagnostics

Reinforcement of good practices

3️⃣ Improve a signal and re-run
Edit sample_team_a.json:

json
Copy code
"golden_path_adoption_pct": 25
Change to:

json
Copy code
"golden_path_adoption_pct": 55
Re-run:

bash
Copy code
python3 ai_diagnose.py model.json sample_team_a.json
Notice:

Maturity score increases

Related diagnostics disappear

This demonstrates a tight feedback loop.

4️⃣ Add a new diagnostic rule (show evolution)
Add a new rule to model.json (for example, alert on slow onboarding):

json
Copy code
{
  "id": "R6",
  "when": { "onboarding_days": { "gt": 10 } },
  "severity": "MEDIUM",
  "category": "SelfService",
  "signal": "Very slow developer onboarding",
  "why": "Long onboarding time indicates missing automation or unclear documentation.",
  "recommendation": "Create a single golden onboarding path with templates and scripts."
}
Re-run the same command:

bash
Copy code
python3 ai_diagnose.py model.json sample_team_a.json
✔ No code changes
✔ Diagnostics adapt automatically

Important Clarification: This Is Not RAG (Yet)
This demo uses rule-based diagnostics, not Retrieval-Augmented Generation (RAG).

Rules detect patterns

Explanations are deterministic

Recommendations are explainable

This is intentional.

Rules like R6 are RAG-ready building blocks — the decision layer that future
LLM and RAG systems plug into.

How This Evolves Toward RAG
In a real platform, the same diagnostic trigger could:

Retrieve onboarding docs, runbooks, and past incidents

Inject that context into an LLM prompt

Generate tailored recommendations per team

The contract stays the same.
Only the intelligence behind it evolves.

What to Say During the Demo (Key Teaching Script)
“This is a maturity scorecard, not a dashboard.”

“The intelligence is transparent.
If it flags something, we can explain exactly why.”

“Notice that we evolve the diagnostic model
without changing code.”

“This is how platforms continuously improve
without rewriting pipelines.”

Why This Matters for DevEx
Developer experience improves through feedback loops

Mature platforms measure and adapt continuously

AI accelerates insight, not decision-making

Explainability builds trust

This is the future of platforms as products.

Key Takeaways
Intelligent diagnostics turn signals into action

Rules provide explainable, trustworthy intelligence

Maturity tracking guides investment decisions

Feedback loops drive continuous improvement

Rule-based systems are the foundation for future RAG