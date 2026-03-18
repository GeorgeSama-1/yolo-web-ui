#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Two-stage inference helpers.

Stage 1 keeps the original detection boxes.
Stage 2 classifies each detected crop and merges the results back for UI display.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any


def _clamp_bbox(bbox, width: int, height: int) -> list[int]:
    x1, y1, x2, y2 = bbox
    x1 = max(0, min(int(round(x1)), width - 1))
    y1 = max(0, min(int(round(y1)), height - 1))
    x2 = max(x1 + 1, min(int(round(x2)), width))
    y2 = max(y1 + 1, min(int(round(y2)), height))
    return [x1, y1, x2, y2]


def add_padding_to_bbox(bbox, width: int, height: int, padding_ratio: float = 0.02) -> list[int]:
    x1, y1, x2, y2 = bbox
    box_w = max(1, x2 - x1)
    box_h = max(1, y2 - y1)
    pad_x = box_w * padding_ratio
    pad_y = box_h * padding_ratio
    return _clamp_bbox([x1 - pad_x, y1 - pad_y, x2 + pad_x, y2 + pad_y], width, height)


def classify_detections_on_image(
    image_path: str | Path,
    detections: list[dict[str, Any]],
    classification_model,
    padding_ratio: float = 0.02,
) -> list[dict[str, Any]]:
    import cv2

    if not detections:
        return []

    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"无法读取图片用于二阶段分类: {image_path}")

    height, width = image.shape[:2]
    results = []

    for detection in detections:
        crop_bbox = add_padding_to_bbox(detection['bbox'], width, height, padding_ratio)
        x1, y1, x2, y2 = crop_bbox
        crop = image[y1:y2, x1:x2]

        if crop.size == 0:
            crop_bbox = _clamp_bbox(detection['bbox'], width, height)
            x1, y1, x2, y2 = crop_bbox
            crop = image[y1:y2, x1:x2]

        prediction = classification_model.predict(source=crop, verbose=False)[0]
        probs = prediction.probs
        top1 = int(probs.top1)
        top1_conf = float(probs.top1conf.item())
        names = prediction.names if hasattr(prediction, 'names') else {}

        scores = {
            names.get(index, f'class_{index}'): float(score)
            for index, score in enumerate(probs.data.tolist())
        }

        results.append({
            'class_id': top1,
            'class_name': names.get(top1, f'class_{top1}'),
            'confidence': top1_conf,
            'scores': scores,
            'crop_bbox': crop_bbox,
        })

    return results


def merge_two_stage_predictions(
    detections: list[dict[str, Any]],
    classifications: list[dict[str, Any]],
    abnormal_label: str = 'abnormal',
) -> dict[str, Any]:
    merged_detections = []
    class_counter: Counter[str] = Counter()

    for detection, classification in zip(detections, classifications):
        final_class_name = classification.get('class_name', detection.get('class_name', 'class_0'))
        final_class_id = classification.get('class_id', detection.get('class_id', 0))
        final_confidence = float(classification.get('confidence', detection.get('confidence', 0.0)))
        stage1_bbox = detection.get('bbox', [])

        merged_detection = {
            **detection,
            'bbox': stage1_bbox,
            'class_id': final_class_id,
            'class_name': final_class_name,
            'confidence': final_confidence,
            'stage1_bbox': stage1_bbox,
            'stage1_class_id': detection.get('class_id'),
            'stage1_class_name': detection.get('class_name'),
            'stage1_confidence': detection.get('confidence'),
            'classification': classification,
            'crop_bbox': classification.get('crop_bbox'),
            'is_abnormal': final_class_name.lower() == abnormal_label.lower(),
        }

        class_counter[final_class_name] += 1
        merged_detections.append(merged_detection)

    return {
        'two_stage_enabled': True,
        'detections': merged_detections,
        'class_counts': dict(class_counter),
        'normal_count': class_counter.get('normal', 0),
        'abnormal_count': class_counter.get(abnormal_label, 0),
        'stage1_total_count': len(detections),
    }
