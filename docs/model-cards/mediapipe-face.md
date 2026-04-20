# Model Card: MediaPipe BlazeFace Short Range

## Model Details
- **Name:** BlazeFace Short Range
- **Version:** MediaPipe Tasks Vision 0.10.9
- **Type:** Face Detection + 6 Keypoints
- **Framework:** MediaPipe (WASM/GPU)
- **License:** Apache 2.0

## Intended Use
- Real-time face detection for emotion analysis pipeline
- Provides 6 facial keypoints (eyes, nose, mouth, ears)
- Optimized for short-range (selfie/webcam) scenarios

## Performance
- **Input:** ImageData from canvas
- **Inference Time:** ~10-30ms (GPU), ~30-80ms (CPU)
- **Precision:** >95% for frontal faces within 2m
- **Keypoints:** 6 (right eye, left eye, nose, mouth, right ear, left ear)

## Limitations
- Short-range model: accuracy drops beyond 2-3 meters
- Profile/side faces may not be detected
- Struggles with heavy occlusion (masks, sunglasses)
- Only 6 keypoints (not 468 mesh landmarks)

## Bias & Fairness
- Google reports testing across skin tones and demographics
- May have lower recall for certain facial structures
- Emotion heuristic built on top is NOT validated for fairness
- Landmark-based emotion detection has inherent geometric bias
