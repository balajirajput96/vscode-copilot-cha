#!/usr/bin/env bash
set -Eeuo pipefail

workflow_file="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.github/workflows/daily-jobs.yml"

grep -Fq 'id: scan-gate' "$workflow_file"
grep -Fq 'echo "available=true" >> "$GITHUB_OUTPUT"' "$workflow_file"
grep -Fq 'echo "available=false" >> "$GITHUB_OUTPUT"' "$workflow_file"
grep -Fq "if: steps.scan-gate.outputs.available == 'true'" "$workflow_file"
count=$(grep -Fc "if: steps.scan-gate.outputs.available == 'true'" "$workflow_file")
test "$count" -eq 2

grep -Fq 'scan skipped without changing tracked results' "$workflow_file"
printf 'PASS: missing OPENROUTER_API_KEY gates scan and commit steps without failing the workflow.\n'
