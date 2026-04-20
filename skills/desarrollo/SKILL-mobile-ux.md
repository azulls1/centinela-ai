# SKILL Mobile UX

> **Version:** 3.8.0
> **Trigger:** Diseno e implementacion de patrones UX/UI nativos en aplicaciones moviles
> **Agente:** nxt-mobile, nxt-design, nxt-accessibility

---

## 1. Platform Design Guidelines

### iOS Human Interface Guidelines (HIG)

#### Navigation

| Patron | Uso | Componente |
|--------|-----|------------|
| Navigation Stack | Drill-down jerarquico | `UINavigationController` |
| Tab Bar | Secciones principales (3-5 tabs) | `UITabBarController` |
| Modal Sheet | Subtareas, formularios | `.sheet()` / `UISheetPresentationController` |
| Page Sheet (detent) | Contenido parcial (iOS 15+) | `.medium()` / `.large()` detents |

```
REGLA: Tab bar SIEMPRE visible en las pantallas principales.
       Modal sheets para flujos que el usuario puede cancelar.
       Navigation stack para profundizar en contenido.
```

#### Controls

```
NUNCA reimplementar controles del sistema cuando existen nativos:

iOS Control Nativo              Cuando Usar
─────────────────────────────── ─────────────────────────────────
UISwitch / Toggle               Activar/desactivar configuracion
UISlider                        Ajustar valor en rango continuo
UIDatePicker                    Seleccion de fecha/hora
UIPickerView                    Seleccion de lista corta
UISegmentedControl              Filtros con 2-5 opciones
UIActivityViewController        Compartir contenido
UISearchController               Busqueda con resultados
```

#### Typography (SF Pro + Dynamic Type)

| Text Style | Default Size | Uso |
|------------|-------------|-----|
| `.largeTitle` | 34pt | Titulos de pantalla |
| `.title1` | 28pt | Secciones principales |
| `.title2` | 22pt | Subsecciones |
| `.title3` | 20pt | Grupos de contenido |
| `.headline` | 17pt semibold | Etiquetas importantes |
| `.body` | 17pt | Contenido general |
| `.callout` | 16pt | Textos secundarios |
| `.subheadline` | 15pt | Metadatos |
| `.footnote` | 13pt | Notas, pies |
| `.caption1` | 12pt | Timestamps |
| `.caption2` | 11pt | Labels auxiliares |

```
REGLA CRITICA: SIEMPRE usar text styles del sistema, NUNCA font sizes fijos.
Dynamic Type permite al usuario escalar el texto (accesibilidad).
```

#### Safe Areas & Layout

```
┌──────────────────────────────────────────┐
│            Status Bar (44pt)             │  <- Safe Area Top
├──────────────────────────────────────────┤
│            Navigation Bar (44pt)         │
├──────────────────────────────────────────┤
│                                          │
│                                          │
│           Content Area                   │  <- Safe Area Insets
│           (respeta leading/trailing)     │
│                                          │
│                                          │
├──────────────────────────────────────────┤
│            Tab Bar (49pt)                │
├──────────────────────────────────────────┤
│            Home Indicator (34pt)         │  <- Safe Area Bottom
└──────────────────────────────────────────┘

Notch/Dynamic Island: NUNCA colocar contenido interactivo en esas zonas.
Home Indicator: NUNCA poner botones cerca del borde inferior.
```

#### Dark Mode

```
iOS Dark Mode - Colores del sistema que se adaptan automaticamente:

Semantic Color        Light           Dark
───────────────────── ─────────────── ───────────────
.systemBackground     #FFFFFF         #000000
.secondaryBackground  #F2F2F7         #1C1C1E
.tertiaryBackground   #FFFFFF         #2C2C2E
.label                #000000         #FFFFFF
.secondaryLabel       #3C3C43 60%     #EBEBF5 60%
.separator            #3C3C43 29%     #545458 60%

REGLA: Usar colores semanticos del sistema. NUNCA hardcodear #FFFFFF o #000000.
```

---

### Material Design 3 (Android)

#### Navigation

| Patron | Uso | Componente |
|--------|-----|------------|
| Top App Bar | Titulo + acciones | `TopAppBar` (Small/Medium/Large) |
| Bottom Navigation | 3-5 destinos principales | `NavigationBar` |
| Navigation Rail | Tablets, pantallas anchas | `NavigationRail` |
| Navigation Drawer | > 5 destinos o poco frecuentes | `ModalNavigationDrawer` |
| Bottom Sheet | Contenido secundario | `ModalBottomSheet` |

#### Components

```
Material 3 Component          Cuando Usar
───────────────────────────── ───────────────────────────────────
FAB (Floating Action Button)  1 accion primaria por pantalla
Extended FAB                  Accion primaria con label descriptivo
Chips (Filter/Input/Assist)   Tags, filtros, sugerencias
Cards (Elevated/Filled/Outlined) Agrupar contenido relacionado
Bottom Sheet                  Opciones contextuales
Snackbar                      Feedback no critico (con accion opcional)
Dialog                        Confirmaciones criticas solamente
```

#### Typography (Roboto + Material Type Scale)

| Role | Size/Weight | Uso |
|------|------------|-----|
| Display Large | 57sp / Regular | Hero text (raro en mobile) |
| Display Medium | 45sp / Regular | Titulos destacados |
| Display Small | 36sp / Regular | Titulos grandes |
| Headline Large | 32sp / Regular | Titulos de pantalla |
| Headline Medium | 28sp / Regular | Secciones |
| Headline Small | 24sp / Regular | Subsecciones |
| Title Large | 22sp / Regular | Top app bar |
| Title Medium | 16sp / Medium | Cards, dialogs |
| Title Small | 14sp / Medium | Subtitulos |
| Body Large | 16sp / Regular | Contenido principal |
| Body Medium | 14sp / Regular | Contenido secundario |
| Body Small | 12sp / Regular | Metadatos |
| Label Large | 14sp / Medium | Botones, tabs |
| Label Medium | 12sp / Medium | Navigation labels |
| Label Small | 11sp / Medium | Badges, hints |

#### Edge-to-Edge & System Bars

```
Android 15+: Edge-to-edge es OBLIGATORIO.
La app dibuja detras de las barras del sistema.

┌──────────────────────────────────────────┐
│       Status Bar (transparente)          │  <- Contenido detras
├──────────────────────────────────────────┤
│       Top App Bar                        │
├──────────────────────────────────────────┤
│                                          │
│       Content Area                       │
│       (WindowInsets.systemBars padding)  │
│                                          │
├──────────────────────────────────────────┤
│       Bottom Navigation                  │
├──────────────────────────────────────────┤
│       Navigation Bar (transparente)      │  <- Contenido detras
└──────────────────────────────────────────┘

REGLA: Usar WindowInsets API para respetar las barras del sistema.
       NUNCA asumir alturas fijas para status bar o navigation bar.
```

#### Dynamic Color (Material You)

