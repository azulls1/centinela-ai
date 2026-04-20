# SKILL Mobile Analytics & Observability

> **Version:** 3.8.0
> **Trigger:** Post-launch monitoring, crash reporting, analytics, A/B testing, OTA updates
> **Agente:** nxt-mobile, nxt-data, nxt-performance
> **Track:** mobile

---

## Stack de Observabilidad Movil

| Capa | Herramientas | Que Mide |
|------|-------------|-----------|
| Crash Reporting | Firebase Crashlytics, Sentry, Bugsnag | Crashes, ANRs, exceptions |
| Analytics | Firebase Analytics, Mixpanel, Amplitude, PostHog | Eventos, funnels, retention |
| Session Replay | LogRocket, UXCam, Smartlook | Como interactuan los users |
| Performance | Firebase Performance, Sentry Performance | Startup, network, renders |
| A/B Testing | Firebase Remote Config, Statsig, Optimizely | Experimentos, variants |
| Feature Flags | LaunchDarkly, Unleash, Flagsmith, Firebase RC | Toggle features remotamente |
| OTA Updates | EAS Update, CodePush, Shorebird | Hotfix sin store review |
| Error Boundaries | Codigo defensivo | Graceful degradation |

---

## 1. Crash Reporting

### Objetivo

Detectar, agrupar y priorizar crashes en produccion. El crash-free rate debe mantenerse por encima del 99.5% en todo momento.

### 1.1 Firebase Crashlytics

#### React Native

```bash
# Instalacion
npm install @react-native-firebase/app @react-native-firebase/crashlytics
cd ios && pod install
```

```typescript
// src/services/crashlytics.ts
import crashlytics from '@react-native-firebase/crashlytics';

// Identificar usuario (para correlacionar crashes)
export async function identifyUser(user: { id: string; email: string; plan: string }) {
  await crashlytics().setUserId(user.id);
  await crashlytics().setAttributes({
    email: user.email,
    plan: user.plan,
    appVersion: DeviceInfo.getVersion(),
    buildNumber: DeviceInfo.getBuildNumber(),
  });
}

// Registrar breadcrumb (contexto antes del crash)
export function logBreadcrumb(message: string, data?: Record<string, string>) {
  crashlytics().log(message);
  if (data) {
    crashlytics().setAttributes(data);
  }
}

// Error no-fatal (se reporta sin crashear la app)
export function recordNonFatalError(error: Error, context?: Record<string, string>) {
  if (context) {
    crashlytics().setAttributes(context);
  }
  crashlytics().recordError(error);
}

// Forzar crash para testing (solo en desarrollo)
export function testCrash() {
  if (__DEV__) {
    crashlytics().crash();
  }
}
```

```typescript
// App.tsx - Inicializacion global
import crashlytics from '@react-native-firebase/crashlytics';

function App() {
  useEffect(() => {
    // Habilitar reporte automatico
    crashlytics().setCrashlyticsCollectionEnabled(true);

    // Capturar errores JS no manejados
    const previousHandler = ErrorUtils.getGlobalHandler();
    ErrorUtils.setGlobalHandler((error, isFatal) => {
      crashlytics().log(`JS Error (fatal: ${isFatal}): ${error.message}`);
      crashlytics().recordError(error);
      previousHandler(error, isFatal);
    });

    // Capturar promise rejections no manejadas
    const rejectionTracking = require('promise/setimmediate/rejection-tracking');
    rejectionTracking.enable({
      allRejections: true,
      onUnhandled: (id: number, error: Error) => {
        crashlytics().log(`Unhandled Promise Rejection: ${error.message}`);
        crashlytics().recordError(error);
      },
    });
  }, []);

  return <NavigationContainer>...</NavigationContainer>;
}
```

#### Flutter

```yaml
# pubspec.yaml
dependencies:
  firebase_core: ^3.9.0
  firebase_crashlytics: ^4.3.3
```

```dart
// lib/services/crashlytics_service.dart
import 'package:firebase_crashlytics/firebase_crashlytics.dart';
import 'package:flutter/foundation.dart';

class CrashlyticsService {
  static final _instance = FirebaseCrashlytics.instance;

  /// Inicializar en main() antes de runApp()
  static Future<void> initialize() async {
    // Pasar errores de Flutter a Crashlytics
    FlutterError.onError = (errorDetails) {
      _instance.recordFlutterFatalError(errorDetails);
    };

    // Capturar errores asincronos de la plataforma
    PlatformDispatcher.instance.onError = (error, stack) {
      _instance.recordError(error, stack, fatal: true);
      return true;
    };

    // Desactivar en modo debug
    await _instance.setCrashlyticsCollectionEnabled(!kDebugMode);
  }

  /// Identificar usuario
  static Future<void> identifyUser({
    required String userId,
    required String email,
    String? plan,
  }) async {
    await _instance.setUserIdentifier(userId);
    await _instance.setCustomKey('email', email);
    await _instance.setCustomKey('plan', plan ?? 'free');
  }

  /// Breadcrumb de contexto
  static Future<void> logBreadcrumb(String message) async {
    await _instance.log(message);
  }

  /// Error no-fatal
  static Future<void> recordNonFatal(
    dynamic exception,
    StackTrace stack, {
    String? reason,
    Map<String, String>? context,
  }) async {
    if (context != null) {
      for (final entry in context.entries) {
        await _instance.setCustomKey(entry.key, entry.value);
      }
    }
    await _instance.recordError(exception, stack, reason: reason);
  }
}
```

```dart
// lib/main.dart
import 'dart:async';
import 'package:firebase_core/firebase_core.dart';

Future<void> main() async {
  // Capturar errores en zona aislada
  runZonedGuarded<Future<void>>(() async {
    WidgetsFlutterBinding.ensureInitialized();
    await Firebase.initializeApp();
    await CrashlyticsService.initialize();
    runApp(const MyApp());
  }, (error, stack) {
    CrashlyticsService.recordNonFatal(error, stack, reason: 'runZonedGuarded');
  });
}
```

#### Swift (iOS nativo)

```swift
// AppDelegate.swift
import FirebaseCrashlytics

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        FirebaseApp.configure()

        // Metadata personalizada
        Crashlytics.crashlytics().setUserID("user-123")
        Crashlytics.crashlytics().setCustomValue("premium", forKey: "plan")

        return true
    }
}

// CrashReporter.swift
final class CrashReporter {
    static let shared = CrashReporter()

    func logBreadcrumb(_ message: String) {
        Crashlytics.crashlytics().log(message)
    }

    func recordNonFatal(_ error: Error, context: [String: Any] = [:]) {
        for (key, value) in context {
            Crashlytics.crashlytics().setCustomValue(value, forKey: key)
        }
        Crashlytics.crashlytics().record(error: error)
    }

    func setUserContext(userId: String, email: String, plan: String) {
        let crashlytics = Crashlytics.crashlytics()
        crashlytics.setUserID(userId)
        crashlytics.setCustomValue(email, forKey: "email")
        crashlytics.setCustomValue(plan, forKey: "plan")
    }
}
```

#### Kotlin (Android nativo)

