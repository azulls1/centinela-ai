# SKILL: Changelog Generation

> **Version:** 3.8.0
> **Trigger:** Generacion automatica de changelogs
> **Agente:** nxt-changelog
> **Track:** shared

## Descripcion

Skill para generar y mantener changelogs siguiendo el estandar [Keep a Changelog](https://keepachangelog.com/) y [Semantic Versioning](https://semver.org/).

---

## Capacidades

### 1. Generacion de Changelog
- Analizar commits de Git
- Parsear Conventional Commits
- Agrupar por categoria
- Formatear salida

### 2. Versionado Semantico
- Detectar tipo de cambio
- Sugerir siguiente version
- Identificar breaking changes

### 3. Validacion
- Validar formato de changelog
- Validar commits
- Verificar consistencia

---

## Formato Keep a Changelog

### Estructura

```markdown
# Changelog

Todos los cambios notables seran documentados aqui.

## [Unreleased]

### Added
- Nueva funcionalidad

### Changed
- Cambio en funcionalidad existente

### Deprecated
- Feature que sera removida

### Removed
- Feature removida

### Fixed
- Bug corregido

### Security
- Vulnerabilidad corregida

## [1.0.0] - 2025-01-20

### Added
- Release inicial
```

### Categorias

| Categoria | Uso | Commit Type |
|-----------|-----|-------------|
| Added | Nuevas features | `feat:` |
| Changed | Cambios en features | `refactor:`, `perf:` |
| Deprecated | Features deprecadas | `deprecate:` |
| Removed | Features removidas | `remove:` |
| Fixed | Bug fixes | `fix:` |
| Security | Security fixes | `security:` |

---

## Conventional Commits

### Formato

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Tipos

| Type | Descripcion | SemVer |
|------|-------------|--------|
| `feat` | Nueva feature | MINOR |
| `fix` | Bug fix | PATCH |
| `docs` | Documentacion | - |
| `style` | Formato | - |
| `refactor` | Refactoring | - |
| `perf` | Performance | PATCH |
| `test` | Tests | - |
| `chore` | Mantenimiento | - |
| `ci` | CI/CD | - |

### Breaking Changes

```bash
# Con ! despues del tipo
feat!: remove deprecated API

# Con footer
feat: new API

BREAKING CHANGE: old API removed
```

---

## Semantic Versioning

### Formato: MAJOR.MINOR.PATCH

| Incremento | Cuando |
|------------|--------|
| MAJOR | Breaking changes |
| MINOR | Nueva funcionalidad (compatible) |
| PATCH | Bug fixes (compatible) |

### Ejemplos

```
1.0.0 -> 1.0.1  (fix)
1.0.0 -> 1.1.0  (feat)
1.0.0 -> 2.0.0  (breaking change)
```

---

## Templates

### Markdown (Default)

```markdown
## [{{version}}] - {{date}}

{{#if added}}
### Added
{{#each added}}
- {{this}}
{{/each}}
{{/if}}

{{#if changed}}
### Changed
{{#each changed}}
- {{this}}
{{/each}}
{{/if}}

{{#if fixed}}
### Fixed
{{#each fixed}}
- {{this}}
{{/each}}
{{/if}}
```

### JSON

```json
{
  "version": "{{version}}",
  "date": "{{date}}",
  "added": [],
  "changed": [],
  "fixed": []
}
```

### Release Notes

```markdown
# Release {{version}}

**Fecha:** {{date}}

## Novedades
{{#each added}}
- {{this}}
{{/each}}

## Mejoras
{{#each changed}}
- {{this}}
{{/each}}

## Correcciones
{{#each fixed}}
- {{this}}
{{/each}}
```

---

## Uso con Git

### Analizar Commits

```bash
# Commits desde ultimo tag
git log v1.0.0..HEAD --oneline

# Con formato detallado
git log v1.0.0..HEAD --format="%h %s"

# Solo conventional commits
git log v1.0.0..HEAD --oneline | grep -E "^[a-f0-9]+ (feat|fix|docs|style|refactor|perf|test|chore)(\(.+\))?:"
```

### Crear Tag

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

---

## Validacion

### Reglas de Changelog

1. Versiones en orden descendente
2. Fechas en formato ISO (YYYY-MM-DD)
3. Categorias en orden estandar
4. Links de comparacion validos
5. [Unreleased] siempre presente

### Reglas de Commits

1. Tipo valido (feat, fix, etc.)
2. Descripcion en imperativo
3. Maximo 72 caracteres en subject
4. Body opcional con mas detalle
5. Footer para breaking changes

---

## Integracion CI/CD

### GitHub Actions

```yaml
- name: Generate Changelog
  run: |
    npx conventional-changelog -p angular -i CHANGELOG.md -s
```

### Pre-commit Hook

```bash
#!/bin/bash
# Validar commit message
commitlint --edit $1
```

---

## Herramientas Recomendadas

| Herramienta | Uso |
|-------------|-----|
| `conventional-changelog` | Generar changelog |
| `commitlint` | Validar commits |
| `standard-version` | Release automation |
| `semantic-release` | CI/CD releases |

---

## Checklist

### Al Generar Changelog
- [ ] Analizar commits desde ultimo tag
- [ ] Clasificar por tipo
- [ ] Detectar breaking changes
- [ ] Formatear segun template
- [ ] Incluir links

### Al Hacer Release
- [ ] Mover [Unreleased] a nueva version
- [ ] Agregar fecha
- [ ] Crear tag
- [ ] Actualizar links

---

---

## Configuracion Completa

### .commitlintrc.json

```json
{
  "extends": ["@commitlint/config-conventional"],
  "rules": {
    "type-enum": [2, "always", [
      "feat", "fix", "docs", "style", "refactor",
      "perf", "test", "chore", "ci", "revert"
    ]],
    "subject-max-length": [2, "always", 72],
    "body-max-line-length": [1, "always", 100]
  }
}
```

### GitHub Actions Release

```yaml
name: Release
on:
  push:
    tags: ['v*']
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: {fetch-depth: 0}
      - name: Generate changelog
        run: |
          git log $(git describe --tags --abbrev=0 HEAD~1)..HEAD \
            --pretty=format:"- %s (%h)" > RELEASE_NOTES.md
      - uses: softprops/action-gh-release@v1
        with:
          body_path: RELEASE_NOTES.md
```

### BREAKING CHANGE Example

```
feat!: remove support for Node 16

BREAKING CHANGE: Minimum Node version is now 18.
Users on Node 16 must upgrade before updating.

Migration: Update .nvmrc to "18" and run `nvm use`.
```

---

*SKILL Changelog v1.0.0 - Keep a Changelog + Semantic Versioning*
