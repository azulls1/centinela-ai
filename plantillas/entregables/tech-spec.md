# Tech Spec: [NOMBRE_FEATURE]

> **Fase:** Disenar
> **Agente:** nxt-architect
> **PRD Relacionado:** [PRD-ID]
> **Version:** 1.0
> **Fecha:** [FECHA]

---

## 1. Resumen

### 1.1 Objetivo
[Que problema tecnico resuelve esta especificacion]

### 1.2 Background
[Contexto tecnico necesario para entender la solucion]

### 1.3 Alcance
- **Incluido:** [Que cubre este tech spec]
- **Excluido:** [Que NO cubre]

## 2. Diseno de la Solucion

### 2.1 Arquitectura de Alto Nivel

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Componente A│────>│ Componente B│────>│ Componente C│
└─────────────┘     └─────────────┘     └─────────────┘
```

### 2.2 Componentes

#### Componente A: [Nombre]
- **Responsabilidad:** [Que hace]
- **Tecnologia:** [Stack usado]
- **Interfaces:** [APIs expuestas/consumidas]

#### Componente B: [Nombre]
- **Responsabilidad:** [Que hace]
- **Tecnologia:** [Stack usado]
- **Interfaces:** [APIs expuestas/consumidas]

## 3. Diseno Detallado

### 3.1 Modelo de Datos

#### Nuevas Entidades
```typescript
interface NuevaEntidad {
  id: string;           // UUID v4
  campo1: string;       // Descripcion
  campo2: number;       // Descripcion
  created_at: Date;     // Timestamp creacion
  updated_at: Date;     // Timestamp actualizacion
}
```

#### Migraciones Requeridas
```sql
-- Migration: add_nueva_entidad
CREATE TABLE nueva_entidad (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campo1 VARCHAR(255) NOT NULL,
    campo2 INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_nueva_entidad_campo1 ON nueva_entidad(campo1);
```

### 3.2 API Specification

#### Endpoint 1: POST /api/resource
**Request:**
```json
{
  "campo1": "string",
  "campo2": 123
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "campo1": "string",
    "campo2": 123,
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

**Errores:**
| Codigo | Mensaje | Cuando |
|--------|---------|--------|
| 400 | "campo1 is required" | Falta campo obligatorio |
| 409 | "Resource already exists" | Duplicado |
| 500 | "Internal server error" | Error inesperado |

#### Endpoint 2: GET /api/resource/:id
**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "campo1": "string",
    "campo2": 123
  }
}
```

### 3.3 Logica de Negocio

#### Algoritmo/Proceso Principal
```
1. Recibir input del usuario
2. Validar datos de entrada
   - Si invalido: retornar error 400
3. Verificar permisos
   - Si no autorizado: retornar error 403
4. Procesar logica de negocio
   - Paso 4.1: [descripcion]
   - Paso 4.2: [descripcion]
5. Persistir en base de datos
6. Emitir evento (si aplica)
7. Retornar respuesta
```

#### Pseudocodigo
```python
def create_resource(data: CreateResourceDTO) -> Resource:
    # Validar
    validate_input(data)

    # Verificar duplicados
    existing = repository.find_by_campo1(data.campo1)
    if existing:
        raise ConflictError("Resource already exists")

    # Crear
    resource = Resource(
        campo1=data.campo1,
        campo2=data.campo2
    )

    # Persistir
    saved = repository.save(resource)

    # Evento
    event_bus.publish(ResourceCreatedEvent(saved))

    return saved
