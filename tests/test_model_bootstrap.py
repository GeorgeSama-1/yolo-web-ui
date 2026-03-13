import unittest

from model_bootstrap import pick_current_model_key


class ModelBootstrapTests(unittest.TestCase):
    def test_returns_none_when_no_models_exist(self):
        self.assertIsNone(pick_current_model_key({}, None))

    def test_keeps_previous_model_when_it_still_exists(self):
        models = {"a": {}, "b": {}}
        self.assertEqual(pick_current_model_key(models, "b"), "b")

    def test_picks_first_model_when_previous_is_missing(self):
        models = {"first": {}, "second": {}}
        self.assertEqual(pick_current_model_key(models, "missing"), "first")


if __name__ == "__main__":
    unittest.main()
