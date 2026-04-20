# 05 - IA & Modelos

> Evaluacion basada en evidencia del codigo fuente del proyecto Vision Human Insight.
> Fecha: 2026-04-05

---

## Resumen Ejecutivo

| # | Area                     | Puntaje | Estado       |
|---|--------------------------|---------|--------------|
| 1 | Calidad del Modelo       | 5/10    | Medio        |
| 2 | Latencia de Inferencia   | 6/10    | Medio        |
| 3 | Data Drift               | 1/10    | Critico      |
| 4 | Sesgo & Fairness         | 2/10    | Critico      |
| 5 | Calidad del Dataset      | 2/10    | Critico      |
| 6 | Costo por Inferencia     | 5/10    | Medio        |
| 7 | Versionado de Prompts    | 1/10    | Critico      |
| **Promedio**              | **3.1/10** | **Critico** |

---

## 1. Calidad del Modelo (5/10)

### Evidencia

| Aspecto | Hallazgo | Archivo |
|---------|----------|---------|
| Deteccion de objetos | COCO-SSD con `base: 'mobilenet_v2'`, 80 clases COCO, umbral 0.5 | `apps/web/src/lib/ml/models/coco-ssd.ts:62` |
| Deteccion de rostros | `blaze_face_short_range` float16, minDetectionConfidence 0.5 | `apps/web/src/lib/ml/models/mediapipe-face.ts:42-43` |
| Deteccion de poses | `pose_landmarker_full` float16 (variante completa, no lite), hasta 5 poses | `apps/web/src/lib/ml/models/mediapipe-pose.ts:13-14, 48` |
| Deteccion de emociones | Heuristica manual basada en 6 landmarks faciales (distancias nariz-boca, ojos) | `apps/web/src/lib/ml/processors.ts:486-526` |
| Deteccion de movimiento | Diferencia pixel-a-pixel entre frames consecutivos, muestreo cada 4to pixel | `apps/web/src/lib/ml/processors.ts:586-612` |
| Metricas de precision | No existen. Cero benchmarks, F1 scores ni evaluaciones documentadas | N/A |
| Confianza de pose hardcodeada | MediaPipe Pose no devuelve confianza por pose, se asume `0.85` fijo | `apps/web/src/lib/ml/processors.ts:102` |

### Hallazgos

- **Modelos reales y reconocidos**: Se usan modelos pre-entrenados de calidad (COCO-SSD MobileNetV2, MediaPipe BlazeFace, MediaPipe Pose Landmarker Full). Esto es correcto para un MVP.
- **Deteccion de emociones es una heuristica fragil**: No usa un modelo ML real. Se basa en solo 6 landmarks faciales de BlazeFace (ojos, nariz, boca, orejas) y calcula ratios geometricos simples (distancia boca-nariz / distancia entre ojos). Solo detecta 5 emociones: `surprised`, `happy`, `sad`, `angry`, `focused`. Los umbrales son arbitrarios (0.85, 0.65, 0.55, 0.35).
- **Deteccion de movimiento es primitiva**: Diferencia de pixeles sin optical flow, sin compensacion de movimiento de camara, sin segmentacion. Alta tasa de falsos positivos ante cambios de iluminacion.
- **Confianza de pose inventada**: El valor `0.85` hardcodeado no refleja confianza real del modelo.
- **No hay metricas ni evaluaciones**: Cero benchmarks en ningun formato (mAP, precision, recall, F1).

### Recomendacion

- Reemplazar la heuristica de emociones por un modelo real (FER-2013 fine-tuned, o MobileFaceNet).
- Implementar metricas de evaluacion offline para cada modelo contra un conjunto de test.
- Usar optical flow (Lucas-Kanade) o background subtraction para deteccion de movimiento.
- Documentar las limitaciones conocidas de cada modelo en un model card.

---

## 2. Latencia de Inferencia (6/10)

### Evidencia

