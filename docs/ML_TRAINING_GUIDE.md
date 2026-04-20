# 🧠 Guía de Entrenamiento de Modelos - Vision Human Insight

Esta guía explica cómo entrenar y mejorar modelos de Machine Learning para el sistema de visión por computadora.

## 📋 Tabla de Contenidos

1. [Arquitectura del Sistema](#arquitectura)
2. [Recolección de Datos](#recoleccion)
3. [Preparación de Datasets](#preparacion)
4. [Entrenamiento de Modelos](#entrenamiento)
5. [Mejora Continua](#mejora)
6. [Librerías y Herramientas](#librerias)

## 🏗️ Arquitectura del Sistema {#arquitectura}

### Tablas de Base de Datos

El sistema utiliza las siguientes tablas para gestionar el entrenamiento:

- **`ml_datasets`**: Información sobre datasets de entrenamiento
- **`ml_training_samples`**: Muestras individuales (imágenes/videos)
- **`ml_annotations`**: Anotaciones detalladas de cada muestra
- **`ml_models`**: Información sobre modelos entrenados
- **`ml_training_runs`**: Registro de ejecuciones de entrenamiento
- **`ml_scraped_data`**: Datos scrapeados de fuentes externas

### Flujo de Datos

```
1. Recolección de Datos
   ├── Scraping de fuentes públicas (Unsplash, Pexels)
   ├── Captura de eventos en tiempo real
   └── Importación de datasets públicos

2. Anotación
   ├── Anotación automática (con modelos base)
   ├── Revisión manual
   └── Validación de calidad

3. Preparación de Dataset
   ├── Conversión a formato YOLO/COCO
   ├── División train/val/test
   └── Data augmentation

4. Entrenamiento
   ├── Fine-tuning de modelos base
   ├── Entrenamiento desde cero (opcional)
   └── Validación y evaluación

5. Despliegue
   ├── Exportación a formato ONNX
   ├── Subida a Supabase Storage
   └── Activación en producción
```

## 🔍 Recolección de Datos {#recoleccion}

### 1. Scraping de Fuentes Públicas

#### Unsplash

```python
from services.data_collector import DataCollector

async with DataCollector(supabase) as collector:
    # Scrapear imágenes de personas
    images = await collector.scrape_unsplash_images(
        query="person",
        count=100,
        categories=["people", "portrait"]
    )
    
    # Guardar en base de datos
    await collector.save_scraped_data(images, dataset_id="my-dataset")
```

**Configuración:**
1. Obtener API key de [Unsplash Developers](https://unsplash.com/developers)
2. Agregar a `.env`: `UNSPLASH_ACCESS_KEY=tu_api_key`

#### Pexels

```python
# Similar a Unsplash
images = await collector.scrape_pexels_images(
    query="person",
    count=100
)
```

**Configuración:**
1. Obtener API key de [Pexels API](https://www.pexels.com/api/)
2. Agregar a `.env`: `PEXELS_API_KEY=tu_api_key`

### 2. Recolección desde Eventos en Tiempo Real

El sistema puede recolectar automáticamente imágenes de eventos detectados:

```python
# Recolectar imágenes de eventos del último día
collected = await collector.collect_from_events(
    hours=24,
    min_confidence=0.7
)
```

### 3. Importación de Datasets Públicos

#### COCO Dataset

```bash
# Descargar COCO dataset
wget http://images.cocodataset.org/zips/train2017.zip
wget http://images.cocodataset.org/zips/val2017.zip
wget http://images.cocodataset.org/annotations/annotations_trainval2017.zip

# Extraer y procesar
unzip train2017.zip
unzip annotations_trainval2017.zip
```

#### Open Images Dataset

```bash
# Descargar Open Images
wget https://storage.googleapis.com/openimages/2018_04/train/train-images-boxable.tar.gz
```

## 📊 Preparación de Datasets {#preparacion}

### 1. Crear un Dataset

```python
from supabase import create_client

supabase = create_client(url, key)

# Crear dataset
dataset = supabase.table("ml_datasets").insert({
    "name": "person-detection-v1",
    "description": "Dataset para detección de personas",
    "source_type": "scraped",
    "categories": ["person", "face", "body"]
}).execute()
```

### 2. Agregar Muestras

```python
# Agregar muestra de entrenamiento
sample = supabase.table("ml_training_samples").insert({
    "dataset_id": dataset_id,
    "file_path": "vishum-images/sample1.jpg",
    "file_type": "image",
    "file_format": "jpg",
    "width": 1920,
    "height": 1080,
    "quality_score": 0.9
}).execute()
```

### 3. Anotar Muestras

```python
# Agregar anotación
annotation = supabase.table("ml_annotations").insert({
    "sample_id": sample_id,
    "annotation_type": "object",
    "label": "person",
    "bbox": {"x": 100, "y": 200, "width": 300, "height": 500},
    "is_manual": True,
    "is_verified": True
}).execute()
```

### 4. Preparar para Entrenamiento

```python
from services.model_trainer import ModelTrainer

trainer = ModelTrainer(supabase)

# Preparar dataset en formato YOLO
dataset_info = trainer.prepare_dataset(
    dataset_id="my-dataset",
    output_format="yolo"
)
```

## 🚀 Entrenamiento de Modelos {#entrenamiento}

### 1. Fine-tuning de YOLO

```python
from services.model_trainer import ModelTrainer

trainer = ModelTrainer(supabase)

# Entrenar modelo YOLO
result = trainer.train_yolo_model(
    dataset_id="my-dataset",
    model_type="yolov8n",  # o yolov8s, yolov8m, yolov8l, yolov8x
    epochs=100,
    batch_size=16,
    img_size=640
)

print(f"Métricas: {result['metrics']}")
```

### 2. Entrenamiento con Ultralytics

```python
from ultralytics import YOLO

# Cargar modelo base
model = YOLO("yolov8n.pt")

# Entrenar
results = model.train(
    data="dataset.yaml",
    epochs=100,
    batch=16,
    imgsz=640,
    device="cuda"  # o "cpu"
)

# Exportar a ONNX para uso en web
model.export(format="onnx")
```

### 3. Entrenamiento de Modelos de Emoción

```python
from transformers import AutoModelForImageClassification, TrainingArguments, Trainer
from datasets import load_dataset

# Cargar dataset de emociones
dataset = load_dataset("imdb")  # Ejemplo

# Cargar modelo base
model = AutoModelForImageClassification.from_pretrained("google/vit-base-patch16-224")

# Configurar entrenamiento
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=10,
    per_device_train_batch_size=16,
)

# Entrenar
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
)
trainer.train()
```

## 🔄 Mejora Continua {#mejora}

### 1. Active Learning

El sistema puede identificar muestras que necesitan más entrenamiento:

```python
# Obtener muestras con baja confianza
low_confidence_samples = supabase.table("ml_training_samples").select("*").lt("quality_score", 0.5).execute()

# Priorizar estas muestras para anotación
```

### 2. Data Augmentation

```python
import albumentations as A

# Definir transformaciones
transform = A.Compose([
    A.RandomRotate90(),
    A.Flip(),
    A.RandomBrightnessContrast(),
    A.HueSaturationValue(),
])

# Aplicar a imágenes
augmented = transform(image=image, bboxes=bboxes)
```

### 3. Versionado de Modelos

```python
# Guardar modelo entrenado
model_id = trainer.save_trained_model(
    model_path="./runs/detect/train/weights/best.pt",
    run_id=run_id,
    model_name="person-detector",
    version="1.1.0",
    metrics=metrics
)

# Activar modelo en producción
supabase.table("ml_models").update({
    "is_active": True
}).eq("id", model_id).execute()
```

## 📚 Librerías y Herramientas {#librerias}

### Librerías Principales

1. **Ultralytics YOLO**: Detección de objetos
   ```bash
   pip install ultralytics
   ```

2. **TensorFlow/PyTorch**: Deep Learning
   ```bash
   pip install tensorflow torch torchvision
   ```

3. **Hugging Face Transformers**: Modelos pre-entrenados
   ```bash
   pip install transformers datasets
   ```

4. **Albumentations**: Data augmentation
   ```bash
   pip install albumentations
   ```

5. **MLflow**: Tracking de experimentos
   ```bash
   pip install mlflow
   ```

### Herramientas de Anotación

1. **LabelImg**: Anotación de bounding boxes
   ```bash
   pip install labelimg
   labelimg
   ```

2. **LabelMe**: Anotación más avanzada
   ```bash
   pip install labelme
   labelme
   ```

3. **Roboflow**: Plataforma online para anotación

### Monitoreo y Visualización

1. **TensorBoard**: Visualizar entrenamiento
   ```bash
   tensorboard --logdir=./runs
   ```

2. **Weights & Biases**: Tracking avanzado
   ```bash
   pip install wandb
   wandb login
   ```

## 🎯 Mejores Prácticas

1. **Diversidad de Datos**: Asegúrate de tener muestras variadas
2. **Balance de Clases**: Evita desbalance excesivo
3. **Validación**: Siempre reserva un conjunto de validación
4. **Versionado**: Mantén versiones de modelos y datasets
5. **Documentación**: Documenta cada entrenamiento
6. **Evaluación**: Usa múltiples métricas (mAP, accuracy, precision, recall)

## 📝 Ejemplo Completo

```python
# 1. Crear dataset
dataset = create_dataset("person-detection-v2")

# 2. Recolectar datos
collector = DataCollector(supabase)
images = await collector.scrape_unsplash_images("person", count=500)
await collector.save_scraped_data(images, dataset["id"])

# 3. Anotar (manual o automático)
annotate_samples(dataset["id"])

# 4. Preparar dataset
trainer = ModelTrainer(supabase)
dataset_info = trainer.prepare_dataset(dataset["id"], "yolo")

# 5. Entrenar
result = trainer.train_yolo_model(
    dataset_id=dataset["id"],
    epochs=100
)

# 6. Guardar y activar
model_id = trainer.save_trained_model(
    model_path=result["model_path"],
    run_id=result["run_id"],
    model_name="person-detector",
    version="2.0.0",
    metrics=result["metrics"]
)

# Activar en producción
activate_model(model_id)
```

## 🔗 Recursos Adicionales

- [Documentación de YOLO](https://docs.ultralytics.com/)
- [Hugging Face](https://huggingface.co/)
- [TensorFlow Tutorials](https://www.tensorflow.org/tutorials)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)

---

**Nota**: Este sistema está diseñado para aprendizaje continuo. Cuanto más uses la aplicación, mejor serán los modelos entrenados.

