# Runbook: Deployment

## Pre-deployment Checklist
- [ ] All CI checks passing (lint, test, build, security scan)
- [ ] Code reviewed and approved
- [ ] Database migrations tested (if any)
- [ ] Environment variables updated (if any)
- [ ] Rollback plan confirmed

## Deployment Steps

### Development
```bash
cd infra && docker compose up --build -d
cd apps/web && npm run dev
```

### Production
```bash
# 1. Tag release
git tag -a v1.x.x -m "Release description"
git push origin v1.x.x

# 2. CI/CD pipeline builds and pushes Docker images automatically

# 3. Deploy to server
ssh production-server
cd /opt/vision-human-insight
docker compose pull
docker compose up -d

# 4. Verify
curl https://api.your-domain.com/api/health
```

### Rollback
```bash
./scripts/rollback.sh v1.x.x  # Previous version tag
```

## Post-deployment
- [ ] Verify health endpoints
- [ ] Check error rates in logs
- [ ] Monitor metrics for 15 minutes
- [ ] Notify team of successful deployment
