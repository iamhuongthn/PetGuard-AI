# PetGuard AI

**A computer vision proof of concept for monitoring pet access to restricted areas**

**Course:** ITAI 1378 Computer Vision and AI  
**Project:** Final Build, Tier 1  
**Team:** Huong Nguyen, Sadia Saeed, Cherluk Sumdin, Mehmiyah Rouf  
**Repository:** https://github.com/iamhuongthn/PetGuard-AI

## Overview

PetGuard AI detects dogs and cats in a video and determines whether they enter a restricted area selected by the user. It turns object detections into visible zone decisions, confirmed violation events, and downloadable evidence.

**Scope:** This is a proof of concept for a **fixed camera**. The restricted polygon is defined in image coordinates and assumes the camera does not move. Supporting a moving camera would require camera motion estimation, alignment of the restricted area across frames, and potentially object tracking. Those capabilities are outside the current scope.

## What was built

1. Upload an MP4 video through Gradio, up to 60 seconds and 250 MB.
2. Choose **Floor or room area** or **Sofa or furniture** mode.
3. Draw and confirm a restricted polygon with at least three points.
4. Process the video using a pretrained **YOLOv8s** model for dogs and cats.
5. Review the annotated video, frame predictions, and confirmed violation events.
6. Edit the polygon and process the video again when needed.

### Detection and zone logic

| Component | Implementation |
| :--- | :--- |
| Pet detection | YOLOv8s pretrained on COCO, dog and cat classes |
| Video processing | Frames resized to 960 pixels wide |
| Detection threshold | Confidence of 0.35 |
| Floor or room mode | Pet bounding box bottom center must fall inside the polygon |
| Sofa or furniture mode | At least 20% of the pet bounding box must overlap the polygon |
| Temporal confirmation | Five consecutive positive frames confirm a scene level violation |
| Event reset | Five frames without a candidate violation clear the confirmed state |

Temporal confirmation applies to the scene, not to a tracked individual pet. The two spatial rules are image based approximations, not measurements of physical contact.

### Output files

Each run is saved under `results/runs/<run_id>/`.

| File | Contents |
| :--- | :--- |
| `annotated.mp4` | Video with bounding boxes, restricted polygon, and status |
| `petguard_browser.mp4` | Browser compatible annotated video |
| `events.csv` | Confirmed violation events |
| `frame_predictions.csv` | Frame level detections and zone decisions |
| `zone_config.json` | Polygon, zone mode, and video configuration |

Selected examples are available in `results/videos/`.

## Run the application

**Google Colab:** Open `notebooks/PetGuard_AI_Final.ipynb`. Run the setup and launch sections, then use the Gradio interface to upload a video and draw the zone. Export the processing ZIP before the runtime disconnects. The notebook also supports creating a labeling template and exporting zone evaluation results.

**Local environment:**

```bash
pip install -r requirements.txt
python -m src.app
```

FFmpeg is needed to create browser compatible MP4 output. Install it separately and make it available on the system path.

## Evaluation

Two evaluations answer different questions. **Detection evaluation** measures whether YOLO finds pets. **Zone evaluation** measures whether PetGuard assigns the correct SAFE or VIOLATION status for a selected frame.

### Model selection

The Midterm used YOLOv8n as a baseline. The Final uses YOLOv8s after comparing both models on selected COCO and Oxford IIIT Pet images.

| Dataset | YOLOv8n recall | YOLOv8s recall | YOLOv8s precision |
| :--- | ---: | ---: | ---: |
| COCO, 50 images | 73.77% | 83.61% | 87.93% |
| Oxford, 100 images | 51.00% | 62.00% | 56.36% |

YOLOv8s improved recall on both sets but required more inference time. Neither result reached the original 85% pet recall target. Source: `results/metrics/model_comparison.csv` and `notebooks/PetGuard_Model_Evaluation.ipynb`.

### Restricted zone results

The repository contains five run specific evaluations with 50 sampled frames each.