```

### 3.4 Integraciones

#### Integracion con [Sistema Externo]
| Aspecto | Detalle |
|---------|---------|
| Protocolo | REST/gRPC/GraphQL |
| Autenticacion | API Key / OAuth |
| Rate Limit | X req/min |
| Timeout | X segundos |
| Retry Policy | 3 intentos, exponential backoff |

## 4. Consideraciones de Seguridad

### 4.1 Autenticacion/Autorizacion
- [ ] Endpoint requiere autenticacion
- [ ] Permisos requeridos: [lista de permisos]
- [ ] Rate limiting: [X] req/min por usuario

### 4.2 Validacion de Datos
| Campo | Validacion | Sanitizacion |
|-------|------------|--------------|
| campo1 | max 255 chars, alphanumeric | trim, escape HTML |
| campo2 | integer, 0-1000 | N/A |

### 4.3 Datos Sensibles
- [ ] No se almacenan passwords en plain text
- [ ] PII encriptado at rest
- [ ] Logs no contienen datos sensibles

## 5. Performance

### 5.1 Objetivos
| Metrica | Target | Actual (si existe) |
|---------|--------|-------------------|
| Latency p50 | < 50ms | - |
| Latency p95 | < 200ms | - |
| Throughput | > 100 req/s | - |

### 5.2 Optimizaciones Planificadas
- [ ] Caching: [estrategia]
- [ ] Indexing: [indices a crear]
- [ ] Query optimization: [queries a optimizar]

## 6. Testing Strategy

### 6.1 Unit Tests
```typescript
describe('ResourceService', () => {
  it('should create resource with valid data', async () => {
    // Arrange
    // Act
    // Assert
  });

  it('should throw error on duplicate', async () => {
    // Arrange
    // Act
    // Assert
  });
});
```

### 6.2 Integration Tests
- [ ] API endpoint tests
- [ ] Database integration tests
- [ ] External service mocks

### 6.3 Test Coverage Target
- Unit: >= 80%
- Integration: >= 60%

## 7. Deployment

### 7.1 Feature Flags
| Flag | Descripcion | Default |
|------|-------------|---------|
| `ENABLE_NEW_FEATURE` | Habilita la nueva funcionalidad | false |

### 7.2 Rollout Plan
1. **Fase 1:** Deploy a staging (1 dia)
2. **Fase 2:** Canary 5% produccion (2 dias)
3. **Fase 3:** Rollout 50% (2 dias)
4. **Fase 4:** Rollout 100%

### 7.3 Rollback Plan
```bash
# En caso de problemas
kubectl rollback deployment/api --to-revision=N
# O deshabilitar feature flag
```

## 8. Monitoreo

### 8.1 Metricas a Agregar
| Metrica | Tipo | Labels |
|---------|------|--------|
| `resource_created_total` | Counter | status |
| `resource_creation_duration_seconds` | Histogram | - |

### 8.2 Alertas
| Condicion | Severidad | Accion |
|-----------|-----------|--------|
| Error rate > 5% | Critical | Page on-call |
| Latency p95 > 500ms | Warning | Slack notification |

### 8.3 Dashboards
- [ ] Crear panel en Grafana para nueva funcionalidad

## 9. Dependencias y Riesgos

### 9.1 Dependencias
| Dependencia | Tipo | Estado | Owner |
|-------------|------|--------|-------|
| [Dep 1] | Bloqueante | En progreso | [Team] |
| [Dep 2] | Soft | Completada | [Team] |

### 9.2 Riesgos Tecnicos
| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|--------------|---------|------------|
| [Riesgo] | Media | Alto | [Plan] |

## 10. Timeline

| Fase | Duracion | Entregable |
|------|----------|------------|
| Implementacion | X dias | Codigo + tests |
| Code Review | X dias | PR aprobado |
| QA | X dias | Tests pasando |
| Deploy | X dias | En produccion |

## 11. Apendice

### 11.1 Referencias
- [Link a PRD]
- [Link a Architecture Doc]
- [Link a API existente]

### 11.2 Glosario
| Termino | Definicion |
|---------|------------|
| [Termino] | [Definicion] |

---

## Siguiente Paso

- [ ] Revisar tech spec con equipo
- [ ] Crear stories con `/nxt/pm`
- [ ] Implementar con `/nxt/dev`

---

*Generado con NXT AI Development v3.8.0*