```
Android 12+: Los colores se generan a partir del wallpaper del usuario.

Esquema generado automaticamente:
- Primary / OnPrimary / PrimaryContainer / OnPrimaryContainer
- Secondary / OnSecondary / SecondaryContainer / OnSecondaryContainer
- Tertiary / OnTertiary / TertiaryContainer / OnTertiaryContainer
- Surface / OnSurface / SurfaceVariant / OnSurfaceVariant
- Error / OnError / ErrorContainer / OnErrorContainer

REGLA: Usar Material color roles, no colores fijos.
       El sistema genera light + dark automaticamente.
```

---

### Platform-Adaptive Components

Un mismo componente debe comportarse de forma nativa en cada plataforma.

#### Date Picker

```
iOS:  Rueda (wheel) o calendario inline (UIDatePicker)
      - Aparece inline o como popover
      - Soporta wheel, compact, inline styles

Android: MaterialDatePicker
      - Aparece como dialog modal
      - Calendario con seleccion de dia
      - Input mode alternativo para escribir fecha
```

#### React Native - Platform.select()

```javascript
import { Platform, ActionSheetIOS } from 'react-native';

// Componente adaptativo
const AdaptiveDatePicker = ({ value, onChange }) => {
  if (Platform.OS === 'ios') {
    return (
      <DateTimePicker
        value={value}
        mode="date"
        display="spinner"  // iOS: wheel style
        onChange={onChange}
      />
    );
  }

  return (
    <DateTimePicker
      value={value}
      mode="date"
      display="calendar"  // Android: calendar dialog
      onChange={onChange}
    />
  );
};

// Accion adaptativa (Action Sheet vs Bottom Sheet)
const showOptions = (options) => {
  if (Platform.OS === 'ios') {
    ActionSheetIOS.showActionSheetWithOptions(
      { options: [...options, 'Cancel'], cancelButtonIndex: options.length },
      (index) => { if (index < options.length) handleSelect(index); }
    );
  } else {
    // Android: mostrar BottomSheet o Menu
    showBottomSheet(options);
  }
};

// Estilos adaptativos
const styles = StyleSheet.create({
  shadow: Platform.select({
    ios: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
    },
    android: {
      elevation: 4,
    },
  }),
});
```

#### Flutter - Adaptive Widgets

```dart
import 'dart:io' show Platform;
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

// Adaptive dialog
Future<void> showAdaptiveDialog(BuildContext context, String message) {
  if (Platform.isIOS) {
    return showCupertinoDialog(
      context: context,
      builder: (ctx) => CupertinoAlertDialog(
        title: const Text('Confirmar'),
        content: Text(message),
        actions: [
          CupertinoDialogAction(
            isDestructiveAction: true,
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancelar'),
          ),
          CupertinoDialogAction(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Aceptar'),
          ),
        ],
      ),
    );
  }

  return showDialog(
    context: context,
    builder: (ctx) => AlertDialog(
      title: const Text('Confirmar'),
      content: Text(message),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(ctx),
          child: const Text('Cancelar'),
        ),
        FilledButton(
          onPressed: () => Navigator.pop(ctx, true),
          child: const Text('Aceptar'),
        ),
      ],
    ),
  );
}

// Adaptive switch
Widget buildAdaptiveSwitch(bool value, ValueChanged<bool> onChanged) {
  if (Platform.isIOS) {
    return CupertinoSwitch(value: value, onChanged: onChanged);
  }
  return Switch(value: value, onChanged: onChanged);
}

// Adaptive loading indicator
Widget buildAdaptiveLoader() {
  if (Platform.isIOS) {
    return const CupertinoActivityIndicator();
  }
  return const CircularProgressIndicator();
}
```

#### Kotlin Multiplatform (KMP) - Expect/Actual

```kotlin
// shared/src/commonMain/kotlin/DatePicker.kt
expect class PlatformDatePicker {
    fun show(onDateSelected: (Long) -> Unit)
}

// shared/src/androidMain/kotlin/DatePicker.kt
actual class PlatformDatePicker(private val activity: FragmentActivity) {
    actual fun show(onDateSelected: (Long) -> Unit) {
        MaterialDatePicker.Builder.datePicker()
            .setTitleText("Seleccionar fecha")
            .build()
            .apply { addOnPositiveButtonClickListener(onDateSelected) }
            .show(activity.supportFragmentManager, "date_picker")
    }
}

// shared/src/iosMain/kotlin/DatePicker.kt
actual class PlatformDatePicker {
    actual fun show(onDateSelected: (Long) -> Unit) {
        // Bridge to UIDatePicker via UIKit interop
    }
}
```

---

## 2. Gesture Patterns

### Decision Tree: Which Gesture for Which Action

```
Accion del usuario           Gesto correcto
───────────────────────────── ─────────────────────────────────
Eliminar item de lista        Swipe left (iOS) / Swipe left o right (Android)
Archivar item                 Swipe right
Refrescar datos               Pull down (pull to refresh)
Ver opciones de un item       Long press -> context menu
Zoom en imagen/mapa           Pinch (dos dedos)
Reaccionar a contenido        Double tap
Cambiar entre tabs/paginas    Horizontal swipe
Reordenar lista               Long press + drag
Navegar atras                 Swipe from left edge (iOS) / Back gesture (Android)
Dismiss modal/sheet           Swipe down
Seleccionar multiples items   Long press primero, luego tap para agregar
```

### Swipe to Delete / Archive

#### React Native (react-native-gesture-handler + Reanimated)

```javascript
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  runOnJS,
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';

const SWIPE_THRESHOLD = -80;
const DELETE_THRESHOLD = -150;

const SwipeableRow = ({ children, onDelete, onArchive }) => {
  const translateX = useSharedValue(0);

  const triggerHaptic = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
  };

  const pan = Gesture.Pan()
    .activeOffsetX([-10, 10])
    .onUpdate((event) => {
      translateX.value = Math.min(0, event.translationX);
      if (translateX.value < DELETE_THRESHOLD) {
        runOnJS(triggerHaptic)();
      }
    })
    .onEnd(() => {
      if (translateX.value < DELETE_THRESHOLD) {
        translateX.value = withSpring(-400);
        runOnJS(onDelete)();
      } else if (translateX.value < SWIPE_THRESHOLD) {
        translateX.value = withSpring(SWIPE_THRESHOLD);
      } else {
        translateX.value = withSpring(0);
      }
    });

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
  }));

  return (
    <View>
      {/* Background actions revealed by swipe */}
      <View style={styles.actionsContainer}>
        <View style={[styles.action, styles.deleteAction]}>
          <Text style={styles.actionText}>Eliminar</Text>
        </View>
      </View>
      {/* Foreground content */}
      <GestureDetector gesture={pan}>
        <Animated.View style={animatedStyle}>
          {children}
        </Animated.View>
      </GestureDetector>
    </View>
  );
};
```

#### Flutter (Dismissible)

```dart
Dismissible(
  key: Key(item.id),
  direction: DismissDirection.endToStart,
  confirmDismiss: (direction) async {
    HapticFeedback.mediumImpact();
    return await showAdaptiveDialog(
      context,
      'Eliminar ${item.title}?',
    );
  },
  onDismissed: (direction) => onDelete(item),
  background: Container(
    alignment: Alignment.centerRight,
    padding: const EdgeInsets.only(right: 20),
    color: Colors.red,
    child: const Icon(Icons.delete, color: Colors.white),
  ),
  child: ListTile(title: Text(item.title)),
)
```