| Run ID | SAFE | VIOLATION | Reported agreement | Interpretation |
| :--- | ---: | ---: | ---: | :--- |
| `e7aee7a13672` | 41 | 9 | 96% | Mixed classes, two missed violations |
| `1c1102d710f9` | 0 | 50 | 100% | Cat on restricted furniture |
| `65e44abd29a1` | 50 | 0 | 100% | Human only negative control |
| `b75cb2a3412b` | 0 | 50 | 100% | Violation only test |
| `e5136306a1a8` | 0 | 50 | 100% | Violation only test |

For the mixed class run, the provisional confusion matrix contains **41 true negatives, 7 true positives, 0 false positives, and 2 false negatives**. This gives 96% zone agreement, 0% false violation rate, and 77.78% violation recall. Frames 188 and 194 are recorded as missed boundary violations.

**How to interpret these results:**

1. Labels are **provisional visual annotations**. Some were reviewed using annotated video, not independently checked against original footage. The percentages describe agreement with those labels, not verified real world accuracy.
2. A test with only VIOLATION frames cannot measure false violation rate. A test with only SAFE frames cannot measure violation recall. These metrics are **N/A**, not zero or 100%.
3. Frames from the same short video are related observations. Fifty sampled frames do not represent fifty independent scenes.
4. Some runs may share source footage. Do not interpret every run as a new independent video.

Evaluation files are under `results/metrics/`. For example, reproduce the mixed class report from the repository root:

```bash
python -m scripts.evaluate_zone_labels data/zone_labels_verified_e7aee7a13672.csv --out results/metrics/metrics_e7aee7a13672
```

## Challenges and limitations

1. **Fixed camera:** The polygon remains meaningful only while the camera position is stable. Moving camera support would need motion estimation, zone alignment, and potentially tracking.
2. **Approximate geometry:** Bounding boxes do not establish physical contact. Floor mode can miss furniture occupancy, while overlap mode depends on camera perspective.
3. **Detection errors:** Lighting, occlusion, small pets, and confidence filtering can produce missed or incorrect detections.
4. **Multiple pets:** Five frame confirmation operates at the scene level and does not track the same animal over time.
5. **Limited evaluation:** Some tests contain only one class, and the visual labels are not fully independent ground truth.
6. **Temporary runtime:** Colab sessions and Gradio share links expire. Videos and CSV reports must be exported.

## Midterm to Final progress

| Midterm Blueprint | Final Build |
| :--- | :--- |
| YOLOv8n image baseline | YOLOv8s video detector |
| Planned restricted zone | Interactive polygon with two spatial modes |
| Planned alerts | Five frame confirmation and event CSV |
| Planned evidence | Annotated MP4, frame predictions, and run configuration |
| Planned evaluation | Model comparison and zone confusion matrices |

## Repository guide

| Path | Purpose |
| :--- | :--- |
| `src/` | Gradio application, detection, zone logic, confirmation, and logging |
| `notebooks/PetGuard_AI_Final.ipynb` | Video processing and zone evaluation workflow |
| `notebooks/PetGuard_Model_Evaluation.ipynb` | YOLO model comparison |
| `notebooks/petguard_baseline.ipynb` | Midterm experiment |
| `scripts/` and `tests/` | Evaluation scripts and automated tests |
| `data/` | Frame labels and supporting manifests |
| `results/videos/` and `results/runs/` | Video examples and processing evidence |
| `results/metrics/` | Model and zone evaluation reports |
| `docs/` | Blueprint, AI usage log, and Final presentation |

## Presentation and responsible AI use

Final presentation: `docs/presentation.pdf` once added. The annotated videos support the live classroom demo. Add a narrated demo link here if one is submitted separately.

AI tools assisted with development and documentation. Specific uses, changes, and verification steps are documented in `docs/AI_usage_log.md`.

## Next steps

Verify labels against original video, test more scenes containing both SAFE and VIOLATION states, improve boundary handling, and investigate camera motion compensation and individual pet tracking for a future version.
