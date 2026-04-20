# WCAG Remediation Plan

> **Fase:** Verificar
> **Agente:** nxt-accessibility
> **Version:** 3.8.0
> **Estado:** [Draft | Review | Approved]

---

## Informacion General

| Campo | Valor |
|-------|-------|
| Proyecto | [nombre] |
| Fecha de Auditoria | YYYY-MM-DD |
| Nivel Objetivo | [WCAG 2.1 AA / WCAG 2.2 AA] |
| Paginas Auditadas | [N] |
| Auditor | [nombre/agente/herramienta] |

## Resumen de Issues

| Severidad | Cantidad | Corregidos | Pendientes |
|-----------|----------|------------|------------|
| Critico (blocker) | 0 | 0 | 0 |
| Serio (major) | 0 | 0 | 0 |
| Moderado (minor) | 0 | 0 | 0 |
| Menor (cosmetic) | 0 | 0 | 0 |

## Inventario de Issues

| # | Severidad | Criterio WCAG | Principio | Elemento | Descripcion | Fix |
|---|-----------|---------------|-----------|----------|-------------|-----|
| 1 | Critico | 1.1.1 Non-text Content | Perceivable | `img.hero` | Imagen sin alt text | Agregar `alt="[desc]"` |
| 2 | Serio | 1.4.3 Contrast | Perceivable | `.btn-secondary` | Ratio 3.2:1 (min 4.5:1) | Cambiar color a #[hex] |
| 3 | Serio | 2.1.1 Keyboard | Operable | `.modal-close` | No accesible via teclado | Agregar `tabindex="0"` + handler |
| 4 | Moderado | 2.4.6 Headings | Operable | `<h3>` en home | Heading salta de h1 a h3 | Cambiar a `<h2>` |
| 5 | Menor | 3.2.2 On Input | Understandable | `select#country` | Cambio de pagina sin aviso | Agregar boton de submit |

## Impacto por Discapacidad

| Grupo Afectado | Issues Criticos | Issues Serios | Paginas Afectadas |
|----------------|-----------------|---------------|-------------------|
| Ceguera (screen reader) | [N] | [N] | [lista] |
| Baja vision | [N] | [N] | [lista] |
| Motricidad (solo teclado) | [N] | [N] | [lista] |
| Cognitivo | [N] | [N] | [lista] |

## Timeline de Remediacion

| Fase | Issues | Deadline | Responsable | Estado |
|------|--------|----------|-------------|--------|
| Sprint 1 | Criticos (#1, #3) | YYYY-MM-DD | [dev] | Pendiente |
| Sprint 2 | Serios (#2, #4) | YYYY-MM-DD | [dev] | Pendiente |
| Sprint 3 | Moderados y menores | YYYY-MM-DD | [dev] | Pendiente |

## Plan de Testing

| Metodo | Herramienta | Frecuencia | Cobertura |
|--------|-------------|------------|-----------|
| Automatizado | axe-core / Lighthouse | Cada PR (CI) | ~30% de issues |
| Manual - Keyboard | Tester humano | Cada sprint | Navegacion completa |
| Screen reader | NVDA / VoiceOver | Cada release | Flujos criticos |
| Zoom 200% | Browser zoom | Cada release | Todas las paginas |

## Checklist de Verificacion Post-Fix

- [ ] axe-core reporta 0 violations criticas
- [ ] Lighthouse Accessibility score >= 95
- [ ] Navegacion completa solo con teclado
- [ ] Screen reader lee contenido correctamente
- [ ] Contraste cumple ratio minimo 4.5:1 (texto) / 3:1 (grande)
- [ ] Focus visible en todos los elementos interactivos

---

*Generado con NXT AI Development v3.8.0*
