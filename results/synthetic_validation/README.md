# SYNTHETIC validation — NOT real YOLO model accuracy

The 30-frame synthetic video is a deterministic unit/integration fixture. A **mock detector** injects known dog bounding boxes, outside → inside → outside a polygon. The actual YOLO model is **not loaded or tested**. The annotated video, frames, event CSV, predictions, and synthetic confusion matrix demonstrate only that the pipeline wiring, 5-frame scene-level alert, and metric computation function on this controlled input. The perfect synthetic metrics are **not** legitimate Final project accuracy results and must never be placed on the real-results slide.

For real application results, follow `docs/EVALUATION_AND_DOWNLOAD_GUIDE.md` and publish verified human labels.
