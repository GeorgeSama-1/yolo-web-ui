#!/usr/bin/env python3

import argparse
import json
from collections import Counter
from pathlib import Path

from PIL import Image


def _normalize_shape_bbox(points):
    if not points or len(points) < 2:
        return None

    x_values = [point[0] for point in points]
    y_values = [point[1] for point in points]
    return [
        int(min(x_values)),
        int(min(y_values)),
        int(max(x_values)),
        int(max(y_values)),
    ]


def load_annotations(annotations_dir):
    annotations = []
    for annotation_path in sorted(Path(annotations_dir).glob("*.json")):
        payload = json.loads(annotation_path.read_text(encoding="utf-8"))
        metadata = payload.get("metadata", {})
        original_path = metadata.get("original_path") or payload.get("imagePath")
        instances = metadata.get("instances", [])

        if instances:
            for instance in instances:
                annotations.append({
                    **instance,
                    "annotation_path": str(annotation_path),
                    "original_path": instance.get("original_path") or original_path,
                })
            continue

        for index, shape in enumerate(payload.get("shapes", []), start=1):
            if shape.get("shape_type", "rectangle") != "rectangle":
                continue

            bbox = _normalize_shape_bbox(shape.get("points", []))
            if not bbox:
                continue

            annotations.append({
                "id": shape.get("id", index),
                "class_name": shape.get("label"),
                "bbox": bbox,
                "annotation_path": str(annotation_path),
                "original_path": original_path,
            })

    return annotations


def _resolve_image_path(source_images_dir, original_path):
    original_path = Path(original_path)
    candidate = Path(source_images_dir) / original_path
    if candidate.exists():
      return candidate
    return Path(source_images_dir) / original_path.name


def _apply_padding(bbox, width, height, padding_ratio):
    x1, y1, x2, y2 = bbox
    box_width = max(x2 - x1, 1)
    box_height = max(y2 - y1, 1)
    pad_x = box_width * padding_ratio
    pad_y = box_height * padding_ratio
    return [
        max(int(x1 - pad_x), 0),
        max(int(y1 - pad_y), 0),
        min(int(x2 + pad_x), width),
        min(int(y2 + pad_y), height),
    ]


def _pick_split(original_path, split_ratios):
    train_ratio, val_ratio, _ = split_ratios
    bucket = sum(ord(char) for char in str(original_path)) % 1000 / 1000.0
    if bucket < train_ratio:
        return "train"
    if bucket < train_ratio + val_ratio:
        return "val"
    return "test"


def build_dataset(
    annotations_dir,
    source_images_dir,
    output_dir,
    split_ratios=(0.8, 0.1, 0.1),
    padding_ratio=0.05,
    min_crop_size=16,
):
    annotations = load_annotations(annotations_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    class_counts = Counter()
    skip_reasons = Counter()
    saved_instances = 0

    for instance in annotations:
        label = instance.get("class_name")
        original_path = instance.get("original_path")
        bbox = instance.get("bbox")

        if not label or not original_path or not bbox:
            skip_reasons["invalid_instance"] += 1
            continue

        image_path = _resolve_image_path(source_images_dir, original_path)
        if not image_path.exists():
            skip_reasons["missing_image"] += 1
            continue

        with Image.open(image_path) as image:
            rgb_image = image.convert("RGB")
            padded_bbox = _apply_padding(bbox, rgb_image.width, rgb_image.height, padding_ratio)
            x1, y1, x2, y2 = padded_bbox

            if (x2 - x1) < min_crop_size or (y2 - y1) < min_crop_size:
                skip_reasons["crop_too_small"] += 1
                continue

            split_name = _pick_split(original_path, split_ratios)
            target_dir = output_dir / split_name / label
            target_dir.mkdir(parents=True, exist_ok=True)

            crop = rgb_image.crop((x1, y1, x2, y2))
            output_name = f"{Path(original_path).stem}_inst{instance.get('id', saved_instances + 1)}.jpg"
            crop.save(target_dir / output_name, quality=95)

            saved_instances += 1
            class_counts[label] += 1

    summary = {
        "total_instances": len(annotations),
        "saved_instances": saved_instances,
        "skipped_instances": len(annotations) - saved_instances,
        "class_counts": dict(class_counts),
        "skip_reasons": dict(skip_reasons),
    }

    summary_path = output_dir / "dataset_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description="Build second-stage insulator classification dataset from exported annotations.")
    parser.add_argument("--annotations-dir", required=True)
    parser.add_argument("--source-images-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--padding-ratio", type=float, default=0.05)
    parser.add_argument("--min-crop-size", type=int, default=16)
    args = parser.parse_args()

    summary = build_dataset(
        annotations_dir=args.annotations_dir,
        source_images_dir=args.source_images_dir,
        output_dir=args.output_dir,
        padding_ratio=args.padding_ratio,
        min_crop_size=args.min_crop_size,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