```kotlin
// CrashReporter.kt
import com.google.firebase.crashlytics.FirebaseCrashlytics

object CrashReporter {
    private val crashlytics = FirebaseCrashlytics.getInstance()

    fun initialize(enabled: Boolean = true) {
        crashlytics.isCrashlyticsCollectionEnabled = enabled
    }

    fun identifyUser(userId: String, email: String, plan: String) {
        crashlytics.setUserId(userId)
        crashlytics.setCustomKey("email", email)
        crashlytics.setCustomKey("plan", plan)
    }

    fun logBreadcrumb(message: String) {
        crashlytics.log(message)
    }

    fun recordNonFatal(exception: Throwable, context: Map<String, String> = emptyMap()) {
        context.forEach { (key, value) ->
            crashlytics.setCustomKey(key, value)
        }
        crashlytics.recordException(exception)
    }

    // Capturar excepciones no manejadas globalmente
    fun setupGlobalHandler() {
        val defaultHandler = Thread.getDefaultUncaughtExceptionHandler()
        Thread.setDefaultUncaughtExceptionHandler { thread, throwable ->
            crashlytics.log("Uncaught exception on thread: ${thread.name}")
            crashlytics.recordException(throwable)
            defaultHandler?.uncaughtException(thread, throwable)
        }
    }
}
```

### 1.2 Sentry (alternativa multiplataforma)

#### React Native

```bash
npx @sentry/wizard@latest -i reactNative
```

```typescript
// src/services/sentry.ts
import * as Sentry from '@sentry/react-native';

export function initSentry() {
  Sentry.init({
    dsn: 'https://examplePublicKey@o0.ingest.sentry.io/0',
    tracesSampleRate: 0.2, // 20% de transacciones para performance
    profilesSampleRate: 0.1,
    environment: __DEV__ ? 'development' : 'production',
    beforeSend(event) {
      // Filtrar datos sensibles
      if (event.request?.headers) {
        delete event.request.headers['Authorization'];
      }
      return event;
    },
    integrations: [
      Sentry.reactNativeTracingIntegration({
        routingInstrumentation: Sentry.reactNavigationIntegration,
      }),
    ],
  });
}

// Capturar con contexto adicional
export function captureWithContext(error: Error, context: Record<string, any>) {
  Sentry.withScope((scope) => {
    scope.setTags(context.tags || {});
    scope.setExtras(context.extras || {});
    scope.setLevel(context.level || 'error');
    Sentry.captureException(error);
  });
}

// Breadcrumb manual
export function addBreadcrumb(category: string, message: string, data?: Record<string, any>) {
  Sentry.addBreadcrumb({
    category,
    message,
    data,
    level: 'info',
  });
}
```

#### Flutter

```dart
// lib/services/sentry_service.dart
import 'package:sentry_flutter/sentry_flutter.dart';

class SentryService {
  static Future<void> initialize(AppRunner appRunner) async {
    await SentryFlutter.init(
      (options) {
        options.dsn = 'https://examplePublicKey@o0.ingest.sentry.io/0';
        options.tracesSampleRate = 0.2;
        options.profilesSampleRate = 0.1;
        options.environment = kDebugMode ? 'development' : 'production';
        options.beforeSend = (event, hint) {
          // Filtrar PII
          return event;
        };
      },
      appRunner: appRunner,
    );
  }

  static Future<void> captureWithContext(
    dynamic exception,
    StackTrace stackTrace, {
    Map<String, String>? tags,
    Map<String, dynamic>? extras,
  }) async {
    await Sentry.captureException(
      exception,
      stackTrace: stackTrace,
      withScope: (scope) {
        tags?.forEach((key, value) => scope.setTag(key, value));
        extras?.forEach((key, value) => scope.setExtra(key, value));
      },
    );
  }
}
```

### 1.3 Metricas Clave de Crash Reporting

| Metrica | Target | Alarma |
|---------|--------|--------|
| Crash-free users | > 99.5% | < 99% |
| Crash-free sessions | > 99.8% | < 99.5% |
| ANR rate (Android) | < 0.5% | > 1% |
| Time to crash resolution | < 24h (P0) | > 48h |
| Non-fatal error rate | < 1% sessions | > 5% |

---

## 2. Event Tracking

### 2.1 Convencion de Nombres de Eventos

```
Formato: {object}_{action}

Reglas:
  - snake_case siempre
  - noun_verb (sustantivo primero, verbo despues)
  - maximo 40 caracteres
  - sin datos PII en el nombre del evento
  - usar propiedades para detalles

Ejemplos correctos:
  screen_viewed
  button_tapped
  form_submitted
  purchase_completed
  error_occurred
  notification_received
  notification_opened
  search_performed
  item_added_to_cart
  onboarding_step_completed
  profile_updated
  subscription_started
  subscription_cancelled
  share_initiated
  deeplink_opened

Propiedades (camelCase):
  screenName, buttonId, formType, amount, currency,
  errorCode, searchQuery, itemId, stepNumber, source

Ejemplos INCORRECTOS (no hacer):
  ClickedButton       -> button_tapped
  user_clicked_btn    -> button_tapped + buttonId property
  PURCHASE            -> purchase_completed
  formSubmit          -> form_submitted
  screen-view         -> screen_viewed
```

### 2.2 Firebase Analytics

#### React Native

```bash
npm install @react-native-firebase/analytics
```

```typescript
// src/services/analytics.ts
import analytics from '@react-native-firebase/analytics';

// Tipos para type-safety
interface AnalyticsEvent {
  name: string;
  params?: Record<string, string | number | boolean>;
}

interface UserProperties {
  plan: string;
  accountAge: string;
  preferredLanguage: string;
  notificationsEnabled: string;
}

class AnalyticsService {
  private static enabled = true;

  static async initialize() {
    await analytics().setAnalyticsCollectionEnabled(!__DEV__);
  }

  // Screen tracking (llamar en cada navegacion)
  static async trackScreen(screenName: string, screenClass?: string) {
    if (!this.enabled) return;
    await analytics().logScreenView({
      screen_name: screenName,
      screen_class: screenClass || screenName,
    });
  }

  // Evento generico con validacion
  static async trackEvent(name: string, params?: Record<string, any>) {
    if (!this.enabled) return;
    if (name.length > 40) {
      console.warn(`[Analytics] Event name too long: ${name}`);
      return;
    }
    await analytics().logEvent(name, params);
  }

  // Eventos estandar predefinidos
  static async trackButtonTap(buttonId: string, screenName: string) {
    await this.trackEvent('button_tapped', { buttonId, screenName });
  }

  static async trackSearch(query: string, resultsCount: number) {
    await analytics().logSearch({ search_term: query });
    await this.trackEvent('search_performed', {
      searchQuery: query,
      resultsCount,
    });
  }

  static async trackPurchase(params: {
    transactionId: string;
    amount: number;
    currency: string;
    items: Array<{ itemId: string; itemName: string; price: number }>;
  }) {
    await analytics().logPurchase({
      transaction_id: params.transactionId,
      value: params.amount,
      currency: params.currency,
      items: params.items.map((item) => ({
        item_id: item.itemId,
        item_name: item.itemName,
        price: item.price,
      })),
    });
  }

  static async trackOnboardingStep(stepNumber: number, stepName: string) {
    await this.trackEvent('onboarding_step_completed', {
      stepNumber,
      stepName,
    });
  }

  // User properties (atributos del usuario, no eventos)
  static async setUserProperties(props: Partial<UserProperties>) {
    for (const [key, value] of Object.entries(props)) {
      await analytics().setUserProperty(key, value);
    }
  }

  static async identifyUser(userId: string) {
    await analytics().setUserId(userId);
  }
}

export default AnalyticsService;
```

```typescript
// Uso en componentes
function ProductScreen({ route }) {
  const { productId, productName } = route.params;

  useEffect(() => {
    AnalyticsService.trackScreen('ProductDetail');
    AnalyticsService.trackEvent('product_viewed', { productId, productName });
  }, []);

  const handleAddToCart = () => {
    AnalyticsService.trackEvent('item_added_to_cart', {
      productId,
      productName,
      price: product.price,
      currency: 'USD',
    });
    addToCart(product);
  };

  const handlePurchase = () => {
    AnalyticsService.trackPurchase({
      transactionId: generateTxId(),
      amount: total,
      currency: 'USD',
      items: cartItems,
    });
  };
}
```