| Aspecto | Hallazgo | Archivo |
|---------|----------|---------|
| Frame interval minimo | `MIN_FRAME_INTERVAL_MS = 400` (2.5 FPS maximo para ML) | `processors.ts:140` |
| Resolucion de procesamiento | `targetWidth = Math.min(480, canvas.width)`, aspecto proporcional | `processors.ts:184-185` |
| Backend GPU (TF.js) | Intenta WebGL primero, fallback a CPU | `coco-ssd.ts:24-29` |
| Backend GPU (MediaPipe) | `delegate: 'GPU'` con fallback a CPU para Face y Pose | `mediapipe-face.ts:40-58`, `mediapipe-pose.ts:41-65` |
| Web Workers | No se usan. Todo corre en el hilo principal (main thread) | Sin coincidencias en busqueda |
| Carga paralela | `Promise.allSettled` para cargar los 3 modelos en paralelo | `processors.ts:97-101` |
| Yield al main thread | `yieldToMainThread()` entre cada etapa de deteccion | `processors.ts:178-179, 225, 265, 282, 289` |
| Estabilizacion temporal | Emociones: 1.5s ventana, Actividad: 1.8s ventana, Personas: 1.2s ventana | `processors.ts:462, 558, 360` |

### Hallazgos

- **Buena estrategia de reduccion de resolucion**: Procesar a 480px max reduce significativamente la carga de inferencia.
- **GPU acelerada con fallback**: Correcto patron de intentar GPU primero y caer a CPU.
- **Sin Web Workers**: El procesamiento ML corre en el main thread. Aunque hay `yieldToMainThread()` para no bloquear completamente, esto puede causar jank en la UI especialmente en dispositivos de gama baja.
- **2.5 FPS es razonable** para deteccion pero insuficiente para tracking fluido.
- **Sin metricas de latencia**: No se mide ni reporta el tiempo real de inferencia por frame.

### Recomendacion

- Mover el pipeline de inferencia a un Web Worker o OffscreenCanvas para liberar el main thread.
- Instrumentar el tiempo de inferencia por modelo y exponerlo en el panel de rendimiento.
- Considerar `requestIdleCallback` en lugar de `setTimeout(0)` para yields.

---

## 3. Data Drift (1/10)

### Evidencia

| Aspecto | Hallazgo | Archivo |
|---------|----------|---------|
| Monitoreo de rendimiento del modelo | No existe | Busqueda sin resultados |
| Logging de detecciones para analisis | Solo `debugLog` silenciado (`const debugLog = (..._args: unknown[]) => {}`) | `processors.ts:6` |
| Feedback loop | No existe mecanismo de retroalimentacion | N/A |
| Tracking de confianza en el tiempo | No hay persistencia de scores de confianza | N/A |
| Alertas de degradacion | No existen | N/A |

### Hallazgos

- **No hay absolutamente ninguna infraestructura de monitoreo de data drift**. Los modelos pre-entrenados se usan tal cual sin ninguna verificacion de que su rendimiento se mantenga estable.
- Las funciones de debug estan completamente desactivadas (`debugLog` es un no-op), lo que significa que incluso durante desarrollo no se recopilan datos de rendimiento.
- No hay mecanismo para detectar si la distribucion de datos de entrada cambia (ej: iluminacion diferente, tipos de camaras nuevas, angulos distintos).

### Recomendacion

- Implementar logging persistente de scores de confianza promedio por sesion.
- Crear alertas cuando la confianza promedio caiga por debajo de un umbral.
- Registrar distribucion de clases detectadas por periodo para detectar cambios.
- Implementar un endpoint de monitoreo que agregue metricas de inferencia.

---

## 4. Sesgo & Fairness (2/10)

### Evidencia

| Aspecto | Hallazgo | Archivo |
|---------|----------|---------|
| Heuristica de emociones | Basada en geometria facial (ratios de distancias entre landmarks) | `processors.ts:494-526` |
| Modelo de rostros | BlazeFace Short Range - conocido por menor precision en tonos de piel oscuros | `mediapipe-face.ts:42` |
| Modelo de objetos | COCO-SSD - entrenado en COCO dataset (sesgo geografico occidental) | `coco-ssd.ts:62` |
| Documentacion de limitaciones | No existe documentacion de sesgos o limitaciones | N/A |
| Plantilla model card | Existe `plantillas/entregables/ml-model-card.md` pero no se usa | Busqueda de archivos |
| Testing de equidad | No existe | N/A |

### Hallazgos

