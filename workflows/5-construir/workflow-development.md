# Workflow: Desarrollo

## Fase
**CONSTRUIR** (Fase 5 de 6)

## Agente Principal
`nxt-dev`

## Objetivo
Implementar codigo de alta calidad siguiendo las stories y sus contextos.

## Triggers
- `*dev-story [story]` - Implementar story
- `*commit [mensaje]` - Hacer commit
- `*test [scope]` - Ejecutar tests
- `*code-review` - Solicitar revision

## Flujo de Trabajo

```
┌─────────────────────────────────────────────────────────────┐
│                    FASE: CONSTRUIR                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   POR CADA STORY:                                           │
│                                                             │
│   1. LEER STORY + CONTEXT                                   │
│      └─> Cargar story desde docs/2-planning/stories/       │
│      └─> Cargar context desde docs/4-implementation/       │
│      └─> Entender alcance y criterios                      │
│                                                             │
│   2. PREPARAR                                               │
│      └─> Crear branch: feature/US-XXX                      │
│      └─> Verificar dependencias instaladas                 │
│      └─> Revisar archivos a modificar                      │
│                                                             │
│   3. IMPLEMENTAR                                            │
│      └─> Seguir patrones del codebase                      │
│      └─> Escribir codigo limpio                            │
│      └─> Aplicar SOLID, DRY, KISS                         │
│                                                             │
│   4. TESTEAR                                                │
│      └─> Escribir tests unitarios                          │
│      └─> Escribir tests de integracion (si aplica)         │
│      └─> Verificar cobertura >= 80%                        │
│                                                             │
│   5. DOCUMENTAR                                             │
│      └─> Comentarios donde sea necesario                   │
│      └─> Actualizar README si aplica                       │
│      └─> Agregar notas en story                            │
│                                                             │
│   6. COMMIT                                                 │
│      └─> Commits atomicos                                  │
│      └─> Mensajes descriptivos (Conventional Commits)      │
│                                                             │
│   7. SOLICITAR REVIEW                                       │
│      └─> Crear PR / solicitar revision                     │
│      └─> Pasar a fase VERIFICAR                           │
│                                                             │
│   SALIDA: Codigo funcional con tests                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
              [Siguiente: FASE VERIFICAR]
```

## Conventional Commits

```
feat(scope): nueva funcionalidad
fix(scope): correccion de bug
docs(scope): cambios en documentacion
refactor(scope): refactorizacion sin cambio funcional
test(scope): agregar o modificar tests
chore(scope): tareas de mantenimiento
perf(scope): mejoras de rendimiento
style(scope): formateo, sin cambio de logica
```

### Ejemplos

```bash
git commit -m "feat(auth): implement login form with validation"
git commit -m "fix(api): handle null response from payment gateway"
git commit -m "test(auth): add unit tests for login service"
git commit -m "docs(readme): update installation instructions"
```

## Principios de Codigo

### SOLID
- **S**ingle Responsibility: Una clase, una responsabilidad
- **O**pen/Closed: Abierto a extension, cerrado a modificacion
- **L**iskov Substitution: Subtipos intercambiables
- **I**nterface Segregation: Interfaces especificas
- **D**ependency Inversion: Depender de abstracciones

### Otros
- **DRY**: Don't Repeat Yourself
- **KISS**: Keep It Simple, Stupid
- **YAGNI**: You Aren't Gonna Need It

## Estructura de Branch

```
main
├── develop
│   ├── feature/US-001-login-form
│   ├── feature/US-002-user-registration
│   ├── fix/bug-123-null-pointer
│   └── refactor/auth-module
```

## Checklist por Story

```markdown
## Story: US-XXX - [Titulo]

### Implementacion
- [ ] Codigo implementado siguiendo context
- [ ] Patrones del codebase respetados
- [ ] Sin codigo duplicado
- [ ] Sin hardcoded values

### Testing
- [ ] Tests unitarios escritos
- [ ] Tests de integracion (si aplica)
- [ ] Cobertura >= 80%
- [ ] Todos los tests pasan

### Calidad
- [ ] Linter sin errores
- [ ] No hay warnings
- [ ] Codigo revisado personalmente

### Documentacion
- [ ] Comentarios donde necesario
- [ ] README actualizado (si aplica)
- [ ] Notas en story actualizadas

### Control de Version
- [ ] Commits atomicos
- [ ] Mensajes descriptivos
- [ ] Branch nombrado correctamente
```

## Integraciones

### Con Gemini (nxt-search)
```bash
# Buscar documentacion o soluciones
python herramientas/gemini_tools.py search "error [mensaje] [framework]"
```

### Con Gemini (nxt-media)
```bash
# Generar assets para la app con Nano Banana Pro
python herramientas/gemini_tools.py image "icono para [feature]" icon.png
```

## Artefactos Generados

| Artefacto | Ubicacion | Formato |
|-----------|-----------|---------|
| Codigo | `src/` | Segun stack |
| Tests | `tests/` | Segun stack |
| Story Updates | `docs/2-planning/stories/` | Markdown |

## Criterios de Salida

Para pasar a la siguiente fase (VERIFICAR):

1. Codigo implementado
2. Tests escritos y pasando
3. Criterios de aceptacion cubiertos
4. Commits realizados
5. PR creado (si aplica)

## Siguiente Paso

```
Al completar la implementacion, ejecuta:
/nxt/qa

Esto activara el agente QA para validar la story.
```

## Dependencias Entre Fases

| Fase Anterior | Entregable Requerido | Fase Siguiente |
|---------------|---------------------|----------------|
| Planificar | `docs/2-planning/stories/` (stories con criterios de aceptacion) | Construir |
| Planificar | `docs/4-implementation/contexts/` (story contexts) | Construir |
| Disenar | `docs/3-solutioning/architecture.md` (arquitectura tecnica) | Construir |
| Disenar | `docs/3-solutioning/tech-specs/` (specs por modulo) | Construir |
| Construir | Codigo funcional con tests en `src/` y `tests/` | Verificar |
| Construir | PR creado con commits atomicos | Verificar |
| Verificar | QA report con bugs criticos | Construir (si FAIL) |