#### Flutter

```dart
// lib/services/analytics_service.dart
import 'package:firebase_analytics/firebase_analytics.dart';

class AnalyticsService {
  static final _analytics = FirebaseAnalytics.instance;
  static final observer = FirebaseAnalyticsObserver(analytics: _analytics);

  // Screen tracking automatico con Navigator observer
  static FirebaseAnalyticsObserver get navigationObserver => observer;

  static Future<void> trackScreen(String screenName) async {
    await _analytics.logScreenView(screenName: screenName);
  }

  static Future<void> trackEvent(
    String name, {
    Map<String, Object>? parameters,
  }) async {
    assert(name.length <= 40, 'Event name must be <= 40 chars');
    await _analytics.logEvent(name: name, parameters: parameters);
  }

  static Future<void> trackButtonTap(String buttonId, String screenName) async {
    await trackEvent('button_tapped', parameters: {
      'buttonId': buttonId,
      'screenName': screenName,
    });
  }

  static Future<void> trackPurchase({
    required String transactionId,
    required double amount,
    required String currency,
    required List<AnalyticsEventItem> items,
  }) async {
    await _analytics.logPurchase(
      transactionId: transactionId,
      value: amount,
      currency: currency,
      items: items,
    );
  }

  static Future<void> trackOnboardingStep(int step, String stepName) async {
    await trackEvent('onboarding_step_completed', parameters: {
      'stepNumber': step,
      'stepName': stepName,
    });
  }

  static Future<void> identifyUser(String userId) async {
    await _analytics.setUserId(id: userId);
  }

  static Future<void> setUserProperty(String name, String value) async {
    await _analytics.setUserProperty(name: name, value: value);
  }
}
```

```dart
// Uso con Navigator observer automatico
MaterialApp(
  navigatorObservers: [AnalyticsService.navigationObserver],
  // ...
);
```

#### Swift (iOS nativo)

```swift
// AnalyticsService.swift
import FirebaseAnalytics

enum AnalyticsService {

    static func trackScreen(_ name: String) {
        Analytics.logEvent(AnalyticsEventScreenView, parameters: [
            AnalyticsParameterScreenName: name
        ])
    }

    static func trackEvent(_ name: String, parameters: [String: Any]? = nil) {
        guard name.count <= 40 else {
            assertionFailure("Event name too long: \(name)")
            return
        }
        Analytics.logEvent(name, parameters: parameters)
    }

    static func trackButtonTap(buttonId: String, screen: String) {
        trackEvent("button_tapped", parameters: [
            "buttonId": buttonId,
            "screenName": screen
        ])
    }

    static func trackPurchase(
        transactionId: String,
        amount: Double,
        currency: String,
        items: [[String: Any]]
    ) {
        Analytics.logEvent(AnalyticsEventPurchase, parameters: [
            AnalyticsParameterTransactionID: transactionId,
            AnalyticsParameterValue: amount,
            AnalyticsParameterCurrency: currency,
            AnalyticsParameterItems: items
        ])
    }

    static func identifyUser(_ userId: String) {
        Analytics.setUserID(userId)
    }

    static func setUserProperty(_ value: String, forName name: String) {
        Analytics.setUserProperty(value, forName: name)
    }
}
```

#### Kotlin (Android nativo)

```kotlin
// AnalyticsService.kt
import com.google.firebase.analytics.FirebaseAnalytics
import com.google.firebase.analytics.logEvent

object AnalyticsService {
    private lateinit var analytics: FirebaseAnalytics

    fun initialize(context: Context) {
        analytics = FirebaseAnalytics.getInstance(context)
    }

    fun trackScreen(screenName: String) {
        analytics.logEvent(FirebaseAnalytics.Event.SCREEN_VIEW) {
            param(FirebaseAnalytics.Param.SCREEN_NAME, screenName)
        }
    }

    fun trackEvent(name: String, params: Map<String, Any> = emptyMap()) {
        require(name.length <= 40) { "Event name must be <= 40 chars" }
        analytics.logEvent(name) {
            params.forEach { (key, value) ->
                when (value) {
                    is String -> param(key, value)
                    is Long -> param(key, value)
                    is Double -> param(key, value)
                    is Int -> param(key, value.toLong())
                    else -> param(key, value.toString())
                }
            }
        }
    }

    fun trackButtonTap(buttonId: String, screenName: String) {
        trackEvent("button_tapped", mapOf(
            "buttonId" to buttonId,
            "screenName" to screenName
        ))
    }

    fun trackPurchase(
        transactionId: String,
        amount: Double,
        currency: String,
        items: List<Bundle>
    ) {
        analytics.logEvent(FirebaseAnalytics.Event.PURCHASE) {
            param(FirebaseAnalytics.Param.TRANSACTION_ID, transactionId)
            param(FirebaseAnalytics.Param.VALUE, amount)
            param(FirebaseAnalytics.Param.CURRENCY, currency)
        }
    }

    fun identifyUser(userId: String) {
        analytics.setUserId(userId)
    }

    fun setUserProperty(name: String, value: String) {
        analytics.setUserProperty(name, value)
    }
}
```

### 2.3 Mixpanel (alternativa con funnels avanzados)

#### React Native

```bash
npm install mixpanel-react-native
```

```typescript
// src/services/mixpanel.ts
import { Mixpanel } from 'mixpanel-react-native';

const mixpanel = new Mixpanel('YOUR_PROJECT_TOKEN', true);

export async function initMixpanel() {
  await mixpanel.init();
}

export async function identify(userId: string, traits: Record<string, any>) {
  mixpanel.identify(userId);
  mixpanel.getPeople().set({
    $email: traits.email,
    $name: traits.name,
    plan: traits.plan,
    signupDate: traits.signupDate,
  });
}

export function track(event: string, properties?: Record<string, any>) {
  mixpanel.track(event, properties);
}

// Super properties (se envian con TODOS los eventos)
export function setSuperProperties(props: Record<string, any>) {
  mixpanel.registerSuperProperties(props);
}

// Ejemplo: tracking de e-commerce
export function trackAddToCart(item: {
  id: string;
  name: string;
  price: number;
  category: string;
}) {
  track('item_added_to_cart', {
    itemId: item.id,
    itemName: item.name,
    price: item.price,
    category: item.category,
  });
}

// Revenue tracking
export function trackRevenue(amount: number, productId: string) {
  mixpanel.getPeople().trackCharge(amount);
  track('purchase_completed', { amount, productId });
}
```

---

## 3. Funnels & Retention

### 3.1 Onboarding Funnel

Definir los pasos y medir la conversion entre cada uno.

```typescript
// src/analytics/funnels.ts

// Definir los pasos del onboarding como constantes
const ONBOARDING_STEPS = {
  WELCOME: { step: 1, name: 'welcome_screen' },
  PERMISSIONS: { step: 2, name: 'permissions_request' },
  PROFILE_SETUP: { step: 3, name: 'profile_setup' },
  INTERESTS: { step: 4, name: 'interests_selection' },
  FIRST_ACTION: { step: 5, name: 'first_action_completed' },
} as const;

export function trackOnboardingStep(
  step: (typeof ONBOARDING_STEPS)[keyof typeof ONBOARDING_STEPS]
) {
  AnalyticsService.trackEvent('onboarding_step_completed', {
    stepNumber: step.step,
    stepName: step.name,
    totalSteps: Object.keys(ONBOARDING_STEPS).length,
  });
}

export function trackOnboardingCompleted(durationMs: number) {
  AnalyticsService.trackEvent('onboarding_completed', {
    durationSeconds: Math.round(durationMs / 1000),
    totalSteps: Object.keys(ONBOARDING_STEPS).length,
  });
}

export function trackOnboardingAbandoned(lastStep: number, reason?: string) {
  AnalyticsService.trackEvent('onboarding_abandoned', {
    lastStepNumber: lastStep,
    reason: reason || 'unknown',
  });
}
```

