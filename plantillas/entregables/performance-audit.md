# Performance Audit Report

> **Fase:** Verificar
> **Agente:** nxt-performance
> **Version:** 3.8.0
> **Estado:** [Draft | Review | Approved]

---

## Informacion General

| Campo | Valor |
|-------|-------|
| Proyecto | [nombre] |
| Fecha | YYYY-MM-DD |
| URL Testeada | [url] |
| Ambiente | [produccion/staging] |
| Auditor | [nombre/agente] |
| Dispositivo | [Desktop / Mobile] |

## Core Web Vitals

| Metrica | Valor | Bueno | Mejorable | Malo | Estado |
|---------|-------|-------|-----------|------|--------|
| **LCP** (Largest Contentful Paint) | [N]s | < 2.5s | 2.5-4.0s | > 4.0s | PASS/FAIL |
| **INP** (Interaction to Next Paint) | [N]ms | < 200ms | 200-500ms | > 500ms | PASS/FAIL |
| **CLS** (Cumulative Layout Shift) | [N] | < 0.1 | 0.1-0.25 | > 0.25 | PASS/FAIL |
| **FCP** (First Contentful Paint) | [N]s | < 1.8s | 1.8-3.0s | > 3.0s | PASS/FAIL |
| **TTFB** (Time to First Byte) | [N]ms | < 800ms | 800-1800ms | > 1800ms | PASS/FAIL |

## Lighthouse Scores

| Categoria | Score | Objetivo |
|-----------|-------|----------|
| Performance | [N]/100 | >= 90 |
| Accessibility | [N]/100 | >= 95 |
| Best Practices | [N]/100 | >= 90 |
| SEO | [N]/100 | >= 90 |

## Bundle Analysis

| Bundle | Tamano (gzip) | Limite | Estado | Accion |
|--------|--------------|--------|--------|--------|
| main.js | [N] KB | < 150 KB | PASS/FAIL | [code split / tree shake] |
| vendor.js | [N] KB | < 200 KB | PASS/FAIL | [lazy load / CDN] |
| styles.css | [N] KB | < 50 KB | PASS/FAIL | [purge unused] |
| Total inicial | [N] KB | < 400 KB | PASS/FAIL | - |

## API Response Times

| Endpoint | Metodo | p50 | p95 | p99 | Objetivo | Estado |
|----------|--------|-----|-----|-----|----------|--------|
| /api/auth/login | POST | [N]ms | [N]ms | [N]ms | < 200ms | PASS/FAIL |
| /api/users | GET | [N]ms | [N]ms | [N]ms | < 100ms | PASS/FAIL |
| /api/data/export | GET | [N]ms | [N]ms | [N]ms | < 2000ms | PASS/FAIL |

## Imagenes y Assets

| Issue | Cantidad | Ahorro Estimado | Fix |
|-------|----------|-----------------|-----|
| Imagenes sin comprimir | [N] | [N] KB | Usar WebP/AVIF |
| Imagenes sin lazy load | [N] | [N] KB | `loading="lazy"` |
| Fonts no optimizados | [N] | [N] KB | `font-display: swap` + subset |

## Recomendaciones por Prioridad

1. **P0:** [ej. Habilitar compresion gzip/brotli en servidor]
2. **P0:** [ej. Lazy load de imagenes below the fold]
3. **P1:** [ej. Code splitting de rutas principales]
4. **P1:** [ej. Implementar caching de API responses]
5. **P2:** [ej. Service worker para offline-first]

## Proximos Pasos

- [ ] Implementar fixes P0
- [ ] Configurar performance budget en CI

---

*Generado con NXT AI Development v3.8.0*
