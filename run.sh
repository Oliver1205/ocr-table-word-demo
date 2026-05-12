#!/usr/bin/env bash
set -euo pipefail

INPUT_PATH="${1:-input/sample.jpg}"
OUTPUT_PATH="${2:-output/result.docx}"
CONF_THRESHOLD="${CONF_THRESHOLD:-0.70}"
DEBUG="${DEBUG:-false}"

ARGS=(
  python -m src.main
  --input "$INPUT_PATH"
  --output "$OUTPUT_PATH"
  --conf-threshold "$CONF_THRESHOLD"
)

if [[ "$DEBUG" == "true" ]]; then
  ARGS+=(--debug)
fi

"${ARGS[@]}"