### 3.2 Conversion Funnel (E-commerce)

```typescript
// src/analytics/conversion-funnel.ts

// Funnel de compra: browse -> view -> cart -> checkout -> purchase
const CONVERSION_EVENTS = [
  'product_list_viewed',   // Vio la lista
  'product_viewed',        // Vio un producto
  'item_added_to_cart',    // Agrego al carrito
  'checkout_started',      // Inicio checkout
  'payment_info_entered',  // Puso datos de pago
  'purchase_completed',    // Compro
] as const;

export function trackConversionStep(
  event: (typeof CONVERSION_EVENTS)[number],
  properties: Record<string, any>
) {
  AnalyticsService.trackEvent(event, {
    ...properties,
    funnelName: 'purchase',
    timestamp: Date.now(),
  });
}
```

### 3.3 Retention Cohorts

Configurar en la herramienta de analytics (Firebase/Mixpanel/Amplitude):

```
Retention Metrics:
  D1  (Day 1 retention):   > 40% target
  D7  (Day 7 retention):   > 20% target
  D14 (Day 14 retention):  > 15% target
  D30 (Day 30 retention):  > 10% target
  D90 (Day 90 retention):  > 5% target

DAU/MAU ratio (stickiness):
  > 20% = Good
  > 50% = Excellent (WhatsApp-level)

Churn Prediction Signals:
  - No abre la app en 3 dias consecutivos
  - Reduce frecuencia de uso > 50%
  - Desactiva notificaciones
  - Reduce session duration > 60%
  - No completa acciones clave (core action)
```

```typescript
// src/analytics/retention.ts

export function trackCoreAction(action: string) {
  // "Core action" = la accion principal que da valor al usuario
  // Ejemplos: enviar mensaje (chat), publicar foto (social), completar workout (fitness)
  AnalyticsService.trackEvent('core_action_completed', {
    actionType: action,
    daysSinceInstall: getDaysSinceInstall(),
    sessionNumber: getSessionNumber(),
  });
}

export function trackSessionStart() {
  AnalyticsService.trackEvent('session_started', {
    daysSinceInstall: getDaysSinceInstall(),
    sessionNumber: getSessionNumber(),
    daysSinceLastSession: getDaysSinceLastSession(),
  });
}
```

---

## 4. A/B Testing

### 4.1 Firebase Remote Config

#### React Native

```bash
npm install @react-native-firebase/remote-config
```

```typescript
// src/services/remote-config.ts
import remoteConfig from '@react-native-firebase/remote-config';

// Defaults (se usan si el servidor no responde)
const DEFAULTS = {
  onboarding_variant: 'control',
  show_premium_banner: false,
  checkout_button_color: '#007AFF',
  max_free_items: 5,
  feature_social_login: false,
};

export async function initRemoteConfig() {
  await remoteConfig().setDefaults(DEFAULTS);
  await remoteConfig().setConfigSettings({
    minimumFetchIntervalMillis: __DEV__ ? 0 : 3600000, // 1h en prod
  });
  await remoteConfig().fetchAndActivate();
}

// Obtener valores tipados
export function getString(key: string): string {
  return remoteConfig().getString(key);
}

export function getBoolean(key: string): boolean {
  return remoteConfig().getBoolean(key);
}

export function getNumber(key: string): number {
  return remoteConfig().getNumber(key);
}

// Helper para A/B test
export function getExperimentVariant(experimentName: string): string {
  const variant = getString(`experiment_${experimentName}`);
  // Trackear exposicion al experimento
  AnalyticsService.trackEvent('experiment_exposure', {
    experimentName,
    variant,
  });
  return variant;
}

// Ejemplo de uso en componente
function OnboardingScreen() {
  const variant = getExperimentVariant('onboarding_v2');

  switch (variant) {
    case 'short':
      return <ShortOnboarding />;      // 3 pasos
    case 'gamified':
      return <GamifiedOnboarding />;   // Con puntos y logros
    default:
      return <StandardOnboarding />;   // Control: 5 pasos
  }
}
```

#### Flutter

```dart
// lib/services/remote_config_service.dart
import 'package:firebase_remote_config/firebase_remote_config.dart';

class RemoteConfigService {
  static final _config = FirebaseRemoteConfig.instance;

  static Future<void> initialize() async {
    await _config.setDefaults(<String, dynamic>{
      'onboarding_variant': 'control',
      'show_premium_banner': false,
      'checkout_button_color': '#007AFF',
      'max_free_items': 5,
      'feature_social_login': false,
    });

    await _config.setConfigSettings(RemoteConfigSettings(
      fetchTimeout: const Duration(seconds: 10),
      minimumFetchInterval: kDebugMode
          ? Duration.zero
          : const Duration(hours: 1),
    ));

    await _config.fetchAndActivate();

    // Escuchar cambios en tiempo real
    _config.onConfigUpdated.listen((event) async {
      await _config.activate();
    });
  }

  static String getString(String key) => _config.getString(key);
  static bool getBool(String key) => _config.getBool(key);
  static int getInt(String key) => _config.getInt(key);
  static double getDouble(String key) => _config.getDouble(key);

  static String getExperimentVariant(String experimentName) {
    final variant = getString('experiment_$experimentName');
    AnalyticsService.trackEvent('experiment_exposure', parameters: {
      'experimentName': experimentName,
      'variant': variant,
    });
    return variant;
  }
}
```

#### Swift (iOS nativo)

```swift
// RemoteConfigService.swift
import FirebaseRemoteConfig

final class RemoteConfigService {
    static let shared = RemoteConfigService()
    private let config = RemoteConfig.remoteConfig()

    func initialize() async throws {
        let settings = RemoteConfigSettings()
        #if DEBUG
        settings.minimumFetchInterval = 0
        #else
        settings.minimumFetchInterval = 3600
        #endif
        config.configSettings = settings

        config.setDefaults([
            "onboarding_variant": NSString(string: "control"),
            "show_premium_banner": NSNumber(value: false),
            "max_free_items": NSNumber(value: 5),
        ])

        let status = try await config.fetchAndActivate()
        print("Remote Config activated: \(status)")
    }

    func getString(_ key: String) -> String {
        config.configValue(forKey: key).stringValue ?? ""
    }

    func getBool(_ key: String) -> Bool {
        config.configValue(forKey: key).boolValue
    }

    func getExperimentVariant(_ experimentName: String) -> String {
        let variant = getString("experiment_\(experimentName)")
        AnalyticsService.trackEvent("experiment_exposure", parameters: [
            "experimentName": experimentName,
            "variant": variant
        ])
        return variant
    }
}
```

#### Kotlin (Android nativo)

```kotlin
// RemoteConfigService.kt
import com.google.firebase.remoteconfig.FirebaseRemoteConfig
import com.google.firebase.remoteconfig.remoteConfigSettings

object RemoteConfigService {
    private val config = FirebaseRemoteConfig.getInstance()

    suspend fun initialize() {
        val settings = remoteConfigSettings {
            minimumFetchIntervalInSeconds = if (BuildConfig.DEBUG) 0 else 3600
        }
        config.setConfigSettingsAsync(settings).await()

        config.setDefaultsAsync(mapOf(
            "onboarding_variant" to "control",
            "show_premium_banner" to false,
            "max_free_items" to 5L,
        )).await()

        config.fetchAndActivate().await()
    }

    fun getString(key: String): String = config.getString(key)
    fun getBoolean(key: String): Boolean = config.getBoolean(key)
    fun getLong(key: String): Long = config.getLong(key)

    fun getExperimentVariant(experimentName: String): String {
        val variant = getString("experiment_$experimentName")
        AnalyticsService.trackEvent("experiment_exposure", mapOf(
            "experimentName" to experimentName,
            "variant" to variant
        ))
        return variant
    }
}
```