### Pull to Refresh

#### React Native

```javascript
import { RefreshControl, FlatList } from 'react-native';

const DataList = () => {
  const [refreshing, setRefreshing] = useState(false);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  }, []);

  return (
    <FlatList
      data={items}
      renderItem={renderItem}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={onRefresh}
          tintColor={Platform.OS === 'ios' ? '#007AFF' : undefined}
          colors={Platform.OS === 'android' ? ['#6200EE'] : undefined}
        />
      }
    />
  );
};
```

#### Flutter

```dart
RefreshIndicator(
  onRefresh: () async {
    await ref.read(dataProvider.notifier).refresh();
  },
  child: ListView.builder(
    itemCount: items.length,
    itemBuilder: (context, index) => ItemTile(item: items[index]),
  ),
)

// iOS style (Cupertino):
CustomScrollView(
  slivers: [
    CupertinoSliverRefreshControl(
      onRefresh: () async => await refreshData(),
    ),
    SliverList(delegate: SliverChildBuilderDelegate(/* ... */)),
  ],
)
```

### Long Press Context Menu

#### React Native (iOS style)

```javascript
import { ContextMenuView } from 'react-native-ios-context-menu';

<ContextMenuView
  menuConfig={{
    menuTitle: '',
    menuItems: [
      {
        actionKey: 'copy',
        actionTitle: 'Copiar',
        icon: { type: 'IMAGE_SYSTEM', imageValue: { systemName: 'doc.on.doc' } },
      },
      {
        actionKey: 'share',
        actionTitle: 'Compartir',
        icon: { type: 'IMAGE_SYSTEM', imageValue: { systemName: 'square.and.arrow.up' } },
      },
      {
        menuTitle: '',
        menuOptions: ['destructive'],
        menuItems: [{
          actionKey: 'delete',
          actionTitle: 'Eliminar',
          menuAttributes: ['destructive'],
          icon: { type: 'IMAGE_SYSTEM', imageValue: { systemName: 'trash' } },
        }],
      },
    ],
  }}
  onPressMenuItem={({ nativeEvent }) => handleAction(nativeEvent.actionKey)}
>
  <ItemCard item={item} />
</ContextMenuView>
```

### Drag to Reorder

#### React Native

```javascript
import DraggableFlatList, { ScaleDecorator } from 'react-native-draggable-flatlist';
import * as Haptics from 'expo-haptics';

<DraggableFlatList
  data={items}
  keyExtractor={(item) => item.id}
  onDragBegin={() => Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium)}
  onDragEnd={({ data }) => setItems(data)}
  renderItem={({ item, drag, isActive }) => (
    <ScaleDecorator>
      <TouchableOpacity
        onLongPress={drag}
        disabled={isActive}
        style={[styles.item, isActive && styles.itemActive]}
      >
        <Text>{item.title}</Text>
        <Icon name="menu" color="#999" />
      </TouchableOpacity>
    </ScaleDecorator>
  )}
/>
```

#### Flutter (ReorderableListView)

```dart
ReorderableListView.builder(
  itemCount: items.length,
  onReorder: (oldIndex, newIndex) {
    HapticFeedback.mediumImpact();
    setState(() {
      if (newIndex > oldIndex) newIndex--;
      final item = items.removeAt(oldIndex);
      items.insert(newIndex, item);
    });
  },
  itemBuilder: (context, index) {
    return ListTile(
      key: ValueKey(items[index].id),
      title: Text(items[index].title),
      trailing: ReorderableDragStartListener(
        index: index,
        child: const Icon(Icons.drag_handle),
      ),
    );
  },
)
```

---

## 3. Haptic Feedback

### Types & When to Use

```
Tipo                    Intensidad    Cuando Usar
─────────────────────── ───────────── ─────────────────────────────────
Impact Light            Sutil         Seleccion en picker, hover sobre opcion
Impact Medium           Moderado      Toggle switch, swipe threshold alcanzado
Impact Heavy            Fuerte        Accion completada, drop despues de drag
Notification Success    Patron ok     Pago exitoso, tarea completada
Notification Warning    Patron warn   Limite alcanzado, confirmacion requerida
Notification Error      Patron error  Error de validacion, accion fallida
Selection Changed       Tick          Scroll en picker, cambio de segmento
```

### When NOT to Use Haptics

```
NUNCA usar haptics para:
- Cada tap en cualquier boton (fatiga haptica)
- Durante scroll normal
- Animaciones decorativas
- Notificaciones push (el sistema maneja eso)
- Typing en teclado (el sistema ya lo hace)
- Mas de 3 haptics en 1 segundo
```

#### React Native (expo-haptics)

```javascript
import * as Haptics from 'expo-haptics';

// Impact feedback
await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);

// Notification feedback
await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);

// Selection feedback (lightest, for pickers)
await Haptics.selectionAsync();

// Practical example: like button
const LikeButton = ({ isLiked, onToggle }) => {
  const handlePress = async () => {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    onToggle();
  };

  return (
    <Pressable onPress={handlePress}>
      <Icon name={isLiked ? 'heart' : 'heart-outline'} />
    </Pressable>
  );
};
```

#### Flutter (HapticFeedback)

```dart
import 'package:flutter/services.dart';

// Light impact
HapticFeedback.lightImpact();

// Medium impact
HapticFeedback.mediumImpact();

// Heavy impact
HapticFeedback.heavyImpact();

// Selection click (picker scroll)
HapticFeedback.selectionClick();

// Vibrate (use sparingly, not recommended for normal UX)
HapticFeedback.vibrate();

// Practical example: toggle with haptic
Switch(
  value: isEnabled,
  onChanged: (value) {
    HapticFeedback.lightImpact();
    setState(() => isEnabled = value);
  },
)
```

#### iOS Native (UIFeedbackGenerator)

```swift
// Impact
let impact = UIImpactFeedbackGenerator(style: .medium)
impact.prepare()  // Call BEFORE the event for zero latency
impact.impactOccurred()

// Notification
let notification = UINotificationFeedbackGenerator()
notification.prepare()
notification.notificationOccurred(.success)

// Selection (for pickers, sliders)
let selection = UISelectionFeedbackGenerator()
selection.prepare()
selection.selectionChanged()
```

#### Android Native (VibrationEffect)

```kotlin
val vibrator = context.getSystemService(Vibrator::class.java)

// Click effect (API 29+)
vibrator.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_CLICK))

// Heavy click
vibrator.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_HEAVY_CLICK))

// Double click
vibrator.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_DOUBLE_CLICK))

// Tick (for selection changes)
vibrator.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_TICK))

// Custom pattern: [delay, vibrate, delay, vibrate, ...]
vibrator.vibrate(
    VibrationEffect.createWaveform(longArrayOf(0, 50, 100, 50), -1)
)
```

---

## 4. Motion & Animation

### Principles

```
1. PURPOSEFUL    - Cada animacion comunica algo (transicion, feedback, estado)
2. FAST          - Duracion < 300ms para interacciones, < 500ms para transiciones
3. INTERRUPTIBLE - El usuario puede cancelar/interrumpir cualquier animacion
4. NATURAL       - Spring physics > linear/ease (se siente organico)
5. CONSISTENT    - Mismo tipo de animacion para misma accion en toda la app
```

