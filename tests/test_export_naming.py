import unittest

from export_naming import build_labelme_json_filename


class ExportNamingTestCase(unittest.TestCase):
    def test_uses_original_image_stem_for_labelme_json(self):
        self.assertEqual(
            build_labelme_json_filename('insulator_001.jpg'),
            'insulator_001.json'
        )

    def test_does_not_append_model_suffix_to_labelme_json(self):
        self.assertEqual(
            build_labelme_json_filename('tower.segment.v2.png'),
            'tower.segment.v2.json'
        )


if __name__ == '__main__':
    unittest.main()