### 4.2 Statsig (alternativa con estadisticas integradas)

```typescript
// React Native con Statsig
import Statsig from 'statsig-react-native';

await Statsig.initialize('client-KEY', {
  userID: user.id,
  email: user.email,
  custom: { plan: user.plan },
});

// Feature gate (boolean)
if (Statsig.checkGate('new_checkout_flow')) {
  return <NewCheckout />;
}

// Experiment (variantes)
const experiment = Statsig.getExperiment('pricing_page');
const variant = experiment.get('variant', 'control');
const headline = experiment.get('headline', 'Choose your plan');

// Dynamic config
const config = Statsig.getConfig('app_settings');
const maxRetries = config.get('maxRetries', 3);
```

### 4.3 Diseno de Experimentos

```
Antes de lanzar un A/B test, definir:

1. HIPOTESIS
   "Si cambiamos [X], entonces [Y] mejorara porque [Z]"
   Ejemplo: "Si reducimos el onboarding de 5 a 3 pasos,
             completion rate aumentara porque hay menos friccion"

2. VARIANTES
   - Control (A): Onboarding actual (5 pasos)
   - Treatment (B): Onboarding corto (3 pasos)
   - (Opcional) Treatment (C): Onboarding gamificado

3. METRICA DE EXITO (primary metric)
   - Onboarding completion rate
   - Secondary: D7 retention, time to first value

4. TAMANO DE MUESTRA
   - Usar calculadora de poder estadistico
   - Minimo: detectar 5% lift con 95% confidence, 80% power
   - Tipico: 1,000-10,000 users por variante

5. DURACION
   - Minimo 1 semana (capturar ciclo semanal)
   - Idealmente 2-4 semanas
   - No cortar antes aunque veas resultados

6. ROLLOUT STRATEGY
   1% -> verificar instrumentacion correcta (1 dia)
   10% -> detectar bugs y crashes (3 dias)
   50% -> recoger datos estadisticamente significativos (1-2 semanas)
   100% -> rollout a todos si gana treatment
```

---

## 5. OTA Updates

### 5.1 Cuando OTA vs Store Update

```
OTA (Over-The-Air) Update:
  PUEDE actualizar:
    - Codigo JavaScript / TypeScript (React Native)
    - Codigo Dart (Flutter con Shorebird)
    - Assets (imagenes, fuentes, traducciones)
    - Configuracion

  NO PUEDE actualizar:
    - Codigo nativo (Swift, Kotlin, Objective-C, Java)
    - Dependencias nativas nuevas (nuevos pods/gradle)
    - Permisos del app
    - Target SDK version
    - App icon, splash screen

Regla simple:
  Solo JS/Dart cambiaron -> OTA
  Cualquier cambio nativo -> Store update
```

### 5.2 EAS Update (Expo / React Native)

```bash
# Instalacion
npx expo install expo-updates

# Configuracion en app.json
{
  "expo": {
    "updates": {
      "url": "https://u.expo.dev/your-project-id",
      "fallbackToCacheTimeout": 30000
    },
    "runtimeVersion": {
      "policy": "appVersion"
    }
  }
}

# Publicar update
eas update --branch production --message "Fix: checkout crash on empty cart"

# Publicar a un canal especifico (para A/B testing con updates)
eas update --branch staging --message "Test: new checkout flow"
```

```typescript
// src/services/ota-updates.ts
import * as Updates from 'expo-updates';

export async function checkForUpdates() {
  if (__DEV__) return; // No verificar en desarrollo

  try {
    const update = await Updates.checkForUpdateAsync();

    if (update.isAvailable) {
      // Descargar en background
      const result = await Updates.fetchUpdateAsync();

      if (result.isNew) {
        // Estrategia: aplicar en proximo restart
        // O forzar reload para fixes criticos
        Alert.alert(
          'Update Available',
          'A new version is ready. Restart to apply?',
          [
            { text: 'Later', style: 'cancel' },
            {
              text: 'Restart',
              onPress: () => Updates.reloadAsync(),
            },
          ]
        );
      }
    }
  } catch (error) {
    // Silently fail - el usuario puede seguir usando la version actual
    CrashReporter.recordNonFatalError(error as Error, {
      context: 'ota_update_check',
    });
  }
}

// Verificar al iniciar la app y cada 30 minutos
export function setupUpdateChecker() {
  checkForUpdates(); // Al inicio
  setInterval(checkForUpdates, 30 * 60 * 1000); // Cada 30 min
}
```

### 5.3 CodePush (React Native con App Center)

```bash
npm install react-native-code-push
npx react-native link react-native-code-push
```

```typescript
// App.tsx con CodePush
import codePush from 'react-native-code-push';

const codePushOptions = {
  checkFrequency: codePush.CheckFrequency.ON_APP_RESUME,
  installMode: codePush.InstallMode.ON_NEXT_RESTART,
  mandatoryInstallMode: codePush.InstallMode.IMMEDIATE,
  minimumBackgroundDuration: 60 * 10, // 10 minutos en background
};

function App() {
  const [updateProgress, setUpdateProgress] = useState<number | null>(null);

  useEffect(() => {
    codePush.sync(
      {
        installMode: codePush.InstallMode.ON_NEXT_RESTART,
        mandatoryInstallMode: codePush.InstallMode.IMMEDIATE,
      },
      (status) => {
        switch (status) {
          case codePush.SyncStatus.DOWNLOADING_PACKAGE:
            console.log('Downloading update...');
            break;
          case codePush.SyncStatus.INSTALLING_UPDATE:
            console.log('Installing update...');
            break;
          case codePush.SyncStatus.UPDATE_INSTALLED:
            console.log('Update installed, will apply on next restart');
            break;
        }
      },
      (progress) => {
        setUpdateProgress(
          Math.round((progress.receivedBytes / progress.totalBytes) * 100)
        );
      }
    );
  }, []);

  return <NavigationContainer>...</NavigationContainer>;
}

export default codePush(codePushOptions)(App);
```

```bash
# Publicar update via CLI
# Staging
appcenter codepush release-react -a Owner/MyApp-iOS -d Staging
appcenter codepush release-react -a Owner/MyApp-Android -d Staging

# Production
appcenter codepush release-react -a Owner/MyApp-iOS -d Production
appcenter codepush release-react -a Owner/MyApp-Android -d Production

# Rollback
appcenter codepush rollback -a Owner/MyApp-iOS Production
```

### 5.4 Shorebird (Flutter OTA)

```bash
# Instalar Shorebird CLI
curl --proto '=https' --tlsv1.2 https://raw.githubusercontent.com/shorebirdtech/install/main/install.sh -sSf | bash

# Inicializar en proyecto Flutter
shorebird init

# Crear release (primera vez)
shorebird release android
shorebird release ios

# Publicar patch (OTA update)
shorebird patch android --release-version 1.0.0
shorebird patch ios --release-version 1.0.0
```

```dart
// lib/services/ota_service.dart (Shorebird no requiere codigo adicional)
// Shorebird parchea el engine de Dart automaticamente.
// El update se aplica en el siguiente cold start.

// Para updates manuales o forzados, se puede complementar con package_info:
import 'package:package_info_plus/package_info_plus.dart';

class OtaService {
  static Future<void> logCurrentVersion() async {
    final info = await PackageInfo.fromPlatform();
    debugPrint('App version: ${info.version}+${info.buildNumber}');
    // Shorebird patch number se refleja en el build number
  }
}
```

