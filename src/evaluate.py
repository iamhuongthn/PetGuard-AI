"""Ground-truth evaluation. No model confidence is treated as accuracy."""
from pathlib import Path
import json
import numpy as np
import pandas as pd


def box_iou(a, b):
    """IoU of xyxy boxes; zero for nonoverlapping or invalid boxes."""
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    intersection = max(0, x2-x1) * max(0, y2-y1)
    area_a = max(0, a[2]-a[0]) * max(0, a[3]-a[1])
    area_b = max(0, b[2]-b[0]) * max(0, b[3]-b[1])
    union = area_a + area_b - intersection
    return intersection / union if union > 0 else 0.0


def match_detections(ground_truth, predictions, iou_threshold=0.5):
    """Greedy one-to-one class-aware matching, highest IoU first.

    Each input is a list of {'class': 'cat'|'dog', 'bbox': [x1,y1,x2,y2]}.
    Predictions may additionally include 'confidence'.
    """
    pairs = []
    for i, gt in enumerate(ground_truth):
        for j, pred in enumerate(predictions):
            if gt["class"] != pred["class"]:
                continue
            iou = box_iou(gt["bbox"], pred["bbox"])
            if iou >= iou_threshold:
                pairs.append((iou, i, j))
    used_gt, used_pred = set(), set()
    for _, i, j in sorted(pairs, reverse=True):
        if i not in used_gt and j not in used_pred:
            used_gt.add(i)
            used_pred.add(j)
    return {
        "TP": len(used_gt),
        "FN": len(ground_truth) - len(used_gt),
        "FP": len(predictions) - len(used_pred),
    }


def detection_metrics(rows):
    """Aggregate object-level TP/FP/FN from per-image match results."""
    tp = sum(int(r["TP"]) for r in rows)
    fp = sum(int(r["FP"]) for r in rows)
    fn = sum(int(r["FN"]) for r in rows)
    return {
        "TP": tp, "FP": fp, "FN": fn,
        "pet_recall": tp/(tp+fn) if tp+fn else float("nan"),
        "pet_precision": tp/(tp+fp) if tp+fp else float("nan"),
    }


def evaluate_zones(labels_csv, output_csv=None):
    """Compare verified SAFE/VIOLATION labels with frame-level predictions.

    Label one row per evaluated sample/frame; don't mix with event-level recall.
    """
    df = pd.read_csv(labels_csv)
    required = {"expected_zone_status", "predicted_zone_status"}
    if df.empty or not required.issubset(df.columns):
        raise ValueError("CSV needs nonempty expected_zone_status and predicted_zone_status columns.")
    a = df["expected_zone_status"].astype(str).str.strip().str.upper()
    p = df["predicted_zone_status"].astype(str).str.strip().str.upper()
    valid = {"SAFE", "VIOLATION"}
    if not a.isin(valid).all() or not p.isin(valid).all():
        raise ValueError("Every row must be SAFE or VIOLATION. No blanks or N/A.")
    tp = int(((a=="VIOLATION") & (p=="VIOLATION")).sum())
    tn = int(((a=="SAFE") & (p=="SAFE")).sum())
    fp = int(((a=="SAFE") & (p=="VIOLATION")).sum())
    fn = int(((a=="VIOLATION") & (p=="SAFE")).sum())
    n = tp+tn+fp+fn
    result = {
        "samples": n, "TP": tp, "TN": tn, "FP": fp, "FN": fn,
        "zone_accuracy": (tp+tn)/n,
        "false_violation_rate": fp/(fp+tn) if fp+tn else float("nan"),
        "violation_recall": tp/(tp+fn) if tp+fn else float("nan"),
    }
    if output_csv:
        output = Path(output_csv)
        output.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame([result]).to_csv(output, index=False)
    return result


def parse_detection_json(value):
    """Parse frame_predictions.csv 'detections' into a list of boxes."""
    parsed = json.loads(value)
    if not isinstance(parsed, list):
        raise ValueError("detections JSON must be a list")
    return parsed
