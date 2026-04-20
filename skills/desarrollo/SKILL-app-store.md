# SKILL App Store Optimization & Compliance

> **Version:** 3.8.0
> **Trigger:** Publicacion en App Store / Google Play, ASO, rejection prevention
> **Agente:** nxt-mobile, nxt-pm, nxt-compliance

## App Store Optimization (ASO)

### Factores de Ranking

| Factor | App Store (iOS) | Google Play |
|--------|----------------|-------------|
| Nombre de app | 30 chars max, keywords al inicio | 30 chars max |
| Subtitulo | 30 chars (solo iOS) | N/A |
| Short description | N/A | 80 chars (clave para ranking) |
| Descripcion larga | 4000 chars (NO indexada) | 4000 chars (SI indexada) |
| Keywords field | 100 chars (separar con comas) | N/A (usa descripcion) |
| Categoria | 1 primaria + 1 secundaria | 1 primaria + tags |
| Screenshots | Hasta 10 por device size | Hasta 8 |
| Video preview | 30s max, sin UI de telefono | 30s-2min |
| Rating & reviews | Alto impacto | Alto impacto |
| Update frequency | Moderado impacto | Alto impacto |
| Downloads velocity | Alto impacto (trending) | Alto impacto |

### Keywords Strategy

```
Ejemplo: App de recetas saludables

iOS Keyword Field (100 chars):
recetas,saludables,cocina,dieta,nutricion,comida,fitness,meal,plan,keto

NO incluir:
- Nombre de la app (ya se indexa)
- Plurales (Apple los deduce)
- Nombres de competidores (violation)
- Palabras genéricas (app, free, best)

Google Play Short Description (80 chars):
"Recetas saludables con plan de comidas semanal, lista de compras y contador de calorías"

Google Play Long Description:
- Repetir keywords naturalmente 3-5 veces
- Primeras 3 lineas son las mas importantes (above the fold)
- Usar bullet points y emojis para scanneability
```

### Screenshots que Convierten

```
Estructura recomendada (5-8 screenshots):

1. Hero Shot       --> Propuesta de valor principal con texto grande
2. Feature clave 1 --> La funcion que mas usan los usuarios
3. Feature clave 2 --> Diferenciador vs competencia
4. Social proof    --> Reviews, premios, numero de usuarios
5. Feature clave 3 --> Otra funcion importante
6. Onboarding      --> Lo facil que es empezar
7. Feature clave 4 --> Feature secundaria
8. CTA final       --> "Descarga gratis" / "Prueba 7 dias"

Specs:
- iPhone 6.7" (1290 x 2796) - OBLIGATORIO
- iPhone 6.5" (1284 x 2778) - Recomendado
- iPad 12.9" (2048 x 2732) - Si hay version iPad
- Android: 1080 x 1920 minimo (16:9)
```

## Store Listing Checklist

```
Pre-submission checklist:

[ ] Nombre de app optimizado con keyword principal
[ ] Subtitulo con keyword secundaria (iOS)
[ ] Short description con CTA (Android)
[ ] Descripcion larga con keywords naturales
[ ] 6-8 screenshots por tamaño de device
[ ] Video preview (opcional pero mejora conversion 25%)
[ ] Icono de app (ver requisitos abajo)
[ ] Categoria correcta seleccionada
[ ] Age rating configurado
[ ] Privacy policy URL activa y accesible
[ ] Support URL activa
[ ] What's New / Release notes escritos
[ ] Localizacion de metadata para mercados clave
```

## Review Guidelines - Razones Comunes de Rechazo

### Apple App Store

| # | Razon | Frecuencia | Guideline |
|---|-------|------------|-----------|
| 1 | Bugs y crashes | 25% | 2.1 Performance |
| 2 | Links rotos o placeholder content | 15% | 2.1 Performance |
| 3 | Metadata inexacta (screenshots falsos) | 12% | 2.3 Accurate Metadata |
| 4 | Falta privacy policy | 10% | 5.1.1 Data Collection |
| 5 | No es suficientemente util (wrapper web) | 8% | 4.2 Minimum Functionality |
| 6 | In-app purchase no usa StoreKit | 8% | 3.1.1 In-App Purchase |
| 7 | Login requerido sin modo guest | 6% | 5.1.1 Data Collection |
| 8 | Falta App Tracking Transparency | 5% | 5.1.2 Tracking |
| 9 | Guarda fotos/contactos sin permiso | 5% | 5.1.1 Data Collection |
| 10 | Design no sigue HIG | 4% | 4.0 Design |

