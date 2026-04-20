# 🤖 Modelos de Machine Learning Integrados

## 📋 Resumen

Se han integrado modelos reales de machine learning y deep learning para mejorar significativamente la precisión de la detección.

## ✅ Modelos Integrados

### 1. TensorFlow.js COCO-SSD
- **Propósito**: Detección de objetos (80 clases COCO)
- **Modelo**: MobileNet v2 + SSD
- **Tamaño**: ~10MB
- **Precisión**: Alta para objetos comunes
- **Velocidad**: ~30-60 FPS en hardware moderno
- **Archivo**: `apps/web/src/lib/ml/models/coco-ssd.ts`

**Objetos detectados**: 
- Personas, vehículos, animales
- Dispositivos (laptop, cell phone, mouse, keyboard, tv)
- Muebles (chair, couch, bed, table)
- Utensilios (cup, bottle, bowl)
- Y más de 80 clases COCO

### 2. MediaPipe Face Detection
- **Propósito**: Detección de rostros y landmarks faciales
- **Modelo**: BlazeFace
- **Tamaño**: ~2MB
- **Precisión**: Muy alta para rostros
- **Velocidad**: ~60+ FPS
- **Archivo**: `apps/web/src/lib/ml/models/mediapipe-face.ts`

**Características**:
- Detección de múltiples rostros
- Landmarks faciales (468 puntos)
- Tracking temporal
- Optimizado para tiempo real

### 3. MediaPipe Pose
- **Propósito**: Detección de poses/personas completas
- **Modelo**: Pose Landmarker Lite
- **Tamaño**: ~5MB
- **Precisión**: Alta para poses
- **Velocidad**: ~30-60 FPS
- **Archivo**: `apps/web/src/lib/ml/models/mediapipe-pose.ts`

**Características**:
- 33 landmarks corporales
- Detección de hasta 2 personas
- Tracking temporal
- Ideal para detección de personas

## 🚀 Cómo Funciona

### Carga de Modelos

Los modelos se cargan automáticamente al iniciar la aplicación:

```typescript
// Los modelos se cargan en paralelo para mayor velocidad
await loadModels()
```

### Uso en Detección

1. **Personas**: 
   - Primero intenta MediaPipe Pose (más preciso)
   - Fallback a COCO-SSD si MediaPipe no está disponible
   - Fallback a simulación si ningún modelo está disponible

2. **Rostros**:
   - Usa MediaPipe Face Detection (modelo real)
   - Fallback a simulación conservadora si no está disponible

3. **Objetos**:
   - Usa COCO-SSD (modelo real)
   - Detecta 80 clases de objetos COCO
   - Filtrado inteligente para reducir falsos positivos

## 📦 Instalación

Las dependencias ya están instaladas:

```json
{
  "@tensorflow/tfjs": "^4.15.0",
  "@tensorflow-models/coco-ssd": "^2.2.3",
  "@mediapipe/tasks-vision": "^0.10.9"
}
```

## 🔧 Configuración

### Umbrales de Confianza

Puedes ajustar los umbrales en la configuración:

```typescript
config.objectDetection.threshold = 0.5  // 50% mínimo
config.faceDetection.threshold = 0.5
config.personDetection.threshold = 0.5
```

### Desactivar Modelos

Para desactivar un modelo específico:

```typescript
config.objectDetection.enabled = false
config.faceDetection.enabled = false
config.personDetection.enabled = false
```

## 🎯 Ventajas de los Modelos Reales

### Antes (Simulación)
- ❌ Falsos positivos frecuentes
- ❌ Detecciones inexistentes
- ❌ No detectaba objetos reales
- ❌ Sin seguimiento real

### Después (Modelos Reales)
- ✅ Detección precisa de objetos reales
- ✅ Menos falsos positivos
- ✅ Detección de 80 clases de objetos
- ✅ Tracking temporal real
- ✅ Funciona con objetos reales (celular, vaso, etc.)

## 📊 Rendimiento

### Tiempo de Carga
- **Primera carga**: 5-10 segundos (descarga de modelos)
- **Cargas posteriores**: 1-3 segundos (caché del navegador)

### Velocidad de Inferencia
- **COCO-SSD**: 30-60 FPS (depende del hardware)
- **MediaPipe Face**: 60+ FPS
- **MediaPipe Pose**: 30-60 FPS

### Recursos
- **RAM**: ~200-300 MB adicionales
- **GPU**: Opcional (acelera inferencia)
- **CPU**: Funciona sin GPU (más lento)

## 🔄 Fallback Inteligente

El sistema tiene un sistema de fallback robusto:

1. **Intenta modelo real** (COCO-SSD, MediaPipe)
2. **Si falla**: Usa simulación conservadora
3. **Evita errores**: La aplicación siempre funciona

## 🐛 Solución de Problemas

### Modelos no cargan

1. **Verifica conexión a internet**: Los modelos se descargan desde CDN
2. **Revisa la consola**: Busca errores de carga
3. **Carga manual**: Los modelos se cargan automáticamente, pero puedes forzar:

```typescript
import { loadModels } from './lib/ml/processors'
await loadModels()
```

### Rendimiento lento

1. **Activa GPU**: Los modelos usan GPU si está disponible
2. **Reduce resolución**: Usa 640x480 en lugar de 1280x720
3. **Desactiva modelos no necesarios**: Solo activa los que usas

### Falsos positivos

1. **Aumenta umbral**: Sube el threshold a 0.7-0.8
2. **Usa filtrado**: El sistema ya tiene filtrado inteligente
3. **Reporta problemas**: Los modelos mejoran con feedback

## 📝 Notas Técnicas

### COCO-SSD
- Usa MobileNet v2 como backbone
- Detecta 80 clases COCO
- Optimizado para navegadores
- Funciona en CPU y GPU

### MediaPipe
- Modelos optimizados por Google
- Usa WebAssembly para velocidad
- Soporte para GPU (WebGL)
- Muy rápido en tiempo real

## 🔮 Próximos Pasos

### Modelos Adicionales (Opcional)

1. **YOLO ONNX**: Para mayor precisión (requiere modelo)
2. **Emotion Detection**: Modelo especializado para emociones
3. **Gesture Recognition**: Reconocimiento de gestos con MediaPipe Hands

### Mejoras Futuras

1. **Caché de modelos**: Guardar modelos localmente
2. **Modelos personalizados**: Entrenar modelos específicos
3. **Optimización**: Cuantización y optimización de modelos

## 📚 Recursos

- [TensorFlow.js](https://www.tensorflow.org/js)
- [MediaPipe](https://mediapipe.dev/)
- [COCO Dataset](https://cocodataset.org/)
- [COCO-SSD Model](https://github.com/tensorflow/tfjs-models/tree/master/coco-ssd)

---

**Última actualización**: Enero 2025
**Versión**: 2.0


