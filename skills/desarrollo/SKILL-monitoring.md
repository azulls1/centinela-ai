# SKILL: Monitoring y Observabilidad

> **Version:** 3.8.0
> **Trigger:** Implementacion de monitoreo y observabilidad
> **Agente:** nxt-devops, nxt-performance
> **Track:** web

## Proposito
Implementar monitoreo completo de aplicaciones incluyendo metricas, logs,
traces y alertas para mantener la salud del sistema.

## Cuando se Activa
- Configurar APM (Application Performance Monitoring)
- Implementar logging estructurado
- Crear dashboards
- Configurar alertas
- Distributed tracing

## Instrucciones

### 1. Los 3 Pilares de Observabilidad

```
┌─────────────────────────────────────────────────────────┐
│                    OBSERVABILIDAD                        │
├─────────────────┬─────────────────┬─────────────────────┤
│     METRICAS    │      LOGS       │      TRACES         │
├─────────────────┼─────────────────┼─────────────────────┤
│ Numeros         │ Eventos         │ Flujo de requests   │
│ Agregados       │ Discretos       │ Distribuido         │
│ Time-series     │ Texto/JSON      │ Spans y contexto    │
│                 │                 │                     │
│ CPU, Memory     │ Errores         │ Request journey     │
│ Request rate    │ Accesos         │ Latencia por paso   │
│ Error rate      │ Auditoría       │ Dependencias        │
└─────────────────┴─────────────────┴─────────────────────┘
```

### 2. Stack de Herramientas

| Categoria | Open Source | SaaS |
|-----------|-------------|------|
| Metricas | Prometheus + Grafana | DataDog, New Relic |
| Logs | ELK Stack, Loki | Papertrail, Loggly |
| Traces | Jaeger, Zipkin | DataDog APM, Honeycomb |
| Alertas | Alertmanager | PagerDuty, OpsGenie |
| All-in-one | Grafana Stack | DataDog, Dynatrace |

### 3. Metricas (Prometheus)

#### Tipos de Metricas
```javascript
// Counter - Solo incrementa
const httpRequestsTotal = new Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'path', 'status'],
});

// Gauge - Puede subir o bajar
const activeConnections = new Gauge({
  name: 'active_connections',
  help: 'Number of active connections',
});

// Histogram - Distribucion de valores
const httpRequestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration',
  labelNames: ['method', 'path'],
  buckets: [0.1, 0.5, 1, 2, 5],
});

// Summary - Percentiles
const httpRequestLatency = new Summary({
  name: 'http_request_latency_seconds',
  help: 'HTTP request latency',
  percentiles: [0.5, 0.9, 0.99],
});
```

#### RED Metrics (Request-oriented)
```javascript
// Rate - Requests per second
http_requests_total

// Errors - Error rate
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))

// Duration - Latency percentiles
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

#### USE Metrics (Resource-oriented)
```javascript
// Utilization - % time resource is busy
node_cpu_seconds_total

// Saturation - Queue length
node_load1

// Errors - Error count
node_disk_io_time_seconds_total
```

### 4. Logging Estructurado

#### Setup con Pino (Node.js)
```javascript
// logger.js
import pino from 'pino';

export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => ({ level: label }),
  },
  base: {
    service: 'api-service',
    version: process.env.APP_VERSION,
    env: process.env.NODE_ENV,
  },
  timestamp: pino.stdTimeFunctions.isoTime,
});

// Uso
logger.info({ userId: user.id, action: 'login' }, 'User logged in');
logger.error({ err, requestId }, 'Failed to process payment');
```

#### Log Levels
```javascript
// FATAL - Sistema no puede continuar
logger.fatal({ err }, 'Database connection lost');

// ERROR - Error que afecta operacion
logger.error({ err, orderId }, 'Payment processing failed');

// WARN - Situacion inesperada pero manejada
logger.warn({ userId }, 'Rate limit approaching');

// INFO - Eventos de negocio importantes
logger.info({ orderId, amount }, 'Order completed');

// DEBUG - Info para debugging
logger.debug({ query, params }, 'Executing database query');

// TRACE - Info muy detallada
logger.trace({ headers }, 'Incoming request');
```

#### Campos Estandar
```javascript
// Siempre incluir
{
  timestamp: '2024-01-15T10:30:00Z',
  level: 'info',
  message: 'User action completed',
  service: 'api-service',
  version: '1.2.3',
  environment: 'production',

  // Contexto de request
  requestId: 'req-123',
  traceId: 'trace-456',
  spanId: 'span-789',

  // Contexto de usuario (si aplica)
  userId: 'user-123',
  tenantId: 'tenant-456',

  // Datos especificos del evento
  action: 'order.created',
  orderId: 'order-789',
  amount: 150.00,

  // Para errores
  error: {
    name: 'ValidationError',
    message: 'Invalid email format',
    stack: '...'
  }
}
```

### 5. Distributed Tracing

#### OpenTelemetry Setup
```javascript
// tracing.js
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';