### 5.5 Rollback Strategy

```
Pre-launch:
  1. Verificar update en canal staging con equipo interno
  2. Medir crash-free rate en staging
  3. Si crash-free > 99.5% -> promover a production

Rollout:
  1. Publicar update a 1% de usuarios
  2. Monitorear 1 hora: crashes, ANRs, errores
  3. Si OK -> 10% (monitorear 4 horas)
  4. Si OK -> 50% (monitorear 24 horas)
  5. Si OK -> 100%

Rollback triggers (automatico si es posible):
  - Crash-free rate < 99%
  - ANR rate > 1%
  - Error rate > 5x baseline
  - User complaints spike

Rollback procedure:
  EAS Update:  eas update --branch production --message "Rollback to v1.2.3"
  CodePush:    appcenter codepush rollback -a Owner/App Production
  Shorebird:   shorebird patch android --release-version 1.0.0 (con codigo anterior)
```

---

## 6. Feature Flags

### 6.1 LaunchDarkly

#### React Native

```bash
npm install launchdarkly-react-native-client-sdk
```

```typescript
// src/services/feature-flags.ts
import LDClient, {
  LDConfig,
  LDContext,
} from 'launchdarkly-react-native-client-sdk';

let ldClient: LDClient;

export async function initFeatureFlags(user: {
  id: string;
  email: string;
  plan: string;
}) {
  const config: LDConfig = {
    mobileKey: 'mob-xxx',
    debugMode: __DEV__,
  };

  const context: LDContext = {
    kind: 'user',
    key: user.id,
    email: user.email,
    custom: {
      plan: user.plan,
    },
  };

  ldClient = new LDClient();
  await ldClient.configure(config, context);
}

// Boolean flag
export async function isFeatureEnabled(flagKey: string): Promise<boolean> {
  return ldClient.boolVariation(flagKey, false);
}

// Multivariate flag
export async function getVariant(
  flagKey: string,
  defaultValue: string
): Promise<string> {
  return ldClient.stringVariation(flagKey, defaultValue);
}

// JSON flag (configuracion compleja)
export async function getConfig(
  flagKey: string,
  defaultValue: Record<string, any>
): Promise<Record<string, any>> {
  return ldClient.jsonVariation(flagKey, defaultValue);
}

// Listener para cambios en tiempo real
export function onFlagChange(
  flagKey: string,
  callback: (value: any) => void
) {
  ldClient.registerFeatureFlagListener(flagKey, callback);
  return () => ldClient.unregisterFeatureFlagListener(flagKey, callback);
}
```

```typescript
// Uso en componente con hook
function useFeatureFlag(flagKey: string, defaultValue: boolean = false) {
  const [enabled, setEnabled] = useState(defaultValue);

  useEffect(() => {
    isFeatureEnabled(flagKey).then(setEnabled);
    const unsubscribe = onFlagChange(flagKey, setEnabled);
    return unsubscribe;
  }, [flagKey]);

  return enabled;
}

function MyScreen() {
  const showNewFeature = useFeatureFlag('new_checkout_v2');

  return showNewFeature ? <NewCheckout /> : <OldCheckout />;
}
```

### 6.2 Unleash (open source)

```typescript
// React Native con Unleash
import { UnleashClient } from 'unleash-proxy-client';

const unleash = new UnleashClient({
  url: 'https://unleash.example.com/api/frontend',
  clientKey: 'proxy-client-key',
  appName: 'my-mobile-app',
  refreshInterval: 30, // seconds
});

await unleash.start();

// Verificar flag
const isEnabled = unleash.isEnabled('new_feature');

// Con variante
const variant = unleash.getVariant('checkout_experiment');
if (variant.name === 'new_flow') {
  // Mostrar nuevo flujo
}

// Context para targeting
unleash.updateContext({
  userId: user.id,
  properties: {
    plan: user.plan,
    country: user.country,
  },
});
```

### 6.3 Flag Types

```
1. BOOLEAN (Kill Switch)
   Uso: Activar/desactivar una feature completa
   Ejemplo: maintenance_mode, feature_chat, enable_payments

2. MULTIVARIATE (String)
   Uso: Multiples variantes de una feature
   Ejemplo: checkout_flow = "classic" | "one_page" | "express"

3. PERCENTAGE ROLLOUT
   Uso: Gradual rollout a porcentaje de usuarios
   Ejemplo: new_home_screen: 0% -> 5% -> 25% -> 50% -> 100%

4. USER TARGETING
   Uso: Activar para usuarios especificos (beta testers, premium)
   Ejemplo: debug_menu: solo para emails @company.com

5. JSON CONFIG
   Uso: Configuracion compleja remotamente
   Ejemplo: rate_limits: { "free": 10, "premium": 100, "enterprise": 1000 }
```

### 6.4 Kill Switch Pattern

```typescript
// src/services/kill-switch.ts

/**
 * Kill Switch: desactivar una feature inmediatamente sin deploy.
 *
 * Uso: cuando una feature en produccion causa problemas,
 * cambiar el flag en el dashboard para desactivarla al instante.
 */
export function withKillSwitch<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  flagKey: string,
  FallbackComponent?: React.ComponentType<P>
) {
  return function KillSwitchWrapper(props: P) {
    const isEnabled = useFeatureFlag(flagKey, true); // default: enabled

    if (!isEnabled) {
      if (FallbackComponent) {
        return <FallbackComponent {...props} />;
      }
      return null; // O un mensaje de "feature no disponible"
    }

    return <WrappedComponent {...props} />;
  };
}

// Uso
const ChatScreen = withKillSwitch(
  ChatScreenImpl,
  'feature_chat',
  ChatMaintenanceScreen
);
```

### 6.5 Flag Lifecycle

```
1. CREATE
   - Definir flag con nombre descriptivo
   - Documentar proposito y owner
   - Establecer default value (siempre off para features nuevas)

2. TEST
   - Activar en ambiente de staging
   - Verificar con equipo interno
   - Validar que el fallback funciona correctamente

3. ROLLOUT
   - 1% -> 10% -> 50% -> 100% (con monitoreo entre cada paso)
   - Verificar metricas clave en cada incremento

4. PERMANENT
   - Feature estable y validada
   - Marcar flag como "permanent"
   - Remover el flag del codigo (cleanup)

5. CLEANUP (critico, no saltar)
   - Eliminar flag del dashboard
   - Eliminar condicionales del codigo
   - Eliminar FallbackComponent si existe
   - Deuda tecnica: cada flag activo es complejidad

Regla: revisar flags cada sprint. Eliminar los que tienen > 30 dias en 100%.
```

---

## 7. Error Boundaries & Graceful Degradation

### 7.1 React Native ErrorBoundary

```typescript
// src/components/ErrorBoundary.tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import crashlytics from '@react-native-firebase/crashlytics';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  level?: 'screen' | 'section' | 'widget';
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Reportar a Crashlytics
    crashlytics().log(`ErrorBoundary caught (${this.props.level || 'unknown'})`);
    crashlytics().recordError(error);

    // Analytics
    AnalyticsService.trackEvent('error_boundary_triggered', {
      errorMessage: error.message,
      componentStack: errorInfo.componentStack?.substring(0, 500) || '',
      level: this.props.level || 'unknown',
    });

    this.props.onError?.(error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <View style={styles.container}>
          <Text style={styles.title}>Something went wrong</Text>
          <Text style={styles.message}>
            {this.props.level === 'widget'
              ? 'This section could not load.'
              : 'An unexpected error occurred.'}
          </Text>
          <TouchableOpacity style={styles.button} onPress={this.handleRetry}>
            <Text style={styles.buttonText}>Try Again</Text>
          </TouchableOpacity>
        </View>
      );
    }

    return this.props.children;
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
  },
  message: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 24,
  },
  button: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  buttonText: {
    color: '#FFF',
    fontWeight: '600',
  },
});

export default ErrorBoundary;
```