### When to Animate vs When NOT to

```
ANIMAR:
- Transiciones entre pantallas (shared element, fade)
- Feedback de acciones (boton press, toggle, like)
- Aparicion/desaparicion de elementos (fade in, slide up)
- Loading states (skeleton shimmer, spinner)
- Cambios de estado (expand/collapse, reorder)

NO ANIMAR:
- Contenido critico que debe aparecer inmediatamente
- Cada scroll o movimiento del usuario
- Elementos decorativos sin proposito funcional
- Si el usuario tiene Reduce Motion activado
- Mas de 2 animaciones simultaneas (distraccion)
```

### Spring Animations (Natural Feel)

#### React Native (Reanimated 3)

```javascript
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  withSequence,
  Easing,
  ReduceMotion,
} from 'react-native-reanimated';

// Spring config for different feels
const SPRING_CONFIGS = {
  gentle: { damping: 20, stiffness: 150, mass: 1 },
  snappy: { damping: 15, stiffness: 400, mass: 0.5 },
  bouncy: { damping: 10, stiffness: 200, mass: 0.8 },
};

// Respect Reduce Motion preference
const springConfig = {
  ...SPRING_CONFIGS.snappy,
  reduceMotion: ReduceMotion.System, // Follows system preference
};

// Button press animation
const ButtonWithFeedback = ({ children, onPress }) => {
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <Pressable
      onPressIn={() => { scale.value = withSpring(0.95, SPRING_CONFIGS.snappy); }}
      onPressOut={() => { scale.value = withSpring(1, SPRING_CONFIGS.gentle); }}
      onPress={onPress}
    >
      <Animated.View style={animatedStyle}>
        {children}
      </Animated.View>
    </Pressable>
  );
};

// Like animation (scale + color)
const LikeAnimation = ({ isLiked }) => {
  const scale = useSharedValue(1);

  useEffect(() => {
    if (isLiked) {
      scale.value = withSequence(
        withSpring(1.3, SPRING_CONFIGS.bouncy),
        withSpring(1, SPRING_CONFIGS.gentle),
      );
    }
  }, [isLiked]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <Animated.View style={animatedStyle}>
      <Icon name="heart" color={isLiked ? 'red' : 'gray'} size={24} />
    </Animated.View>
  );
};
```

#### Flutter (Implicit vs Explicit Animations)

```dart
// IMPLICIT: Simple, declarativa. Usar para la mayoria de casos.
AnimatedContainer(
  duration: const Duration(milliseconds: 250),
  curve: Curves.easeOutCubic,
  width: isExpanded ? 300 : 100,
  height: isExpanded ? 200 : 60,
  decoration: BoxDecoration(
    color: isSelected ? Colors.blue : Colors.grey.shade200,
    borderRadius: BorderRadius.circular(isExpanded ? 16 : 8),
  ),
  child: content,
)

// AnimatedSwitcher: swap widgets with animation
AnimatedSwitcher(
  duration: const Duration(milliseconds: 200),
  transitionBuilder: (child, animation) => FadeTransition(
    opacity: animation,
    child: SlideTransition(
      position: Tween<Offset>(
        begin: const Offset(0, 0.1),
        end: Offset.zero,
      ).animate(animation),
      child: child,
    ),
  ),
  child: Text(status, key: ValueKey(status)),
)

// EXPLICIT: For complex, multi-step, or physics-based animations.
class _BounceButtonState extends State<BounceButton>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<double> _scale;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 150),
    );
    _scale = Tween<double>(begin: 1.0, end: 0.95).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  Widget build(BuildContext context) {
    // Respect Reduce Motion
    final reduceMotion = MediaQuery.of(context).disableAnimations;

    return GestureDetector(
      onTapDown: (_) => reduceMotion ? null : _controller.forward(),
      onTapUp: (_) => _controller.reverse(),
      onTapCancel: () => _controller.reverse(),
      child: ScaleTransition(scale: _scale, child: widget.child),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
```

### Skeleton Loading (Shimmer)

#### React Native

```javascript
import { MotiView } from 'moti';
import { Skeleton } from 'moti/skeleton';

const SkeletonCard = () => (
  <MotiView
    transition={{ type: 'timing' }}
    animate={{ backgroundColor: '#f5f5f5' }}
    style={styles.card}
  >
    <Skeleton colorMode="light" width={60} height={60} radius="round" />
    <View style={{ flex: 1, marginLeft: 12 }}>
      <Skeleton colorMode="light" width="70%" height={16} />
      <Skeleton colorMode="light" width="40%" height={12} />
    </View>
  </MotiView>
);

// Usage pattern
const UserList = () => {
  const { data, isLoading } = useQuery('users', fetchUsers);

  if (isLoading) {
    return Array.from({ length: 5 }).map((_, i) => <SkeletonCard key={i} />);
  }

  return data.map(user => <UserCard key={user.id} user={user} />);
};
```

#### Flutter (shimmer package)

```dart
import 'package:shimmer/shimmer.dart';

class SkeletonCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Shimmer.fromColors(
      baseColor: Colors.grey.shade300,
      highlightColor: Colors.grey.shade100,
      child: Row(
        children: [
          Container(
            width: 60, height: 60,
            decoration: const BoxDecoration(
              color: Colors.white, shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(width: double.infinity, height: 16, color: Colors.white),
                const SizedBox(height: 8),
                Container(width: 100, height: 12, color: Colors.white),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
```

### Hero / Shared Element Transitions

#### React Native (React Navigation)

```javascript
import { SharedElement } from 'react-navigation-shared-element';

// List screen
const ListScreen = ({ navigation }) => (
  <FlatList
    data={items}
    renderItem={({ item }) => (
      <Pressable onPress={() => navigation.push('Detail', { item })}>
        <SharedElement id={`item.${item.id}.photo`}>
          <Image source={{ uri: item.photo }} style={styles.thumb} />
        </SharedElement>
        <SharedElement id={`item.${item.id}.title`}>
          <Text style={styles.title}>{item.title}</Text>
        </SharedElement>
      </Pressable>
    )}
  />
);

// Detail screen
const DetailScreen = ({ route }) => {
  const { item } = route.params;
  return (
    <View>
      <SharedElement id={`item.${item.id}.photo`}>
        <Image source={{ uri: item.photo }} style={styles.hero} />
      </SharedElement>
      <SharedElement id={`item.${item.id}.title`}>
        <Text style={styles.heroTitle}>{item.title}</Text>
      </SharedElement>
    </View>
  );
};
```

#### Flutter (Hero widget)

```dart
// List screen
GestureDetector(
  onTap: () => Navigator.push(context,
    MaterialPageRoute(builder: (_) => DetailScreen(item: item))),
  child: Hero(
    tag: 'photo-${item.id}',
    child: ClipRRect(
      borderRadius: BorderRadius.circular(8),
      child: Image.network(item.photoUrl, width: 80, height: 80, fit: BoxFit.cover),
    ),
  ),
)

// Detail screen
Hero(
  tag: 'photo-${item.id}',
  child: Image.network(item.photoUrl, width: double.infinity, height: 300, fit: BoxFit.cover),
)
```

