# Workflow: Vendoring

> **Basado en:** BMAD v6 Alpha - Standalone Bundles
> **Propósito:** Crear bundles standalone de workflows para distribución
> **Versión:** 3.8.0

## Descripción

El Workflow Vendoring permite empaquetar workflows completos como bundles
independientes que pueden ser:
- Distribuidos a otros proyectos
- Ejecutados sin dependencias del framework completo
- Versionados y compartidos

## Cuándo Usar

- Compartir un workflow con otro equipo
- Crear versión portable de un proceso
- Distribuir metodología sin el framework completo
- Backup de workflows críticos

---

## Estructura de un Bundle

```
my-workflow.bundle/
├── manifest.json          # Metadatos del bundle
├── workflow.md            # El workflow principal
├── agents/                # Agentes requeridos
│   └── *.md
├── skills/                # Skills requeridos
│   └── *.md
├── templates/             # Plantillas necesarias
│   └── *.md
├── config/                # Configuración mínima
│   └── defaults.yaml
└── README.md              # Documentación de uso
```

---

## Proceso de Vendoring

### Paso 1: Analizar Dependencias

```bash
*vendor analyze [workflow-name]
```

El sistema analiza:
- Agentes referenciados en el workflow
- Skills mencionados
- Plantillas utilizadas
- Configuraciones requeridas

**Output:**
```yaml
workflow: create-prd
dependencies:
  agents:
    - nxt-pm
    - nxt-analyst
  skills:
    - SKILL-docx
  templates:
    - prd.md
  config:
    - escala.nivel_2
estimated_size: 45KB
```

### Paso 2: Resolver Dependencias

```bash
*vendor resolve [workflow-name]
```

Opciones:
- `--include-all`: Incluir todas las dependencias
- `--minimal`: Solo lo esencial
- `--exclude [item]`: Excluir elementos específicos

### Paso 3: Crear Bundle

```bash
*vendor create [workflow-name] [output-dir]
```

Genera el bundle con:
- Todos los archivos necesarios
- manifest.json con metadatos
- README con instrucciones de uso

### Paso 4: Validar Bundle

```bash
*vendor validate [bundle-path]
```

Verifica:
- Integridad de archivos
- Dependencias completas
- Sintaxis correcta
- Ejecutabilidad standalone

---

## Manifest Schema

```json
{
  "$schema": "https://nxt.dev/schemas/bundle-v1.json",
  "name": "create-prd-bundle",
  "version": "1.0.0",
  "workflow": "create-prd",
  "framework_version": "3.8.0",
  "created": "2025-01-19T00:00:00Z",
  "author": "NXT Grupo",
  "description": "Bundle para crear PRDs usando metodología NXT",

  "dependencies": {
    "agents": ["nxt-pm", "nxt-analyst"],
    "skills": ["SKILL-docx"],
    "templates": ["prd.md"]
  },

  "requirements": {
    "claude_code": ">=1.0.0",
    "features": ["slash_commands"]
  },

  "entry_point": "workflow.md",

  "config": {
    "defaults": "config/defaults.yaml",
    "overridable": ["empresa.nombre", "desarrollador.nombre"]
  }
}
```

---

## Comandos de Vendoring

| Comando | Descripción |
|---------|-------------|
| `*vendor analyze [wf]` | Analizar dependencias |
| `*vendor resolve [wf]` | Resolver y listar |
| `*vendor create [wf] [out]` | Crear bundle |
| `*vendor validate [bundle]` | Validar bundle |
| `*vendor install [bundle]` | Instalar bundle |
| `*vendor list` | Listar bundles instalados |
| `*vendor export [wf] --zip` | Exportar como ZIP |

---

## Ejemplo: Crear Bundle de PRD Workflow

### 1. Analizar

```bash
*vendor analyze workflows/fase-2-definir/create-prd.md
```

Output:
```
📦 Análisis de Dependencias: create-prd

Agentes (2):
  ✓ nxt-pm (found)
  ✓ nxt-analyst (found)

Skills (1):
  ✓ SKILL-docx (found)

Templates (1):
  ✓ plantillas/entregables/prd.md (found)

Config:
  ✓ escala.nivel_2 (default)

Estado: ✅ Todas las dependencias encontradas
Tamaño estimado: 52KB
```

### 2. Crear Bundle

```bash
*vendor create create-prd ./bundles/
```

Output:
```
📦 Creando bundle: create-prd

Copiando archivos...
  ✓ workflow.md
  ✓ agents/nxt-pm.md
  ✓ agents/nxt-analyst.md
  ✓ skills/SKILL-docx.md
  ✓ templates/prd.md
  ✓ config/defaults.yaml

Generando manifest.json...
  ✓ Manifest creado

Generando README.md...
  ✓ README creado

✅ Bundle creado: ./bundles/create-prd.bundle/
   Tamaño: 48KB
   Archivos: 8
```

### 3. Distribuir

El bundle puede ser:
- Copiado a otro proyecto
- Subido a un repositorio
- Compartido como ZIP

### 4. Instalar en Otro Proyecto

```bash
*vendor install ./create-prd.bundle/
```

---

## Bundles Predefinidos

NXT incluye bundles predefinidos para distribución:

| Bundle | Descripción | Tamaño |
|--------|-------------|--------|
| `quick-bugfix` | Workflow para bug fixes rápidos | 15KB |
| `feature-flow` | Flujo completo de feature | 85KB |
| `code-review` | Sistema de code review | 35KB |
| `qa-pipeline` | Pipeline de QA completo | 65KB |
| `documentation` | Generación de docs | 45KB |

---

## Integración con CI/CD

### GitHub Action para Bundles

```yaml
# .github/workflows/vendor-bundle.yml
name: Create Workflow Bundle

on:
  push:
    paths:
      - 'workflows/**'

jobs:
  bundle:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Create Bundle
        run: |
          python herramientas/vendor.py create \
            workflows/my-workflow.md \
            ./dist/

      - name: Upload Bundle
        uses: actions/upload-artifact@v4
        with:
          name: workflow-bundle
          path: ./dist/*.bundle/
```

---

## Best Practices

### DO
- Versionar bundles con semver
- Incluir README detallado
- Validar antes de distribuir
- Documentar configuraciones requeridas

### DON'T
- Incluir secretos o API keys
- Bundles mayores a 500KB
- Dependencias circulares
- Hardcodear paths absolutos

---

## Troubleshooting

### Bundle no se instala

```
Error: Missing dependency: nxt-architect
```

**Solución:** El bundle fue creado con `--minimal`. Recrear con `--include-all`.

### Workflow no ejecuta

```
Error: Template not found: custom-template.md
```

**Solución:** La plantilla referenciada no fue incluida. Agregar al bundle manualmente.

### Versión incompatible

```
Warning: Bundle requires framework 3.8.0, current is 3.8.0
```

**Solución:** Actualizar framework o usar flag `--force`.

---

*Workflow Vendoring v3.8.0 - Bundles standalone para workflows*