- **La heuristica de emociones es inherentemente sesgada**: Las proporciones faciales varian significativamente entre etnias, edades y generos. Una distancia boca-nariz "normal" para una etnia puede clasificarse como "angry" o "surprised" para otra. Esto es un riesgo serio.
- **BlazeFace Short Range** tiene limitaciones documentadas por Google en condiciones de baja iluminacion y con tonos de piel oscuros.
- **COCO dataset** tiene sesgo geografico conocido (predominantemente imagenes de contextos occidentales).
- **No hay model card ni documentacion de sesgos**. Existe una plantilla (`ml-model-card.md`) pero no se ha completado para ninguno de los modelos usados.
- **No hay testing de equidad** entre diferentes demografias.

### Recomendacion

- Reemplazar urgentemente la heuristica de emociones por un modelo entrenado con diversidad demografica.
- Completar model cards para los 3 modelos en uso, documentando sesgos conocidos.
- Agregar disclaimer visible al usuario sobre limitaciones de la deteccion de emociones.
- Considerar FairFace o datasets balanceados para validacion de equidad.

---

## 5. Calidad del Dataset (2/10)

### Evidencia

| Aspecto | Hallazgo | Archivo |
|---------|----------|---------|
| Datasets de entrenamiento | No existen datasets en el proyecto | N/A |
| Infraestructura de training | `ModelTrainer` existe pero con TODOs en funciones criticas | `apps/api/services/model_trainer.py` |
| Formato YOLO | Preparacion parcial, falta conversion de bbox (`TODO: Implementar conversion completa`) | `model_trainer.py:85` |
| Formato COCO | `return {"format": "coco", "status": "not_implemented"}` | `model_trainer.py:107` |
| Entrenamiento real | Comentado: `# TODO: Ejecutar entrenamiento real con ultralytics` | `model_trainer.py:157-164` |
| Metricas | Hardcodeadas/simuladas: `accuracy: 0.85, precision: 0.82...` | `model_trainer.py:167-171` |
| Guia de entrenamiento | Documento extenso pero teorico, sin implementacion real | `docs/ML_TRAINING_GUIDE.md` |
| Schema SQL | Tablas `ml_datasets`, `ml_training_samples`, `ml_annotations` definidas | `infra/supabase/ml_training_setup.sql` |

### Hallazgos

- **No hay datasets reales en el proyecto**. Se usan exclusivamente modelos pre-entrenados sin ningun fine-tuning.
- **La infraestructura de entrenamiento es un stub**: `ModelTrainer` tiene la estructura correcta pero las funciones criticas estan sin implementar (TODOs). Las metricas son valores simulados hardcodeados.
- **La guia de entrenamiento es documentacion aspiracional**: Describe un flujo completo de recoleccion -> anotacion -> entrenamiento -> despliegue, pero nada de esto esta implementado.
- **El schema de base de datos para ML existe** pero no se usa activamente.

### Recomendacion

- Priorizar la implementacion real del pipeline de entrenamiento o eliminarlo del codigo.
- Si se usan solo modelos pre-entrenados, documentar esa decision explicitamente.
- Completar la conversion de bounding boxes en formato YOLO.
- Implementar al menos el pipeline de validacion con un pequeno dataset de prueba.

---

## 6. Costo por Inferencia (5/10)

### Evidencia

| Aspecto | Hallazgo | Archivo |
|---------|----------|---------|
| Inferencia client-side | 100% en navegador (TF.js + MediaPipe WASM), costo servidor = $0 | `processors.ts`, modelos en `/models/` |
| Tamano de modelos | COCO-SSD ~10MB, Face ~2MB, Pose ~5MB (CDN, cache del navegador) | `processors.ts:85-88` |
| OpenAI API - Resumen | `gpt-4o-mini`, max 500 tokens, temperature 0.7 | `ai_summary.py:121-122, 133` |
| OpenAI API - Validacion | `gpt-4o-mini` con vision (imagen base64), max 500 tokens | `ai_summary.py:247-248` |
| OpenAI API - TTS | Modelo `tts-1` para audio | `ai_summary.py:172-173` |
| Tracking de costos | No existe ningun mecanismo de tracking de uso/costos de API | N/A |
| Rate limiting | No hay rate limiting en endpoints de OpenAI | `ai_summary.py` |
| Caching de respuestas | Solo `@lru_cache(maxsize=1)` para el cliente, no para respuestas | `ai_summary.py:22` |

### Hallazgos

