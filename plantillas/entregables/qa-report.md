# QA Report: [RELEASE/FEATURE]

> **Fase:** Verificar
> **Agente:** nxt-qa
> **Version:** [VERSION]
> **Fecha:** [FECHA]
> **QA Lead:** [NOMBRE]

---

## Resumen Ejecutivo

### Estado General
| Metrica | Valor |
|---------|-------|
| **Estado** | PASS / FAIL / BLOQUEADO |
| Tests Ejecutados | [N] |
| Tests Pasados | [N] ([N]%) |
| Tests Fallidos | [N] ([N]%) |
| Bugs Criticos | [N] |
| Bugs Mayores | [N] |
| Bugs Menores | [N] |

### Recomendacion
- [ ] **Aprobado para Release** - Todos los criterios cumplidos
- [ ] **Aprobado con Riesgos** - Bugs menores aceptados
- [ ] **No Aprobado** - Requiere correcciones
- [ ] **Bloqueado** - Dependencias no resueltas

## Alcance del Testing

### Features Testeadas
| Feature | Stories | Estado |
|---------|---------|--------|
| [Feature 1] | STORY-001, STORY-002 | PASS/FAIL |
| [Feature 2] | STORY-003 | PASS/FAIL |

### Fuera de Alcance
- [Feature/area no testeada y razon]

## Ambiente de Testing

| Componente | Version/Config |
|------------|----------------|
| Ambiente | Staging / QA / Dev |
| URL | [URL del ambiente] |
| Branch | [branch testeado] |
| Commit | [hash del commit] |
| Base de Datos | [tipo y version] |
| Browser(s) | [browsers testeados] |
| Dispositivos | [dispositivos testeados] |

## Resultados por Tipo de Test

### Tests Funcionales
| Test Suite | Total | Pass | Fail | Skip |
|------------|-------|------|------|------|
| [Suite 1] | [N] | [N] | [N] | [N] |
| [Suite 2] | [N] | [N] | [N] | [N] |
| **Total** | [N] | [N] | [N] | [N] |

### Tests de Regresion
| Area | Total | Pass | Fail | Notas |
|------|-------|------|------|-------|
| Auth | [N] | [N] | [N] | [Nota] |
| Core | [N] | [N] | [N] | [Nota] |
| API | [N] | [N] | [N] | [Nota] |

### Tests de Performance
| Metrica | Objetivo | Actual | Estado |
|---------|----------|--------|--------|
| Response Time (p50) | < 100ms | [N]ms | PASS/FAIL |
| Response Time (p95) | < 300ms | [N]ms | PASS/FAIL |
| Throughput | > 100 req/s | [N] req/s | PASS/FAIL |
| Error Rate | < 1% | [N]% | PASS/FAIL |

### Tests de Seguridad
| Check | Estado | Notas |
|-------|--------|-------|
| SQL Injection | PASS/FAIL | [Nota] |
| XSS | PASS/FAIL | [Nota] |
| CSRF | PASS/FAIL | [Nota] |
| Auth Bypass | PASS/FAIL | [Nota] |
| Data Exposure | PASS/FAIL | [Nota] |

## Bugs Encontrados

### Criticos (P0)
| ID | Titulo | Estado | Asignado |
|----|--------|--------|----------|
| BUG-001 | [Titulo] | Abierto/Resuelto | [Dev] |

### Mayores (P1)
| ID | Titulo | Estado | Asignado |
|----|--------|--------|----------|
| BUG-002 | [Titulo] | Abierto/Resuelto | [Dev] |

### Menores (P2)
| ID | Titulo | Estado | Asignado |
|----|--------|--------|----------|
| BUG-003 | [Titulo] | Abierto/Resuelto | [Dev] |

## Detalle de Bugs

### BUG-001: [Titulo]
| Campo | Valor |
|-------|-------|
| Severidad | Critico |
| Prioridad | P0 |
| Componente | [Componente] |
| Steps to Reproduce | 1. [Paso 1]<br>2. [Paso 2]<br>3. [Paso 3] |
| Resultado Esperado | [Que deberia pasar] |
| Resultado Actual | [Que pasa] |
| Evidencia | [Screenshot/video link] |
| Estado | Abierto / En Progreso / Resuelto |

---

## Cobertura de Tests

### Cobertura de Codigo
| Metrica | Objetivo | Actual | Estado |
|---------|----------|--------|--------|
| Lines | >= 80% | [N]% | PASS/FAIL |
| Branches | >= 70% | [N]% | PASS/FAIL |
| Functions | >= 80% | [N]% | PASS/FAIL |
| Statements | >= 80% | [N]% | PASS/FAIL |

### Cobertura de Requisitos
| Requisito | Tests | Estado |
|-----------|-------|--------|
| RF-001 | TC-001, TC-002 | Cubierto |
| RF-002 | TC-003 | Cubierto |
| RF-003 | - | NO Cubierto |

## Matriz de Compatibilidad

### Browsers
| Browser | Version | Estado |
|---------|---------|--------|
| Chrome | Latest | PASS/FAIL |
| Firefox | Latest | PASS/FAIL |
| Safari | Latest | PASS/FAIL |
| Edge | Latest | PASS/FAIL |

### Dispositivos
| Dispositivo | OS | Estado |
|-------------|-----|--------|
| Desktop | Windows 11 | PASS/FAIL |
| Desktop | macOS | PASS/FAIL |
| Mobile | iOS 17 | PASS/FAIL |
| Mobile | Android 14 | PASS/FAIL |

## Riesgos Identificados

| Riesgo | Severidad | Mitigacion | Decision |
|--------|-----------|------------|----------|
| [Riesgo 1] | Alta | [Plan] | Aceptado/Mitigar |
| [Riesgo 2] | Media | [Plan] | Aceptado/Mitigar |

## Criterios de Aceptacion

### Criterios de Exit
| Criterio | Estado |
|----------|--------|
| 0 bugs criticos abiertos | PASS/FAIL |
| < 3 bugs mayores abiertos | PASS/FAIL |
| Cobertura >= 80% | PASS/FAIL |
| Performance dentro de SLA | PASS/FAIL |
| Tests de regresion pasando | PASS/FAIL |
| Aprobacion de stakeholders | PASS/FAIL |

## Metricas de Calidad

| Metrica | Valor |
|---------|-------|
| Defect Density | [N] bugs/KLOC |
| Test Effectiveness | [N]% |
| Defect Removal Efficiency | [N]% |
| Escaped Defects | [N] |

## Conclusion

### Resumen
[Resumen de hallazgos principales y estado general de calidad]

### Recomendaciones
1. [Recomendacion 1]
2. [Recomendacion 2]
3. [Recomendacion 3]

### Proximos Pasos
- [ ] [Accion 1]
- [ ] [Accion 2]
- [ ] [Accion 3]

## Aprobaciones

| Rol | Nombre | Fecha | Firma |
|-----|--------|-------|-------|
| QA Lead | [Nombre] | [Fecha] | [ ] |
| Tech Lead | [Nombre] | [Fecha] | [ ] |
| Product Owner | [Nombre] | [Fecha] | [ ] |

---

## Siguiente Paso

- [ ] Resolver bugs criticos (si hay)
- [ ] Deploy con `/nxt/devops`
- [ ] Monitoreo post-release

---

*Generado con NXT AI Development v3.8.0*