---

## 5. Adaptive Layouts

### Breakpoints

```
Dispositivo          Ancho (dp/pt)    Layout
──────────────────── ──────────────── ─────────────────────────────
Phone compact        < 360            Single column, minimal padding
Phone standard       360-411          Single column
Phone large          412-599          Single column, wider cards
Tablet portrait      600-839          Two columns, master-detail option
Tablet landscape     840-1199         Two columns, navigation rail
Foldable (unfolded)  600-900          Adaptive (varies by device)
Desktop/Large        1200+            Three columns, navigation rail
```

### React Native

```javascript
import { useWindowDimensions, Platform } from 'react-native';

const useAdaptiveLayout = () => {
  const { width, height } = useWindowDimensions();

  return {
    isPhone: width < 600,
    isTablet: width >= 600 && width < 1200,
    isLandscape: width > height,
    columns: width < 600 ? 1 : width < 900 ? 2 : 3,
    contentPadding: width < 600 ? 16 : 24,
    maxContentWidth: Math.min(width, 1200),
  };
};

// Usage
const ProductGrid = () => {
  const { columns, contentPadding } = useAdaptiveLayout();

  return (
    <FlatList
      data={products}
      numColumns={columns}
      key={columns} // Force re-render on column change
      contentContainerStyle={{ padding: contentPadding }}
      renderItem={({ item }) => (
        <View style={{ flex: 1 / columns, padding: 8 }}>
          <ProductCard product={item} />
        </View>
      )}
    />
  );
};
```

### Flutter

```dart
class AdaptiveScaffold extends StatelessWidget {
  final Widget body;

  const AdaptiveScaffold({required this.body});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth >= 840) {
          // Tablet landscape: navigation rail + body
          return Row(
            children: [
              NavigationRail(
                selectedIndex: currentIndex,
                onDestinationSelected: onTabChanged,
                labelType: NavigationRailLabelType.all,
                destinations: _destinations,
              ),
              const VerticalDivider(width: 1),
              Expanded(child: body),
            ],
          );
        }

        if (constraints.maxWidth >= 600) {
          // Tablet portrait: bottom nav + wider layout
          return Scaffold(
            body: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: body,
            ),
            bottomNavigationBar: NavigationBar(
              selectedIndex: currentIndex,
              onDestinationSelected: onTabChanged,
              destinations: _barDestinations,
            ),
          );
        }

        // Phone: standard layout
        return Scaffold(
          body: body,
          bottomNavigationBar: NavigationBar(
            selectedIndex: currentIndex,
            onDestinationSelected: onTabChanged,
            destinations: _barDestinations,
          ),
        );
      },
    );
  }
}

// Master-Detail for tablets
class MasterDetail extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final isWide = MediaQuery.of(context).size.width >= 600;

    if (isWide) {
      return Row(
        children: [
          SizedBox(width: 350, child: MasterList(onSelect: selectItem)),
          const VerticalDivider(width: 1),
          Expanded(child: DetailView(item: selectedItem)),
        ],
      );
    }

    // On phone, navigate to detail screen
    return MasterList(
      onSelect: (item) => Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => DetailView(item: item)),
      ),
    );
  }
}
```

### Orientation Handling

```javascript
// React Native
import { useWindowDimensions } from 'react-native';

const App = () => {
  const { width, height } = useWindowDimensions();
  const isLandscape = width > height;

  return (
    <View style={isLandscape ? styles.landscape : styles.portrait}>
      {isLandscape ? <SideBySideLayout /> : <StackedLayout />}
    </View>
  );
};
```

```dart
// Flutter
OrientationBuilder(
  builder: (context, orientation) {
    return GridView.count(
      crossAxisCount: orientation == Orientation.portrait ? 2 : 4,
      children: items.map((item) => ItemCard(item: item)).toList(),
    );
  },
)
```

### Foldable Support (Samsung Fold, Pixel Fold)

```dart
// Flutter - MediaQuery for foldables
final displayFeatures = MediaQuery.of(context).displayFeatures;
final hasFold = displayFeatures.any(
  (feature) => feature.type == DisplayFeatureType.fold,
);

if (hasFold) {
  final foldFeature = displayFeatures.firstWhere(
    (f) => f.type == DisplayFeatureType.fold,
  );
  // Layout content on either side of the fold
  return TwoPane(
    startPane: MasterList(),
    endPane: DetailView(),
    paneProportion: 0.4,
  );
}
```

---

## 6. System Integration

### Decision Tree: Which Integrations Add Real Value

```
Integracion                  Usar cuando...
──────────────────────────── ───────────────────────────────────────
Home Widget                  Usuario necesita info-at-a-glance (clima, tareas, stats)
Share Extension              App consume contenido de otras apps (URLs, fotos, texto)
Quick Actions (3D Touch)     3-4 acciones frecuentes (nuevo, buscar, escanear)
Siri/Assistant               Acciones que se hacen sin abrir la app
App Clip / Instant App       Onboarding sin instalar (QR, NFC, links)
Live Activities (iOS)        Estado en tiempo real (delivery, timer, score)
```

### Home Screen Widgets

#### iOS WidgetKit (SwiftUI)

```swift
struct TaskWidget: Widget {
    let kind: String = "TaskWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: TaskProvider()) { entry in
            TaskWidgetView(entry: entry)
        }
        .configurationDisplayName("Tareas Pendientes")
        .description("Ver tus tareas del dia")
        .supportedFamilies([.systemSmall, .systemMedium, .systemLarge])
    }
}

struct TaskWidgetView: View {
    var entry: TaskEntry

    var body: some View {
        VStack(alignment: .leading) {
            Text("Hoy")
                .font(.headline)
            ForEach(entry.tasks.prefix(3), id: \.id) { task in
                HStack {
                    Image(systemName: task.isDone ? "checkmark.circle.fill" : "circle")
                    Text(task.title)
                        .lineLimit(1)
                }
            }
        }
        .padding()
    }
}
```

#### Android App Widgets (Glance - Jetpack Compose)

```kotlin
class TaskWidget : GlanceAppWidget() {
    override suspend fun provideGlance(context: Context, id: GlanceId) {
        provideContent {
            TaskWidgetContent(tasks = loadTasks())
        }
    }
}

@Composable
fun TaskWidgetContent(tasks: List<Task>) {
    Column(
        modifier = GlanceModifier
            .fillMaxSize()
            .padding(16.dp)
            .background(GlanceTheme.colors.surface)
    ) {
        Text(
            text = "Hoy",
            style = TextStyle(fontWeight = FontWeight.Bold, fontSize = 16.sp),
        )
        tasks.take(3).forEach { task ->
            Row(modifier = GlanceModifier.padding(vertical = 4.dp)) {
                Image(
                    provider = ImageProvider(
                        if (task.isDone) R.drawable.ic_check else R.drawable.ic_circle
                    ),
                    contentDescription = null,
                )
                Text(text = task.title, maxLines = 1)
            }
        }
    }
}
```

