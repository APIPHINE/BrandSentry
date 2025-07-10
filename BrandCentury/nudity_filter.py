import os
# Nudenet can be heavy, so only import if necessary or make it clear models download on first run.
# from nudenet import NudeDetector # This will be used in the detection function
import cv2 # For image loading and blurring
import numpy as np # For image manipulation with OpenCV

# Initialize the detector. This can take time as it might download models.
# It's better to initialize it once and reuse, perhaps in a class structure later if needed.
# For now, a global detector instance can be created when the module is first used.
# Or, initialize it within the first function call that needs it.

DEFAULT_NUDENET_MODEL_PATH = os.path.expanduser("~/.NudeNet")

class NudityFilter:
    def __init__(self, model_path=None):
        """
        Initializes the NudityFilter.
        The NudeDetector model will be loaded on the first call to detect().
        """
        self.detector = None
        self.model_path = model_path if model_path else DEFAULT_NUDENET_MODEL_PATH
        # We can check if model_path exists or if NudeNet default models are present
        # but NudeNet itself handles model downloads.

        # Note: NudeNet's NudeDetector might download models to ~/.NudeNet by default
        # if specific model files aren't provided.
        # For a serverless or restricted environment, pre-packaging models would be necessary.
        # In this sandboxed environment, it will likely try to download to the user's home dir.

    def _load_detector_if_needed(self):
        if self.detector is None:
            print("Loading NudeDetector model...")
            try:
                from nudenet import NudeDetector
                # One can specify model files like:
                # self.detector = NudeDetector(model_files=['path_to_onnx_model.onnx'])
                # If no specific files, it uses its default (and downloads if not present)
                # Forcing a specific path for models might be useful for sandboxed environments
                # if ~/.NudeNet is not writable or persistent.
                # However, NudeNet's internal logic might still try to write to ~/.NudeNet for its classifier.
                # For now, let's use the default behavior.
                self.detector = NudeDetector()
                print("NudeDetector model loaded.")
            except Exception as e:
                print(f"Error loading NudeDetector: {e}")
                # Potentially raise an error or handle it so the app can continue degraded
                raise

    def detect_nudity(self, image_path):
        """
        Detects nudity in an image.
        Placeholder for now - will be fully implemented in step 2.2.
        """
        self._load_detector_if_needed()
        if not self.detector:
            print("NudityFilter: Detector not loaded. Cannot perform detection.")
            return []

        try:
            if not os.path.exists(image_path):
                print(f"NudityFilter: Image path not found: {image_path}")
                return []

            print(f"NudityFilter: Detecting nudity in {image_path}...")
            # The NudeDetector.detect() method returns a list of dictionaries.
            # Each dictionary contains 'box' (list of x_min, y_min, x_max, y_max),
            # 'score' (float), 'label' (str, e.g., 'EXPOSED_BREAST_F').
            results = self.detector.detect(image_path)

            # Nudenet results can sometimes be structured with 'parts' under a main detection.
            # For simplicity, we'll extract all 'box' items.
            # The structure might be like: [{'label': 'unsafe', 'score': X, 'parts': [{'box': [], 'label': Y, 'score': Z}, ... ]}]
            # Or just a flat list of detections: [{'box': [], 'label': Y, 'score': Z}, ...]

            detected_boxes = []
            if isinstance(results, list):
                for item in results:
                    if isinstance(item, dict):
                        if 'box' in item and item['box']: # Ensure box is not empty
                            # Filter by labels considered as "nudity" if necessary.
                            # NudeNet's classifiers are generally for various levels of exposure.
                            # For blurring, we are interested in any detected part nudenet identifies.
                            # Example labels: 'EXPOSED_ANUS_M', 'EXPOSED_BREAST_F', 'EXPOSED_GENITALIA_F', etc.
                            # We can add a filter here if some labels should be ignored.
                            # For now, assume all detected parts with a box are relevant for blurring.
                            detected_boxes.append(item['box'])
                        elif 'parts' in item and isinstance(item['parts'], list): # Handle nested structure
                            for part in item['parts']:
                                if isinstance(part, dict) and 'box' in part and part['box']:
                                     detected_boxes.append(part['box'])

            if detected_boxes:
                print(f"NudityFilter: Detected {len(detected_boxes)} nude regions.")
            else:
                print(f"NudityFilter: No nude regions detected in {image_path}.")
            return detected_boxes

        except Exception as e:
            print(f"NudityFilter: Error during nudity detection for {image_path}: {e}")
            return []

    def blur_regions(self, image_path_or_matrix, boxes):
        """
        Applies blur to the specified regions (boxes) of an image.

        :param image_path_or_matrix: Path to the image file or an OpenCV image matrix (numpy array).
        :param boxes: A list of bounding boxes, where each box is [x_min, y_min, x_max, y_max].
        :return: An OpenCV image matrix (numpy array) with specified regions blurred, or None if an error occurs.
        """
        if not boxes:
            # If no boxes, no blurring needed. If it's a path, load and return. If matrix, return as is.
            if isinstance(image_path_or_matrix, str):
                if not os.path.exists(image_path_or_matrix):
                    print(f"NudityFilter: Image path not found for blurring: {image_path_or_matrix}")
                    return None
                try:
                    image = cv2.imread(image_path_or_matrix)
                    if image is None:
                        print(f"NudityFilter: Failed to load image for blurring: {image_path_or_matrix}")
                        return None
                    return image
                except Exception as e:
                    print(f"NudityFilter: Error loading image {image_path_or_matrix} for blurring: {e}")
                    return None
            elif isinstance(image_path_or_matrix, np.ndarray):
                return image_path_or_matrix.copy() # Return a copy
            else:
                print("NudityFilter: Invalid image input for blurring.")
                return None

        try:
            if isinstance(image_path_or_matrix, str):
                if not os.path.exists(image_path_or_matrix):
                    print(f"NudityFilter: Image path not found for blurring: {image_path_or_matrix}")
                    return None
                image = cv2.imread(image_path_or_matrix)
                if image is None:
                    print(f"NudityFilter: Failed to load image for blurring: {image_path_or_matrix}")
                    return None
            elif isinstance(image_path_or_matrix, np.ndarray):
                image = image_path_or_matrix.copy() # Work on a copy
            else:
                print("NudityFilter: Invalid image input type for blurring.")
                return None

            height, width = image.shape[:2]

            for box in boxes:
                x_min, y_min, x_max, y_max = map(int, box) # Ensure coordinates are integers

                # Clamp coordinates to image dimensions
                x_min = max(0, x_min)
                y_min = max(0, y_min)
                x_max = min(width, x_max)
                y_max = min(height, y_max)

                if x_min >= x_max or y_min >= y_max: # Skip if box is invalid or has no area
                    print(f"NudityFilter: Skipping invalid or zero-area box {box}")
                    continue

                region_of_interest = image[y_min:y_max, x_min:x_max]

                # Apply Gaussian blur. Kernel size must be odd and positive.
                # Adjust kernel size based on region size for better effect, or use a fixed substantial blur.
                # For simplicity, using a fixed kernel size. Larger means more blur.
                # Kernel size should be appropriate for the size of typical regions.
                k_size = (51, 51) # Must be odd integers

                # Ensure kernel size is not larger than the ROI dimensions
                roi_h, roi_w = region_of_interest.shape[:2]
                if roi_h > 0 and roi_w > 0: # Check if ROI is valid
                    actual_k_w = min(k_size[0], roi_w if roi_w % 2 != 0 else roi_w -1)
                    actual_k_h = min(k_size[1], roi_h if roi_h % 2 != 0 else roi_h -1)

                    if actual_k_w > 0 and actual_k_h > 0:
                        blurred_region = cv2.GaussianBlur(region_of_interest, (actual_k_w, actual_k_h), 0)
                        image[y_min:y_max, x_min:x_max] = blurred_region
                    else:
                        print(f"NudityFilter: ROI too small for blurring for box {box}")
                else:
                    print(f"NudityFilter: Invalid ROI for box {box}")

            print(f"NudityFilter: Applied blur to {len(boxes)} regions.")
            return image

        except Exception as e:
            print(f"NudityFilter: Error during image blurring: {e}")
            return None


# Example of how it might be used (for testing or later integration)
if __name__ == '__main__':
    # This part is for direct testing of this script, not for the main app.
    # It assumes an image 'test_image.jpg' exists in the same directory.
    print("Nudity Filter Module - Direct Test")

    # Since NudeNet might download models, running this directly might take time
    # and require internet access.

    # filter_instance = NudityFilter()
    # try:
    #     # Create a dummy image file for testing if one doesn't exist.
    #     # This is tricky as we need an actual image for nudenet.
    #     # For now, just illustrate the call.
    #     if not os.path.exists("test_image.jpg"):
    #       print("test_image.jpg not found. Skipping detection test.")
    #     else:
    #       detections = filter_instance.detect_nudity("test_image.jpg")
    #       if detections:
    #           print(f"Detected {len(detections)} nude parts.")
    #           for detection in detections:
    #               print(f" - Box: {detection['box']}, Score: {detection['score']}, Label: {detection['label']}")
    #       else:
    #           print("No nudity detected or detector not loaded.")
    # except Exception as e:
    #     print(f"Error during NudityFilter direct test: {e}")
    pass # End of __main__ block for now.
