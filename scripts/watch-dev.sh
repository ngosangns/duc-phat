#!/usr/bin/env bash
set -euo pipefail

echo "Watching for .typ changes across the library (Ctrl+C to stop)..."

fswatch -0 -r \
  -e ".*" -i "\\.typ$" \
  --event Updated --event Created --event Renamed \
  . |
while IFS= read -r -d '' file; do
  [ -f "$file" ] || continue
  echo "→ rebuilding: $file"
  if typst compile "$file"; then
    echo "  ok"
  else
    echo "  FAILED: $file"
  fi
done
