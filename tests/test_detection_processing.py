import unittest

from detection_processing import apply_priority_suppression


class DetectionProcessingTests(unittest.TestCase):
    def test_abnormal_wins_when_overlap_is_high_and_confidence_is_close(self):
        detections = [
            {
                'id': 1,
                'class_name': 'normal',
                'confidence': 0.82,
                'bbox': [0, 0, 100, 100],
            },
            {
                'id': 2,
                'class_name': 'abnormal',
                'confidence': 0.78,
                'bbox': [2, 2, 98, 98],
            },
        ]

        result = apply_priority_suppression(detections, iou_threshold=0.3, abnormal_margin=0.1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['class_name'], 'abnormal')

    def test_normal_survives_when_abnormal_is_far_weaker(self):
        detections = [
            {
                'id': 1,
                'class_name': 'normal',
                'confidence': 0.93,
                'bbox': [0, 0, 100, 100],
            },
            {
                'id': 2,
                'class_name': 'abnormal',
                'confidence': 0.40,
                'bbox': [2, 2, 98, 98],
            },
        ]

        result = apply_priority_suppression(detections, iou_threshold=0.3, abnormal_margin=0.1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['class_name'], 'normal')


if __name__ == '__main__':
    unittest.main()
