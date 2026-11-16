# PetGuard AI Final Presentation

**Course:** ITAI 1378 Computer Vision  
**Format:** In class presentation with live Gradio demonstration  
**Target duration:** 10 minutes  
**Slides:** 11  
**Team:** Huong Nguyen, Sadia Saeed, Cherluk Sumdin, Mehmiyah Rouf

## Presentation message

**Detecting a pet is only the first step. The real challenge is deciding whether the pet is somewhere it should not be.**

### Suggested timing

| Section | Duration |
| :--- | :--- |
| Problem and design | 3 minutes |
| Live demo | 3 minutes |
| Results | 2 minutes |
| Lessons and closing | 2 minutes |

## Slide 1. PetGuard AI

**Time:** 20 seconds

### On slide

**PetGuard AI**  
From Pet Detection to Restricted Area Monitoring  
Computer Vision Proof of Concept  
ITAI 1378 | Group Project

**Visual:** Actual annotated dog frame from `results/videos/violation_demo_e7aee7a13672.mp4`.

**Speaker note:** PetGuard AI detects dogs and cats, checks whether they enter a restricted area, and records confirmed violations.

## Slide 2. The Problem

**Time:** 40 seconds

### On slide

**Detection Alone Is Not Enough**

| Computer vision | PetGuard AI |
| :--- | :--- |
| Is there a pet? | Is the pet inside a restricted area? |

**Key point:** A detected pet is not automatically a violation. Location and timing matter.

**Visual:** Two actual dog frames, one outside the zone and one inside.

**Speaker note:** Object detection tells us what is present. PetGuard adds a spatial decision and event confirmation.

## Slide 3. System Architecture

**Time:** 50 seconds

### On slide

**From Video to Actionable Events**

```text
Fixed camera MP4
       ↓
YOLOv8s dog and cat detection
       ↓
Restricted polygon check
       ↓
Five frame confirmation
       ↓
Annotated video and events CSV
```

**Visual:** Convert the pipeline into a simple flow diagram.

**Speaker note:** The system combines a pretrained detector with geometric rules and temporal confirmation. The fixed camera keeps the selected zone aligned across frames.

## Slide 4. Two Zone Modes

**Time:** 45 seconds

### On slide

**One Detector. Two Spatial Rules.**

| Floor or room mode | Sofa or furniture mode |
| :--- | :--- |
| Checks the bottom center of the pet bounding box | Checks bounding box overlap with the selected polygon |

**Visual:** Actual dog floor screenshot beside a cat furniture screenshot.

**Speaker note:** A floor and a sofa need different geometric rules. Choosing the wrong mode can produce incorrect decisions even when YOLO detects the pet correctly.

## Slide 5. Live Demonstration

**Time:** 3 minutes

### On slide

**Live Demo: Input → Decision → Evidence**

1. Upload the dog MP4.
2. Choose **Floor or room area**.
3. Draw and confirm the restricted polygon.
4. Select **Process Video**.
5. Show annotated output and `events.csv`.

**Show:** SAFE, PENDING, and CONFIRMED VIOLATION states where available.

**Demo source:** `notebooks/PetGuard_AI_Final.ipynb` and its Gradio interface.

**Backup:** `results/videos/violation_demo_e7aee7a13672.mp4`.

**Preparation:** Open Gradio and prepare the video before presenting. Keep a previously generated output ready in case processing takes longer than expected.

## Slide 6. Model Selection

**Time:** 40 seconds

### On slide

**Why YOLOv8s?**

| Dataset | YOLOv8n recall | YOLOv8s recall |
| :--- | ---: | ---: |
| COCO | 73.77% | 83.61% |
| Oxford | 51.00% | 62.00% |

**Takeaway:** YOLOv8s improved recall on both evaluation sets, with higher inference latency.

**Chart:** Grouped bar chart of the two models across COCO and Oxford.

**Source:** `results/metrics/model_comparison.csv`.

**Speaker note:** The team selected YOLOv8s because recall mattered more than speed for this proof of concept. Neither dataset reached the original 85% recall target.

## Slide 7. Application Evaluation

**Time:** 45 seconds

### On slide

**96% Zone Accuracy on the Mixed Test**

