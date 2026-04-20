#!/bin/bash
set -euo pipefail

VERSION=${1:-""}
if [ -z "$VERSION" ]; then
  echo "Usage: ./scripts/rollback.sh <version-tag>"
  echo "Example: ./scripts/rollback.sh v1.2.0"
  echo ""
  echo "Available tags:"
  git tag --sort=-version:refname | head -10
  exit 1
fi

echo "=== Rolling back to $VERSION ==="
echo "1. Checking out code..."
git checkout "$VERSION"

echo "2. Rebuilding containers..."
cd infra && docker compose up --build -d

echo "3. Verifying health..."
sleep 10
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health)
GW_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/health)

if [ "$API_STATUS" = "200" ] && [ "$GW_STATUS" = "200" ]; then
  echo "=== Rollback to $VERSION successful ==="
else
  echo "=== WARNING: Health checks failed (API=$API_STATUS, Gateway=$GW_STATUS) ==="
  exit 1
fi
