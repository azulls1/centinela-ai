# Code Review: [PR-ID]

> **Fase:** Construir
> **Agente:** nxt-dev
> **Story:** [STORY-ID]
> **Autor:** [AUTOR]
> **Reviewer:** [REVIEWER]
> **Fecha:** [FECHA]

---

## Resumen del PR

### Titulo
**[Titulo descriptivo del cambio]**

### Descripcion
[Que hace este PR y por que]

### Tipo de Cambio
- [ ] Feature nueva
- [ ] Bug fix
- [ ] Refactoring
- [ ] Hotfix
- [ ] Documentacion
- [ ] Configuracion

## Checklist Pre-Review

### Autor
- [ ] Codigo sigue las convenciones del proyecto
- [ ] Tests unitarios agregados/actualizados
- [ ] Tests de integracion pasando
- [ ] Sin console.log/print de debug
- [ ] Documentacion actualizada
- [ ] Self-review completado
- [ ] PR tiene descripcion clara

### Reviewer
- [ ] Revise la descripcion del PR
- [ ] Entiendo el contexto del cambio
- [ ] Revise la story/issue relacionada

## Archivos Modificados

| Archivo | Lineas +/- | Tipo de Cambio |
|---------|------------|----------------|
| `src/components/X.tsx` | +50/-20 | Modificado |
| `src/services/Y.ts` | +100/-0 | Nuevo |
| `tests/X.test.ts` | +30/-0 | Nuevo |

## Revision de Codigo

### Aspectos Positivos
- [Aspecto positivo 1]
- [Aspecto positivo 2]

### Comentarios/Sugerencias

#### Archivo: `src/components/X.tsx`

**Linea 25:** [Severidad: Sugerencia/Importante/Critico]
```typescript
// Codigo actual
const data = fetchData();

// Sugerencia
const data = await fetchData(); // Falta await
```
**Razon:** [Explicacion de por que el cambio es necesario]

---

**Linea 45:** [Severidad: Sugerencia]
```typescript
// Codigo actual
if (x == null) { ... }

// Sugerencia
if (x === null || x === undefined) { ... }
// O usar optional chaining
```
**Razon:** Usar comparacion estricta para evitar coercion

---

#### Archivo: `src/services/Y.ts`

**Linea 10:** [Severidad: Importante]
```typescript
// Codigo actual
function process(data: any) { ... }

// Sugerencia
function process(data: ProcessInput) { ... }
```
**Razon:** Evitar `any`, usar tipos especificos

---

### Preguntas para el Autor
1. [Pregunta sobre decision de diseno]
2. [Pregunta sobre caso edge]

## Evaluacion por Categoria

| Categoria | Calificacion | Notas |
|-----------|--------------|-------|
| Funcionalidad | OK / Mejorar / Bloquear | [Nota] |
| Legibilidad | OK / Mejorar / Bloquear | [Nota] |
| Performance | OK / Mejorar / Bloquear | [Nota] |
| Seguridad | OK / Mejorar / Bloquear | [Nota] |
| Testing | OK / Mejorar / Bloquear | [Nota] |
| Documentacion | OK / Mejorar / Bloquear | [Nota] |

## Tests

### Cobertura
| Metrica | Antes | Despues | Delta |
|---------|-------|---------|-------|
| Lines | [N]% | [N]% | [+/-N]% |
| Branches | [N]% | [N]% | [+/-N]% |
| Functions | [N]% | [N]% | [+/-N]% |

### Tests Ejecutados
```
 PASS  src/components/X.test.tsx
 PASS  src/services/Y.test.ts

Test Suites: 2 passed, 2 total
Tests:       15 passed, 15 total
```

## Seguridad

### Checklist de Seguridad
- [ ] No hay credenciales hardcodeadas
- [ ] Inputs sanitizados correctamente
- [ ] No hay vulnerabilidades de inyeccion
- [ ] Autorizacion verificada donde aplica
- [ ] Datos sensibles no expuestos en logs

### Vulnerabilidades Detectadas
| Tipo | Severidad | Ubicacion | Estado |
|------|-----------|-----------|--------|
| - | - | - | - |

## Performance

### Impacto Estimado
- [ ] Sin impacto significativo
- [ ] Mejora de performance
- [ ] Degradacion aceptable
- [ ] Requiere optimizacion

### Notas de Performance
[Observaciones sobre el impacto en performance]

## Decision Final

### Veredicto
- [ ] **Aprobado** - Listo para merge
- [ ] **Aprobado con comentarios** - Puede mergear, considerar sugerencias
- [ ] **Requiere cambios** - Debe corregir antes de merge
- [ ] **Rechazado** - Requiere rediseno significativo

### Comentario Final
[Resumen de la revision y proximos pasos]

## Historial de Revisiones

| Fecha | Reviewer | Veredicto | Comentario |
|-------|----------|-----------|------------|
| [Fecha] | [Nombre] | [Veredicto] | [Comentario] |

---

## Siguiente Paso

- [ ] Aplicar correcciones (si aplica)
- [ ] Merge a branch destino
- [ ] QA con `/nxt/qa`

---

*Generado con NXT AI Development v3.8.0*
