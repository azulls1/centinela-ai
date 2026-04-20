# Model Card: MediaPipe Pose Landmarker Full

## Model Details
- **Name:** Pose Landmarker Full
- **Version:** MediaPipe Tasks Vision 0.10.9
- **Type:** Full-body pose estimation (33 landmarks)
- **Framework:** MediaPipe (WASM/GPU)
- **License:** Apache 2.0

## Intended Use
- Person detection via body pose estimation
- Activity classification (standing, sitting, walking)
- Supports up to 5 simultaneous poses

## Performance
- **Input:** ImageData from canvas
- **Inference Time:** ~30-80ms (GPU), ~100-250ms (CPU)
- **Landmarks:** 33 body keypoints per person
- **Max Poses:** 5 simultaneous

## Limitations
- Full model is heavier than lite (~5MB vs ~2MB)
- Accuracy drops with heavy clothing or unusual poses
- Cannot distinguish between individuals (no re-ID)
- Z-coordinate (depth) has limited accuracy

## Bias & Fairness
- Trained on diverse body types but may underperform for:
  - Wheelchair users
  - People with prosthetics
  - Non-standard body proportions
- Activity classification heuristic is simple and not validated
