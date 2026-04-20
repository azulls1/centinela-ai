# Mobile Development Workflow

> **Version:** 3.8.0
> **Lead:** nxt-mobile
> **Trigger:** Desarrollo de app movil nueva o feature movil

## Flujo

```
[Spec] → [Setup] → [UI] → [Logic] → [Test] → [Ship] → [Monitor]
  │        │        │        │         │        │
  ▼        ▼        ▼        ▼         ▼        ▼
design   project  screens  APIs+DB   E2E    store
  +      init +   + nav    + state   Detox  Fastlane
mobile   config   + theme  + offline Maestro EAS
spec     expo/rn                     device  submit
```

## Fases

### 1. Spec (nxt-mobile + nxt-design)
- Crear mobile-app-spec.md con screens, navigation, APIs
- Definir framework (RN vs Flutter vs Native)
- Definir plataformas target

### 2. Setup
- Inicializar proyecto (expo init / flutter create)
- Configurar navigation, theme, env
- Configurar CI (EAS / Fastlane)

### 3. UI (nxt-design + nxt-mobile)
- Implementar screens siguiendo el spec
- Navigation structure
- Theme / Design tokens
- Responsive (phone + tablet si aplica)

### 4. Logic (nxt-mobile + nxt-api)
- State management (Zustand/Riverpod)
- API integration
- Offline-first (si aplica)
- Push notifications
- Deep linking

### 5. Test (nxt-qa + nxt-mobile)
- Unit tests (logica de negocio)
- E2E tests (Detox/Maestro)
- Device testing (simulador + real)
- Performance check (startup, memory, fps)

### 6. Ship (nxt-mobile + nxt-devops)
- Build de produccion
- App signing
- Submit a TestFlight / Internal Track
- Submit a App Store / Play Store
- Monitor crashes (Sentry/Firebase Crashlytics)

### 7. Monitor (nxt-mobile + nxt-performance)
- Verificar crash-free rate (> 99.5%)
- Monitorear analytics y funnels
- Revisar store ratings y reviews
- Configurar alerts para crashes críticos
- Planificar OTA updates si hay hotfixes
- A/B testing de features nuevas

## Duracion Estimada por Fase

| Fase | App Nueva | Feature Nueva | Nivel BMAD |
|------|-----------|---------------|-----------|
| 1. Spec | 2-4 horas | 30 min | 2+ |
| 2. Setup | 1-2 horas | 0 (ya existe) | 2+ |
| 3. UI | 4-16 horas | 2-8 horas | 2+ |
| 4. Logic | 4-16 horas | 2-8 horas | 2+ |
| 5. Test | 2-8 horas | 1-4 horas | 1+ |
| 6. Ship | 1-2 horas | 30 min | 1+ |
| 7. Monitor | Ongoing | 1-2 horas/semana | 1+ |

## Skills Utilizados por Fase

| Fase | Skills |
|------|--------|
| 1. Spec | Template: `plantillas/entregables/mobile-app-spec.md` |
| 2. Setup | SKILL-mobile-ci (EAS/Fastlane config) |
| 3. UI | SKILL-mobile-performance (60fps desde el inicio) |
| 4. Logic | SKILL-mobile-performance (memory, offline) |
| 5. Test | SKILL-mobile-testing (Detox/Maestro/patrol) |
| 6. Ship | SKILL-mobile-ci (signing), SKILL-app-store (ASO, compliance) |
| 7. Monitor | SKILL-mobile-analytics (crash reporting, events, A/B, OTA) |

## Decision Tree: Que Fase Necesito?
```
¿En que etapa estas?
├── App nueva desde cero → Empezar en Fase 1 (Spec)
├── Ya tengo spec, necesito codigo → Empezar en Fase 2 (Setup)
├── Ya tengo app, nueva feature → Empezar en Fase 3 (UI) o 4 (Logic)
├── App lista, necesito testing → Empezar en Fase 5 (Test)
├── App tested, publicar → Empezar en Fase 6 (Ship)
├── Bug fix en app existente → Quick Dev workflow (no este)
├── App en produccion, monitorear → Empezar en Fase 7 (Monitor)
```

## Iteraciones y Rework
```
Si durante una fase descubres que necesitas volver atras:
├── UI no matchea el spec → Volver a Fase 1, ajustar spec
├── API no existe → Pausar Fase 4, activar /nxt/api primero
├── Test falla por design → Volver a Fase 3, corregir UI
├── Store rechaza → Revisar SKILL-app-store, corregir y re-submit
```

## Dependencias Entre Fases
| Fase | Requiere | Produce |
|------|----------|---------|
| Spec | Nada | mobile-app-spec.md |
| Setup | mobile-app-spec.md | Proyecto inicializado |
| UI | Proyecto + spec | Screens implementadas |
| Logic | Screens + APIs definidas | App funcional |
| Test | App funcional | QA report + bugs |
| Ship | Tests passing | App en stores |
