# PetGuard AI

## Computer Vision-Based Pet Restricted-Zone Monitoring

PetGuard AI is a Tier 1 computer vision application designed to detect dogs and cats in images or video and determine whether a detected pet has entered a user-defined restricted area.

Rather than treating object detection as the final output, PetGuard combines pretrained object detection with spatial reasoning and application logic to convert visual detections into meaningful SAFE or VIOLATION events.

## Problem

Home cameras can record pet activity, but video alone does not determine whether a pet is somewhere it should not be.

PetGuard addresses two questions:
1. Where is the pet?
2. Is that location inside a restricted area?

Potential restricted areas include couches, beds, kitchens, dining areas, or other user-defined regions.

## System Architecture

Camera / Image / Video  
→ YOLO Object Detection  
→ Dog/Cat Filtering  
→ Confidence Filtering  
→ Pet Localization  
→ Restricted-Zone Analysis  
→ Temporal Confirmation  
→ SAFE / VIOLATION  
→ Event Log / Alert

## Computer Vision Approach

The initial prototype uses a pretrained YOLOv8n object detector.

YOLO provides both object classification and localization. PetGuard retains dog and cat detections and uses their bounding-box coordinates for subsequent spatial reasoning.

The baseline approach intentionally begins with pretrained weights so development can focus on the complete application pipeline before considering model adaptation or fine-tuning.

## Current Progress

Initial YOLO feasibility testing has been completed.

The baseline prototype successfully:

- loads a pretrained YOLOv8n model;
- processes a pet image;
- detects a dog;
- extracts detection confidence;
- extracts bounding-box coordinates; and
- filters detections to supported pet classes.

In the initial test image, YOLO detected the dog with approximately 87.9% confidence.

This validates the first major technical dependency of the PetGuard pipeline.

## Spatial Reasoning

For floor-based zones, PetGuard will initially evaluate a representative point derived from the detected pet bounding box against a user-defined polygon.

For furniture-based scenarios, bounding-box/zone overlap may provide a more appropriate spatial relationship.

These approaches will be experimentally evaluated during development.

## Temporal Confirmation

Video detections may fluctuate between frames. PetGuard will therefore investigate temporal confirmation before generating a violation event.

A persistent violation across multiple frames is more reliable than triggering an alert from a single frame.

## Evaluation

The system will be evaluated using:

- Pet Detection Recall
- Zone Decision Accuracy
- False Violation Rate
- Processing Latency / FPS

Testing will include safe cases, violations, boundary cases, occlusion, lighting variation, different camera angles, multiple pets, and images without pets.

## Initial Success Targets

- Pet Detection Recall: ≥ 85%
- Zone Decision Accuracy: ≥ 90%
- False Violation Rate: ≤ 10%

Performance targets may be refined after establishing the baseline environment.

## Final Proof of Concept

The intended final system is:

Video  
→ Pet Detection  
→ Restricted-Zone Reasoning  
→ Temporal Confirmation  
→ SAFE / VIOLATION  
→ Visual Alert + Event Log

The project prioritizes a reliable end-to-end proof of concept over unnecessary feature expansion.

## Team

1. Huong Nguyen
2. Sadia Saeed 
3. Cherluk Sumdin
4. Mehmiyah Rouf

## Course

ITAI 1378 - Computer Vision