### Quick Actions (3D Touch / Long Press on Icon)

#### iOS (Info.plist + AppDelegate)

```xml
<!-- Info.plist -->
<key>UIApplicationShortcutItems</key>
<array>
    <dict>
        <key>UIApplicationShortcutItemType</key>
        <string>com.app.newTask</string>
        <key>UIApplicationShortcutItemTitle</key>
        <string>Nueva Tarea</string>
        <key>UIApplicationShortcutItemIconType</key>
        <string>UIApplicationShortcutIconTypeAdd</string>
    </dict>
    <dict>
        <key>UIApplicationShortcutItemType</key>
        <string>com.app.search</string>
        <key>UIApplicationShortcutItemTitle</key>
        <string>Buscar</string>
        <key>UIApplicationShortcutItemIconType</key>
        <string>UIApplicationShortcutIconTypeSearch</string>
    </dict>
</array>
```

#### React Native (react-native-quick-actions)

```javascript
import QuickActions from 'react-native-quick-actions';

QuickActions.setShortcutItems([
  {
    type: 'NewTask',
    title: 'Nueva Tarea',
    icon: 'Add',
    userInfo: { url: 'app://task/new' },
  },
  {
    type: 'Search',
    title: 'Buscar',
    icon: 'Search',
    userInfo: { url: 'app://search' },
  },
]);

// Handle action
QuickActions.popInitialAction().then((action) => {
  if (action) handleQuickAction(action);
});

DeviceEventEmitter.addListener('quickActionShortcut', handleQuickAction);
```

### Share Extension (Receiving Shared Content)

#### React Native (react-native-share-menu)

```javascript
import ShareMenu from 'react-native-share-menu';

// In your app's entry point
useEffect(() => {
  ShareMenu.getInitialShare((share) => {
    if (share) handleSharedContent(share);
  });

  const listener = ShareMenu.addNewShareListener((share) => {
    handleSharedContent(share);
  });

  return () => listener.remove();
}, []);

const handleSharedContent = (share) => {
  if (share.mimeType === 'text/plain') {
    // Shared URL or text
    navigation.navigate('CreateFromShare', { text: share.data });
  } else if (share.mimeType.startsWith('image/')) {
    // Shared image
    navigation.navigate('CreateFromShare', { imageUri: share.data });
  }
};
```

---

## 7. Mobile Accessibility

### Minimum Touch Targets

```
Plataforma    Minimo         Recomendado
───────────── ────────────── ──────────────
iOS           44 x 44 pt     48 x 48 pt
Android       48 x 48 dp     56 x 56 dp

REGLA: Si el area visual es menor (ej: icono de 24px),
       expandir el area tappable con padding invisible.
```

### VoiceOver (iOS) Patterns

```swift
// SwiftUI
Image(systemName: "heart.fill")
    .accessibilityLabel("Favorito")
    .accessibilityHint("Doble tap para quitar de favoritos")
    .accessibilityAddTraits(.isButton)

// Group related elements
VStack {
    Text(product.name)
    Text(product.price)
}
.accessibilityElement(children: .combine)
// VoiceOver reads: "AirPods Pro, $249"

// Custom actions
.accessibilityAction(named: "Eliminar") {
    deleteItem()
}
```

### TalkBack (Android) Patterns

```kotlin
// Jetpack Compose
Icon(
    imageVector = Icons.Default.Favorite,
    contentDescription = "Favorito",
    modifier = Modifier.semantics {
        role = Role.Button
        stateDescription = if (isFav) "Activado" else "Desactivado"
        onClick(label = "Cambiar favorito") { toggleFav(); true }
    }
)

// Merge related elements
Row(modifier = Modifier.semantics(mergeDescendants = true) {}) {
    Text(product.name)
    Text(product.price)
}
// TalkBack reads: "AirPods Pro $249"

// Heading semantics (for navigation)
Text(
    text = "Productos",
    modifier = Modifier.semantics { heading() }
)
```

### React Native Accessibility

```javascript
// Basic labeling
<Pressable
  accessibilityLabel="Agregar al carrito"
  accessibilityHint="Agrega este producto a tu carrito de compras"
  accessibilityRole="button"
  onPress={addToCart}
>
  <Icon name="cart-plus" />
</Pressable>

// State description
<Pressable
  accessibilityLabel={`Favorito ${isFav ? 'activado' : 'desactivado'}`}
  accessibilityRole="togglebutton"
  accessibilityState={{ checked: isFav }}
  onPress={toggleFav}
>
  <Icon name={isFav ? 'heart' : 'heart-outline'} />
</Pressable>

// Group related elements
<View accessible={true} accessibilityLabel={`${name}, ${price}`}>
  <Text>{name}</Text>
  <Text>{price}</Text>
</View>

// Live region (announce changes)
<Text accessibilityLiveRegion="polite">
  {itemCount} items en el carrito
</Text>

// Focus order (importantForAccessibility)
<View importantForAccessibility="yes">
  <Text>Este contenido tiene prioridad para screen readers</Text>
</View>
<View importantForAccessibility="no-hide-descendants">
  <Text>Este contenido se ignora por screen readers</Text>
</View>
```

### Flutter Semantics

```dart
// Basic labeling
Semantics(
  label: 'Agregar al carrito',
  hint: 'Agrega este producto a tu carrito',
  button: true,
  child: IconButton(
    icon: const Icon(Icons.add_shopping_cart),
    onPressed: addToCart,
  ),
)

// Toggle state
Semantics(
  label: 'Favorito',
  toggled: isFav,
  child: IconButton(
    icon: Icon(isFav ? Icons.favorite : Icons.favorite_border),
    onPressed: toggleFav,
  ),
)

// Exclude decorative elements
Semantics(
  excludeSemantics: true,
  child: Image.asset('decorative_banner.png'),
)

// Live region
Semantics(
  liveRegion: true,
  child: Text('$itemCount items en el carrito'),
)
```

### Dynamic Type / Font Scaling

```javascript
// React Native: respect system font size
import { PixelRatio, Text } from 'react-native';

// Check if user has enlarged text
const fontScale = PixelRatio.getFontScale(); // 1.0 = normal, > 1.0 = enlarged

// ALWAYS use relative sizes, NEVER fixed pixel sizes for text
// Use maxFontSizeMultiplier to prevent extreme scaling that breaks layout
<Text
  style={{ fontSize: 16 }}
  maxFontSizeMultiplier={1.5}  // Cap at 1.5x for layout-critical text
>
  Contenido
</Text>
```

```dart
// Flutter: respect system text scale
final textScaleFactor = MediaQuery.of(context).textScaleFactor;

// NEVER override textScaleFactor globally.
// Use maxLines + overflow for layout stability:
Text(
  'Contenido largo que podria crecer',
  maxLines: 2,
  overflow: TextOverflow.ellipsis,
  style: Theme.of(context).textTheme.bodyLarge,
)
```

### Reduce Motion Support

```javascript
// React Native
import { AccessibilityInfo } from 'react-native';

const [reduceMotion, setReduceMotion] = useState(false);

useEffect(() => {
  AccessibilityInfo.isReduceMotionEnabled().then(setReduceMotion);
  const sub = AccessibilityInfo.addEventListener(
    'reduceMotionChanged',
    setReduceMotion,
  );
  return () => sub.remove();
}, []);

// Use in animations
const animationDuration = reduceMotion ? 0 : 300;
```

