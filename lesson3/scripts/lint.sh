#!/usr/bin/env bash
set -euo pipefail
tflint --init >/dev/null || true
tflint
