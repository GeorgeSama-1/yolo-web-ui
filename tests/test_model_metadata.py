import unittest

from model_metadata import parse_experiment_name, summarize_model_info


class ModelMetadataTests(unittest.TestCase):
    def test_parses_baseline_mixed_tokens(self):
        info = parse_experiment_name(
            "20260309_165615_bbox_yolo11x_2class_exp003_bs8_is1280_gpu2_data_v0_base005"
        )

        self.assertEqual(info["timestamp"], "20260309_165615")
        self.assertEqual(info["task"], "bbox")
        self.assertEqual(info["model"], "yolo11x")
        self.assertEqual(info["num_classes"], 2)
        self.assertEqual(info["exp"], "exp003")
        self.assertEqual(info["batch_size"], "8")
        self.assertEqual(info["img_size"], "1280")
        self.assertEqual(info["gpu"], "gpu2")
        self.assertEqual(info["data_version"], "datav0")
        self.assertTrue(info["is_baseline"])
        self.assertEqual(info["baseline_tag"], "base005")

    def test_parses_newdata_baseline_without_batch_size(self):
        info = parse_experiment_name(
            "20260311_093111_bbox_yolo11x_2class_newdata_exp004_base005"
        )

        self.assertEqual(info["num_classes"], 2)
        self.assertEqual(info["data_version"], "newdata")
        self.assertEqual(info["exp"], "exp004")
        self.assertTrue(info["is_baseline"])
        self.assertEqual(info["baseline_tag"], "base005")
        self.assertIsNone(info["batch_size"])
        self.assertIsNone(info["img_size"])

    def test_parses_legacy_single_class_experiment(self):
        info = parse_experiment_name(
            "20260210_092222_bbox_yolo11x_exp003_bs8_is1280_gpu2_datav2"
        )

        self.assertIsNone(info["num_classes"])
        self.assertEqual(info["data_version"], "datav2")
        self.assertFalse(info["is_baseline"])

    def test_builds_clean_summary_for_display(self):
        info = parse_experiment_name(
            "20260312_135352_bbox_yolo11x_2class_exp008_base005"
        )

        summary = summarize_model_info(info)

        self.assertEqual(summary["name"], "YOLO11X | 2类 | exp008 | base005")
        self.assertEqual(summary["description"], "2类 baseline base005 exp008")


if __name__ == "__main__":
    unittest.main()
