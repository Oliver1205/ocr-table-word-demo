#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: bash run.sh <input_image> [output_docx]"
  echo "Example: bash run.sh input/sample.jpg output/result.docx"
  exit 1
fi

INPUT_PATH="$1"
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