### Google Play

| # | Razon | Guideline |
|---|-------|-----------|
| 1 | Politica de privacidad faltante o incompleta | Privacy Policy |
| 2 | Contenido inapropiado | Content Policy |
| 3 | Permisos excesivos | Permissions Policy |
| 4 | Ads policy violation | Ads Policy |
| 5 | Data Safety section incompleta | Data Safety |
| 6 | Target API level desactualizado | Target API Requirements |
| 7 | Impersonation / misleading | Impersonation Policy |

## Decision Tree: Mi App fue Rechazada

```
App rechazada - que hacer
|
+-- Guideline 2.1: Performance
|   +-- Crash en review --> Probar en dispositivos reales (no solo simulador)
|   +-- Crash en iOS version especifica --> Verificar deployment target
|   +-- Pantalla en blanco --> Verificar API calls con timeout
|   +-- Placeholder content --> Eliminar Lorem Ipsum y TODO
|   +-- Links rotos --> Verificar TODAS las URLs
|
+-- Guideline 2.3: Metadata
|   +-- Screenshots no coinciden --> Regenerar con app actual
|   +-- Descripcion misleading --> Reescribir sin exagerar features
|   +-- Categoria incorrecta --> Cambiar categoria
|   +-- Nombre con keywords spam --> Simplificar nombre
|
+-- Guideline 3.1.1: In-App Purchase
|   +-- Pagos fuera de Apple --> Migrar a StoreKit/BillingClient
|   +-- Link a web para pagar --> Eliminar (excepto "reader" apps)
|   +-- Tipo de IAP incorrecto --> Verificar consumable vs subscription
|   +-- Restaurar compras faltante --> Agregar boton "Restore Purchases"
|
+-- Guideline 4.0: Design
|   +-- No parece nativa --> Seguir HIG/Material Design
|   +-- Solo un WebView --> Agregar funcionalidad nativa
|   +-- Funcionalidad minima --> Agregar valor sobre una web
|
+-- Guideline 5.1: Privacy
|   +-- Sin privacy policy --> Crear y publicar privacy policy
|   +-- Sin ATT prompt --> Implementar App Tracking Transparency
|   +-- Permisos sin justificar --> Agregar usage description strings
|   +-- Data Safety incompleta --> Completar formulario en Play Console
|
+-- No se cual es el problema
|   +-- Leer Resolution Center en App Store Connect
|   +-- Responder al reviewer pidiendo clarificacion
|   +-- Apelar si crees que es un error (Apple Review Board)
```

## In-App Purchases (IAP)

### Reglas Criticas

```
Obligatorio usar sistema del store para:
- Contenido digital (premium features, coins, tokens)
- Subscripciones a contenido digital
- Desbloquear funcionalidad de la app

NO obligatorio (puedes usar Stripe/otro):
- Productos fisicos (e-commerce)
- Servicios en el mundo real (Uber, Airbnb)
- Person-to-person services (tutoria, consultoria)
- "Reader" apps (Netflix, Spotify) - con restricciones

Comision del store:
- Apple: 30% (15% para Small Business Program < $1M/año)
- Google: 30% (15% primer $1M/año, automatico)
```

### Implementacion Basica (React Native)

```javascript
// Con react-native-iap
import { initConnection, getProducts, requestPurchase } from 'react-native-iap';

const productIds = ['com.myapp.premium_monthly', 'com.myapp.premium_yearly'];

// Inicializar
await initConnection();

// Obtener productos
const products = await getProducts({ skus: productIds });

// Comprar
const purchase = await requestPurchase({ sku: 'com.myapp.premium_monthly' });

// Verificar receipt en backend (OBLIGATORIO para seguridad)
await api.post('/verify-purchase', {
  receipt: purchase.transactionReceipt,
  platform: Platform.OS,
});

// Restaurar compras (OBLIGATORIO tener este boton)
import { getAvailablePurchases } from 'react-native-iap';
const purchases = await getAvailablePurchases();
```

