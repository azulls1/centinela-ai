# SKILL Root Cause Analysis

> **Version:** 3.8.0
> **Fuente:** BMAD v6.0.3 + NXT Quality Patterns
> **Trigger:** Cuando se analiza un bug fix o se investiga un error recurrente

## Cuando Usar
- Despues de corregir un bug: analizar POR QUE ocurrio
- Cuando hay errores recurrentes en el mismo modulo
- Post-mortem de incidentes
- Para prevenir regresiones

## Metodo: 5 Whys + Pyramid Communication

### Paso 1: Identificar el Sintoma
Que fallo? Cual fue el error exacto?

## Cómo Recolectar Evidencia

### Comandos para Investigar
```bash
# Ver commits recientes relacionados con el bug
git log --oneline --all --grep="fix" | head -20

# Ver qué archivos cambiaron en el fix
git diff HEAD~1 --name-only

# Buscar el error en el código
grep -rn "ERROR\|error\|Exception\|catch" src/ --include="*.ts" --include="*.py" | head -20

# Ver logs recientes (si existen)
tail -100 logs/app.log 2>/dev/null || echo "No log file found"

# Ver historial de cambios en un archivo específico
git log --oneline -10 -- src/[archivo-sospechoso]

# Buscar TODOs y FIXMEs relacionados
grep -rn "TODO\|FIXME\|HACK\|XXX" src/ | head -10
```

### Decision Tree: ¿Dónde Buscar la Causa?
```
¿Qué tipo de error es?
├── Runtime crash → Revisar stack trace + git blame en la línea
├── Resultado incorrecto → Revisar lógica + tests que deberían cubrir
├── Intermitente → Revisar race conditions + timing + caching
├── Solo en producción → Revisar env vars + config + data differences
├── Después de deploy → git diff entre versiones + changelog
```

### Paso 2: 5 Whys
1. Por que fallo? -> [respuesta]
2. Por que [respuesta 1]? -> [respuesta]
3. Por que [respuesta 2]? -> [respuesta]
4. Por que [respuesta 3]? -> [respuesta]
5. Por que [respuesta 4]? -> CAUSA RAIZ

### Paso 3: Pyramid Communication (resumen ejecutivo)
```
CONCLUSION: [causa raiz en 1 oracion]
EVIDENCIA:
  - [dato 1 que soporta la conclusion]
  - [dato 2]
  - [dato 3]
RECOMENDACION: [accion para prevenir recurrencia]
```

### Paso 4: Action Items
| # | Accion | Tipo | Prioridad |
|---|--------|------|-----------|
| 1 | [fix inmediato] | Correctiva | P0 |
| 2 | [prevencion] | Preventiva | P1 |
| 3 | [mejora de proceso] | Sistemica | P2 |

## Ejemplo Real

### Bug: "Login falla intermitentemente los lunes"
1. Por que falla? -> Session token expira
2. Por que expira? -> TTL es 48 horas, configurado el viernes
3. Por que 48h? -> Default del framework, nunca se ajusto
4. Por que no se ajusto? -> No hay test que verifique TTL
5. Por que no hay test? -> **CAUSA RAIZ: No hay politica de testing para configuracion de seguridad**

**Conclusion:** Falta testing de security config
**Accion:** Agregar test que valida session TTL >= 7 dias

## Decision Tree
```
Cuando usar Root Cause Analysis?
|-- Bug corregido pero podria volver -> SI (prevenir regresion)
|-- Error en produccion (P0/P1) -> SI (post-mortem obligatorio)
|-- Mismo modulo falla 3+ veces -> SI (patron recurrente)
|-- Typo o error obvio -> NO (no necesita analisis profundo)
|-- Feature request -> NO (no es un bug)
```
