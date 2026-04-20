# Quick Dev Workflow - Implementacion Directa

> **Version:** 3.8.0
> **Fuente:** BMAD v6 Quick Dev + NXT Nivel 0-1
> **Lead:** nxt-dev
> **Trigger:** Tareas nivel 0 (trivial) y nivel 1 (simple)

## Cuando Usar Quick Dev
- Bug fixes de 1-3 archivos
- Typos y correcciones menores
- Cambios de configuracion
- Features muy pequenas (< 1 hora)
- Refactoring localizado

## Cuando NO Usar Quick Dev
- Features que tocan 4+ archivos -> usar workflow completo
- Cambios de arquitectura -> /nxt/architect primero
- Cambios de base de datos -> /nxt/database primero
- Cualquier cosa nivel 2+ -> workflow estandar

## Flujo

```
+---------------------------------------------------------------------+
|                     QUICK DEV WORKFLOW                                |
+---------------------------------------------------------------------+
|                                                                       |
|   [Tarea] -> [Dev] -> [Test] -> [Done]                               |
|       |        |        |        |                                    |
|       v        v        v        v                                    |
|   * Entender* Codear * Tests  * Commit                               |
|   * Scope  * Edit   * Lint   * Checkpoint                            |
|   * Files  * Write  * Build  * Report                                |
|                                                                       |
|   SIN: Analysis, PRD, Architecture, Sprint Planning                  |
|   SIN: Multiple agents coordination                                  |
|   SOLO: nxt-dev + nxt-qa (opcional para nivel 0)                     |
|                                                                       |
+---------------------------------------------------------------------+
```

## Pasos

### 1. Entender (30 segundos)
- Leer la tarea
- Identificar archivos afectados
- Verificar que es realmente nivel 0-1

### 2. Implementar (el trabajo real)
- Usar Write/Edit tools para crear/modificar codigo
- Seguir convenciones existentes del proyecto
- NO sobre-engineerar

### 3. Verificar (1-2 minutos)
- Ejecutar tests existentes
- Verificar lint
- Build exitoso

### 4. Cerrar
- Commit con conventional commits
- Actualizar state.json
- Checkpoint si fue significativo

## Decision Tree: Quick Dev o Workflow Completo?
```
La tarea...?
|-- Cambia 1-3 archivos y es un bug fix -> QUICK DEV
|-- Cambia 1 archivo de config -> QUICK DEV
|-- Es un typo o formatting -> QUICK DEV
|-- Requiere nuevo endpoint API -> WORKFLOW COMPLETO
|-- Toca autenticacion/seguridad -> WORKFLOW COMPLETO + /nxt/cybersec
|-- Crea tabla nueva en DB -> WORKFLOW COMPLETO + /nxt/database
|-- Es una feature para usuarios -> WORKFLOW COMPLETO
```
