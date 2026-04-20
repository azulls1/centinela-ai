# SKILL Mobile Performance

> **Version:** 3.8.0
> **Trigger:** Optimizacion de rendimiento en apps moviles
> **Agente:** nxt-mobile, nxt-performance

## Metricas Clave

| Metrica | Objetivo | Herramienta |
|---------|----------|-------------|
| Cold Start | < 1s (iOS), < 1.5s (Android) | Xcode Instruments / Android Vitals |
| TTI (Time to Interactive) | < 2s | Flipper / DevTools |
| Frame Rate | 60 fps constante (0 jank) | Perf Monitor / GPU Profiler |
| Memory (idle) | < 150 MB | Instruments / Android Profiler |
| Memory (active) | < 300 MB | Instruments / Android Profiler |
| App Size (download) | < 50 MB ideal | App Store Connect / Play Console |
| Battery (1h uso) | < 5% drain | Battery Historian / Energy Log |
| ANR Rate | < 0.5% | Play Console Vitals |
| Crash Free Rate | > 99.5% | Firebase Crashlytics / Sentry |

## Startup Time Optimization

### React Native

```javascript
// 1. Lazy loading de pantallas (React Navigation)
const HomeScreen = React.lazy(() => import('./screens/HomeScreen'));
const ProfileScreen = React.lazy(() => import('./screens/ProfileScreen'));

// 2. Reducir imports en el entry point
// BAD: import everything at startup
// import { AnalyticsService, PushService, CacheService } from './services';

// GOOD: defer non-critical services
const initDeferredServices = () => {
  InteractionManager.runAfterInteractions(() => {
    require('./services/AnalyticsService').init();
    require('./services/PushService').register();
  });
};

// 3. Hermes engine (verificar que esta activo)
// android/app/build.gradle
// hermesEnabled = true

// 4. Precargar datos criticos
import { AppRegistry } from 'react-native';
AppRegistry.registerRunnable('prefetch', async () => {
  await AsyncStorage.multiGet(['user_token', 'user_profile', 'settings']);
});
```

### Flutter

```dart
// 1. Deferred loading de features
import 'package:my_app/heavy_feature.dart' deferred as heavy;

Future<void> loadFeature() async {
  await heavy.loadLibrary();
  heavy.showFeature();
}

// 2. Precache de imagenes criticas
@override
void didChangeDependencies() {
  super.didChangeDependencies();
  precacheImage(AssetImage('assets/logo.png'), context);
  precacheImage(AssetImage('assets/hero.png'), context);
}

// 3. Isolate para trabajo pesado
Future<List<Item>> parseItems(String json) async {
  return await compute(_parseItemsInBackground, json);
}

List<Item> _parseItemsInBackground(String json) {
  final data = jsonDecode(json) as List;
  return data.map((e) => Item.fromJson(e)).toList();
}
```

## Memory Profiling

### Deteccion de Leaks (React Native)

```javascript
// Patron comun de memory leak: subscripciones sin cleanup
useEffect(() => {
  const subscription = eventEmitter.addListener('update', handler);
  const interval = setInterval(pollData, 5000);

  // SIEMPRE limpiar en el return
  return () => {
    subscription.remove();
    clearInterval(interval);
  };
}, []);

// Leak comun: closures que retienen referencias
// BAD
const [data, setData] = useState([]);
const fetchData = async () => {
  const result = await api.get('/items'); // closure retiene component ref
  setData(result); // si componente se desmonto, leak
};

// GOOD - con cleanup para evitar memory leak
const isMountedRef = useRef(true);
useEffect(() => {
  return () => { isMountedRef.current = false; };
}, []);

const fetchData = async () => {
  const result = await api.get('/items');
  if (isMountedRef.current) {
    setData(result);  // Solo actualizar si componente sigue montado
  }
};
```

### Deteccion de Leaks (Flutter)

```dart
// Usar DevTools Memory tab para detectar leaks
// Patron comun: StreamController sin close
class MyBloc {
  final _controller = StreamController<State>.broadcast();
  Stream<State> get stream => _controller.stream;

  // SIEMPRE implementar dispose
  void dispose() {
    _controller.close();
  }
}

// En StatefulWidget
@override
void dispose() {
  _bloc.dispose();
  _scrollController.dispose();
  _animationController.dispose();
  _focusNode.dispose();
  super.dispose();
}
```

## 60 FPS Optimization

```javascript
// React Native - Evitar renders innecesarios
// 1. useMemo para listas grandes
const sortedItems = useMemo(
  () => items.sort((a, b) => a.name.localeCompare(b.name)),
  [items]
);

// 2. FlatList optimizada
<FlatList
  data={items}
  renderItem={renderItem}
  keyExtractor={item => item.id}
  getItemLayout={(data, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
  maxToRenderPerBatch={10}
  windowSize={5}
  removeClippedSubviews={true}
  initialNumToRender={10}
/>

// 3. Animaciones en el UI thread (Reanimated)
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from 'react-native-reanimated';

const offset = useSharedValue(0);
const animatedStyle = useAnimatedStyle(() => ({
  transform: [{ translateX: withSpring(offset.value) }],
}));
```