const sdk = new NodeSDK({
  serviceName: 'api-service',
  traceExporter: new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT,
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();

// Manual span
import { trace } from '@opentelemetry/api';

const tracer = trace.getTracer('my-service');

async function processOrder(order) {
  return tracer.startActiveSpan('processOrder', async (span) => {
    span.setAttribute('order.id', order.id);
    span.setAttribute('order.amount', order.amount);

    try {
      await validateOrder(order);
      await chargePayment(order);
      await sendConfirmation(order);
      span.setStatus({ code: SpanStatusCode.OK });
    } catch (error) {
      span.setStatus({ code: SpanStatusCode.ERROR });
      span.recordException(error);
      throw error;
    } finally {
      span.end();
    }
  });
}
```

### 6. Dashboards

#### Dashboard Template (Grafana JSON)
```json
{
  "title": "API Service Dashboard",
  "panels": [
    {
      "title": "Request Rate",
      "type": "graph",
      "targets": [
        {
          "expr": "sum(rate(http_requests_total[5m]))",
          "legendFormat": "Requests/s"
        }
      ]
    },
    {
      "title": "Error Rate",
      "type": "stat",
      "targets": [
        {
          "expr": "sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m])) * 100"
        }
      ],
      "thresholds": [
        { "value": 0, "color": "green" },
        { "value": 1, "color": "yellow" },
        { "value": 5, "color": "red" }
      ]
    },
    {
      "title": "P99 Latency",
      "type": "gauge",
      "targets": [
        {
          "expr": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))"
        }
      ]
    }
  ]
}
```

### 7. Alertas

#### Alertmanager Rules
```yaml
# prometheus/alerts.yml
groups:
  - name: api-alerts
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: HighLatency
        expr: |
          histogram_quantile(0.99,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "P99 latency is {{ $value }}s"

      - alert: ServiceDown
        expr: up{job="api-service"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
```

### 8. Health Checks

```javascript
// routes/health.js
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.get('/ready', async (req, res) => {
  const checks = {
    database: await checkDatabase(),
    redis: await checkRedis(),
    external_api: await checkExternalAPI(),
  };

  const allHealthy = Object.values(checks).every(c => c.healthy);

  res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? 'ready' : 'not_ready',
    checks,
  });
});

async function checkDatabase() {
  try {
    await db.query('SELECT 1');
    return { healthy: true, latency: '5ms' };
  } catch (err) {
    return { healthy: false, error: err.message };
  }
}
```

### 9. SLOs y SLIs

```yaml
# Service Level Objectives
slos:
  - name: API Availability
    sli: sum(rate(http_requests_total{status!~"5.."}[30d])) / sum(rate(http_requests_total[30d]))
    target: 99.9%  # 43 min downtime/month

  - name: API Latency
    sli: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[30d]))
    target: < 500ms for 99% of requests

  - name: Error Budget
    calculation: 1 - (actual_availability / target_availability)
    alert_threshold: 50%  # Alert when 50% budget consumed
```

### 10. Checklist de Observabilidad

- [ ] Metricas RED implementadas
- [ ] Logging estructurado
- [ ] Trace IDs propagados
- [ ] Health checks configurados
- [ ] Dashboards creados
- [ ] Alertas configuradas
- [ ] SLOs definidos
- [ ] On-call runbooks documentados

## Configuraciones Reales

### prometheus.yml (produccion)
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alerts.yml"

scrape_configs:
  - job_name: "api"
    static_targets: [{targets: ["localhost:3000"]}]
    metrics_path: "/metrics"

  - job_name: "node-exporter"
    static_targets: [{targets: ["localhost:9100"]}]

alerting:
  alertmanagers:
    - static_configs:
        - targets: ["localhost:9093"]
```

### alerts.yml
```yaml
groups:
  - name: api_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels: {severity: critical}
        annotations:
          summary: "Error rate > 5% for 5 minutes"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels: {severity: warning}
        annotations:
          summary: "P95 latency > 1s"
```

### OpenTelemetry (Node.js)
```javascript
// tracing.js - Agregar al inicio de la app
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({ url: 'http://localhost:4318/v1/traces' }),
  instrumentations: [getNodeAutoInstrumentations()],
});
sdk.start();
```

## Comandos de Ejemplo

```
"Configura Prometheus metrics para Express"
"Implementa logging estructurado con Pino"
"Crea un dashboard de Grafana para el servicio"
"Configura alertas para error rate > 1%"
"Implementa distributed tracing con OpenTelemetry"
```