```typescript
// Uso a multiples niveles
function App() {
  return (
    <ErrorBoundary level="screen">
      <NavigationContainer>
        <HomeScreen />
      </NavigationContainer>
    </ErrorBoundary>
  );
}

function HomeScreen() {
  return (
    <ScrollView>
      <ErrorBoundary level="section" fallback={<BannerPlaceholder />}>
        <PromoBanner />
      </ErrorBoundary>

      <ErrorBoundary level="section">
        <ProductList />
      </ErrorBoundary>

      <ErrorBoundary level="widget" fallback={null}>
        <RecommendationsCarousel />
      </ErrorBoundary>
    </ScrollView>
  );
}
```

### 7.2 Flutter Error Handling

```dart
// lib/core/error_handling.dart
import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:firebase_crashlytics/firebase_crashlytics.dart';

class AppErrorHandler {
  static void initialize() {
    // Errores sincronos de Flutter (widgets, rendering)
    FlutterError.onError = (FlutterErrorDetails details) {
      FlutterError.presentError(details); // Mostrar en consola
      FirebaseCrashlytics.instance.recordFlutterFatalError(details);
    };

    // Errores asincronos de la plataforma
    PlatformDispatcher.instance.onError = (error, stack) {
      FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
      return true;
    };
  }

  /// Wrap runApp con zona de errores
  static void runGuarded(Widget app) {
    runZonedGuarded(() {
      WidgetsFlutterBinding.ensureInitialized();
      initialize();
      runApp(app);
    }, (error, stack) {
      FirebaseCrashlytics.instance.recordError(error, stack);
    });
  }
}

/// Widget ErrorBoundary para Flutter
class ErrorBoundary extends StatefulWidget {
  final Widget child;
  final Widget Function(FlutterErrorDetails)? errorBuilder;

  const ErrorBoundary({
    super.key,
    required this.child,
    this.errorBuilder,
  });

  @override
  State<ErrorBoundary> createState() => _ErrorBoundaryState();
}

class _ErrorBoundaryState extends State<ErrorBoundary> {
  FlutterErrorDetails? _error;

  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    if (_error != null) {
      return widget.errorBuilder?.call(_error!) ?? _defaultErrorWidget();
    }

    return widget.child;
  }

  Widget _defaultErrorWidget() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.error_outline, size: 48, color: Colors.red),
          const SizedBox(height: 16),
          const Text('Something went wrong'),
          const SizedBox(height: 8),
          ElevatedButton(
            onPressed: () => setState(() => _error = null),
            child: const Text('Try Again'),
          ),
        ],
      ),
    );
  }
}
```

```dart
// Uso
void main() {
  AppErrorHandler.runGuarded(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // Definir error widget global
    ErrorWidget.builder = (FlutterErrorDetails details) {
      return const Center(
        child: Text('An error occurred in this section.'),
      );
    };

    return MaterialApp(
      builder: (context, child) {
        return ErrorBoundary(child: child ?? const SizedBox.shrink());
      },
      home: const HomeScreen(),
    );
  }
}
```

### 7.3 Offline Mode Detection

```typescript
// src/hooks/useNetworkStatus.ts (React Native)
import NetInfo, { NetInfoState } from '@react-native-community/netinfo';
import { useEffect, useState } from 'react';

interface NetworkStatus {
  isConnected: boolean;
  isInternetReachable: boolean | null;
  connectionType: string;
}

export function useNetworkStatus(): NetworkStatus {
  const [status, setStatus] = useState<NetworkStatus>({
    isConnected: true,
    isInternetReachable: true,
    connectionType: 'unknown',
  });

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener((state: NetInfoState) => {
      setStatus({
        isConnected: state.isConnected ?? false,
        isInternetReachable: state.isInternetReachable,
        connectionType: state.type,
      });

      if (!state.isConnected) {
        AnalyticsService.trackEvent('connectivity_lost', {
          lastConnectionType: state.type,
        });
      }
    });

    return () => unsubscribe();
  }, []);

  return status;
}

// Offline banner component
function OfflineBanner() {
  const { isConnected } = useNetworkStatus();

  if (isConnected) return null;

  return (
    <View style={styles.offlineBanner}>
      <Text style={styles.offlineText}>
        No internet connection. Some features may be unavailable.
      </Text>
    </View>
  );
}
```

```dart
// Flutter offline detection
// lib/core/connectivity_service.dart
import 'package:connectivity_plus/connectivity_plus.dart';

class ConnectivityService {
  static final _connectivity = Connectivity();

  static Stream<bool> get onConnectivityChanged {
    return _connectivity.onConnectivityChanged.map((results) {
      final isConnected = results.isNotEmpty &&
          !results.contains(ConnectivityResult.none);
      if (!isConnected) {
        AnalyticsService.trackEvent('connectivity_lost');
      }
      return isConnected;
    });
  }

  static Future<bool> get isConnected async {
    final results = await _connectivity.checkConnectivity();
    return results.isNotEmpty &&
        !results.contains(ConnectivityResult.none);
  }
}
```

### 7.4 Retry Pattern

```typescript
// src/utils/retry.ts

interface RetryOptions {
  maxAttempts: number;
  baseDelay: number;        // ms
  maxDelay: number;          // ms
  backoffMultiplier: number;
  retryableErrors?: string[];
}

const DEFAULT_OPTIONS: RetryOptions = {
  maxAttempts: 3,
  baseDelay: 1000,
  maxDelay: 10000,
  backoffMultiplier: 2,
};

export async function withRetry<T>(
  fn: () => Promise<T>,
  options: Partial<RetryOptions> = {}
): Promise<T> {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  let lastError: Error;

  for (let attempt = 1; attempt <= opts.maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;

      // No reintentar errores no recuperables
      if (isNonRetryableError(error)) {
        throw error;
      }

      if (attempt < opts.maxAttempts) {
        const delay = Math.min(
          opts.baseDelay * Math.pow(opts.backoffMultiplier, attempt - 1),
          opts.maxDelay
        );
        // Jitter para evitar thundering herd
        const jitteredDelay = delay * (0.5 + Math.random() * 0.5);

        AnalyticsService.trackEvent('api_retry', {
          attempt: attempt.toString(),
          delay: Math.round(jitteredDelay).toString(),
          errorMessage: lastError.message,
        });

        await new Promise((resolve) => setTimeout(resolve, jitteredDelay));
      }
    }
  }

  AnalyticsService.trackEvent('api_retry_exhausted', {
    maxAttempts: opts.maxAttempts.toString(),
    errorMessage: lastError!.message,
  });

  throw lastError!;
}

function isNonRetryableError(error: any): boolean {
  // No reintentar errores de cliente (4xx excepto 429)
  if (error?.status >= 400 && error?.status < 500 && error?.status !== 429) {
    return true;
  }
  // No reintentar errores de autenticacion
  if (error?.status === 401 || error?.status === 403) {
    return true;
  }
  return false;
}

// Uso
const data = await withRetry(
  () => api.fetchProducts(),
  { maxAttempts: 3, baseDelay: 1000 }
);
```

---

## 8. Decision Tree: Que Analytics Stack Necesito

