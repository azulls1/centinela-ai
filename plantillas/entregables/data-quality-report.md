# Data Quality Report

> **Fase:** Verificar
> **Agente:** nxt-data
> **Version:** 3.8.0
> **Estado:** [Draft | Review | Approved]

---

## Informacion General

| Campo | Valor |
|-------|-------|
| Proyecto | [nombre] |
| Fecha de Analisis | YYYY-MM-DD |
| Analista | [nombre/agente] |
| Periodo de Datos | [fecha inicio - fecha fin] |
| Registros Analizados | [N total] |

## Fuentes de Datos

| Fuente | Tipo | Registros | Frecuencia Actualizacion | Owner |
|--------|------|-----------|-------------------------|-------|
| [tabla/API/archivo] | PostgreSQL / REST / CSV | [N] | Real-time / Diario / Semanal | [equipo] |

## Metricas de Calidad

| Dimension | Metrica | Resultado | Objetivo | Estado |
|-----------|---------|-----------|----------|--------|
| **Completeness** | Campos no-nulos | [N]% | >= 95% | PASS/FAIL |
| **Accuracy** | Registros validos vs total | [N]% | >= 98% | PASS/FAIL |
| **Consistency** | Conflictos entre fuentes | [N] | 0 | PASS/FAIL |
| **Freshness** | Edad del dato mas reciente | [N] horas | < 24h | PASS/FAIL |
| **Uniqueness** | Duplicados encontrados | [N] ([%]) | < 1% | PASS/FAIL |
| **Validity** | Formato/rango correcto | [N]% | >= 99% | PASS/FAIL |

## Completeness por Campo

| Campo | % No-Nulo | % Valido | Patron de Nulos | Accion |
|-------|-----------|----------|-----------------|--------|
| email | [N]% | [N]% | Aleatorio | Requerir en formulario |
| phone | [N]% | [N]% | Sistematico (campo opcional) | Aceptable |
| address | [N]% | [N]% | Concentrado en imports | Limpiar imports |
| created_at | 100% | 100% | - | OK |

## Issues Encontrados

| # | Severidad | Dimension | Tabla/Campo | Descripcion | Registros Afectados | Remediacion |
|---|-----------|-----------|-------------|-------------|---------------------|-------------|
| 1 | CRITICO | Accuracy | users.email | Emails con formato invalido | [N] ([%]) | Validar + limpiar |
| 2 | ALTO | Uniqueness | orders | Ordenes duplicadas por race condition | [N] | Dedup + unique constraint |
| 3 | MEDIO | Freshness | products.price | Precios sin actualizar > 30 dias | [N] | Sync con ERP |
| 4 | BAJO | Consistency | users.country | Formatos mixtos (US/USA/United States) | [N] | Normalizar con lookup table |

## Tendencia de Calidad

| Periodo | Completeness | Accuracy | Freshness | Score General |
|---------|-------------|----------|-----------|---------------|
| [mes-2] | [N]% | [N]% | [N]h | [N]/100 |
| [mes-1] | [N]% | [N]% | [N]h | [N]/100 |
| [actual] | [N]% | [N]% | [N]h | [N]/100 |

## Plan de Remediacion

| # Issue | Accion | Responsable | Deadline | Estado |
|---------|--------|-------------|----------|--------|
| 1 | Script de limpieza + validacion en ingesta | [dev] | YYYY-MM-DD | Pendiente |
| 2 | Agregar unique constraint + dedup batch | [dev] | YYYY-MM-DD | Pendiente |
| 3 | Configurar sync automatico | [dev] | YYYY-MM-DD | Pendiente |
| 4 | Crear tabla de referencia + migration | [dev] | YYYY-MM-DD | Pendiente |

## Monitoreo Recomendado

- [ ] Alerta si completeness cae debajo del 95%
- [ ] Check diario de duplicados en tablas criticas
- [ ] Validacion automatica en pipelines de ingesta

---

*Generado con NXT AI Development v3.8.0*
