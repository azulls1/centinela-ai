# NXT Mobile CI/CD - Build, Sign y Deploy de Apps

Ejecuta estos pasos EN ORDEN, sin preguntar:

## PASO 1: Leer Skill
Lee el archivo `skills/desarrollo/SKILL-mobile-ci.md` y sigue sus instrucciones.

## PASO 2: Detectar Stack
Determina que herramienta de CI/CD usar:
- Expo/React Native → EAS Build
- Flutter → Codemagic o Fastlane
- Nativo → Fastlane + GitHub Actions

## PASO 3: Configurar Pipeline
Segun el stack:
- Crear/actualizar archivos de CI (eas.json, Fastfile, codemagic.yaml, GitHub Actions)
- Configurar app signing (certs, keystores)
- Configurar distribucion beta (TestFlight, Play internal)

## PASO 4: Crear Archivos
Usar Write tool para crear los archivos de configuracion en disco.

## PASO FINAL: Persistencia
Actualizar `.nxt/state.json` con cambios de CI/CD.
Si hubo cambios: `python herramientas/context_manager.py checkpoint "mobile-ci_$(date +%H%M%S)"`

**NO PREGUNTES. LEE EL SKILL Y EJECUTA.**
