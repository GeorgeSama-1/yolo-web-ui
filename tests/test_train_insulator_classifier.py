import tempfile
import unittest
from pathlib import Path

from training.train_insulator_classifier import (
    build_training_config,
    ensure_classification_dataset,
    write_experiment_metadata,
)


class TrainInsulatorClassifierTests(unittest.TestCase):
    def test_validate_dataset_requires_train_and_val_class_folders(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dataset_dir = Path(temp_dir)
            (dataset_dir / "train" / "normal").mkdir(parents=True)

            with self.assertRaises(ValueError):
                ensure_classification_dataset(dataset_dir)

    def test_build_training_config_assembles_output_paths(self):
        config = build_training_config(
            dataset_dir=Path("/tmp/dataset"),
            experiment_root=Path("/tmp/experiments_cls"),
            experiment_name="insulator_cls_exp001",
            model_weights="yolo11n-cls.pt",
            epochs=50,
            imgsz=224,
            batch=16,
            device="0",
        )

        self.assertEqual(config["data"], "/tmp/dataset")
        self.assertEqual(config["project"], "/tmp/experiments_cls")
        self.assertEqual(config["name"], "insulator_cls_exp001")
        self.assertEqual(config["model"], "yolo11n-cls.pt")
        self.assertEqual(config["epochs"], 50)

    def test_writes_experiment_metadata_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "run"
            output_dir.mkdir(parents=True)

            metadata_path = write_experiment_metadata(
                output_dir=output_dir,
                config={"epochs": 20, "model": "yolo11n-cls.pt"},
                dataset_summary={"total_instances": 120, "class_counts": {"normal": 60, "abnormal": 60}},
            )

            self.assertTrue(metadata_path.exists())
            content = metadata_path.read_text(encoding="utf-8")
            self.assertIn('"epochs": 20', content)
            self.assertIn('"total_instances": 120', content)


if __name__ == "__main__":
    unittest.main()
