# NXT Mobile Performance - Optimizacion de Apps Moviles

Ejecuta estos pasos EN ORDEN, sin preguntar:

## PASO 1: Leer Skill
Lee el archivo `skills/desarrollo/SKILL-mobile-performance.md` y sigue sus instrucciones.

## PASO 2: Diagnosticar
Identifica el problema de performance:
- Startup lento → Optimizar imports, lazy loading, Hermes
- Jank/stuttering → Optimizar FlatList, usar Reanimated
- Memory leaks → Cleanup useEffect, cancel subscriptions
- Bundle grande → Code splitting, tree shaking, assets
- ANR (Android Not Responding) → Mover trabajo pesado a background

## PASO 3: Aplicar Fixes
Usar Edit tool para aplicar las optimizaciones directamente en el codigo.

## PASO 4: Verificar
```bash
# React Native - bundle size
npx react-native-bundle-visualizer

# Flutter - build size
flutter build apk --analyze-size

# Android - startup time
adb shell am start -W com.myapp/.MainActivity
```

## PASO FINAL: Persistencia
Documentar mejoras en `.nxt/state.json`.
Si hubo cambios: `python herramientas/context_manager.py checkpoint "mobile-perf_$(date +%H%M%S)"`

**NO PREGUNTES. LEE EL SKILL Y EJECUTA.**
