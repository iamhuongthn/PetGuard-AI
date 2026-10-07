# 🐾 PetGuard AI

## Computer Vision-Based Pet Restricted-Zone Monitoring

**Tier 1 - Object Detection Application**

**Tier justification:** PetGuard uses a pretrained YOLOv8n object detector for visual perception and focuses project development on restricted-zone reasoning, application logic, alerts, and evaluation rather than training a custom detector from scratch.

PetGuard AI is a computer vision application designed to detect dogs and cats in images or video and determine whether a detected pet enters a user-defined restricted area.

Rather than treating object detection as the final output, PetGuard combines **pretrained object detection, spatial reasoning, and application logic** to transform visual detections into meaningful **SAFE / VIOLATION** events.

> **YOLO tells PetGuard what and where. PetGuard determines whether that location matters.**

---

## 🎯 The Problem

Home cameras can record pet activity, but recording alone does not answer:

> **Where is the pet, and is it somewhere it should not be?**

Pet owners may want pets to stay away from areas such as:

- couches;
- beds;
- kitchens;
- dining areas; and
- other user-defined restricted regions.

Reviewing camera footage manually is inefficient and provides little immediate context.

PetGuard addresses two different computer-vision questions:

### Perception

**What object is present, and where is it?**

### Spatial Reasoning

**Is the detected pet inside a restricted area?**

The objective is to convert:

**Pet Detection → Pet Localization → Spatial Evaluation → Meaningful Event**

---

## 🧠 System Architecture

The proposed end-to-end PetGuard pipeline is:

```text
Camera / Image / Video
          ↓
      Frame Input
          ↓
Pretrained YOLO Detector
          ↓
    Dog / Cat Filter
          ↓
  Confidence Filtering
          ↓
    Pet Bounding Box
          ↓
 Spatial Zone Reasoning
          ↓
 Temporal Confirmation
          ↓
   ┌──────┴──────┐
   ↓             ↓
 SAFE        VIOLATION
                  ↓
          Event Log / Alert
```

The AI model performs **visual perception**.

The PetGuard application layer is responsible for:

- pet-class filtering;
- confidence analysis;
- spatial reasoning;
- boundary decisions;
- temporal confirmation; and
- event generation.

This makes PetGuard more than simply running YOLO on an image.

---

# 🔬 Computer Vision Approach

## Technique

**Object Detection**

## Baseline Model

**YOLOv8n with pretrained COCO weights**

COCO stands for **Common Objects in Context**.

Dog and cat are existing COCO object classes, allowing PetGuard to establish a working detection baseline without training a new object detector from scratch.

## Technology

- Python
- Ultralytics YOLO
- PyTorch
- OpenCV
- Matplotlib
- Pandas
- Google Colab

YOLO is appropriate because PetGuard requires both:

### Classification

> **Dog or cat?**

and

### Localization

> **Where is the pet?**

For an input frame \(I_t\):

\[
I_t \rightarrow YOLO \rightarrow \{B_i,C_i,S_i\}
\]

where:

- \(B_i\) = bounding box;
- \(C_i\) = predicted class; and
- \(S_i\) = confidence score.

PetGuard retains detections where:

\[
C_i \in \{dog,cat\}
\]

---

# 🧪 Midterm Baseline Prototype

The Midterm prototype intentionally validates **Phase 1** of the PetGuard architecture.

Rather than relying on one successful detection, the feasibility experiment uses four representative scenarios stored in the GitHub repository.

| Scenario | Purpose |
|---|---|
| 🐶 Dog on couch | Dog detection baseline |
| 🐱 Cat on bed | Cat detection baseline |
| 🐶 + 🐱 Dog and cat together | Multi-pet feasibility |
| 🛋️ Room with no pet | Negative-control case |

The test images are stored under:

```text
samples/images/
```

The notebook retrieves these inputs directly from GitHub so that the baseline experiment can be reproduced in Google Colab.

---

## Baseline Capabilities Demonstrated

The current prototype demonstrates:

- reproducible GitHub-hosted test inputs;
- pretrained YOLOv8n inference;
- dog/cat class filtering;
- confidence-score extraction;
- bounding-box extraction;
- single-pet testing;
- multi-pet testing;
- negative-control testing; and
- representative pet-position calculation.

---

# 📊 Baseline Observations

The initial single-pet tests produced strong detections:

- **Dog on couch:** approximately **87.9% confidence**
- **Cat on bed:** approximately **90.5% confidence**

The multi-pet scene was more challenging.

Both expected pet classes were detected, but the model also produced an additional same-class dog detection and lower confidence scores.

