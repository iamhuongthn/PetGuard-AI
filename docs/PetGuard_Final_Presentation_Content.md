# PetGuard AI Final Presentation Content

**ITAI 1378 | 11 slides | 10 minute in class presentation**

Use the material below as slide text and presenter cues. Keep each slide visual and short. The narration is a guide, not text to place on the slide.

## Slide 1. PetGuard AI

**Slide text**

Pet Restricted Area Monitoring  
Computer Vision Proof of Concept  
Tier 1  
Huong Nguyen, Sadia Saeed, Cherluk Sumdin, Mehmiyah Rouf

**Visual:** `results/images/confirmed_violation.jpg` if available. Otherwise use a clear still from `results/videos/violation_demo_e7aee7a13672.mp4`.

**Talk track:** Introduce PetGuard as a system that detects dogs and cats in video and checks whether they enter an area selected by the user.

## Slide 2. The problem

**Slide text**

Pets may enter furniture or rooms where they are not allowed.  
Manual monitoring is inconvenient.  
PetGuard turns video detections into useful zone events.

**Visual:** One input frame with the restricted area outlined.

**Talk track:** Explain why detecting a pet alone is not enough. The application must also determine whether the pet is in a restricted area.

## Slide 3. What was built

**Slide text**

Upload video → Detect pet → Check zone → Confirm event → Export results

Fixed camera MP4 input  
Interactive polygon  
Annotated video and CSV output

**Visual:** A simple five stage flow diagram. Match the code in `src/main.py` and `src/app.py`.

## Slide 4. Live demo

**Slide text**

1. Upload MP4
2. Choose zone mode
3. Draw and confirm polygon
4. Process video
5. Review status, video, and event CSV

**Visual:** Live Gradio interface. Use `results/videos/violation_demo_e7aee7a13672.mp4` as backup.

**Talk track:** Show the real input and output. Briefly explain the five frame confirmation and open the event CSV. Include a short actual failure example in the demo or immediately afterward.

**Time:** About 3 minutes.

## Slide 5. How the system works

**Slide text**

YOLOv8s pretrained on COCO  
Dog and cat detections  
Floor mode: bounding box bottom center  
Furniture mode: bounding box overlap  
Five consecutive frames for scene level confirmation

**Visual:** Two annotated stills, one floor polygon and one furniture polygon.

**Talk track:** Clarify that this is scene level confirmation, not individual pet tracking. Furniture overlap is a 2D approximation.

## Slide 6. Data and test scenarios

**Slide text**

Detection evaluation: 50 COCO and 100 Oxford images  
Application evaluation: five run specific 50 frame samples  
Scenes include dogs, cats, furniture, and a human only control

**Visual:** Three small screenshots from `results/videos/`, with run IDs in captions.

**Talk track:** Explain that the detector evaluation and the full application evaluation answer different questions. Repeated frames in one video are not independent scenes.

## Slide 7. Results versus Blueprint

**Slide text**

| Metric | Target | Observed |
| :--- | :--- | :--- |
| Pet recall, COCO, YOLOv8s | At least 85% | 83.61% |
| Pet recall, Oxford, YOLOv8s | At least 85% | 62.00% |
| Zone accuracy, mixed class clip | At least 90% | 96% provisional |
| False violation rate, mixed class clip | At most 10% | 0% provisional |

**Visual 1:** Bar chart of model recall: YOLOv8n versus YOLOv8s, split by COCO and Oxford. Source: `results/metrics/model_comparison.csv`.

**Visual 2:** Confusion matrix for `e7aee7a13672`: TN 41, FP 0, FN 2, TP 7. Source: `results/metrics/metrics_e7aee7a13672/zone_confusion_matrix.csv`.

**Talk track:** The model upgrade improves recall but costs more processing time. Zone accuracy exceeds the target on one mixed class clip, but the labels remain provisional and violation recall is only 77.78%.

## Slide 8. What changed from the Midterm

**Slide text**

YOLOv8n → YOLOv8s  
Image baseline → Video application  
Planned polygon → Interactive zone drawing  
Planned alerts → Confirmed events and CSV reports  
Planned evaluation → Recorded model and zone metrics

**Visual:** Two columns labeled Midterm and Final.

**Talk track:** Explain that changes were based on testing and manageable scope. The system remains a Tier 1 proof of concept.

## Slide 9. Challenges and failure analysis

**Slide text**

Boundary cases can be missed.  
Floor mode does not reliably represent furniture occupancy.  
Single class tests cannot measure both error types.  
Frame level agreement does not equal real world reliability.

**Visual:** Screenshots at frames 188 and 194 from run `e7aee7a13672`. Show the expected VIOLATION and predicted SAFE labels. Add a cat furniture example from run `1c1102d710f9`.

**Talk track:** The two dog boundary frames were marked as missed violations in the visual review. They need confirmation against original footage. The cat test shows why furniture mode is more appropriate than floor mode for a chair.

## Slide 10. Lessons and next steps

**Slide text**

Model confidence is not system accuracy.  
Geometry and zone selection matter.  
Failure cases reveal useful improvements.  
Next: independent labels, more varied clips, better boundary handling.

**Visual:** A small summary image showing detection, zone, and evaluation.

**Talk track:** Explain what the team learned from connecting a pretrained model to an actual application.

## Slide 11. Project resources and questions

**Slide text**

GitHub: https://github.com/iamhuongthn/PetGuard-AI  
Final notebook: `notebooks/PetGuard_AI_Final.ipynb`  
Model comparison: `results/metrics/model_comparison.csv`  
Zone evaluation: `results/metrics/metrics_e7aee7a13672/`

**Visual:** GitHub QR code if available.

**Talk track:** Close with the repository and invite questions.

## Presentation checklist

1. Add the required Tier and confirm team member names.
2. Use real screenshots from the repository, not stock images, for the results slides.
3. Test the Gradio demo and keep an exported video ready as backup.
4. Create a 3 to 5 minute narrated backup demo and link it in the README. The course instructions require it even for on campus presentations.
5. Save the final slide deck as `docs/presentation.pdf` and use the required Canvas submission filename.
6. Keep the entire live presentation within 10 minutes.
7. Clearly describe provisional labels and undefined single class metrics.
