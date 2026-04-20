# Runbook: Incident Response

## Severity Levels
| Level | Description | Response Time | Example |
|-------|-------------|---------------|---------|
| P0 | Service down | < 15 min | API unresponsive, DB connection lost |
| P1 | Major degradation | < 30 min | ML models failing, auth broken |
| P2 | Minor degradation | < 2 hours | Slow queries, UI glitches |
| P3 | Low impact | Next business day | Cosmetic issues, non-critical bugs |

## Response Procedure
1. **Acknowledge** - Confirm incident in team channel
2. **Assess** - Check health endpoints: `curl http://localhost:8000/api/health`
3. **Diagnose** - Check logs: `docker logs vision-api --tail 100`
4. **Mitigate** - Apply immediate fix or rollback: `./scripts/rollback.sh <version>`
5. **Resolve** - Deploy permanent fix
6. **Postmortem** - Write report within 48 hours

## Common Issues

### API Not Responding
```bash
docker ps --filter name=vision-api
docker restart vision-api
docker logs vision-api --tail 50
```

### Database Connection Failed
```bash
# Check Supabase connectivity
curl -s https://iagenteksupabase.iagentek.com.mx/rest/v1/ -H "apikey: $SUPABASE_ANON_KEY"
```

### Stream Gateway Crash
```bash
docker restart vision-stream-gateway
# Check FFmpeg processes
docker exec vision-stream-gateway ps aux | grep ffmpeg
```

### High Memory Usage
```bash
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### ML Models Not Loading
- Check browser console for CORS/network errors
- Verify CDN accessibility: `curl -I https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.9/wasm/`
- Check TensorFlow.js WebGL: browser devtools > Performance tab

## Escalation
1. **Developer:** Samael Hernandez (azull.samael@gmail.com)
2. **Infrastructure:** Check Docker Desktop logs
3. **Database:** Supabase dashboard