## Privacy Requirements

### App Tracking Transparency (iOS 14.5+)

```xml
<!-- Info.plist -->
<key>NSUserTrackingUsageDescription</key>
<string>We use this to provide personalized recommendations and measure ad performance.</string>
```

```swift
import AppTrackingTransparency

func requestTracking() {
    ATTrackingManager.requestTrackingAuthorization { status in
        switch status {
        case .authorized: enableTracking()
        case .denied, .restricted: disableTracking()
        case .notDetermined: break
        @unknown default: disableTracking()
        }
    }
}
```

### Privacy Manifest (iOS 17+)

```xml
<!-- PrivacyInfo.xcprivacy -->
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
  <key>NSPrivacyAccessedAPITypes</key>
  <array>
    <dict>
      <key>NSPrivacyAccessedAPIType</key>
      <string>NSPrivacyAccessedAPICategoryUserDefaults</string>
      <key>NSPrivacyAccessedAPITypeReasons</key>
      <array><string>CA92.1</string></array>
    </dict>
  </array>
  <key>NSPrivacyCollectedDataTypes</key>
  <array/>
  <key>NSPrivacyTracking</key>
  <false/>
</dict>
</plist>
```

### Google Play Data Safety

```
Completar en Play Console > App Content > Data Safety:

1. Recoleccion de datos:
   - Listar TODOS los tipos de datos que la app recolecta
   - Marcar cuales son opcionales vs obligatorios
   - Indicar si se comparten con terceros

2. Practicas de seguridad:
   - Datos encriptados en transito (HTTPS)
   - Mecanismo de eliminacion de datos
   - Compromiso con Families Policy (si aplica)

3. Categorias comunes:
   - Nombre, email (Account info)
   - Crash logs (App diagnostics)
   - Device ID (Device identifiers)
   - Purchase history (Financial info)
```

## Release Checklist Final

```
Pre-release (ambas plataformas):

[ ] Version y build number incrementados
[ ] Todos los tests pasan (unit + E2E)
[ ] Probado en dispositivos reales (no solo simulador)
[ ] Sin console.log / print statements en release
[ ] Sin API keys hardcodeadas
[ ] Privacy policy actualizada
[ ] Deep links funcionan
[ ] Push notifications configuradas
[ ] Analytics / crash reporting activo
[ ] Performance: startup < 2s, 60fps, < 300MB RAM
[ ] Accessibility: VoiceOver/TalkBack funciona en flujos criticos

iOS especifico:
[ ] Probado en iPhone SE (pantalla chica) y iPad
[ ] App Tracking Transparency implementado
[ ] Privacy Manifest (PrivacyInfo.xcprivacy) incluido
[ ] StoreKit para IAP (si aplica)
[ ] Boton "Restore Purchases" (si IAP)
[ ] Export compliance (usa encryption?)

## App Icon Requirements

| Plataforma | Tamano | Formato | Notas |
|-----------|--------|---------|-------|
| iOS App Store | 1024x1024 | PNG, no alpha | Apple aplica rounded corners automaticamente |
| iOS app | 60x60, 76x76, 83.5x83.5 (@2x, @3x) | PNG | Xcode genera desde 1024 |
| Android Play Store | 512x512 | PNG, 32-bit | Adaptive icon recomendado |
| Android app | 48dp base (mdpi→xxxhdpi) | PNG/Vector | Foreground + background layers |

**Reglas de diseño:**
- Sin texto pequeño (ilegible a 29x29)
- Sin screenshots del app como icono
- Background solido o gradiente simple
- 1 elemento central reconocible
- Probar a 29x29 px - si no se reconoce, simplificar

Android especifico:
[ ] Target API level >= requerido por Google (API 34+ en 2025)
[ ] Data Safety section completa en Play Console
[ ] ProGuard/R8 activo en release
[ ] Probado en Android Go / dispositivos low-end
[ ] ABI splits configurados (reduce APK size)
[ ] Permisos minimos necesarios
```