- **Buena decision arquitectural**: La inferencia principal (deteccion de objetos, rostros, poses) es 100% client-side, eliminando costos de servidor por inferencia.
- **OpenAI gpt-4o-mini es economico**: ~$0.15/1M input tokens, ~$0.60/1M output tokens. Con max 500 tokens de salida, cada resumen cuesta fracciones de centavo.
- **Sin tracking de costos**: No hay forma de saber cuanto se esta gastando en OpenAI API. No hay conteo de tokens, no hay logging de uso.
- **Sin rate limiting**: Los endpoints `/generate-summary`, `/validate-detections`, y `/generate-voice-description` no tienen rate limiting, lo que permite abuso y costos inesperados.
- **Validacion con vision envia imagen base64 completa**: Potencialmente costoso en tokens de input si las imagenes son grandes.

### Recomendacion

- Implementar rate limiting en todos los endpoints que llaman a OpenAI.
- Agregar tracking de tokens usados por request y acumular costos.
- Implementar cache de respuestas para resumenes similares.
- Limitar el tamano de las imagenes base64 antes de enviarlas a la API de vision.
- Agregar un dashboard de costos de API.

---

## 7. Versionado de Prompts (1/10)

### Evidencia

| Aspecto | Hallazgo | Archivo |
|---------|----------|---------|
| Prompt de resumen | Inline, hardcodeado en funcion `generate_ai_summary` | `ai_summary.py:105-117` |
| System prompt de resumen | Inline: `"Eres un asistente experto en analisis de datos..."` | `ai_summary.py:125-126` |
| Prompt de validacion | Inline, hardcodeado en funcion `validate_detections_with_openai` | `ai_summary.py:230-244` |
| System prompt de validacion | Inline: `"Eres un experto en analisis de imagenes..."` | `ai_summary.py:252-253` |
| Versionado | No existe ningun sistema de versionado de prompts | Busqueda sin resultados |
| Archivos de configuracion de prompts | No existen | N/A |
| Historial de cambios de prompts | No existe | N/A |
| A/B testing de prompts | No existe | N/A |

### Hallazgos

- **Todos los prompts estan hardcodeados directamente en las funciones**: No hay separacion entre logica y contenido de prompts.
- **No hay versionado**: Si se cambia un prompt, no queda registro del anterior. No hay forma de hacer rollback.
- **No hay configuracion externalizada**: Los prompts no se pueden cambiar sin modificar codigo y redesplegar.
- **Idioma parcialmente parametrizado**: El prompt de resumen recibe `language` como parametro pero el prompt siempre dice "Responde SOLO en espanol" hardcodeado, contradiciendo el parametro.
- **No hay A/B testing**: No hay forma de comparar efectividad de diferentes versiones de prompts.

### Recomendacion

- Extraer todos los prompts a archivos de configuracion separados (ej: `prompts/v1/summary.txt`).
- Implementar un sistema de versionado simple (ej: carpetas por version o tabla en base de datos).
- Corregir la inconsistencia del idioma en el prompt de resumen.
- Agregar logging de prompt version usado en cada request.
- Considerar una tabla `prompt_versions` en Supabase para gestionar prompts dinamicamente.

---

## Puntaje Global: 3.1 / 10

### Fortalezas
- Modelos pre-entrenados de buena calidad (COCO-SSD, MediaPipe).
- Inferencia client-side elimina costos de servidor.
- GPU acceleration con fallback a CPU.
- Resolucion reducida para procesamiento ML.

### Debilidades Criticas
- Deteccion de emociones basada en heuristica fragil y potencialmente sesgada.
- Cero monitoreo de data drift o rendimiento del modelo.
- Infraestructura de entrenamiento sin implementar (solo stubs).
- Prompts hardcodeados sin versionado.
- Sin metricas de evaluacion de ningun modelo.
- Sin documentacion de sesgos o limitaciones.

### Prioridades de Mejora
1. **P0**: Documentar limitaciones y sesgos de los modelos (model cards).
2. **P0**: Agregar disclaimer de emociones al usuario.
3. **P1**: Extraer y versionar prompts de OpenAI.
4. **P1**: Implementar rate limiting en endpoints de OpenAI.
5. **P2**: Reemplazar heuristica de emociones por modelo ML real.
6. **P2**: Mover inferencia a Web Worker.
7. **P3**: Implementar monitoreo de data drift.
