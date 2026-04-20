# Model Card: COCO-SSD (MobileNet V2)

## Model Details
- **Name:** COCO-SSD with MobileNet V2 backbone
- **Version:** TensorFlow.js @tensorflow-models/coco-ssd
- **Type:** Object Detection (Single Shot MultiBox Detector)
- **Framework:** TensorFlow.js (WebGL/CPU backends)
- **License:** Apache 2.0

## Intended Use
- Real-time object detection in browser for surveillance/monitoring
- Detects 80 COCO classes including persons, devices, furniture, vehicles
- Optimized for 480px input resolution

## Performance
- **Input Resolution:** 480x360 (downscaled from camera feed)
- **Inference Time:** ~50-150ms (GPU), ~200-500ms (CPU)
- **mAP (COCO val):** ~22% (MobileNet V2 base)
- **Classes:** 80 COCO categories

## Limitations
- Accuracy drops significantly for small objects (<32px)
- Performance varies with lighting conditions
- May miss partially occluded objects
- MobileNet V2 trades accuracy for speed

## Ethical Considerations
- Person detection may have varying accuracy across demographics
- Not suitable for critical security decisions without human oversight
- Privacy implications of continuous video monitoring

## Bias & Fairness
- COCO dataset has known demographic imbalances
- Better performance on well-lit, frontal views
- May underperform in non-Western indoor environments
