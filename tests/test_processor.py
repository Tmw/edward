import unittest
from unittest.mock import patch
from PIL import Image

import processor


class ProcessorTest(unittest.TestCase):

    def test_normalize_input(self):
        img = Image.new("RGB", (400, 400), "#ff0000")
        normalized = processor.normalize_input(img)
        assert normalized.shape == (224, 224, 3), "Incorrect shape"

    @patch('processor.load_model', return_value="OK")
    def test_prepare(self, MockLoadModel):
        processor.prepare()

        assert MockLoadModel.called, "load_model not called"
        assert processor.model == "OK", "model not assigned"
