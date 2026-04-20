# SKILL: Webhooks

> **Version:** 3.8.0
> **Trigger:** Implementacion de webhooks inbound y outbound
> **Agente:** nxt-integrations
> **Track:** shared

## Proposito
Implementar webhooks seguros y confiables, tanto como emisor (outbound)
como receptor (inbound), con manejo de reintentos y validacion.

## Cuando se Activa
- Recibir webhooks de servicios externos
- Enviar webhooks a integraciones
- Validar firmas de webhooks
- Implementar retry logic
- Procesar eventos asincronos

## Instrucciones

### 1. Anatomia de un Webhook

```
┌──────────────┐    HTTP POST    ┌──────────────┐
│   Emisor     │ ──────────────► │   Receptor   │
│  (Source)    │                 │  (Consumer)  │
└──────────────┘                 └──────────────┘

Request:
POST /webhooks/stripe HTTP/1.1
Host: api.yoursite.com
Content-Type: application/json
Stripe-Signature: t=1234,v1=abc123...
X-Request-ID: req_123

{
  "id": "evt_123",
  "type": "payment_intent.succeeded",
  "data": {
    "object": { ... }
  }
}

Response:
HTTP/1.1 200 OK
```

### 2. Recibir Webhooks (Inbound)

#### Endpoint Basico
```javascript
// routes/webhooks.js
import express from 'express';
import crypto from 'crypto';

const router = express.Router();

// Raw body necesario para verificar firma
router.use('/stripe', express.raw({ type: 'application/json' }));

router.post('/stripe', async (req, res) => {
  const signature = req.headers['stripe-signature'];

  // 1. Verificar firma
  let event;
  try {
    event = stripe.webhooks.constructEvent(
      req.body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // 2. Responder rapido (antes de procesar)
  res.status(200).json({ received: true });

  // 3. Procesar asincrono
  try {
    await processWebhookEvent(event);
  } catch (err) {
    console.error('Error processing webhook:', err);
    // No fallar el request - el evento ya fue aceptado
  }
});
```

#### Verificacion de Firma (Manual)
```javascript
function verifyWebhookSignature(payload, signature, secret) {
  // Formato comun: timestamp.signature
  const [timestamp, providedSignature] = signature.split('.');

  // Verificar timestamp (prevenir replay attacks)
  const currentTime = Math.floor(Date.now() / 1000);
  const webhookTime = parseInt(timestamp);
  if (currentTime - webhookTime > 300) { // 5 minutos
    throw new Error('Webhook timestamp too old');
  }

  // Calcular firma esperada
  const signedPayload = `${timestamp}.${payload}`;
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(signedPayload)
    .digest('hex');

  // Comparar de forma segura (timing-safe)
  const isValid = crypto.timingSafeEqual(
    Buffer.from(providedSignature),
    Buffer.from(expectedSignature)
  );

  if (!isValid) {
    throw new Error('Invalid signature');
  }

  return true;
}
```

#### Idempotencia
```javascript
// Evitar procesar el mismo evento dos veces
async function processWebhookEvent(event) {
  const eventId = event.id;

  // Check si ya procesamos este evento
  const processed = await redis.get(`webhook:processed:${eventId}`);
  if (processed) {
    console.log(`Event ${eventId} already processed, skipping`);
    return;
  }

  // Procesar evento
  await handleEvent(event);

  // Marcar como procesado (con TTL)
  await redis.setex(`webhook:processed:${eventId}`, 86400, '1'); // 24h
}
```

### 3. Enviar Webhooks (Outbound)

#### Sistema de Envio
```javascript
// services/webhookSender.js
import crypto from 'crypto';
import fetch from 'node-fetch';

class WebhookSender {
  constructor(options = {}) {
    this.timeout = options.timeout || 30000;
    this.maxRetries = options.maxRetries || 5;
  }

  generateSignature(payload, secret, timestamp) {
    const signedPayload = `${timestamp}.${JSON.stringify(payload)}`;
    return crypto
      .createHmac('sha256', secret)
      .update(signedPayload)
      .digest('hex');
  }

  async send(url, payload, secret) {
    const timestamp = Math.floor(Date.now() / 1000);
    const signature = this.generateSignature(payload, secret, timestamp);

    const headers = {
      'Content-Type': 'application/json',
      'X-Webhook-Signature': `${timestamp}.${signature}`,
      'X-Webhook-ID': crypto.randomUUID(),
      'X-Webhook-Timestamp': timestamp.toString(),
    };

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
      timeout: this.timeout,
    });

    return {
      status: response.status,
      success: response.ok,
      body: await response.text(),
    };
  }
}
```

