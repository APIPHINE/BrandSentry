import unittest
from unittest.mock import patch, MagicMock, ANY
import numpy as np
import cv2

# Add the project root to the path to allow imports from main
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import the class from main
from main import ScreenScanner

class TestScreenScanner(unittest.TestCase):

    @patch('main.load_brand_model')
    @patch('main.load_nudity_detection_model')
    @patch('mss.mss')
    def setUp(self, mock_mss, mock_load_nudity_model, mock_load_brand_model):
        """Set up a fresh scanner for each test."""
        self.mock_nudity_model = MagicMock()
        self.mock_brand_model = MagicMock()
        mock_load_nudity_model.return_value = self.mock_nudity_model
        mock_load_brand_model.return_value = self.mock_brand_model

        # Prevent the scanner from creating directories during tests
        with patch('os.makedirs'):
            self.scanner = ScreenScanner()

    @patch('main.add_scan_result')
    @patch('cv2.imwrite')
    @patch('main.detect_brands')
    @patch('main.detect_and_blur_nudity')
    def test_process_frame_with_detection(self, mock_blur, mock_detect_brands, mock_imwrite, mock_add_scan):
        """
        Tests the frame processing logic when a brand is detected.
        Ensures that images are saved and database entries are created.
        """
        # --- Arrange ---
        dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        blurred_frame = dummy_frame + 1 # Simulate a different frame after blurring
        brand_detections = [{'label': 'test_brand'}]

        mock_blur.return_value = blurred_frame
        mock_detect_brands.return_value = brand_detections

        # --- Act ---
        result = self.scanner.process_frame(dummy_frame)

        # --- Assert ---
        self.assertEqual(result, brand_detections)
        # Check that imwrite was called for original and blurred images
        self.assertEqual(mock_imwrite.call_count, 2)
        # Check that add_scan_result was called once
        mock_add_scan.assert_called_once()
        # Check the arguments passed to add_scan_result.
        # The thumbnail path will be None because cv2.imwrite is mocked.
        mock_add_scan.assert_called_with(ANY, ANY, None, brand_detections)

    @patch('main.add_scan_result')
    @patch('cv2.imwrite')
    @patch('main.detect_brands')
    @patch('main.detect_and_blur_nudity')
    def test_process_frame_no_detection(self, mock_blur, mock_detect_brands, mock_imwrite, mock_add_scan):
        """
        Tests the frame processing logic when no brand is detected.
        Ensures that nothing is saved to disk or the database.
        """
        # --- Arrange ---
        dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_detect_brands.return_value = [] # No detections

        # --- Act ---
        result = self.scanner.process_frame(dummy_frame)

        # --- Assert ---
        self.assertEqual(result, [])
        # Check that no save operations were called
        mock_imwrite.assert_not_called()
        mock_add_scan.assert_not_called()

    @patch('mss.mss')
    def test_capture_screen(self, mock_mss_constructor):
        """Tests that the screen capture method returns a valid OpenCV frame."""
        # --- Arrange ---
        mock_sct_instance = MagicMock()
        mock_mss_constructor.return_value = mock_sct_instance

        mock_grab_result = MagicMock()
        dummy_bgra_frame = np.zeros((100, 100, 4), dtype=np.uint8)
        mock_grab_result.__array__ = MagicMock(return_value=dummy_bgra_frame)
        mock_sct_instance.grab.return_value = mock_grab_result

        with patch('os.makedirs'):
            scanner = ScreenScanner()

        # --- Act ---
        frame = scanner.capture_screen()

        # --- Assert ---
        self.assertIsInstance(frame, np.ndarray)
        self.assertEqual(frame.shape, (100, 100, 3))
        mock_sct_instance.grab.assert_called_with(mock_sct_instance.monitors[1])

if __name__ == '__main__':
    unittest.main()
