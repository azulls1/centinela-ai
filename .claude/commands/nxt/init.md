# NXT INIT - Inicializar Proyecto

Ejecuta estos pasos EN ORDEN, sin preguntar:

## PASO 1: Validar Entorno
Ejecuta con Bash:
```bash
echo "=== NXT Init v3.8.0 ===" && \
echo "Python: $(python --version 2>&1 || python3 --version 2>&1 || echo 'NOT FOUND')" && \
echo "Git: $(git --version 2>&1 || echo 'NOT FOUND')" && \
echo "Bash: $(bash --version 2>&1 | head -1 || echo 'NOT FOUND')" && \
echo "Curl: $(curl --version 2>&1 | head -1 || echo 'NOT FOUND')"
```

## PASO 2: Verificar Estructura NXT
Ejecuta con Bash:
```bash
cd "$(pwd)" && \
echo "=== Verificando estructura ===" && \
[ -d ".nxt" ] && echo "OK: .nxt/" || echo "CREAR: mkdir -p .nxt/checkpoints .nxt/context .nxt/state" && \
[ -f ".nxt/state.json" ] && echo "OK: state.json" || echo "MISSING: state.json" && \
[ -f ".nxt/nxt.config.yaml" ] && echo "OK: nxt.config.yaml" || echo "MISSING: config" && \
[ -f ".env" ] && echo "OK: .env configurado" || echo "WARN: .env no existe (telemetria deshabilitada)" && \
echo "Agentes: $(ls agentes/nxt-*.md 2>/dev/null | wc -l)" && \
echo "Skills: $(ls skills/**/*.md 2>/dev/null | wc -l)" && \
echo "Hooks: $(ls hooks/*.sh 2>/dev/null | wc -l) (opcionales, para telemetria)"
```

## PASO 3: Crear directorios faltantes
Si algun directorio no existe, crealo:
```bash
mkdir -p .nxt/checkpoints .nxt/context .nxt/state 2>/dev/null; echo "Directorios verificados"
```

## PASO 4: Analizar Proyecto
Ejecuta con Bash (si Python está disponible, si no, omitir este paso):
```bash
python herramientas/nxt_orchestrator_v3.py analyze 2>&1 || echo "WARN: Python CLI no disponible. Puedes usar /nxt/orchestrator directamente."
```

## PASO 5: Mostrar Estado
Ejecuta con Bash:
```bash
python herramientas/nxt_orchestrator_v3.py status
```

## PASO 6: Resumen al Usuario
Muestra:
- Version del framework
- Numero de agentes y skills disponibles
- Si telemetria esta habilitada (.env existe)
- Tareas pendientes (si hay)
- Comando sugerido: "Usa /nxt/orchestrator para empezar o /nxt/help para ver comandos"
