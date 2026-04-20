# Mobile App Specification

> **Fase:** Disenar/Planificar
> **Agente:** nxt-mobile, nxt-design
> **Version:** 3.8.0

## Informacion General

| Campo | Valor |
|-------|-------|
| App Name | [nombre] |
| Bundle ID | com.[company].[app] |
| Plataformas | iOS / Android / Both |
| Framework | React Native / Flutter / Native |
| Min iOS | 16.0 |
| Min Android | API 26 (Android 8.0) |

## Screens

| # | Screen | Descripcion | Navigation |
|---|--------|-------------|-----------|
| 1 | Splash | Logo + loading | → Login or Home |
| 2 | Login | Email + password + social | → Home |
| 3 | Home | Feed principal | Tab navigator |
| 4 | Profile | Info del usuario | → Edit Profile |

## Navigation Structure
```
[Tab Navigator]
├── Home (Stack)
│   ├── Feed
│   ├── Detail
│   └── Comments
├── Search (Stack)
│   ├── Search
│   └── Results
├── Notifications
└── Profile (Stack)
    ├── Profile
    ├── Edit
    └── Settings
```

## APIs Requeridas

| Endpoint | Metodo | Descripcion |
|----------|--------|-------------|
| /auth/login | POST | Login con email/password |
| /auth/social | POST | Login con Google/Apple |
| /users/me | GET | Perfil del usuario |
| /feed | GET | Feed principal (paginado) |
| /notifications | GET | Notificaciones |

## Funcionalidades Nativas

- [ ] Push Notifications (Firebase/APNs)
- [ ] Camera / Photo Library
- [ ] Location Services
- [ ] Biometric Auth (Face ID / Fingerprint)
- [ ] Deep Links / Universal Links
- [ ] Offline Mode
- [ ] Background Sync

## State Management

| Aspecto | Tecnologia | Notas |
|---------|-----------|-------|
| State global | Zustand / Riverpod / Redux | [elegir uno] |
| Cache/offline | WatermelonDB / Hive / MMKV | [si offline-first] |
| Auth state | SecureStore / Keychain | [tokens JWT] |
| Server state | TanStack Query / SWR | [cache de API] |

## Internationalization (i18n)

- [ ] Idiomas soportados: [es, en, ...]
- [ ] Framework: react-i18next / flutter_localizations
- [ ] RTL support requerido: [si/no]
- [ ] Traducciones externas: [si/no]

## Accessibility (a11y)

- [ ] VoiceOver (iOS) / TalkBack (Android) support
- [ ] Dynamic type / font scaling
- [ ] Color contrast AA minimum
- [ ] Labels en todos los elementos interactivos

## Analytics & Monitoring

| Herramienta | Proposito |
|-------------|-----------|
| Firebase Analytics | Eventos de usuario |
| Sentry / Crashlytics | Crash reporting |
| Performance Monitoring | Startup, screens |

## Push Notification Strategy

| Tipo | Trigger | Contenido |
|------|---------|-----------|
| Transaccional | Accion del usuario | Confirmacion de compra, etc. |
| Engagement | Cron / segmento | Recordatorio, promo |
| Real-time | Evento del sistema | Nuevo mensaje, alerta |

## Performance Targets

| Metrica | Target |
|---------|--------|
| Cold Start | < 2s |
| Screen Transition | < 300ms |
| Frame Rate | 60 fps |
| Bundle Size (iOS) | < 50 MB |
| Bundle Size (Android) | < 30 MB |
| Memory Usage | < 150 MB |

## Store Checklist

- [ ] App icon (1024x1024 iOS, 512x512 Android)
- [ ] Screenshots (6.7", 6.5", 5.5" iOS + phone/tablet Android)
- [ ] App Store description (4000 chars max)
- [ ] Privacy policy URL
- [ ] Keywords (100 chars iOS)
- [ ] Age rating configured
- [ ] In-app purchases configured (if applicable)
