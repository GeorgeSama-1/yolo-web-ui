import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from training.build_insulator_cls_dataset import build_dataset, load_annotations


class BuildInsulatorClsDatasetTests(unittest.TestCase):
    def test_loads_instances_from_labelme_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            annotation_path = root / "sample.json"
            annotation_path.write_text(json.dumps({
                "metadata": {
                    "image_path": "server_image.jpg",
                    "original_path": "folder/sample.jpg",
                    "instances": [
                        {
                            "id": 1,
                            "class_name": "abnormal",
                            "bbox": [10, 20, 40, 60],
                            "confidence": 0.9
                        }
                    ]
                }
            }), encoding="utf-8")

            instances = load_annotations(root)

            self.assertEqual(len(instances), 1)
            self.assertEqual(instances[0]["class_name"], "abnormal")
            self.assertEqual(instances[0]["bbox"], [10, 20, 40, 60])

    def test_builds_padded_classification_crops_and_split_by_image(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            images_dir = root / "images"
            annotations_dir = root / "annotations"
            output_dir = root / "dataset"
            images_dir.mkdir()
            annotations_dir.mkdir()

            for name, color in [("a.jpg", (255, 0, 0)), ("b.jpg", (0, 255, 0))]:
                Image.new("RGB", (100, 80), color).save(images_dir / name)

            for image_name, label in [("a.jpg", "normal"), ("b.jpg", "abnormal")]:
                (annotations_dir / f"{Path(image_name).stem}.json").write_text(json.dumps({
                    "metadata": {
                        "original_path": image_name,
                        "instances": [
                            {
                                "id": 1,
                                "class_name": label,
                                "bbox": [10, 10, 40, 40],
                                "confidence": 0.8
                            }
                        ]
                    }
                }), encoding="utf-8")

            summary = build_dataset(
                annotations_dir=annotations_dir,
                source_images_dir=images_dir,
                output_dir=output_dir,
                split_ratios=(0.5, 0.5, 0.0),
                padding_ratio=0.1,
                min_crop_size=8
            )

            self.assertEqual(summary["total_instances"], 2)
            self.assertEqual(summary["saved_instances"], 2)
            self.assertEqual(summary["class_counts"], {"normal": 1, "abnormal": 1})

            saved_files = sorted(output_dir.glob("*/*/*.jpg"))
            self.assertEqual(len(saved_files), 2)
            self.assertTrue(any("normal" in str(path) for path in saved_files))
            self.assertTrue(any("abnormal" in str(path) for path in saved_files))

    def test_loads_instances_from_standard_labelme_shapes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            annotation_path = root / "sample.json"
            annotation_path.write_text(json.dumps({
                "imagePath": "sample.jpg",
                "shapes": [
                    {
                        "label": "normal",
                        "points": [[12, 18], [40, 52]],
                        "shape_type": "rectangle"
                    },
                    {
                        "label": "abnormal",
                        "points": [[50, 20], [80, 60]],
                        "shape_type": "rectangle"
                    }
                ]
            }), encoding="utf-8")

            instances = load_annotations(root)

            self.assertEqual(len(instances), 2)
            self.assertEqual(instances[0]["id"], 1)
            self.assertEqual(instances[0]["class_name"], "normal")
            self.assertEqual(instances[0]["bbox"], [12, 18, 40, 52])
            self.assertEqual(instances[0]["original_path"], "sample.jpg")
            self.assertEqual(instances[1]["id"], 2)
            self.assertEqual(instances[1]["class_name"], "abnormal")
            self.assertEqual(instances[1]["bbox"], [50, 20, 80, 60])

    def test_reports_skipped_small_crops(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            images_dir = root / "images"
            annotations_dir = root / "annotations"
            output_dir = root / "dataset"
            images_dir.mkdir()
            annotations_dir.mkdir()

            Image.new("RGB", (20, 20), (255, 255, 255)).save(images_dir / "tiny.jpg")
            (annotations_dir / "tiny.json").write_text(json.dumps({
                "metadata": {
                    "original_path": "tiny.jpg",
                    "instances": [
                        {
                            "id": 1,
                            "class_name": "normal",
                            "bbox": [1, 1, 4, 4],
                            "confidence": 0.5
                        }
                    ]
                }
            }), encoding="utf-8")

            summary = build_dataset(
                annotations_dir=annotations_dir,
                source_images_dir=images_dir,
                output_dir=output_dir,
                min_crop_size=10
            )

            self.assertEqual(summary["saved_instances"], 0)
            self.assertEqual(summary["skipped_instances"], 1)
            self.assertEqual(summary["skip_reasons"]["crop_too_small"], 1)


if __name__ == "__main__":
    unittest.main()