This is an important observation because:

> **Correct class coverage does not automatically mean correct object-level detection.**

The negative-control room image also contained several household objects detected by YOLO.

However, because none belonged to the supported classes:

```text
{dog, cat}
```

PetGuard's class-filtering layer prevented those unrelated objects from entering the pet-monitoring pipeline.

---

## ⚠️ Interpreting Confidence Correctly

YOLO confidence represents the model's confidence in an **individual detection**.

It should not be interpreted as PetGuard's overall system accuracy.

For example:

> A dog detection with 87.9% confidence does **not** mean PetGuard is 87.9% accurate.

Application-level performance must be measured separately using a larger labeled evaluation set containing both successful and failure cases.

---

# 🎚️ Confidence Threshold Tradeoff

The multi-pet experiment also demonstrates why PetGuard should not choose a confidence threshold arbitrarily.

A higher confidence threshold may suppress uncertain or additional detections, but it can also remove valid pets.

The baseline notebook therefore includes an **illustrative threshold analysis** using the detections already produced by the multi-pet scenario.

The experiment demonstrates the general tradeoff:

```text
Higher Threshold
       ↓
Fewer uncertain detections
       ↓
BUT potentially more missed pets
```

versus:

```text
Lower Threshold
       ↓
More valid pets retained
       ↓
BUT potentially more false or additional detections
```

No final PetGuard confidence threshold is selected from this small experiment.

The Final evaluation will use a larger test set to evaluate this tradeoff systematically.

---

# 📐 Spatial Reasoning

YOLO provides a pet bounding box:

\[
B=(x_1,y_1,x_2,y_2)
\]

For floor-based restricted zones, PetGuard can estimate a representative pet position using the **bottom-center point**:

\[
P=
\left(
\frac{x_1+x_2}{2},
y_2
\right)
\]

This point approximately represents where the detected animal contacts the scene.

PetGuard can then compare \(P\) against a restricted polygon:

\[
Z=\{p_1,p_2,\ldots,p_n\}
\]

and evaluate:

\[
Violation =
\begin{cases}
1 & P \in Z\\
0 & P \notin Z
\end{cases}
\]

---

## Geometric Limitation

The bottom-center point is an **image-space approximation**, not a true 3D physical coordinate.

Camera perspective, furniture height, viewing angle, and occlusion can cause the image-space position to differ from the pet's actual physical position.

PetGuard will therefore investigate different spatial strategies for different restricted-zone types:

### Floor-Based Zones

**Point-in-polygon**

### Furniture-Based Zones

**Bounding-box / restricted-zone overlap**

These approaches will be compared during later development.

---

# ⏱️ Temporal Confirmation

Video detections may fluctuate between frames.

PetGuard therefore plans to investigate **temporal confirmation** before generating a violation event.

For example:

```text
Frame 1 → VIOLATION
Frame 2 → VIOLATION
Frame 3 → SAFE

Result → Do not confirm
```

versus:

```text
Frame 1 → VIOLATION
Frame 2 → VIOLATION
Frame 3 → VIOLATION
Frame 4 → VIOLATION
Frame 5 → VIOLATION

Result → CONFIRMED VIOLATION
```

This can help reduce false alerts caused by:

- bounding-box jitter;
- momentary detection errors;
- brief zone crossings; and
- boundary ambiguity.

---

# 📂 Data Strategy

# 📂 Data Strategy

PetGuard separates data into two purposes:

1. validating the pretrained dog/cat detection baseline; and
2. evaluating the complete PetGuard restricted-zone application.

## 1. Detection Baseline

The Midterm uses pretrained YOLOv8n COCO weights to validate dog/cat detection feasibility.

The Midterm feasibility experiment uses four representative scenarios:

- dog on couch;
- cat on bed;
- dog and cat together; and
- room with no pet.

These four images demonstrate technical feasibility but are not large enough to establish statistically meaningful real-world performance.

---

## 2. Final Evaluation Dataset

For the Final project, PetGuard will expand evaluation to approximately **200 representative images or selected video frames** from three complementary sources.