| Measure | Provisional result |
| :--- | ---: |
| Zone accuracy | 96% |
| False positives | 0 |
| Missed violations | 2 |
| Violation recall | 77.78% |

**Confusion matrix:**

| Actual / Predicted | SAFE | VIOLATION |
| :--- | ---: | ---: |
| SAFE | 41 | 0 |
| VIOLATION | 2 | 7 |

**Source:** `results/metrics/metrics_e7aee7a13672/zone_confusion_matrix.csv`.

**Scope:** 50 sampled frames from run `e7aee7a13672`. Visual labels are provisional.

**Speaker note:** Accuracy exceeded the 90% target on this mixed class sample, but the two missed violations show why accuracy alone is not sufficient.

## Slide 8. Testing Different Scenarios

**Time:** 35 seconds

### On slide

**Different Scenarios, Different Risks**

| Scenario | Reported agreement | Focus |
| :--- | ---: | :--- |
| Dogs entering a zone | 96% | Both SAFE and VIOLATION |
| Cat on furniture | 100% | Furniture overlap |
| Human only | 100% | False pet alerts |
| Other pet scenarios | 100% | Additional violation cases |

**Visual:** Three real screenshots showing dog, cat, and human only scenarios.

**Speaker note:** The 100% results come from samples containing only SAFE or only VIOLATION frames. They show agreement within those scenarios, not general system accuracy. All labels remain provisional.

## Slide 9. Failure Analysis

**Time:** 50 seconds

### On slide

**A Correct Detection Can Still Produce a Wrong Decision**

**Boundary failure:** Two dog frames labeled VIOLATION were predicted SAFE.  
**Frames:** 188 and 194, run `e7aee7a13672`.

**Geometry mismatch:** Floor mode can miss a cat occupying furniture. Furniture overlap is better suited to a chair.

**Visual:** Annotated dog frames 188 and 194, plus one cat furniture frame.

**Speaker note:** These examples show that the spatial rule matters as much as the detector. The frame labels need independent confirmation using the original unannotated footage.

## Slide 10. Engineering Decisions and Next Steps

**Time:** 45 seconds

### On slide

**Built for a Fixed Camera, Not Every Camera**

**Current scope:** Fixed camera, user selected polygon, scene level confirmation.

**Why:** A moving camera changes the zone position in image coordinates.

**Future work:** Camera motion estimation, dynamic zone alignment, individual pet tracking, and independently labeled evaluation.

**Speaker note:** Fixed camera operation is an intentional proof of concept decision. Moving camera support requires additional geometry and motion handling.

## Slide 11. Conclusion

**Time:** 25 seconds

### On slide

**PetGuard AI: From Detection to Decisions**

1. Working video processing and restricted area monitoring.
2. Confirmed events with annotated video and CSV evidence.
3. Measured results with documented limitations.

**Repository:** https://github.com/iamhuongthn/PetGuard-AI

**Closing line:** PetGuard AI shows how object detection, spatial reasoning, and temporal confirmation can work together in a practical computer vision application. The next step is improving reliability beyond controlled, fixed camera scenarios.

## Visual and Demo Preparation Checklist

| Item | File or location | Slides |
| :--- | :--- | :--- |
| Gradio application | `notebooks/PetGuard_AI_Final.ipynb` | 5 |
| Dog demo | `results/videos/violation_demo_e7aee7a13672.mp4` | 1, 2, 5 |
| Model comparison data | `results/metrics/model_comparison.csv` | 6 |
| Mixed class confusion matrix | `results/metrics/metrics_e7aee7a13672/zone_confusion_matrix.csv` | 7 |
| Cat furniture run | `results/runs/1c1102d710f9/` | 4, 8, 9 |
| Human only run | `results/runs/65e44abd29a1/` | 8 |
| Dog failure frames | `results/runs/e7aee7a13672/` at frames 188 and 194 | 9 |

## Important Presentation Notes

* Use actual PetGuard screenshots rather than stock images.
* Keep the live demo near three minutes. Prepare a completed run as backup.
* Describe the reported metrics as provisional visual evaluation results.
* Explain that single class samples cannot evaluate both false alerts and missed violations.
* Do not claim that the 85% detection recall target was achieved.
* Keep the full presentation within ten minutes and export the finished slides as `docs/presentation.pdf`.