```dart
// Flutter
final reduceMotion = MediaQuery.of(context).disableAnimations;

AnimatedContainer(
  duration: Duration(milliseconds: reduceMotion ? 0 : 300),
  // ...
)
```

### Testing Accessibility

```
iOS VoiceOver Testing:
1. Settings > Accessibility > VoiceOver > ON
2. Swipe right to move to next element
3. Double tap to activate
4. Verify: every interactive element has a label
5. Verify: reading order is logical
6. Verify: no unlabeled images or buttons

Android TalkBack Testing:
1. Settings > Accessibility > TalkBack > ON
2. Swipe right to move to next element
3. Double tap to activate
4. Verify: every interactive element has contentDescription
5. Verify: headings are marked for navigation
6. Verify: custom views announce state changes

Automated Testing:
- iOS: Accessibility Inspector (Xcode)
- Android: Accessibility Scanner (Play Store)
- React Native: detox + a11y assertions
- Flutter: flutter test --accessibility
```

---

## 8. Advanced Notifications

### Notification Channels (Android 8+)

```kotlin
// Users can control each channel independently in Settings
class NotificationChannels {
    companion object {
        fun createAll(context: Context) {
            val manager = context.getSystemService(NotificationManager::class.java)

            // Messages: high priority, sound + vibrate
            manager.createNotificationChannel(
                NotificationChannel(
                    "messages", "Mensajes",
                    NotificationManager.IMPORTANCE_HIGH
                ).apply {
                    description = "Mensajes directos y conversaciones"
                    enableVibration(true)
                    setShowBadge(true)
                }
            )

            // Updates: default priority
            manager.createNotificationChannel(
                NotificationChannel(
                    "updates", "Actualizaciones",
                    NotificationManager.IMPORTANCE_DEFAULT
                ).apply {
                    description = "Actualizaciones de estado y progreso"
                }
            )

            // Background: low priority, silent
            manager.createNotificationChannel(
                NotificationChannel(
                    "background", "Sincronizacion",
                    NotificationManager.IMPORTANCE_LOW
                ).apply {
                    description = "Sincronizacion en segundo plano"
                    enableVibration(false)
                    setSound(null, null)
                }
            )
        }
    }
}
```

### Rich Notifications (Images + Actions)

#### iOS

```swift
// Rich notification with image
let content = UNMutableNotificationContent()
content.title = "Nuevo pedido"
content.body = "Tu pedido #1234 ha sido enviado"
content.sound = .default

// Attach image
if let url = URL(string: "https://example.com/product.jpg"),
   let data = try? Data(contentsOf: url) {
    let tempDir = FileManager.default.temporaryDirectory
    let tempFile = tempDir.appendingPathComponent("notification.jpg")
    try? data.write(to: tempFile)
    let attachment = try? UNNotificationAttachment(
        identifier: "image", url: tempFile)
    content.attachments = [attachment].compactMap { $0 }
}

// Action buttons
let trackAction = UNNotificationAction(
    identifier: "TRACK", title: "Rastrear", options: .foreground)
let dismissAction = UNNotificationAction(
    identifier: "DISMISS", title: "Descartar", options: .destructive)
let category = UNNotificationCategory(
    identifier: "ORDER_UPDATE",
    actions: [trackAction, dismissAction],
    intentIdentifiers: [])
UNUserNotificationCenter.current().setNotificationCategories([category])
content.categoryIdentifier = "ORDER_UPDATE"
```

#### React Native (notifee)

```javascript
import notifee, { AndroidImportance, AndroidStyle } from '@notifee/react-native';

// Rich notification with big picture (Android)
await notifee.displayNotification({
  title: 'Nuevo pedido',
  body: 'Tu pedido #1234 ha sido enviado',
  android: {
    channelId: 'updates',
    importance: AndroidImportance.HIGH,
    style: {
      type: AndroidStyle.BIGPICTURE,
      picture: 'https://example.com/product.jpg',
    },
    actions: [
      { title: 'Rastrear', pressAction: { id: 'track' } },
      { title: 'Descartar', pressAction: { id: 'dismiss' } },
    ],
  },
  ios: {
    attachments: [{ url: 'https://example.com/product.jpg' }],
    categoryId: 'ORDER_UPDATE',
  },
});

// Handle action press
notifee.onBackgroundEvent(async ({ type, detail }) => {
  if (type === EventType.ACTION_PRESS) {
    switch (detail.pressAction.id) {
      case 'track':
        // Navigate to tracking screen
        break;
      case 'dismiss':
        await notifee.cancelNotification(detail.notification.id);
        break;
    }
  }
});
```

### Local Notifications (Scheduled + Geofenced)

```javascript
// React Native (notifee) - Scheduled
import notifee, { TimestampTrigger, TriggerType } from '@notifee/react-native';

// Schedule for specific time
const trigger: TimestampTrigger = {
  type: TriggerType.TIMESTAMP,
  timestamp: Date.now() + 60 * 60 * 1000, // 1 hour from now
  repeatFrequency: RepeatFrequency.DAILY,  // Repeat daily
};

await notifee.createTriggerNotification(
  {
    title: 'Recordatorio',
    body: 'Revisa tus tareas pendientes',
    android: { channelId: 'reminders' },
  },
  trigger,
);

// Geofenced (react-native-geofencing)
import Geofencing from 'react-native-geofencing';

Geofencing.addGeofence({
  id: 'office',
  latitude: 40.7128,
  longitude: -74.0060,
  radius: 200, // meters
  transitionTypes: [Geofencing.ENTER],
}).then(() => {
  // Show notification when user enters geofence
});
```

### Notification Grouping / Threading

```javascript
// React Native (notifee) - Group notifications
// Android: bundled notifications
await notifee.displayNotification({
  title: 'Maria',
  body: 'Hola! Como estas?',
  android: {
    channelId: 'messages',
    groupId: 'chat-messages',
    groupSummary: false,
  },
});

// Group summary (Android - required for bundling)
await notifee.displayNotification({
  title: '3 mensajes nuevos',
  android: {
    channelId: 'messages',
    groupId: 'chat-messages',
    groupSummary: true,
    groupAlertBehavior: AndroidGroupAlertBehavior.SUMMARY,
  },
});

// iOS: thread identifier for grouping
await notifee.displayNotification({
  title: 'Maria',
  body: 'Hola! Como estas?',
  ios: {
    threadId: 'chat-maria', // Groups in notification center
  },
});
```

### Silent / Background Notifications

```javascript
// React Native - background data sync
// iOS: content-available push
// Android: data-only FCM message

import messaging from '@react-native-firebase/messaging';

// Register background handler (OUTSIDE of any component)
messaging().setBackgroundMessageHandler(async (remoteMessage) => {
  // This runs even when app is killed
  if (remoteMessage.data.type === 'sync') {
    await syncDataInBackground(remoteMessage.data);
  }
});

// Server-side: send silent push
// {
//   "to": "<device_token>",
//   "content_available": true,  // iOS
//   "priority": "high",
//   "data": {
//     "type": "sync",
//     "entity": "orders",
//     "lastSync": "2026-03-20T10:00:00Z"
//   }
// }
```

