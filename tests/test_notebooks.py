import json
import unittest
from pathlib import Path


class NotebookTests(unittest.TestCase):
    def test_training_notebooks_are_self_contained(self):
        root = Path(__file__).resolve().parent.parent
        notebook_expectations = {
            "offline_workspace/notebooks/build_insulator_cls_dataset.ipynb": "def _build_split_assignments(image_labels",
            "offline_workspace/notebooks/augment_insulator_cls_dataset.ipynb": "AUGMENT_ABNORMAL_ONLY = True",
            "offline_workspace/notebooks/review_labelme_annotations.ipynb": "offline_workspace/",
            "offline_workspace/notebooks/train_insulator_classifier.ipynb": "'amp': False",
            "offline_workspace/notebooks/run_two_stage_inference.ipynb": "from ultralytics import YOLO",
        }

        for notebook_name, expected_text in notebook_expectations.items():
            notebook_path = root / notebook_name
            self.assertTrue(notebook_path.exists(), f"missing notebook: {notebook_name}")

            payload = json.loads(notebook_path.read_text(encoding="utf-8"))
            self.assertIn("cells", payload)

            all_source = "\n".join(
                "".join(cell.get("source", []))
                for cell in payload.get("cells", [])
            )
            self.assertIn(expected_text, all_source)
            self.assertNotIn("from training.", all_source)
            self.assertNotIn("training.", all_source)

        inference_source = "\n".join(
            "".join(cell.get("source", []))
            for cell in json.loads((root / "offline_workspace/notebooks/run_two_stage_inference.ipynb").read_text(encoding="utf-8")).get("cells", [])
        )
        self.assertIn("summary.json", inference_source)
        self.assertIn("abnormal", inference_source)
        self.assertIn("detections", inference_source)
        self.assertIn("overview", inference_source)
        self.assertIn("instances", inference_source)
        self.assertIn("contact_sheet", inference_source)

        train_source = "\n".join(
            "".join(cell.get("source", []))
            for cell in json.loads((root / "offline_workspace/notebooks/train_insulator_classifier.ipynb").read_text(encoding="utf-8")).get("cells", [])
        )
        self.assertIn("results.png", train_source)
        self.assertIn("confusion_matrix.png", train_source)
        self.assertIn("confusion_matrix_normalized.png", train_source)
        self.assertIn("hsv_h", train_source)
        self.assertIn("fliplr", train_source)


if __name__ == "__main__":
    unittest.main()
