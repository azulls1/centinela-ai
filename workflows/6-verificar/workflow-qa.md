# Workflow: Verificacion y QA

## Fase
**VERIFICAR** (Fase 6 de 6)

## Agente Principal
`nxt-qa`

## Objetivo
Validar que el codigo cumple con los criterios de aceptacion y estandares de calidad.

## Triggers
- `*qa-validate [story]` - Validar story
- `*test-plan [sprint]` - Crear test plan
- `*bug [titulo]` - Reportar bug
- `*qa-report` - Generar reporte QA

## Flujo de Trabajo

```
┌─────────────────────────────────────────────────────────────┐
│                    FASE: VERIFICAR                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   POR CADA STORY:                                           │
│                                                             │
│   1. REVISAR CRITERIOS                                      │
│      └─> Cargar story con criterios de aceptacion          │
│      └─> Revisar notas del desarrollador                   │
│      └─> Preparar escenarios de prueba                     │
│                                                             │
│   2. CREAR TEST CASES                                       │
│      └─> Happy path                                        │
│      └─> Edge cases                                        │
│      └─> Error scenarios                                   │
│      └─> Regression tests                                  │
│                                                             │
│   3. EJECUTAR TESTS                                         │
│      └─> Tests automatizados                               │
│      └─> Tests manuales                                    │
│      └─> Tests de performance (si aplica)                  │
│      └─> Tests de seguridad (si aplica)                    │
│                                                             │
│   4. REPORTAR                                               │
│      └─> Documentar resultados                             │
│      └─> Reportar bugs encontrados                         │
│      └─> Sugerir mejoras                                   │
│                                                             │
│   5. DECIDIR                                                │
│      ├─> PASS: Story completada -> DONE                    │
│      └─> FAIL: Devolver a Dev con bugs                     │
│                                                             │
│   SALIDAS:                                                  │
│   - docs/4-implementation/qa/test-results/                 │
│   - docs/4-implementation/qa/bugs/                         │
│   - docs/4-implementation/qa/qa-report.md                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────┴───────────┐
              │                       │
           [PASS]                  [FAIL]
              │                       │
              ▼                       ▼
         Story DONE            Devolver a Dev
```

## Tipos de Testing

| Tipo | Alcance | Herramientas |
|------|---------|--------------|
| Unit | Funciones/Clases | Jest, Pytest |
| Integration | APIs, Servicios | Supertest, pytest |
| E2E | Flujos completos | Playwright, Cypress |
| Manual | Exploratorio | Checklist |
| Performance | Carga, stress | k6, Artillery |
| Security | Vulnerabilidades | OWASP ZAP |

## Test Case Template

```markdown
# Test Case: TC-XXX

## Informacion
| Campo | Valor |
|-------|-------|
| Story | US-XXX |
| Prioridad | Alta/Media/Baja |
| Tipo | Funcional/UI/API |

## Descripcion
[Que se prueba]

## Precondiciones
- Usuario autenticado
- Feature flag habilitado

## Pasos
| # | Accion | Dato | Resultado Esperado |
|---|--------|------|-------------------|
| 1 | Navegar a /login | - | Formulario visible |
| 2 | Ingresar email | test@test.com | Campo acepta input |
| 3 | Ingresar password | ******* | Campo oculta texto |
| 4 | Click Login | - | Redirect a /dashboard |

## Resultado
- [ ] PASSED
- [ ] FAILED
- [ ] BLOCKED
- [ ] SKIPPED

## Notas
[Observaciones durante la prueba]

## Evidencia
[Screenshots, logs]
```

## Bug Report Template

```markdown
# Bug: BUG-XXX

## Informacion
| Campo | Valor |
|-------|-------|
| Severidad | Critico/Alto/Medio/Bajo |
| Prioridad | P1/P2/P3/P4 |
| Story | US-XXX |
| Encontrado por | QA |
| Asignado a | [Dev] |
| Estado | Abierto |

## Descripcion
[Descripcion clara del problema]

## Pasos para Reproducir
1. Ir a [pagina]
2. Click en [elemento]
3. Ingresar [dato]
4. Observar [resultado]

## Resultado Actual
[Que sucede - el bug]

## Resultado Esperado
[Que deberia suceder]

## Ambiente
- Browser: Chrome 120
- OS: Windows 11
- Version: 1.0.0-beta

## Evidencia
[Screenshots, videos, logs de consola]

## Workaround
[Si existe forma de evitar el bug temporalmente]
```

