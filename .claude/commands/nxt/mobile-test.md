# NXT Mobile Testing - Testing E2E de Apps Moviles

Ejecuta estos pasos EN ORDEN, sin preguntar:

## PASO 1: Leer Skill
Lee el archivo `skills/desarrollo/SKILL-mobile-testing.md` y sigue sus instrucciones.

## PASO 2: Identificar Framework
Detecta que framework usa el proyecto:
- `package.json` con `react-native` → React Native (Detox/Maestro)
- `pubspec.yaml` → Flutter (patrol/integration_test)
- `*.xcodeproj` → iOS nativo (XCTest)
- `build.gradle` con android → Android nativo (Espresso)

## PASO 3: Ejecutar Testing
Segun el framework detectado:
- Configurar herramienta de E2E apropiada
- Escribir tests para los flujos criticos
- Ejecutar tests y reportar resultados

## PASO 4: Crear Reporte
Crear reporte de testing con Write tool en `docs/4-implementation/mobile-test-report.md`

## PASO FINAL: Persistencia
Si hubo hallazgos, actualizar `.nxt/state.json`.
Si hubo cambios significativos: `python herramientas/context_manager.py checkpoint "mobile-test_$(date +%H%M%S)"`

**NO PREGUNTES. LEE EL SKILL Y EJECUTA.**
