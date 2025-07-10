import cv2
import numpy as np
import os

class LogoScanner:
    def __init__(self, default_match_threshold=0.8):
        """
        Initializes the LogoScanner.
        :param default_match_threshold: Default threshold for template matching confidence.
        """
        self.default_match_threshold = default_match_threshold
        print(f"LogoScanner initialized with default threshold: {self.default_match_threshold}")

    def detect_logos(self, screenshot_path, logo_to_brand_map, threshold=None):
        """
        Detects logos in a screenshot using template matching.

        :param screenshot_path: Path to the screenshot image file.
        :param logo_to_brand_map: Dictionary mapping logo template file paths to brand names.
                                 (e.g., from BrandManager.get_logo_map())
        :param threshold: Optional specific threshold for this detection run. Uses default if None.
        :return: A list of detection results, where each result is a dictionary:
                 {'brand_name': str, 'box': [x, y, w, h], 'confidence': float, 'type': 'logo'}
        """
        if threshold is None:
            threshold = self.default_match_threshold

        detections = []

        if not os.path.exists(screenshot_path):
            print(f"LogoScanner Error: Screenshot path not found: {screenshot_path}")
            return detections

        try:
            screenshot_img = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
            if screenshot_img is None:
                print(f"LogoScanner Error: Failed to load screenshot image: {screenshot_path}")
                return detections
        except Exception as e:
            print(f"LogoScanner Error: Exception loading screenshot {screenshot_path}: {e}")
            return detections

        if not logo_to_brand_map:
            print("LogoScanner: No logo templates provided for detection.")
            return detections

        for logo_path, brand_name in logo_to_brand_map.items():
            if not os.path.exists(logo_path):
                print(f"LogoScanner Warning: Logo template not found: {logo_path} for brand {brand_name}. Skipping.")
                continue

            try:
                template_img = cv2.imread(logo_path, cv2.IMREAD_GRAYSCALE)
                if template_img is None:
                    print(f"LogoScanner Warning: Failed to load logo template: {logo_path} for brand {brand_name}. Skipping.")
                    continue

                w, h = template_img.shape[::-1] # width, height of template

                # Perform template matching
                # TM_CCOEFF_NORMED is often a good choice
                match_method = cv2.TM_CCOEFF_NORMED
                res = cv2.matchTemplate(screenshot_img, template_img, match_method)

                # Find locations where the match exceeds the threshold
                loc = np.where(res >= threshold)

                # For TM_CCOEFF_NORMED, the max value in 'res' is the best match confidence for that template.
                # We can iterate through all points 'loc' that are above threshold for multi-matching,
                # or just take the best one if non-overlapping is assumed or handled later.
                # For simplicity, let's consider all matches above threshold.

                # Need to handle overlapping detections if multiple logos are close or same logo appears multiple times.
                # A common approach is Non-Maximum Suppression (NMS).
                # For this initial version, we'll add all raw matches over threshold.
                # This might result in multiple bounding boxes for the same logo instance if they are slightly offset.

                match_points_count = 0
                for pt in zip(*loc[::-1]): # Switch x and y, loc is (y,x)
                    confidence = res[pt[1], pt[0]] # Get the confidence at this specific point
                    # pt is (x, y) which is top-left of the matched area

                    # Create bounding box: [x, y, width, height]
                    box = [pt[0], pt[1], w, h]

                    detections.append({
                        'brand_name': brand_name,
                        'box': box,
                        'confidence': float(confidence), # Ensure it's a Python float
                        'type': 'logo'
                    })
                    match_points_count += 1

                if match_points_count > 0:
                    print(f"LogoScanner: Found {match_points_count} potential matches for {brand_name} (logo: {os.path.basename(logo_path)}) with threshold {threshold:.2f}.")

            except Exception as e:
                print(f"LogoScanner Error: Exception during template matching for {logo_path}: {e}")
                continue # Continue with the next logo template

        if detections:
            print(f"LogoScanner: Total logo detections: {len(detections)}")
        else:
            print("LogoScanner: No logos detected meeting the criteria.")

        return detections

# Example Usage (for testing this module directly)
if __name__ == '__main__':
    print("Logo Scanner Module - Direct Test")

    # This test requires OpenCV and some sample images.
    # Create dummy screenshot and logo images for testing.

    # Dummy screenshot (e.g., a white background with a black square)
    dummy_screenshot_path = "dummy_screenshot.png"
    screenshot = np.zeros((300, 400), dtype=np.uint8) # Grayscale
    screenshot[50:150, 100:200] = 255 # A white square (logo area)
    cv2.imwrite(dummy_screenshot_path, screenshot)
    print(f"Created dummy screenshot: {dummy_screenshot_path}")

    # Dummy logo (the white square itself)
    dummy_logo_path = "dummy_logo.png"
    logo = np.ones((100, 100), dtype=np.uint8) * 255 # White square
    cv2.imwrite(dummy_logo_path, logo)
    print(f"Created dummy logo: {dummy_logo_path}")

    # Dummy logo map
    dummy_logo_brand_map = {
        dummy_logo_path: "TestBrandLogo"
    }

    scanner = LogoScanner(default_match_threshold=0.7)

    try:
        found_logos = scanner.detect_logos(dummy_screenshot_path, dummy_logo_brand_map)

        if found_logos:
            print("\nDetected Logos:")
            for item in found_logos:
                print(f" - Brand: {item['brand_name']}, Box: {item['box']}, Confidence: {item['confidence']:.4f}")
        else:
            print("\nNo logos detected in the dummy test.")

    except Exception as e:
        print(f"Error during LogoScanner direct test: {e}")
    finally:
        # Clean up dummy files
        if os.path.exists(dummy_screenshot_path):
            os.remove(dummy_screenshot_path)
        if os.path.exists(dummy_logo_path):
            os.remove(dummy_logo_path)
        print("Cleaned up dummy image files.")
