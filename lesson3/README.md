# Lesson 3 – IaC Guardrails with Fast Feedback (bad → good → better → best)

This lesson demonstrates how **platform guardrails** improve infrastructure quality and security
*before* code reaches CI/CD or production.

Instead of committing code live during a demo, this repo contains **multiple versions of the same intent**,
showing how automated checks progressively guide engineers toward safer defaults.

---

## Learning Objectives

By the end of this lesson, you will understand:

- Why **Infrastructure as Code (IaC)** needs guardrails
- How to shift quality and security checks **left**
- The difference between:
  - syntax correctness
  - best-practice correctness
  - security posture
- The idea of **“dumb pipelines, smart scripts”**

---

## Folder Structure

lesson3/
├── bad/ # Intentionally broken & insecure IaC
├── good/ # Valid & lint-clean IaC
├── better/ # Security-hardened IaC
├── best/ # Clean (validate + lint + security scan)
├── scripts/ # Reusable guardrail scripts
│ ├── validate.sh
│ ├── lint.sh
│ └── scan.sh
├── .terraform.lock.hcl
└── README.md


Each folder represents the **same infrastructure intent**, but at different levels of maturity.

---

## Tooling Used

This lesson uses lightweight, local tools to provide fast feedback:

- **Terraform** – IaC authoring & validation
- **TFLint** – Terraform best-practice linting
- **Trivy** – IaC security & misconfiguration scanning

> The scripts in `scripts/` can be reused locally, in CI, or in pre-commit hooks.

---

## Installation

### macOS (recommended for the demo)

```bash
brew install terraform tflint trivy

##Verify

terraform version
tflint --version
trivy --version

The Progression Explained
1️⃣ bad/ – No Guardrails

Represents common real-world mistakes:

Invalid or incorrect resource definitions

Insecure defaults (e.g., public storage, weak metadata settings)

Invalid instance types or missing constraints

Expected outcome:

../scripts/validate.sh   # ❌ fails
../scripts/lint.sh       # ❌ fails
../scripts/scan.sh       # ❌ fails


This is what happens before platform guardrails exist.

2️⃣ good/ – Valid & Lint-Clean

Code is:

Syntactically valid Terraform

Passes terraform validate

Passes tflint

But still lacks strong security defaults.

Expected outcome:

../scripts/validate.sh   # ✅ passes
../scripts/lint.sh       # ✅ passes
../scripts/scan.sh       # ❌ security findings remain


This reflects many teams’ definition of “done” — and why issues still escape.

3️⃣ better/ – Security Hardened

Security improvements are added:

IMDSv2 enforced

Encrypted root volumes

Monitoring enabled

Secure S3 defaults (no public access, encryption, versioning)

Expected outcome:

../scripts/validate.sh   # ✅
../scripts/lint.sh       # ✅
../scripts/scan.sh       # ⚠️ fewer findings


This shows how guardrails guide engineers toward safer defaults.

4️⃣ best/ – Clean & Compliant

The “best” version:

Passes Terraform validation

Passes TFLint

Passes Trivy misconfiguration scanning

Uses pinned provider versions via .terraform.lock.hcl

Expected outcome:

../scripts/validate.sh   # ✅
../scripts/lint.sh       # ✅
../scripts/scan.sh       # ✅ (clean)


This represents a platform-approved golden path.

Running the Demo (No Git Commits Required)

From within lesson3/:

cd bad
../scripts/validate.sh
../scripts/lint.sh
../scripts/scan.sh


Then repeat for good/, better/, and best/.

The only thing that changes is the code —
the scripts stay the same.

Why This Matters (Platform Engineering View)

Developers shouldn’t need to be Terraform or security experts

Guardrails provide fast, automated feedback

Quality and security become default behaviors

Pipelines stay simple; intelligence lives in reusable checks

This lesson illustrates how platform teams scale impact
without becoming ticket bottlenecks.

Notes on .terraform.lock.hcl

This repo intentionally includes .terraform.lock.hcl to ensure:

Consistent provider versions

Reproducible demos

Fewer “works on my machine” issues

This is recommended for workshops and teaching environments.

Optional Extensions

Wire scripts/ into GitHub Actions

Enable pre-commit hooks (opt-in)

Add policy-as-code (OPA / Checkov) for deeper governance