---

## 9. Decision Tree: Web Component to Mobile Equivalent

```
Web Component              Mobile Equivalent                  Razon
────────────────────────── ────────────────────────────────── ────────────────────────────
Dropdown <select>          Bottom sheet picker                Mejor alcance del pulgar,
                           o native picker (iOS wheel,       mas area de toque
                           Android spinner)

Hover tooltip              Long press tooltip                 No existe hover en mobile,
                           o inline hint text                 la info debe ser descubrible

Right-click context menu   Long press context menu            Gesto equivalente en mobile

Sidebar navigation         Bottom tab bar (3-5 items)         Pulgar alcanza la parte
                           o hamburger drawer (>5 items)      inferior de la pantalla

Modal dialog               Bottom sheet (parcial)             Los modales centrados cubren
                           o full-screen modal                poco contenido en mobile

Data table                 Card list (vertical scroll)        Las tablas no caben en 360dp;
                           o horizontal scroll por fila       cards muestran datos clave

Multi-step form wizard     Step indicator + swipe entre       Paginacion con indicador de
                           pasos, o full-screen steps         progreso visual

Toast notification         In-app notification banner         Banner arriba o abajo con
                           (top o bottom)                     accion de dismiss

Infinite scroll            FlatList/ListView con              Virtualizacion obligatoria
                           pagination                         para performance

Drag and drop              Long press + drag con              Haptic confirma el inicio
                           haptic feedback                    del drag

Breadcrumbs                Back button + screen title         La jerarquia se muestra
                                                             en el navigation stack

Tabs (horizontal)          Top tabs con swipe                 Swipeable tabs con indicador
                           o segmented control                de seleccion

Search with filters        Search bar + filter chips          Filtros como chips debajo
                           o filter bottom sheet              de la barra de busqueda

Accordion/Collapsible      Expandable list sections           Tappable headers que expanden
                                                             o colapsan contenido

File upload button         Camera/gallery picker              Action sheet con opciones:
                           + document picker                  Camara, Galeria, Archivos

Date range picker          Two date pickers                   Un picker por fecha (inicio
                           (start + end)                      y fin) con validacion

Pagination (page numbers)  Load more button                   Infinite scroll o boton
                           o infinite scroll                  "cargar mas" al final

Color picker               Preset color grid                  Grid de colores predefinidos
                           o slider-based picker              (evitar precision de pixel)
```

---

## 10. Mobile UX Checklist

```
NAVEGACION
──────────────────────────────────────────────────────────────
[ ] Back gesture funciona (iOS swipe back, Android back button/gesture)
[ ] Tab bar tiene 3-5 items maximo
[ ] Deep links abren la pantalla correcta con el estado correcto
[ ] Estado preservado al cambiar de tab (no se resetea)
[ ] Navigation stack tiene titulo en cada pantalla
[ ] Modal sheets se pueden cerrar con swipe down
[ ] No hay dead ends (siempre hay forma de volver atras)
[ ] Landscape orientation funciona o esta correctamente bloqueada

INPUT
──────────────────────────────────────────────────────────────
[ ] Keyboard type correcto para cada campo:
    - email: keyboardType="email-address"
    - telefono: keyboardType="phone-pad"
    - numero: keyboardType="numeric" o "decimal-pad"
    - URL: keyboardType="url"
    - password: secureTextEntry={true}
[ ] Keyboard no cubre los campos de input (KeyboardAvoidingView)
[ ] Auto-focus en el primer campo al abrir formulario
[ ] Dismiss keyboard al tap fuera del campo
[ ] Return key navega al siguiente campo (returnKeyType="next")
[ ] Ultimo campo tiene returnKeyType="done" o "send"
[ ] Autofill funciona (textContentType en iOS, autofillHints en Android)
[ ] Validacion inline (no solo al submit)
[ ] Campos obligatorios claramente marcados

FEEDBACK
──────────────────────────────────────────────────────────────
[ ] Loading states con skeleton o spinner (NUNCA pantalla en blanco)
[ ] Error states con mensaje claro y accion de retry
[ ] Empty states con ilustracion/icono y call to action
[ ] Success confirmation: haptic + visual (checkmark, color, animacion)
[ ] Pull to refresh en listas de datos
[ ] Optimistic UI para acciones de red (like, save, toggle)
[ ] Progress indicator para operaciones largas (upload, download)
[ ] Toast/snackbar para feedback no critico

PERFORMANCE PERCIBIDA
──────────────────────────────────────────────────────────────
[ ] No hay pantallas en blanco (skeleton inmediato)
[ ] Transiciones entre pantallas < 300ms
[ ] Respuesta al touch < 100ms (visual feedback)
[ ] 60fps durante scroll y animaciones (0 jank frames)
[ ] Optimistic UI para acciones de red
[ ] Lazy loading de imagenes con placeholder
[ ] Listas virtualizadas (FlatList, no ScrollView con map)
[ ] Cache de datos para navegacion instantanea (back)

ACCESIBILIDAD
──────────────────────────────────────────────────────────────
[ ] Touch targets >= 44x44pt (iOS) / 48x48dp (Android)
[ ] Todos los iconos/imagenes tienen label descriptivo
[ ] Contraste de texto >= 4.5:1 (WCAG AA)
[ ] Dynamic Type / font scaling respetado
[ ] VoiceOver / TalkBack: orden de lectura logico
[ ] Reduce Motion respetado (animaciones desactivadas)
[ ] Focus trap correcto en modals y bottom sheets
[ ] Errores anunciados a screen readers (accessibilityLiveRegion)

PLATAFORMA
──────────────────────────────────────────────────────────────
[ ] Safe areas respetadas (notch, home indicator, rounded corners)
[ ] Dark mode soportado con colores semanticos
[ ] Haptic feedback en acciones clave (toggle, delete, success)
[ ] Controles nativos usados cuando existen (picker, switch, alert)
[ ] Comportamiento de scroll nativo (bounce en iOS, overscroll en Android)
[ ] Permisos solicitados en contexto (no al inicio)
[ ] App funciona offline (o muestra estado offline claro)
[ ] Deep links y universal links configurados
[ ] Push notifications con channels (Android) y categories (iOS)
```

---

## Referencias Rapidas

| Recurso | URL |
|---------|-----|
| Apple HIG | https://developer.apple.com/design/human-interface-guidelines |
| Material Design 3 | https://m3.material.io |
| WCAG 2.1 Mobile | https://www.w3.org/TR/mobile-accessibility-mapping |
| React Native Accessibility | https://reactnative.dev/docs/accessibility |
| Flutter Accessibility | https://docs.flutter.dev/accessibility-and-internationalization/accessibility |
| Reanimated 3 | https://docs.swmansion.com/react-native-reanimated |
| Notifee (RN Notifications) | https://notifee.app |

---

*NXT AI Development Framework v3.8.0 - SKILL Mobile UX*
*"Cada pixel tiene proposito. Cada gesto tiene intencion."*
