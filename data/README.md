# PetGuard AI — Data Documentation

## Purpose:

PetGuard AI uses data for two distinct purposes:

1. validating pet detection;
2. evaluating the complete restricted-zone decision pipeline.

The initial project does not require training an object detector from scratch. A pretrained YOLO model provides the baseline dog/cat detection capability.

## Evaluation Data
The project will construct a targeted evaluation set representing realistic PetGuard scenarios.

Planned scenarios include:
- pet outside restricted zone;
- pet inside restricted zone;
- pet near zone boundary;
- partial occlusion;
- lighting variation;
- different camera angles;
- multiple pets; and
- no pet present.

## Initial Evaluation Target

Approximately 100–200 representative images or evaluated frames will be used for the initial application-level evaluation.
The dataset may be expanded if early testing reveals insufficient coverage.

## Ground Truth

Each evaluation sample should include:
- image/frame ID;
- whether a pet is present;
- pet type;
- expected SAFE/VIOLATION