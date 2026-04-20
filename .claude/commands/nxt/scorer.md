# AGENTE NXT-SCORER - EJECUCIÓN DIRECTA

## Instrucciones para Claude

Al recibir este comando, Claude DEBE:

1. **Leer** el archivo del agente: `agentes/nxt-scorer.md`
2. **Seguir** las instrucciones del agente al pie de la letra
3. **Usar** herramientas disponibles: Read, Write, Edit, Bash, Grep, Glob

## Ejecución

### Paso 1: Cargar agente
Lee `agentes/nxt-scorer.md` completo y sigue sus instrucciones.

### Paso 2: Detectar stack
- Leer package.json, requirements.txt, pyproject.toml, go.mod (lo que exista)
- Identificar tipo de proyecto

### Paso 3: Evaluar las 10 areas
Seguir los procedimientos de cada area del agente:
1. Deuda Tecnica
2. Arquitectura
3. Mantenibilidad
4. Cobertura de Pruebas
5. Performance
6. Seguridad
7. Resiliencia
8. DevOps
9. IA & Modelos
10. Producto & Equipo

### Paso 4: Producir score card
- Escribir `.nxt/scores.json` con resultados estructurados
- Mostrar reporte visual en consola
- Listar top 3 fortalezas y top 3 areas criticas
- Recomendar agentes para mejoras

### Argumento opcional: $ARGUMENTS
- Sin argumento: evaluacion completa (10 areas)
- `quick`: evaluacion rapida (4 areas core)
- Nombre de area: evaluar solo esa area (ej: `seguridad`)
- `compare`: comparar con evaluacion anterior
- `trends`: ver tendencias

## Persistencia
Al finalizar, actualizar `.nxt/state.json` con la decision de evaluacion.

---
*NXT Scorer - "Lo que no se mide, no se mejora"*
