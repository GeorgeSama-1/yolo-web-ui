#!/usr/bin/env python3

import argparse
import json
from datetime import datetime
from pathlib import Path


def ensure_classification_dataset(dataset_dir):
    dataset_dir = Path(dataset_dir)
    required_dirs = [
        dataset_dir / "train",
        dataset_dir / "val",
    ]

    for directory in required_dirs:
        if not directory.exists():
            raise ValueError(f"Missing dataset split directory: {directory}")
        class_dirs = [path for path in directory.iterdir() if path.is_dir()]
        if not class_dirs:
            raise ValueError(f"No class directories found in: {directory}")

    return dataset_dir


def build_training_config(
    dataset_dir,
    experiment_root,
    experiment_name,
    model_weights="yolo11n-cls.pt",
    epochs=100,
    imgsz=224,
    batch=32,
    device="0",
):
    return {
        "model": model_weights,
        "data": str(Path(dataset_dir)),
        "project": str(Path(experiment_root)),
        "name": experiment_name,
        "epochs": epochs,
        "imgsz": imgsz,
        "batch": batch,
        "device": device,
        "save": True,
        "exist_ok": True,
    }


def write_experiment_metadata(output_dir, config, dataset_summary=None):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "created_at": datetime.now().isoformat(),
        "config": config,
        "dataset_summary": dataset_summary or {},
    }
    metadata_path = output_dir / "classifier_experiment.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    return metadata_path


def run_training(config):
    from ultralytics import YOLO

    model = YOLO(config["model"])
    return model.train(**{key: value for key, value in config.items() if key != "model"})


def main():
    parser = argparse.ArgumentParser(description="Train second-stage insulator classifier.")
    parser.add_argument("--dataset-dir", required=True)
    parser.add_argument("--experiment-root", default="experiments_cls")
    parser.add_argument("--experiment-name", required=True)
    parser.add_argument("--model-weights", default="yolo11n-cls.pt")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=224)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--device", default="0")
    args = parser.parse_args()

    dataset_dir = ensure_classification_dataset(args.dataset_dir)
    config = build_training_config(
        dataset_dir=dataset_dir,
        experiment_root=args.experiment_root,
        experiment_name=args.experiment_name,
        model_weights=args.model_weights,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
    )
    write_experiment_metadata(
        output_dir=Path(args.experiment_root) / args.experiment_name,
        config=config,
    )
    run_training(config)


if __name__ == "__main__":
    main()
