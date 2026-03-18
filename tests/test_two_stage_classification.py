import unittest

from two_stage_classification import merge_two_stage_predictions


class TwoStageClassificationTests(unittest.TestCase):
    def test_merge_two_stage_predictions_keeps_stage1_bbox_and_adds_classification_fields(self):
        detections = [
            {
                'id': 1,
                'bbox': [10, 20, 110, 220],
                'class_id': 0,
                'class_name': 'insulator',
                'confidence': 0.92,
            }
        ]
        classifications = [
            {
                'class_id': 1,
                'class_name': 'abnormal',
                'confidence': 0.88,
                'scores': {'normal': 0.12, 'abnormal': 0.88},
                'crop_bbox': [8, 18, 112, 224],
            }
        ]

        result = merge_two_stage_predictions(detections, classifications)

        self.assertTrue(result['two_stage_enabled'])
        self.assertEqual(result['normal_count'], 0)
        self.assertEqual(result['abnormal_count'], 1)
        self.assertEqual(result['class_counts'], {'abnormal': 1})
        self.assertEqual(result['detections'][0]['bbox'], [10, 20, 110, 220])
        self.assertEqual(result['detections'][0]['stage1_bbox'], [10, 20, 110, 220])
        self.assertEqual(result['detections'][0]['stage1_class_name'], 'insulator')
        self.assertEqual(result['detections'][0]['classification']['class_name'], 'abnormal')
        self.assertTrue(result['detections'][0]['is_abnormal'])


if __name__ == '__main__':
    unittest.main()
