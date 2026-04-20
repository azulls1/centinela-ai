# Runbook: Disaster Recovery

## Recovery Time Objectives
| Component | RTO | RPO | Backup Method |
|-----------|-----|-----|---------------|
| Database (Supabase) | 1 hour | 24 hours | Supabase automatic backups |
| API Service | 15 min | 0 (stateless) | Docker rebuild |
| Stream Gateway | 15 min | 0 (stateless) | Docker rebuild |
| Frontend | 15 min | 0 (static) | Rebuild from source |
| Configuration | 5 min | Daily | Git + backup script |

## Recovery Procedures

### Full System Recovery
```bash
# 1. Clone repository
git clone <repo-url> && cd vision-human-insight

# 2. Restore environment
cp backups/latest/.env .env

# 3. Rebuild all services
cd infra && docker compose up --build -d

# 4. Verify health
curl http://localhost:8000/api/health
curl http://localhost:8081/health

# 5. Restore database (if needed)
# Use Supabase dashboard > Database > Backups
```

### Partial Recovery (Single Service)
```bash
docker compose up --build -d <service-name>
```

### Database Recovery
1. Go to Supabase Dashboard > Database > Backups
2. Select the most recent backup before the incident
3. Click "Restore"
4. Verify data integrity via API health check

## Backup Schedule
- **Database:** Automatic (Supabase Pro plan) every 24h
- **Configuration:** Manual via `./scripts/backup.sh`
- **Code:** Git repository (every commit)

## Testing Recovery
Run quarterly:
1. Spin up fresh environment from backup
2. Verify all services start
3. Verify data integrity
4. Document any issues