## Severidad de Bugs

| Nivel | Simbolo | Descripcion | Ejemplo |
|-------|---------|-------------|---------|
| Critico | P1 | Sistema no usable | App crash, data loss |
| Alto | P2 | Feature principal roto | Login falla, no puede pagar |
| Medio | P3 | Feature secundario | Filtro no funciona |
| Bajo | P4 | Cosmetico | Typo, alineacion |

## QA Report Template

```markdown
# QA Report: Sprint [X]

## Resumen Ejecutivo
| Metrica | Valor |
|---------|-------|
| Total Test Cases | XX |
| Passed | XX |
| Failed | XX |
| Blocked | XX |
| Pass Rate | XX% |

## Stories Validadas

| Story | Estado | Bugs |
|-------|--------|------|
| US-001 | PASS | 0 |
| US-002 | PASS | 1 (low) |
| US-003 | FAIL | 2 (1 high) |

## Bugs Encontrados

### Criticos/Altos
- BUG-001: [Titulo] - Asignado a [Dev]

### Medios/Bajos
- BUG-002: [Titulo]

## Recomendaciones
1. [Recomendacion]
2. [Recomendacion]

## Veredicto
[ ] APROBADO para produccion
[ ] REQUIERE FIXES antes de produccion
[ ] BLOQUEADO - no puede desplegarse

## Firma
QA: NXT QA
Fecha: [FECHA]
```

## Checklist de QA

### Por Story
- [ ] Criterios de aceptacion verificados
- [ ] Happy path funciona
- [ ] Edge cases probados
- [ ] Errores manejados correctamente
- [ ] Performance aceptable
- [ ] UX consistente
- [ ] Accesibilidad basica (WCAG A)
- [ ] Sin errores en consola
- [ ] Responsive (si aplica)
- [ ] Cross-browser (si aplica)

### Por Sprint
- [ ] Todas las stories validadas
- [ ] Bugs criticos resueltos
- [ ] Regression tests pasando
- [ ] Performance general OK
- [ ] Documentacion actualizada

## Artefactos Generados

| Artefacto | Ubicacion | Formato |
|-----------|-----------|---------|
| Test Plan | `docs/4-implementation/qa/test-plan.md` | Markdown |
| Test Cases | `docs/4-implementation/qa/test-cases/` | Markdown |
| Bug Reports | `docs/4-implementation/qa/bugs/` | Markdown |
| QA Report | `docs/4-implementation/qa/qa-report.md` | Markdown |

## Criterios de Salida

Para marcar story como DONE:

1. Todos los criterios de aceptacion verificados
2. Sin bugs criticos o altos abiertos
3. Tests automatizados pasando
4. QA sign-off

## Ciclo Completo

```
Story DONE
    │
    ▼
¿Mas stories en sprint?
    │
  Si ┴ No
    │   │
    ▼   ▼
  Siguiente story   Sprint Completado
    │                    │
    └──── DESCUBRIR ◄────┘
         (nuevo ciclo)
```

## Dependencias Entre Fases

| Fase Anterior | Entregable Requerido | Fase Siguiente |
|---------------|---------------------|----------------|
| Construir | Codigo funcional en branch `feature/US-XXX` | Verificar |
| Construir | Tests unitarios y de integracion pasando | Verificar |
| Construir | PR creado con commits atomicos | Verificar |
| Planificar | `docs/2-planning/stories/` (criterios de aceptacion) | Verificar |
| Verificar | QA Report (`docs/4-implementation/qa/qa-report.md`) | Deploy / Done |
| Verificar | Bug Reports (`docs/4-implementation/qa/bugs/`) | Construir (si FAIL) |
| Verificar | Story marcada DONE | Descubrir (nuevo ciclo) |
