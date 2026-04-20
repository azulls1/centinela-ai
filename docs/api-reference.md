# Vision Human Insight - API Reference

## Base URL
- **Development:** `http://localhost:8000`
- **Production:** `https://api.your-domain.com`

## Authentication
Most endpoints require an API key:
```
Header: x-api-key: <your-api-key>
```
Admin endpoints require Bearer token:
```
Header: Authorization: Bearer <admin-token>
```

## Endpoints

### Health & Info
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | None | API info |
| GET | `/api/health` | None | Health check |
| GET | `/api/info` | None | Capabilities |
| GET | `/metrics` | None | Prometheus metrics |

### Events
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/events/` | API Key | List events (paginated) |
| POST | `/api/events/` | API Key | Create event |
| GET | `/api/events/{id}` | API Key | Get event by ID |
| DELETE | `/api/events/{id}` | Admin | Delete event |

### Analytics
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/analytics/stats` | API Key | Event statistics |
| GET | `/api/analytics/hourly` | API Key | Hourly breakdown |

### Sessions
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/sessions/init` | None | Start demo session |
| POST | `/api/sessions/heartbeat` | None | Session heartbeat |
| GET | `/api/sessions/admin/sessions` | Admin | List all sessions |
| POST | `/api/sessions/admin/action` | Admin | Admin action on session |

### AI Summary
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/ai/summary` | API Key | Generate AI summary |

### External Cameras
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/external-cameras/` | API Key | List cameras |
| POST | `/api/external-cameras/` | API Key | Register camera |
| DELETE | `/api/external-cameras/{id}` | Admin | Remove camera |

### Reports
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/reports/generate` | API Key | Generate PDF report |

## Error Responses
All errors follow this format:
```json
{
  "detail": "Human-readable error message"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request (invalid input) |
| 401 | Authentication required |
| 403 | Forbidden (invalid credentials) |
| 404 | Resource not found |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

## Rate Limits
- **Default:** 120 requests/minute per IP
- **AI endpoints:** 20 requests/minute per IP
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After`
