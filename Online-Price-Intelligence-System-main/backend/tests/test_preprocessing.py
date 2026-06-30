import unittest
import numpy as np
import io
import sys
import os
from PIL import Image

# Add the backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.preprocessing import preprocess_image

class TestPreprocessing(unittest.TestCase):
    def setUp(self):
        # Create a dummy image for testing
        self.img = Image.new('RGB', (500, 300), color = 'red')
        self.img_byte_arr = io.BytesIO()
        self.img.save(self.img_byte_arr, format='JPEG')
        self.img_bytes = self.img_byte_arr.getvalue()

    def test_output_shape(self):
        # Test if output shape is (1, 224, 224, 3)
        processed_img = preprocess_image(self.img_bytes)
        self.assertEqual(processed_img.shape, (1, 224, 224, 3))

    def test_output_type(self):
        # Test if output is numpy array
        processed_img = preprocess_image(self.img_bytes)
        self.assertIsInstance(processed_img, np.ndarray)

    def test_grayscale_conversion(self):
        # Test if grayscale image is converted and processed correctly
        gray_img = Image.new('L', (100, 100), color = 128)
        byte_arr = io.BytesIO()
        gray_img.save(byte_arr, format='JPEG')
        processed_img = preprocess_image(byte_arr.getvalue())
        self.assertEqual(processed_img.shape, (1, 224, 224, 3))

    def test_small_image_resizing(self):
        # Test if small image is resized up
        small_img = Image.new('RGB', (10, 10), color = 'blue')
        byte_arr = io.BytesIO()
        small_img.save(byte_arr, format='PNG')
        processed_img = preprocess_image(byte_arr.getvalue())
        self.assertEqual(processed_img.shape, (1, 224, 224, 3))

if __name__ == '__main__':
    unittest.main()
