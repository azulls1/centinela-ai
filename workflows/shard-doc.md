# Workflow: Shard-Doc (Document Sharding)

> **Basado en:** BMAD v6 Alpha - Universal Document Sharding
> **Propósito:** Dividir documentos grandes en secciones organizadas

## Descripción

El workflow Shard-Doc permite dividir documentos markdown grandes en
múltiples archivos más pequeños y manejables, manteniendo la estructura
y las referencias cruzadas.

## Cuándo Usar

- Documentos de más de 500 líneas
- PRDs extensos que necesitan dividirse por módulo
- Arquitecturas complejas con múltiples componentes
- Documentación técnica que crece orgánicamente

## Proceso

### Paso 1: Análisis del Documento

```yaml
input:
  file: path/to/large-document.md

analysis:
  - Identificar secciones principales (H1, H2)
  - Detectar dependencias entre secciones
  - Calcular tamaño de cada sección
  - Identificar referencias cruzadas
```

### Paso 2: Estrategia de División

```yaml
strategies:
  by_heading:
    description: Dividir por encabezados H2
    output: Carpeta con archivos por sección

  by_size:
    description: Dividir cuando supere N líneas
    max_lines: 200

  by_component:
    description: Dividir por componente/módulo
    requires: Detectar patrones de componentes

  by_phase:
    description: Dividir por fase del proyecto
    phases: [discovery, design, build, verify]
```

### Paso 3: Generación de Índice

```markdown
# [Nombre del Documento] - Índice

## Secciones

1. [Introducción](./01-introduction.md)
2. [Arquitectura](./02-architecture.md)
3. [Componentes](./03-components.md)
4. [API Reference](./04-api-reference.md)
5. [Testing](./05-testing.md)

## Navegación

- **Anterior:** N/A
- **Siguiente:** [Introducción](./01-introduction.md)

## Metadata

| Propiedad | Valor |
|-----------|-------|
| Documento Original | `large-document.md` |
| Fecha de División | YYYY-MM-DD |
| Total Secciones | 5 |
| Líneas Original | 1200 |
```

### Paso 4: Template de Sección

Cada sección generada incluye:

```markdown
# [Título de Sección]

> **Parte de:** [Nombre Documento Original](./README.md)
> **Sección:** 2 de 5

---

[Contenido de la sección]

---

## Navegación

- **Anterior:** [Introducción](./01-introduction.md)
- **Siguiente:** [Componentes](./03-components.md)
- **Índice:** [README](./README.md)
```

## Comandos

```bash
# Activar workflow de sharding
*shard-doc path/to/document.md

# Con estrategia específica
*shard-doc document.md --strategy by_heading

# Con límite de líneas
*shard-doc document.md --max-lines 150

# Preview sin crear archivos
*shard-doc document.md --dry-run
```

## Ejemplo Práctico

### Input: PRD Extenso (800 líneas)

```
docs/prd-sistema-auth.md (800 líneas)
├── Introducción (50 líneas)
├── Objetivos (30 líneas)
├── Requisitos Funcionales (200 líneas)
├── Requisitos No Funcionales (100 líneas)
├── Arquitectura (150 líneas)
├── API Specification (200 líneas)
└── Testing Strategy (70 líneas)
```

### Output: Documentos Sharded

```
docs/prd-sistema-auth/
├── README.md              # Índice con links
├── 01-introduction.md     # 50 líneas
├── 02-objectives.md       # 30 líneas
├── 03-functional-reqs.md  # 200 líneas
├── 04-non-functional.md   # 100 líneas
├── 05-architecture.md     # 150 líneas
├── 06-api-spec.md         # 200 líneas
└── 07-testing.md          # 70 líneas
```

## Manejo de Referencias

### Referencias Internas

El workflow actualiza automáticamente las referencias:

```markdown
# Antes (documento único)
Ver [Arquitectura](#arquitectura) para detalles.

# Después (documento sharded)
Ver [Arquitectura](./05-architecture.md) para detalles.
```

### Referencias Externas

Se mantiene un mapa de referencias:

```yaml
# .shard-map.yaml
original: docs/prd-sistema-auth.md
sharded_to: docs/prd-sistema-auth/
references:
  "#introduccion": "./01-introduction.md"
  "#arquitectura": "./05-architecture.md"
  "#api": "./06-api-spec.md"
```

## Reconstrucción

Para volver a unir los documentos:

```bash
# Reconstruir documento original
*unshard-doc docs/prd-sistema-auth/

# Output: docs/prd-sistema-auth-merged.md
```

## Integración con Agentes

| Agente | Uso del Sharding |
|--------|------------------|
| nxt-docs | Crear documentación modular |
| nxt-pm | Dividir PRDs por módulo |
| nxt-architect | Separar arquitectura por componente |
| nxt-paige | Navegar documentos grandes |

## Configuración

```yaml
# .nxt/shard-config.yaml
shard_doc:
  default_strategy: by_heading
  max_lines_per_shard: 200
  min_lines_per_shard: 20
  include_navigation: true
  include_metadata: true
  preserve_original: true
  output_format: numbered  # numbered | named | kebab
```

---

*Workflow Shard-Doc - Documentos manejables, conocimiento organizado*