```
Tipo de app
|
+-- MVP / Side Project
|   Presupuesto: $0
|   Stack: Firebase Analytics + Crashlytics
|   Razon: Gratis, zero config, suficiente para validar
|   Setup time: 30 minutos
|
+-- Startup (Product-Led Growth)
|   Presupuesto: $0-500/mes
|   Stack: Mixpanel/Amplitude (free tier) + Crashlytics + Remote Config
|   Razon: Funnels avanzados, retention analysis, A/B testing
|   Setup time: 2-4 horas
|
+-- Scale-up (Product-Market Fit confirmado)
|   Presupuesto: $500-5000/mes
|   Stack: Amplitude + Sentry + LaunchDarkly + PostHog (session replay)
|   Razon: Feature flags, experimentation platform, crash management
|   Setup time: 1-2 dias
|
+-- Enterprise
|   Presupuesto: $5000+/mes
|   Stack: Amplitude/Mixpanel + Sentry + LaunchDarkly + custom pipeline
|   Razon: Compliance, data warehouse, custom dashboards, SLAs
|   Setup time: 1-2 semanas
|
+-- E-commerce App
|   Stack: Firebase + GA4 + enhanced e-commerce + Crashlytics
|   Razon: E-commerce funnels, revenue tracking, Google Ads integration
|   Eventos clave: product_viewed, item_added_to_cart, checkout_started,
|                  purchase_completed, refund_requested
|
+-- Gaming App
|   Stack: Firebase + custom telemetry + Remote Config (game balancing)
|   Razon: Session time, level progression, IAP tracking, balancing via RC
|   Eventos clave: level_started, level_completed, level_failed,
|                  iap_initiated, ad_watched, session_duration
|
+-- SaaS B2B App
|   Stack: Amplitude + Sentry + LaunchDarkly + Intercom
|   Razon: Feature adoption, user segmentation by company, support
|   Eventos clave: feature_used, workspace_created, invite_sent,
|                  subscription_upgraded, api_key_generated
```

### Tabla comparativa rapida

| Criterio | Firebase | Mixpanel | Amplitude | PostHog |
|----------|----------|----------|-----------|---------|
| Precio inicial | Gratis | Gratis (20M events) | Gratis (50K MTU) | Gratis (1M events) |
| Funnels | Basico | Avanzado | Avanzado | Avanzado |
| Retention | Basico | Avanzado | Avanzado | Avanzado |
| Session Replay | No | No | Session Replay addon | Si (incluido) |
| Self-hosted | No | No | No | Si |
| Real-time | No (24h delay) | Si | Si | Si |
| Mobile SDK | Excelente | Bueno | Bueno | Bueno |
| A/B Testing | Remote Config | Experiments addon | Experiment | Feature Flags |

---

## 9. Post-Launch Monitoring Checklist

### Dia 1 Post-Launch

```
[ ] Crash-free rate > 99%
[ ] No ANRs en Play Console Vitals (Android)
[ ] No crashes en App Store Connect Crashes (iOS)
[ ] Startup time < 2s (cold start)
[ ] Startup time < 1s (warm start)
[ ] Funnel de onboarding > 60% completion
[ ] Eventos de analytics llegando correctamente
[ ] Verificar no hay PII en los eventos
[ ] Revisar logs de Crashlytics/Sentry por errores nuevos
[ ] Feature flags respondiendo correctamente
[ ] Push notifications entregandose
[ ] Deep links funcionando
```

### Semana 1

```
[ ] Retention D1 > 40%
[ ] Rating promedio > 4.0 en stores
[ ] 0 crashes criticos (P0 = crash en core flow)
[ ] Crash-free rate > 99.5%
[ ] Feature flags validados con metricas
[ ] Primer OTA update exitoso (si aplica)
[ ] Session duration aceptable (benchmark: 3-5 min para utility apps)
[ ] Uninstall rate < 5%
[ ] Errores de red < 2% de requests
[ ] Revisar reviews en stores (responder si es necesario)
```

### Mes 1

```
[ ] Retention D7 > 20%
[ ] Retention D30 > 10%
[ ] Crash-free rate > 99.5%
[ ] First A/B test launched
[ ] DAU/MAU ratio establecido como baseline
[ ] Core action conversion medida y documentada
[ ] Performance baselines documentadas
[ ] Alertas configuradas para metricas criticas
[ ] Runbook de incidentes documentado
[ ] Revision de flags: limpiar los que ya no se usan
```

### Mes 3

```
[ ] Retention D30 estable o mejorando
[ ] Retention D90 > 5%
[ ] Al menos 3 A/B tests completados
[ ] Feature adoption medida para cada feature nueva
[ ] Crash-free rate > 99.8%
[ ] Performance optimizada basada en datos reales
[ ] Analytics dashboard compartido con equipo
[ ] Proceso de release estable (OTA + store)
```

---

## 10. Event Naming Convention (Referencia Rapida)

```
FORMAT: {object}_{action}

OBJETOS COMUNES:
  screen       ->  screen_viewed
  button       ->  button_tapped
  form         ->  form_submitted, form_abandoned
  search       ->  search_performed
  item         ->  item_viewed, item_added_to_cart, item_removed_from_cart
  purchase     ->  purchase_started, purchase_completed, purchase_failed
  notification ->  notification_received, notification_opened, notification_dismissed
  error        ->  error_occurred, error_boundary_triggered
  session      ->  session_started, session_ended
  profile      ->  profile_updated, profile_photo_changed
  onboarding   ->  onboarding_step_completed, onboarding_completed, onboarding_abandoned
  subscription ->  subscription_started, subscription_renewed, subscription_cancelled
  share        ->  share_initiated, share_completed
  deeplink     ->  deeplink_opened
  permission   ->  permission_requested, permission_granted, permission_denied
  review       ->  review_prompted, review_submitted, review_dismissed
  tab          ->  tab_switched
  filter       ->  filter_applied, filter_cleared

PROPIEDADES (camelCase):
  screenName       -> "HomeScreen", "ProductDetail"
  buttonId         -> "btn_checkout", "btn_share"
  formType         -> "login", "registration", "profile_edit"
  searchQuery      -> "blue shoes"
  itemId           -> "prod_123"
  itemName         -> "Blue Running Shoes"
  amount           -> 49.99
  currency         -> "USD"
  errorCode        -> "NETWORK_TIMEOUT"
  errorMessage     -> "Request timed out" (no PII)
  source           -> "push_notification", "deeplink", "organic"
  stepNumber       -> 1, 2, 3
  stepName         -> "welcome", "permissions", "profile"
  category         -> "electronics", "clothing"
  method           -> "google", "apple", "email"
  success          -> true, false
  durationMs       -> 1234

REGLAS:
  1. snake_case para nombres de eventos
  2. camelCase para nombres de propiedades
  3. Maximo 40 caracteres en nombre de evento
  4. No incluir PII (email, nombre, telefono) en eventos
  5. Usar propiedades para contexto, no el nombre del evento
  6. Prefijo consistente por dominio (onboarding_*, purchase_*, etc.)
  7. Documentar cada evento nuevo en un event dictionary compartido
```

---

## Integracion con Agentes NXT

| Agente | Responsabilidad en Analytics |
|--------|------------------------------|
| `nxt-mobile` | Implementar SDKs, error boundaries, OTA updates |
| `nxt-data` | Definir eventos, funnels, dashboards, data quality |
| `nxt-performance` | Monitorear startup time, render time, network latency |
| `nxt-qa` | Verificar que eventos se envian correctamente en tests |
| `nxt-cybersec` | Auditar que no se envie PII en analytics |
| `nxt-pm` | Definir metricas de exito, KPIs, experiment design |

---

*NXT AI Development Framework v3.8.0*
*"Construyendo el futuro, un sprint a la vez"*