#### Cola de Webhooks con Reintentos
```javascript
// jobs/webhookJob.js
import { Queue, Worker } from 'bullmq';

const webhookQueue = new Queue('webhooks', {
  connection: redis,
  defaultJobOptions: {
    attempts: 5,
    backoff: {
      type: 'exponential',
      delay: 1000, // 1s, 2s, 4s, 8s, 16s
    },
    removeOnComplete: 100,
    removeOnFail: 1000,
  },
});

// Agregar webhook a la cola
export async function queueWebhook(subscription, event) {
  await webhookQueue.add('deliver', {
    subscriptionId: subscription.id,
    url: subscription.url,
    secret: subscription.secret,
    event: {
      id: crypto.randomUUID(),
      type: event.type,
      data: event.data,
      created_at: new Date().toISOString(),
    },
  });
}

// Worker que procesa webhooks
const worker = new Worker('webhooks', async (job) => {
  const { url, secret, event } = job.data;
  const sender = new WebhookSender();

  const result = await sender.send(url, event, secret);

  if (!result.success) {
    // Log para debugging
    await logWebhookAttempt({
      jobId: job.id,
      attempt: job.attemptsMade,
      status: result.status,
      response: result.body,
    });

    // Throw para trigger retry
    if (result.status >= 500 || result.status === 429) {
      throw new Error(`Webhook failed with status ${result.status}`);
    }

    // 4xx (excepto 429) = no reintentar
    console.log(`Webhook permanently failed: ${result.status}`);
  }

  return result;
}, { connection: redis });
```

### 4. Modelo de Datos

```sql
-- Subscripciones de webhooks
CREATE TABLE webhook_subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  url VARCHAR(2048) NOT NULL,
  secret VARCHAR(255) NOT NULL,
  events TEXT[] NOT NULL, -- ['order.created', 'order.updated']
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Log de entregas
CREATE TABLE webhook_deliveries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subscription_id UUID REFERENCES webhook_subscriptions(id),
  event_type VARCHAR(100) NOT NULL,
  event_id VARCHAR(100) NOT NULL,
  payload JSONB NOT NULL,
  status_code INTEGER,
  response_body TEXT,
  attempts INTEGER DEFAULT 0,
  next_retry_at TIMESTAMP,
  delivered_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_deliveries_retry ON webhook_deliveries(next_retry_at)
  WHERE delivered_at IS NULL;
```

### 5. API de Gestion

```javascript
// routes/webhookSubscriptions.js

// Crear subscription
router.post('/webhooks/subscriptions', auth, async (req, res) => {
  const { url, events } = req.body;

  // Validar URL
  try {
    new URL(url);
  } catch {
    return res.status(400).json({ error: 'Invalid URL' });
  }

  // Generar secret
  const secret = crypto.randomBytes(32).toString('hex');

  const subscription = await db.webhookSubscriptions.create({
    userId: req.user.id,
    url,
    events,
    secret,
  });

  // Retornar secret solo en creacion
  res.json({
    id: subscription.id,
    url: subscription.url,
    events: subscription.events,
    secret, // Solo visible una vez!
    created_at: subscription.created_at,
  });
});

// Listar subscriptions
router.get('/webhooks/subscriptions', auth, async (req, res) => {
  const subscriptions = await db.webhookSubscriptions.findAll({
    where: { userId: req.user.id },
    attributes: { exclude: ['secret'] }, // No exponer secret
  });
  res.json(subscriptions);
});

// Test webhook
router.post('/webhooks/subscriptions/:id/test', auth, async (req, res) => {
  const subscription = await db.webhookSubscriptions.findOne({
    where: { id: req.params.id, userId: req.user.id },
  });

  if (!subscription) {
    return res.status(404).json({ error: 'Subscription not found' });
  }

  const testEvent = {
    id: `test_${crypto.randomUUID()}`,
    type: 'test.webhook',
    data: { message: 'This is a test webhook' },
    created_at: new Date().toISOString(),
  };

  const sender = new WebhookSender();
  const result = await sender.send(
    subscription.url,
    testEvent,
    subscription.secret
  );

  res.json({
    success: result.success,
    status: result.status,
    response: result.body,
  });
});
```

### 6. Patrones Comunes

#### Fan-out de Eventos
```javascript
async function emitEvent(eventType, data) {
  const event = {
    id: crypto.randomUUID(),
    type: eventType,
    data,
    created_at: new Date().toISOString(),
  };

  // Encontrar todas las subscriptions para este evento
  const subscriptions = await db.webhookSubscriptions.findAll({
    where: {
      isActive: true,
      events: { [Op.contains]: [eventType] },
    },
  });

  // Encolar entrega para cada subscription
  await Promise.all(
    subscriptions.map(sub => queueWebhook(sub, event))
  );

  return event;
}

// Uso
await emitEvent('order.created', {
  order_id: order.id,
  customer_id: order.customerId,
  total: order.total,
});
```

### 7. Checklist

#### Receptor (Inbound)
- [ ] Verificacion de firma
- [ ] Respuesta rapida (< 5s)
- [ ] Procesamiento asincrono
- [ ] Idempotencia
- [ ] Logging de eventos

#### Emisor (Outbound)
- [ ] Firma de payloads
- [ ] Retry con backoff
- [ ] Timeout configurado
- [ ] Dead letter queue
- [ ] Dashboard de estado

#### Seguridad
- [ ] HTTPS obligatorio
- [ ] Secrets rotables
- [ ] Rate limiting
- [ ] IP allowlisting (opcional)

## Comandos de Ejemplo

```
"Implementa receptor de webhooks de Stripe"
"Crea sistema de envio de webhooks con reintentos"
"Agrega verificacion de firma HMAC"
"Implementa idempotencia para webhooks"
"Crea API para gestionar subscriptions"
```
