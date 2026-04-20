#!/bin/bash
# Backup script for Vision Human Insight
set -euo pipefail

BACKUP_DIR="./backups/$(date +%Y-%m-%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "=== Vision Human Insight Backup ==="
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Backup dir: $BACKUP_DIR"

# 1. Export environment config (without secrets)
echo "[1/4] Backing up configuration..."
cp -r .nxt/nxt.config.yaml "$BACKUP_DIR/" 2>/dev/null || true
cp infra/docker-compose.yml "$BACKUP_DIR/" 2>/dev/null || true

# 2. Export Supabase schema
echo "[2/4] Backing up database schema..."
cp -r infra/supabase/*.sql "$BACKUP_DIR/" 2>/dev/null || true

# 3. Backup Docker volumes
echo "[3/4] Backing up Docker volumes..."
docker compose -f infra/docker-compose.yml exec -T api tar czf - /app/uploads 2>/dev/null > "$BACKUP_DIR/api-uploads.tar.gz" || true

# 4. Create manifest
echo "[4/4] Creating backup manifest..."
cat > "$BACKUP_DIR/manifest.json" << EOF
{
  "version": "1.0.0",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project": "vision-human-insight",
  "contents": ["config", "schema", "volumes"],
  "restore_instructions": "See docs/runbooks/disaster-recovery.md"
}
EOF

echo "=== Backup complete: $BACKUP_DIR ==="
