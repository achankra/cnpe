#!/usr/bin/env bash
set -euo pipefail

INPUT="${1:-}"
if [[ -z "${INPUT}" ]]; then
  echo "usage: ./scripts/check.sh inputs/<file>.json"
  exit 2
fi

# Evaluate allow + violations in one shot
ALLOW=$(opa eval -f raw -d policies/k8s.rego -i "$INPUT" "data.cnpe.compliance.allow")
echo "allow: ${ALLOW}"

if [[ "${ALLOW}" != "true" ]]; then
  echo ""
  echo "DENY: policy violations:"
  opa eval -f pretty -d policies/k8s.rego -i "$INPUT" "data.cnpe.compliance.violations"
  exit 1
fi

echo "PASS: compliant"
