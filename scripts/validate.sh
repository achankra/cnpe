#!/usr/bin/env bash
set -euo pipefail
terraform fmt -check
terraform init -backend=false -input=false >/dev/null
terraform validate
