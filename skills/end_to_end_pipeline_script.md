# End-to-End Pipeline Script

## Purpose
Automate the entire visual regression testing process from capturing baselines and current screenshots to generating the report.

## Key Code Snippets/Patterns
```bash
#!/bin/bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
VENDOR="$ROOT/vendor"
BASELINE_URL="${1:-$ROOT/web_output.html}"
CURRENT_URL="${2:-$ROOT/web_output.html}"
THRESHOLD="${3:-0.5}"

BASELINE_DIR="$ROOT/baselines"
CURRENT_DIR="$ROOT/current"
DIFF_DIR="$ROOT/diff_report"
REPORT="$ROOT/report.html"

mkdir -p "$BASELINE_DIR" "$CURRENT_DIR" "$DIFF_DIR"

cd "$VENDOR"

node cross_browser_test.mjs "$BASELINE_URL" "$BASELINE_DIR" baseline
node cross_browser_test.mjs "$CURRENT_URL" "$CURRENT_DIR" current
node diff.mjs "$BASELINE_DIR" "$CURRENT_DIR" "$DIFF_DIR" "$THRESHOLD"
node build_report.mjs "$DIFF_DIR/diff_metrics.json" "$REPORT"
```

## Common Errors and How to Avoid Them
- **Error**: Missing dependencies.
  **Solution**: Ensure that all required Node.js modules are installed in the `vendor` directory.