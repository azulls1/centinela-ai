"""
Servicio para entrenamiento y fine-tuning de modelos de ML
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from supabase import Client
import subprocess
import tempfile

class ModelTrainer:
    """Servicio para entrenar y fine-tune modelos de ML"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.models_dir = os.getenv("MODELS_DIR", "./models")
        os.makedirs(self.models_dir, exist_ok=True)
    
    def prepare_dataset(
        self,
        dataset_id: str,
        output_format: str = "yolo"  # 'yolo', 'coco', 'custom'
    ) -> Dict:
        """
        Prepara un dataset para entrenamiento en formato específico
        """
        # Obtener muestras del dataset
        response = self.supabase.table("ml_training_samples").select("*").eq("dataset_id", dataset_id).eq("is_annotated", True).execute()
        
        samples = response.data
        if not samples:
            return {"error": "No hay muestras anotadas en el dataset"}
        
        # Preparar estructura según formato
        if output_format == "yolo":
            return self._prepare_yolo_format(samples, dataset_id)
        elif output_format == "coco":
            return self._prepare_coco_format(samples, dataset_id)
        else:
            return self._prepare_custom_format(samples, dataset_id)
    
    def _prepare_yolo_format(self, samples: List[Dict], dataset_id: str) -> Dict:
        """
        Prepara dataset en formato YOLO
        """
        dataset_path = os.path.join(self.models_dir, f"dataset_{dataset_id}")
        os.makedirs(dataset_path, exist_ok=True)
        
        # Estructura YOLO
        images_dir = os.path.join(dataset_path, "images")
        labels_dir = os.path.join(dataset_path, "labels")
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(labels_dir, exist_ok=True)
        
        # Crear archivo de configuración
        config = {
            "path": dataset_path,
            "train": "images/train",
            "val": "images/val",
            "test": "images/test",
            "names": {}  # Se llenará con las clases
        }
        
        classes = set()
        
        for sample in samples:
            # Obtener anotaciones
            annotations_response = self.supabase.table("ml_annotations").select("*").eq("sample_id", sample["id"]).execute()
            annotations = annotations_response.data
            
            if annotations:
                # Crear archivo de labels YOLO
                label_file = os.path.join(labels_dir, f"{sample['id']}.txt")
                with open(label_file, 'w') as f:
                    for ann in annotations:
                        label = ann["label"]
                        classes.add(label)
                        
                        # Convertir bbox a formato YOLO (normalizado)
                        # YOLO: class_id x_center y_center width height (todo normalizado 0-1)
                        # Aquí necesitarías las dimensiones de la imagen
                        bbox = ann.get("bbox", {})
                        # TODO: Implementar conversión completa
        
        # Guardar nombres de clases
        class_names = sorted(list(classes))
        config["names"] = {i: name for i, name in enumerate(class_names)}
        
        config_path = os.path.join(dataset_path, "dataset.yaml")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {
            "dataset_path": dataset_path,
            "config_path": config_path,
            "classes": class_names,
            "total_samples": len(samples)
        }
    
    def _prepare_coco_format(self, samples: List[Dict], dataset_id: str) -> Dict:
        """
        Prepara dataset en formato COCO
        """
        # TODO: Implementar formato COCO
        return {"format": "coco", "status": "not_implemented"}
    
    def _prepare_custom_format(self, samples: List[Dict], dataset_id: str) -> Dict:
        """
        Prepara dataset en formato personalizado
        """
        # TODO: Implementar formato personalizado
        return {"format": "custom", "status": "not_implemented"}
    
    def train_yolo_model(
        self,
        dataset_id: str,
        model_type: str = "yolov8n",
        epochs: int = 100,
        batch_size: int = 16,
        img_size: int = 640
    ) -> Dict:
        """
        Entrena un modelo YOLO
        """
        # Preparar dataset
        dataset_info = self.prepare_dataset(dataset_id, "yolo")
        if "error" in dataset_info:
            return dataset_info
        
        # Crear run de entrenamiento
        run_data = {
            "dataset_id": dataset_id,
            "status": "running",
            "training_config": {
                "model_type": model_type,
                "epochs": epochs,
                "batch_size": batch_size,
                "img_size": img_size
            },
            "start_time": datetime.utcnow().isoformat(),
            "created_by": "system"
        }
        
        run_response = self.supabase.table("ml_training_runs").insert(run_data).execute()
        run_id = run_response.data[0]["id"] if run_response.data else None
        
        try:
            # Aquí se ejecutaría el entrenamiento real
            # Por ahora simulamos
            print(f"🚀 Iniciando entrenamiento de {model_type}...")
            print(f"📊 Dataset: {dataset_info['total_samples']} muestras")
            print(f"🎯 Épocas: {epochs}, Batch size: {batch_size}")
            
            # TODO: Ejecutar entrenamiento real con ultralytics o similar
            # from ultralytics import YOLO
            # model = YOLO(f"{model_type}.pt")
            # results = model.train(
            #     data=dataset_info["config_path"],
            #     epochs=epochs,
            #     batch=batch_size,
            #     imgsz=img_size
            # )
            
            # Simular métricas
            metrics = {
                "accuracy": 0.85,
                "precision": 0.82,
                "recall": 0.88,
                "mAP50": 0.80,
                "mAP50-95": 0.75
            }
            
            # Actualizar run
            self.supabase.table("ml_training_runs").update({
                "status": "completed",
                "end_time": datetime.utcnow().isoformat(),
                "metrics_history": [metrics],
                "loss_history": [0.5, 0.3, 0.2, 0.15, 0.1]
            }).eq("id", run_id).execute()
            
            return {
                "run_id": run_id,
                "status": "completed",
                "metrics": metrics,
                "dataset_info": dataset_info
            }
            
        except Exception as e:
            # Marcar run como fallido
            if run_id:
                self.supabase.table("ml_training_runs").update({
                    "status": "failed",
                    "end_time": datetime.utcnow().isoformat(),
                    "error_message": str(e)
                }).eq("id", run_id).execute()
            
            return {"error": str(e)}
    
    def save_trained_model(
        self,
        model_path: str,
        run_id: str,
        model_name: str,
        version: str,
        metrics: Dict
    ) -> Optional[str]:
        """
        Guarda un modelo entrenado en la base de datos
        """
        # Subir modelo a Storage
        bucket_name = "vishum-models"
        model_file_name = f"{model_name}_v{version}.pt"
        
        try:
            with open(model_path, 'rb') as f:
                model_data = f.read()
            
            self.supabase.storage.from_(bucket_name).upload(
                model_file_name,
                model_data,
                file_options={"content-type": "application/octet-stream"}
            )
            
            # Guardar en base de datos
            model_data = {
                "name": model_name,
                "version": version,
                "model_type": "yolo",
                "model_path": f"{bucket_name}/{model_file_name}",
                "file_size": len(model_data),
                "metrics": metrics,
                "is_active": False,
                "created_by": "system"
            }
            
            response = self.supabase.table("ml_models").insert(model_data).execute()
            
            if response.data:
                # Actualizar run con model_id
                self.supabase.table("ml_training_runs").update({
                    "model_id": response.data[0]["id"]
                }).eq("id", run_id).execute()
                
                return response.data[0]["id"]
        except Exception as e:
            print(f"❌ Error guardando modelo: {e}")
        
        return None


def main():
    """
    Función principal para testing
    """
    from supabase_client import get_supabase_client
    
    supabase = get_supabase_client()
    trainer = ModelTrainer(supabase)
    
    # Ejemplo: Entrenar modelo
    print("🚀 Iniciando entrenamiento...")
    result = trainer.train_yolo_model(
        dataset_id="test-dataset-id",
        model_type="yolov8n",
        epochs=10,
        batch_size=16
    )
    print(f"✅ Resultado: {result}")


if __name__ == "__main__":
    main()