| Source | Target Size | Purpose |
|---|---:|---|
| [Oxford-IIIT Pet Dataset](https://www.robots.ox.ac.uk/~vgg/data/pets/) | 100 (50 cats + 50 dogs) | Controlled dog/cat detection evaluation across different breeds, appearances, and poses |
| [COCO 2017 Validation Dataset](https://cocodataset.org/#download) | 50 cat/dog scenes | Realistic detection evaluation with complex backgrounds, multiple objects, occlusion, and varied pet sizes |
| PetGuard-Specific Data | 50 images/video frames | Application-level evaluation of restricted-zone SAFE / VIOLATION decisions |

### Oxford-IIIT Pet Dataset

Oxford-IIIT will provide a controlled set of different cat and dog breeds, appearances, sizes, and poses.

Its primary purpose is to evaluate:

- Pet Detection Recall; and
- detection consistency across different pet appearances.

### COCO 2017 Validation Dataset

COCO will provide more realistic scenes where cats and dogs may appear with other objects and more complex backgrounds.

It will support evaluation of:

- Pet Detection Recall;
- confidence behavior;
- false or additional detections;
- multiple-object scenes;
- partial occlusion; and
- small or distant pets.

### PetGuard-Specific Data

Approximately 50 team-collected images or selected video frames will test the complete PetGuard application under controlled restricted-zone scenarios.

Planned scenarios include:

- pet clearly outside a restricted zone;
- pet clearly inside a restricted zone;
- pet near a zone boundary;
- partial occlusion;
- poor or different lighting;
- different viewing angles;
- multiple pets;
- small or distant pets; and
- no-pet negative controls.

These samples will primarily evaluate:

- Zone Decision Accuracy;
- False Violation Rate; and
- processing performance.

Oxford-IIIT and COCO samples primarily evaluate the **pet-detection stage** and will normally use `expected_zone_status = N/A`.

PetGuard-specific samples will evaluate the complete **SAFE / VIOLATION decision pipeline**.

Because PetGuard is a Tier 1 application using pretrained YOLOv8n COCO weights, these datasets are primarily used for **evaluation rather than training a new object detector**.

> **PetGuard will be evaluated using situations that challenge the application not only easy pet photographs.**

More detailed data documentation is available in:

`data/README.md`


---

# 🎯 Success Metrics

PetGuard will evaluate multiple stages of the application rather than reporting only one generic accuracy value.

## 1. Pet Detection Recall

Of the pets actually present, how many were detected?

\[
Recall=\frac{TP}{TP+FN}
\]

**Initial target: ≥ 85%**

---

## 2. Zone Decision Accuracy

How often does PetGuard correctly classify:

**SAFE vs. VIOLATION?**

\[
Accuracy =
\frac{Correct\ Zone\ Decisions}
{Total\ Evaluated\ Cases}
\]

**Initial target: ≥ 90%**

---

## 3. False Violation Rate

How often does PetGuard incorrectly generate a violation when the pet is actually safe?

**Initial target: ≤ 10%**

---

## 4. Processing Performance

Performance will be measured using:

- milliseconds per frame; and/or
- frames per second (FPS).

Inference timing depends on the runtime environment, input resolution, and available hardware.

Therefore, timing observed during the Midterm experiment is treated as a **baseline measurement**, not guaranteed final-system performance.

---

# ⚠️ Risks and Mitigation

| Risk | Impact | Mitigation / Plan B |
|---|---|---|
| Pet not detected | High | Confidence analysis and controlled evaluation |
| Occlusion | Medium | Include occlusion test cases |
| Poor lighting | Medium | Evaluate separately and document limitations |
| Zone-boundary ambiguity | High | Compare point and overlap methods |
| Bounding-box jitter | Medium | Temporal confirmation |
| Video processing too slow | Medium | Reduce resolution or sample frames |
| Repeated alerts | Medium | Event cooldown / debouncing |
| Multiple pets | Medium | Evaluate each detected pet independently |
| Complex custom zones | Low | Begin with predefined polygons |
| Dataset limitations | Medium | Controlled targeted evaluation set |
| Custom training becomes necessary | High | Preserve pretrained Tier 1 baseline |
| Final scope becomes too large | High | Protect minimum viable pipeline |

---

# 🗓️ Course Milestone Plan

The PetGuard development schedule follows the course Blueprint → Build structure while establishing a working baseline before expanding application features and evaluation.

| Course Phase | PetGuard Goal | Milestone |
|---|---|---|
| 🧭 **Blueprint** | Define the problem, architecture, technical approach, data plan, success metrics, risks, and project scope | Midterm Blueprint submitted |
| 🔌 **First Working Demo** | Run pretrained YOLO end-to-end and begin restricted-zone logic | Working dog/cat detection pipeline |
| 🛠 **Make It Yours** | Add restricted-zone reasoning, video processing, temporal confirmation, alerts, and PetGuard-specific evaluation data | Complete application pipeline |
| 📈 **Improve and Measure** | Evaluate Oxford-IIIT, COCO, and PetGuard-specific samples against the defined success metrics | Quantitative metrics recorded |
| 🎥 **Package and Present** | Finalize the application, README, evaluation results, demo, and presentation | Final project submitted |

The detailed technical roadmap below breaks these course milestones into PetGuard-specific development phases.


---

# 🚀 Development Roadmap

## Phase 1 - Baseline ✅

```text
Image
  ↓
YOLO
  ↓
Dog / Cat Detection
```

**Status: Demonstrated in the Midterm notebook**

---

## Phase 2 - Spatial Reasoning 🔄

```text
Pet Detection
      ↓
Restricted Zone
      ↓
SAFE / VIOLATION
```

---

## Phase 3 - Video

```text
Video
  ↓
Frames
  ↓
Detection
  ↓
Zone Analysis
```

---

## Phase 4 - Reliability

Add:

- confidence filtering;
- temporal confirmation; and
- event suppression.

---

## Phase 5 - Evaluation

Test:

- lighting;
- occlusion;
- camera angle;
- boundary cases;
- multiple pets; and
- negative-control scenes.

---

## Phase 6 - Final Proof of Concept

```text
Video
  ↓
Pet Detection
  ↓
Zone Reasoning
  ↓
Temporal Confirmation
  ↓
Confirmed Violation
  ↓
Visual Alert + Event Log
```

---

# 🛟 Minimum Viable Plan B

If advanced features become technically difficult, the minimum successful Final remains:

```text
Uploaded Image / Short Video
          ↓
     Dog/Cat Detection
          ↓
    One Defined Zone
          ↓
     SAFE / VIOLATION
          ↓
     Annotated Output
```

This protects the core end-to-end computer-vision application while preventing unnecessary scope expansion.

---

# 📌 Midterm Scope Boundary

The Midterm prototype intentionally validates **Phase 1**.

## Completed for Midterm

- pretrained YOLOv8n inference;
- reproducible GitHub test inputs;
- dog/cat filtering;
- confidence analysis;
- single-pet testing;
- multi-pet testing;
- negative-control testing;
- bounding-box localization; and
- representative pet-position calculation.

## Reserved for Final Development

- restricted-zone implementation;
- SAFE / VIOLATION decisions;
- video-frame processing;
- temporal confirmation;
- event suppression;
- event logging; and
- larger quantitative evaluation.

This separation keeps the Midterm focused on **technical feasibility** while maintaining a realistic path toward the Final application.

---

# 📁 Repository Structure

```text
PetGuard-AI/
│
├── README.md
├── requirements.txt
│
├── data/
│   └── README.md
│
├── docs/
│   ├── AI_usage_log.md
│   └── PetGuard_AI_Midterm_Blueprint.pdf
│
├── notebooks/
│   └── petguard_baseline.ipynb
│
├── samples/
│   ├── images/
│   │   ├── dog_on_couch.jpg
│   │   ├── cat_on_bed.jpg
│   │   ├── dog_n_cat_together.jpg
│   │   └── room_w_no_pet.jpg
│   └── videos/
│
├── results/
│   ├── images/
│   └── metrics/
│
└── src/
    ├── detector.py
    ├── zone.py
    ├── temporal.py
    ├── event_logger.py
    └── main.py
```

The `src/` modules represent the planned Final application structure and are intentionally developed incrementally as the project progresses.

---

# 🔁 Reproducibility

Install project dependencies using:

```bash
pip install -r requirements.txt
```

The Midterm baseline notebook is located at:

```text
notebooks/petguard_baseline.ipynb
```

The baseline test images are stored under:

```text
samples/images/
```

The notebook retrieves the same GitHub-hosted test inputs to make the feasibility experiment reproducible.

---

# 🧪 Current Conclusion

The Midterm baseline supports the **technical feasibility** of the PetGuard architecture.

Pretrained YOLOv8n can provide the dog/cat classification and localization information required by the application without requiring custom detector training at the start of the project.

However, the experiment also reveals important challenges:

- multi-pet scenes can produce lower-confidence and additional detections;
- confidence-threshold selection involves a recall/false-detection tradeoff;
- image-space localization has geometric limitations; and
- four test images are insufficient to establish real-world reliability.

These observations directly inform the next development stage.

> **The goal of the Midterm is not to claim PetGuard is finished.  
> It is to demonstrate that the proposed architecture is technically feasible and that there is a measurable, realistic path to the Final proof of concept.**

---

# 👥 Team

1. Huong Nguyen
2. Sadia Saeed
3. Cherluk Sumdin
4. Mehmiyah Rouf

---

# 🎓 Course

**ITAI 1378 - Computer Vision**

**Professor:** Patricia McManus