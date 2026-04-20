# NXT App Store - Publicacion y ASO

Ejecuta estos pasos EN ORDEN, sin preguntar:

## PASO 1: Leer Skill
Lee el archivo `skills/desarrollo/SKILL-app-store.md` y sigue sus instrucciones.

## PASO 2: Determinar Accion
```
¿Que necesitas?
├── Preparar app para publicar → Ejecutar pre-release checklist
├── Optimizar listing (ASO) → Revisar keywords, screenshots, descripcion
├── App fue rechazada → Consultar decision tree de rechazos
├── Configurar IAP → Seguir guia de In-App Purchases
├── Privacy compliance → Revisar ATT, Privacy Manifest, Data Safety
```

## PASO 3: Ejecutar
Segun la accion determinada, seguir las instrucciones del skill.
Crear/actualizar archivos necesarios con Write tool.

## PASO 4: Generar Checklist
Crear checklist pre-release en `docs/4-implementation/app-store-checklist.md` con Write tool.

## PASO FINAL: Persistencia
Actualizar `.nxt/state.json`.
Si hubo cambios: `python herramientas/context_manager.py checkpoint "app-store_$(date +%H%M%S)"`

**NO PREGUNTES. LEE EL SKILL Y EJECUTA.**