## Bundle Size Reduction

```bash
# React Native - Analizar bundle
npx react-native-bundle-visualizer

# React Native - Eliminar dependencias grandes
npx depcheck                           # Detectar dependencias no usadas

# Flutter - Analizar tamano
flutter build apk --analyze-size
flutter build ipa --analyze-size

# Android - Habilitar ProGuard/R8
# android/app/build.gradle
# minifyEnabled true
# shrinkResources true
```

### Estrategias de Reduccion

| Estrategia | Ahorro Tipico | Plataforma |
|------------|---------------|------------|
| Hermes engine | 30-50% RAM, 20% size | React Native |
| ProGuard/R8 | 20-40% APK size | Android |
| App Thinning + Bitcode | 30-50% download | iOS |
| Tree shaking | 10-30% | Flutter |
| Comprimir assets (WebP) | 40-70% imagenes | Ambas |
| Dynamic delivery / On-demand resources | Variable | Android / iOS |
| Eliminar console.log | 5-10% bundle JS | React Native |

## ANR Detection (Android)

```kotlin
// Detectar operaciones bloqueantes en main thread
// StrictMode en debug builds
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectDiskReads()
            .detectDiskWrites()
            .detectNetwork()
            .penaltyLog()
            .build()
    )
}

// Mover trabajo pesado fuera del main thread
viewModelScope.launch(Dispatchers.IO) {
    val data = repository.fetchLargeDataset()
    withContext(Dispatchers.Main) {
        _uiState.value = UiState.Success(data)
    }
}
```

## Decision Tree: Diagnosticar Problemas de Performance

```
La app va lenta
|
+-- Startup lento (> 2s)
|   +-- Medir cold start con profiler
|   +-- Demasiados imports al inicio --> Lazy loading
|   +-- Splash screen tapa el problema --> Medir TTI real
|   +-- SDK de terceros bloquean --> Inicializar en background
|   +-- React Native sin Hermes --> Activar Hermes
|
+-- UI jank / frames dropped
|   +-- Listas largas sin virtualizar --> FlatList/ListView.builder
|   +-- Re-renders innecesarios --> React.memo/useMemo/const widgets
|   +-- Animaciones en JS thread --> Reanimated/rive/Lottie nativo
|   +-- Imagenes grandes sin cache --> FastImage/cached_network_image
|   +-- Layout complejo --> Simplificar arbol de widgets
|
+-- Alto consumo de memoria
|   +-- Leaks (crece sin parar) --> Profiler + buscar subscripciones sin cleanup
|   +-- Imagenes en memoria --> Resize antes de mostrar, cache con limites
|   +-- Cache sin limites --> Implementar eviction policy (LRU)
|   +-- WebViews acumulados --> Destruir al salir de pantalla
|
+-- Bateria se drena rapido
|   +-- Polling frecuente --> WebSocket o push notifications
|   +-- GPS siempre activo --> Reducir precision/frecuencia
|   +-- Wakelock innecesario --> Liberar cuando no se necesita
|   +-- Background tasks excesivos --> WorkManager/BGTaskScheduler
|
+-- App size muy grande (> 100MB)
|   +-- Assets sin comprimir --> WebP, AVIF, vector cuando posible
|   +-- Dependencias innecesarias --> Auditar con depcheck
|   +-- Sin code splitting --> Dynamic imports / deferred loading
|   +-- Arquitecturas incluidas --> ABI splits (Android), App Thinning (iOS)
|
+-- Crashes / ANR
|   +-- ANR en Android --> StrictMode + mover I/O fuera de main thread
|   +-- OOM Crash --> Reducir memoria, liberar resources en onLowMemory
|   +-- Null pointer --> Null safety + defensive coding
```

## Comandos de Profiling

```bash
# React Native
npx react-devtools                     # Component profiler
npx react-native info                  # Verificar Hermes activo
adb shell dumpsys meminfo com.myapp    # Memoria Android

# Flutter
flutter run --profile                  # Modo profile
flutter analyze                        # Analisis estatico
flutter test --coverage                # Coverage

# Android
adb shell dumpsys gfxinfo com.myapp    # Frame stats
adb shell dumpsys batterystats         # Battery stats
adb bugreport > bugreport.zip          # Reporte completo

# iOS
xcrun instruments -t "Time Profiler" -D output.trace MyApp.app
# O usar Xcode > Product > Profile (Instruments)

# General
npx react-native-bundle-visualizer    # Bundle size (RN)
maestro test --format junit            # Medir tiempos E2E
```
