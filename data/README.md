# PetGuard AI - Data Documentation

## Purpose

PetGuard AI uses data for two distinct purposes:

1. validating pretrained pet detection; and
2. evaluating the complete restricted-zone decision pipeline.

The initial project does not require training an object detector from
scratch.

A pretrained YOLOv8n model using COCO weights provides the baseline
dog/cat detection capability.

---

## Midterm Baseline Data

The Midterm feasibility experiment uses four representative test
scenarios:

| Scenario | Purpose |
|---|---|
| Dog on couch | Verify dog detection |
| Cat on bed | Verify cat detection |
| Dog and cat together | Evaluate multi-pet detection behavior |
| Room with no pet | Negative-control / false-pet detection check |

The current sample images are stored in:

`samples/images/`

Current files:

- `dog_on_couch.jpg`
- `cat_on_bed.jpg`
- `dog_n_cat_together.jpg`
- `room_w_no_pet.jpg`

These four images are intended only as a **feasibility test**.

They are not large enough to support statistically meaningful claims
about model or system accuracy.

---

## Final Evaluation Data

The Final project will construct a larger targeted evaluation set
representing realistic PetGuard scenarios.

### Planned Data Sources

The Final evaluation will target approximately **200 representative images or selected video frames** from three complementary sources.

| Source | Target Size | Primary Purpose |
|---|---:|---|
| [Oxford-IIIT Pet Dataset](https://www.robots.ox.ac.uk/~vgg/data/pets/) | 100 (50 cats + 50 dogs) | Controlled pet-detection evaluation |
| [COCO 2017 Validation Dataset](https://cocodataset.org/#download) | 50 cat/dog scenes | Realistic and challenging pet-detection evaluation |
| PetGuard-Specific Data | 50 images/video frames | Restricted-zone SAFE / VIOLATION evaluation |

#### 1. Oxford-IIIT Pet Dataset

The Oxford-IIIT Pet Dataset will provide 50 cat images and 50 dog images selected across different breeds, appearances, and poses.

These samples will primarily evaluate:

- Pet Detection Recall;
- detection consistency across different breeds; and
- detection behavior across different pet appearances and poses.

Public source:

[Oxford-IIIT Pet Dataset](https://www.robots.ox.ac.uk/~vgg/data/pets/)

#### 2. COCO 2017 Validation Dataset

Fifty images containing cats and/or dogs will be selected from the COCO 2017 Validation dataset.

These samples will provide more realistic scenes containing complex backgrounds and other objects.

They will support evaluation of:

- Pet Detection Recall;
- confidence behavior;
- false or additional detections;
- multiple-object scenes;
- partial occlusion; and
- small or distant pets.

Public source:

[COCO Dataset](https://cocodataset.org/#download)

#### 3. PetGuard-Specific Evaluation Data

Approximately 50 team-collected images or selected video frames will be used to evaluate the application-specific restricted-zone functionality.

The planned scenarios include:

- clearly SAFE;
- clearly VIOLATION;
- zone-boundary cases;
- partial occlusion;
- different lighting;
- different viewing angles;
- multiple pets;
- small or distant pets; and
- no-pet negative controls.

These samples will primarily measure:

- Zone Decision Accuracy;
- False Violation Rate; and
- processing performance.

Oxford-IIIT and COCO samples primarily evaluate the pet-detection stage and will normally use `expected_zone_status = N/A`.

PetGuard-specific samples will evaluate the complete SAFE / VIOLATION decision pipeline.

Because PetGuard is a Tier 1 application using pretrained YOLOv8n COCO weights, these datasets are primarily used for evaluation rather than training a new object detector.

---

Planned scenarios include:

- pet outside restricted zone;
- pet inside restricted zone;
- pet near zone boundary;
- partial occlusion;
- lighting variation;
- different camera angles;
- multiple pets;
- no pet present; and
- potentially challenging or visually ambiguous scenes.

---

## Initial Evaluation Target

The planned Final evaluation target is approximately:

**200 representative images or selected video frames**

The planned distribution is:

- **100 Oxford-IIIT Pet images:** 50 cats + 50 dogs;
- **50 COCO 2017 Validation images:** realistic cat/dog scenes; and
- **50 PetGuard-specific images or selected video frames:** application-level SAFE / VIOLATION scenarios.

The evaluation set may be adjusted if early testing reveals insufficient coverage of important failure cases.

The objective is not simply to collect many pet images.

The evaluation set should contain scenarios that challenge both the pretrained detector and the complete PetGuard application.

---

## Ground Truth

Each evaluation sample should contain metadata such as:

- image/frame ID;
- pet present: Yes / No;
- expected pet type;
- expected restricted-zone status;
- predicted pet type;
- predicted restricted-zone status;
- detection confidence;
- restricted-zone identifier;
- test scenario/category; and
- notes about unusual conditions.

Example:

| image_id | pet_present | pet_type | expected_zone_status | predicted_zone_status | confidence | notes |
|---|---|---|---|---|---:|---|
| 001 | Yes | Dog | Violation | Violation | 0.91 | Clear view |
| 002 | Yes | Cat | Safe | Safe | 0.86 | Side angle |
| 003 | Yes | Dog | Safe | Violation | 0.73 | Boundary case |

---

## Planned Evaluation Categories

The evaluation data should include both normal and difficult cases.

### Standard Cases

- clearly visible dog;
- clearly visible cat;
- pet clearly outside restricted area;
- pet clearly inside restricted area.

### Challenging Cases

- partial occlusion;
- poor lighting;
- unusual camera angle;
- pet near zone boundary;
- small or distant pet;
- multiple pets;
- overlapping detections.

### Negative-Control Cases

Images or frames containing no supported pet will also be included.

These cases help determine whether unrelated household objects are
incorrectly interpreted as pets.

---

## Data Principle

> PetGuard will be evaluated on situations that challenge the
> application not only easy pet photographs.

The Final evaluation should measure the complete decision pipeline rather
than relying on individual YOLO confidence scores as a measure of system
accuracy.