# Model Card: Emotion Detection

## Model Details
- **Name:** FaceExpressionNet (MobileNet-based CNN)
- **Version:** 2.0.0 (replaced geometric heuristic in v1.0.0)
- **Type:** Convolutional Neural Network (real ML model)
- **Framework:** TensorFlow.js (via @vladmandic/face-api)
- **Size:** ~330 KB (quantized uint8 weights)
- **Source:** @vladmandic/face-api v1.7.x (maintained fork of face-api.js)

## How It Works
1. MediaPipe BlazeFace detects face bounding boxes in the video frame
2. Each face region is cropped and resized to 136x136 pixels (with 15% margin)
3. The crop is fed to FaceExpressionNet, a MobileNet-based CNN that outputs a
   7-class softmax probability distribution
4. The top prediction is mapped to the app's `EmotionType` enum
5. Temporal stabilization (1.5s window, majority vote) smooths predictions

### Architecture
- 4 dense blocks of depthwise-separable convolutions (32 -> 64 -> 128 -> 256 channels)
- Global average pooling + fully connected layer (256 -> 7)
- Quantized to uint8 for minimal download size

### Classified Emotions (7 classes)
| Model Output | App EmotionType | Notes |
|---|---|---|
| neutral | neutral / focused | "focused" when neutral >0.65 and runner-up <0.12 |
| happy | happy | |
| sad | sad | |
| angry | angry | |
| fearful | fearful | |
| disgusted | disgusted | |
| surprised | surprised | |

## Training Data
- Trained on FER2013+ dataset (facial expression recognition)
- ~35,000 grayscale 48x48 images labeled with 7 emotions
- Additional augmentation and transfer learning from face recognition features

## Fallback Behavior
If the FaceExpressionNet model fails to load (network error, memory constraint),
the system falls back to the legacy geometric heuristic that uses 6 MediaPipe
keypoints with hardcoded thresholds. This fallback is clearly limited and exists
only to maintain basic functionality.

## Performance
- **Inference time:** ~5-15ms per face on modern hardware (GPU-accelerated via WebGL)
- **Accuracy:** FER2013 test set ~65-70% (consistent with published benchmarks for
  this dataset; human agreement on FER2013 is ~65%)
- **Model load time:** <1s on broadband (330KB download)

## Improvements Over Previous Heuristic (v1.0.0)
- Uses actual learned features instead of 6 geometric ratios
- Can distinguish all 7 basic emotions (heuristic could only detect 5)
- Significantly more robust across different face shapes, ethnicities, and angles
- Confidence scores are meaningful probabilities, not arbitrary thresholds

## Known Limitations
- FER2013 dataset has known label noise (~10% mislabeled samples)
- Training data skews Western/Caucasian; accuracy may vary across demographics
- Subtle expressions (mild sadness, slight disgust) are harder to classify
- "focused" is approximated from neutral+low-competition, not a trained class
- The model processes face crops, so extreme head angles degrade accuracy

## Bias & Fairness Assessment
- **MODERATE RISK:** FER2013 has demographic imbalances; the model may perform
  better on faces similar to the training distribution
- **Improvement over v1.0.0:** The CNN learns expression features from data rather
  than relying on geometric ratios calibrated to a single face shape
- **Recommendation:** Continue labeling predictions as "estimated" in the UI;
  do not use for high-stakes decisions

## Ethical Considerations
- Emotion detection from facial expressions remains scientifically debated
- Cultural differences in emotional expression are partially but not fully
  captured by FER2013 training data
- This feature should NOT be used for hiring, security clearance, or legal decisions
- Privacy: face crops are processed in-browser and never sent to a server
