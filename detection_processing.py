from copy import deepcopy


def normalize_class_name(class_name):
    return str(class_name or "").strip().lower()


def calculate_iou(box1, box2):
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2

    inter_x_min = max(x1_min, x2_min)
    inter_y_min = max(y1_min, y2_min)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)

    if inter_x_max <= inter_x_min or inter_y_max <= inter_y_min:
        return 0.0

    inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
    box1_area = (x1_max - x1_min) * (y1_max - y1_min)
    box2_area = (x2_max - x2_min) * (y2_max - y2_min)
    union_area = box1_area + box2_area - inter_area

    return inter_area / union_area if union_area > 0 else 0.0


def _priority_score(detection, abnormal_margin):
    score = float(detection["confidence"])
    if normalize_class_name(detection.get("class_name")) == "abnormal":
        score += abnormal_margin
    return score


def _is_abnormal_normal_pair(detection_a, detection_b):
    pair = {
        normalize_class_name(detection_a.get("class_name")),
        normalize_class_name(detection_b.get("class_name")),
    }
    return pair == {"normal", "abnormal"}


def apply_priority_suppression(detections, iou_threshold=0.3, abnormal_margin=0.1):
    if not detections:
        return []

    ranked = sorted(
        (deepcopy(detection) for detection in detections),
        key=lambda detection: _priority_score(detection, abnormal_margin),
        reverse=True,
    )

    kept = []
    for detection in ranked:
        should_keep = True
        for existing in kept:
            if not _is_abnormal_normal_pair(existing, detection):
                continue

            if calculate_iou(existing["bbox"], detection["bbox"]) >= iou_threshold:
                should_keep = False
                break

        if should_keep:
            kept.append(detection)

    for index, detection in enumerate(kept, start=1):
        detection["id"] = index

    return kept
