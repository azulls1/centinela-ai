# Test Plan: [Feature/Sprint]

## Metadata
| Campo | Valor |
|-------|-------|
| Version | 1.0 |
| Fecha | [YYYY-MM-DD] |
| Autor | NXT QA |
| Sprint | [Numero] |
| Estado | Draft |

---

## 1. Alcance

### 1.1 En Alcance
[Lista de features/stories que se probaran]
- [US-001]: [Titulo]
- [US-002]: [Titulo]
- [US-003]: [Titulo]

### 1.2 Fuera de Alcance
[Lo que NO se probara en este ciclo]
- [Feature X] - Razon: [Por que]

---

## 2. Estrategia de Testing

### 2.1 Tipos de Tests

| Tipo | Cobertura | Herramienta | Responsable |
|------|-----------|-------------|-------------|
| Unit | 80% del codigo nuevo | Jest/Vitest | Desarrollador |
| Integration | APIs criticas | Supertest | Desarrollador |
| E2E | Happy paths | Playwright | QA |
| Manual | Exploratorio | Checklist | QA |

### 2.2 Ambientes

| Ambiente | URL | Datos |
|----------|-----|-------|
| Dev | localhost:3000 | Mock data |
| Staging | staging.app.com | Test data |
| Prod | app.com | Real data |

---

## 3. Criterios de Entrada

Para comenzar testing:
- [ ] Codigo desplegado en staging
- [ ] Tests unitarios pasando (>= 80%)
- [ ] Documentacion de stories disponible
- [ ] Ambiente estable

---

## 4. Criterios de Salida

Para aprobar release:
- [ ] Todos los test cases ejecutados
- [ ] 0 bugs criticos abiertos
- [ ] 0 bugs altos abiertos
- [ ] Bugs medios documentados con workaround
- [ ] Regression tests pasando
- [ ] Performance dentro de SLAs

---

## 5. Test Cases

### 5.1 US-001: [Titulo de la Story]

#### TC-001: [Nombre del Test Case]

| Campo | Valor |
|-------|-------|
| Prioridad | Alta |
| Tipo | Funcional |
| Precondiciones | Usuario autenticado |

**Pasos:**
| # | Accion | Datos | Resultado Esperado |
|---|--------|-------|-------------------|
| 1 | Navegar a | /feature | Pagina carga |
| 2 | Click en | Boton X | Modal aparece |
| 3 | Ingresar | datos validos | Validacion pasa |
| 4 | Submit | - | Success message |

**Estado:** [ ] Pending [ ] Passed [ ] Failed

---

#### TC-002: [Nombre del Test Case]

| Campo | Valor |
|-------|-------|
| Prioridad | Media |
| Tipo | Negativo |
| Precondiciones | - |

**Pasos:**
| # | Accion | Datos | Resultado Esperado |
|---|--------|-------|-------------------|
| 1 | | | |

**Estado:** [ ] Pending [ ] Passed [ ] Failed

---

### 5.2 US-002: [Titulo de la Story]

[Repetir estructura de test cases]

---

## 6. Regression Tests

### 6.1 Areas de Impacto
- [Modulo A] - Razon: [cambios relacionados]
- [Modulo B] - Razon: [dependencia]

### 6.2 Test Cases de Regression

| ID | Test Case | Modulo | Estado |
|----|-----------|--------|--------|
| REG-001 | Login funciona | Auth | [ ] |
| REG-002 | Checkout completo | Payments | [ ] |
| REG-003 | Busqueda funciona | Search | [ ] |

---

## 7. Performance Testing

### 7.1 Metricas Target

| Metrica | Target | Herramienta |
|---------|--------|-------------|
| Page Load Time | < 3s | Lighthouse |
| API Response Time | < 200ms | k6 |
| Concurrent Users | 100 | k6 |

### 7.2 Escenarios de Carga

| Escenario | VUs | Duracion | Ramp-up |
|-----------|-----|----------|---------|
| Smoke | 5 | 1 min | 10s |
| Load | 50 | 10 min | 2 min |
| Stress | 100 | 5 min | 1 min |

---

## 8. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|--------------|---------|------------|
| Ambiente inestable | Media | Alto | Backup environment |
| Datos de prueba insuficientes | Baja | Medio | Seed scripts |
| Tiempo limitado | Alta | Alto | Priorizar criticos |

---

## 9. Entregables

- [ ] Test cases documentados
- [ ] Test execution report
- [ ] Bug reports
- [ ] QA sign-off

---

## 10. Schedule

| Actividad | Fecha Inicio | Fecha Fin | Responsable |
|-----------|--------------|-----------|-------------|
| Preparacion | [Fecha] | [Fecha] | QA |
| Ejecucion Unit | [Fecha] | [Fecha] | Dev |
| Ejecucion E2E | [Fecha] | [Fecha] | QA |
| Regression | [Fecha] | [Fecha] | QA |
| Reporte final | [Fecha] | [Fecha] | QA |

---

## Aprobaciones

| Rol | Nombre | Fecha | Firma |
|-----|--------|-------|-------|
| QA Lead | NXT QA | | |
| Dev Lead | | | |
| PM | | | |

---

*Generado con NXT AI Development*
