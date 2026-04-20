#!/bin/bash
# Download YOLOv8n ONNX model
MODELS_DIR="$(dirname "$0")/../public/models"
mkdir -p "$MODELS_DIR"

if [ ! -f "$MODELS_DIR/yolov8n.onnx" ]; then
  echo "Downloading YOLOv8n ONNX model..."
  curl -L -o "$MODELS_DIR/yolov8n.onnx" "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.onnx"
  echo "Done! Model saved to $MODELS_DIR/yolov8n.onnx"
else
  echo "Model already exists at $MODELS_DIR/yolov8n.onnx"
fi
