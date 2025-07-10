from .brand_manager import BrandManager
from .ocr_scanner import OCRScanner
from .logo_scanner import LogoScanner
import os

class ScannerEngine:
    def __init__(self, brand_manager: BrandManager):
        """
        Initializes the ScannerEngine.
        :param brand_manager: An instance of BrandManager.
        """
        if not isinstance(brand_manager, BrandManager):
            raise ValueError("ScannerEngine requires a valid BrandManager instance.")

        self.brand_manager = brand_manager

        try:
            self.ocr_scanner = OCRScanner() # This will check for Tesseract
        except Exception as e:
            print(f"ScannerEngine: Failed to initialize OCRScanner: {e}. Text scanning will be disabled.")
            self.ocr_scanner = None # Allow engine to run without OCR if it fails to init

        self.logo_scanner = LogoScanner() # Threshold can be adjusted if needed, uses default for now

        print("ScannerEngine initialized.")

    def scan_image(self, image_path):
        """
        Performs a full scan (OCR and Logo) on the given image.
        :param image_path: Path to the image file to be scanned.
        :return: A list of aggregated detection results. Each result is a dictionary, e.g.,
                 {'brand_name': str, 'type': 'ocr'/'logo', 'details': str_keyword_or_logo_path,
                  'box': [x,y,w,h] (optional for text), 'confidence': float (optional for text)}
        """
        if not os.path.exists(image_path):
            print(f"ScannerEngine Error: Image path not found: {image_path}")
            return []

        print(f"\nScannerEngine: Starting scan for image: {image_path}")
        aggregated_results = []

        # 1. OCR and Keyword Spotting
        if self.ocr_scanner:
            print("ScannerEngine: Performing OCR scan...")
            extracted_text = self.ocr_scanner.extract_text(image_path)
            if extracted_text:
                keyword_map = self.brand_manager.get_keyword_map()
                found_brands_by_text = self.ocr_scanner.spot_keywords_in_text(extracted_text, keyword_map)
                for brand_name in found_brands_by_text:
                    # Find which keyword(s) led to this brand for more detailed reporting
                    matched_keywords = []
                    for kw, brands in keyword_map.items():
                        if brand_name in brands and kw in extracted_text.lower():
                            matched_keywords.append(kw)

                    aggregated_results.append({
                        'brand_name': brand_name,
                        'type': 'ocr',
                        'details': f"Matched keywords: {', '.join(matched_keywords)}",
                        'box': None, # Text matches don't typically have a precise box from this method
                        'confidence': 1.0 # Assuming keyword match is high confidence for now
                    })
                if found_brands_by_text:
                     print(f"ScannerEngine: OCR scan found brands: {found_brands_by_text}")
                else:
                     print("ScannerEngine: OCR scan found no matching brands.")
            else:
                print("ScannerEngine: OCR scan extracted no text or failed.")
        else:
            print("ScannerEngine: OCRScanner not available, skipping text scan.")

        # 2. Logo Detection
        print("ScannerEngine: Performing logo scan...")
        logo_map = self.brand_manager.get_logo_map()
        if logo_map: # Check if there are any logos to scan for
            logo_detections = self.logo_scanner.detect_logos(image_path, logo_map)
            # The detect_logos already returns list of dicts in the desired format for 'logo' type
            for detection in logo_detections:
                aggregated_results.append(detection) # Append directly

            if logo_detections:
                print(f"ScannerEngine: Logo scan found {len(logo_detections)} potential logos.")
            else:
                print("ScannerEngine: Logo scan found no matching logos.")
        else:
            print("ScannerEngine: No logos defined in BrandManager, skipping logo scan.")

        if aggregated_results:
            print(f"ScannerEngine: Scan complete for {image_path}. Total potential detections: {len(aggregated_results)}")
        else:
            print(f"ScannerEngine: Scan complete for {image_path}. No items detected.")

        return aggregated_results

# Example Usage (for testing this module directly)
if __name__ == '__main__':
    print("ScannerEngine Module - Direct Test")

    # This test requires:
    # - dummy_brands.json (created by brand_manager.py's test or manually)
    # - Potentially dummy logo files if brand_manager points to them
    # - A dummy image to scan
    # - Tesseract installed for OCR part to run

    # Setup dummy brand_manager stuff (similar to brand_manager.py test)
    dummy_config_content_engine = [
        {
            "name": "BrandAlpha",
            "keywords": ["AlphaText", "Product A"],
            "logo_templates": ["logos/alpha_logo.png"] # Needs a dummy logos/alpha_logo.png
        },
        {
            "name": "BrandBeta",
            "keywords": ["BetaText", "Product B"]
        }
    ]
    dummy_config_path_engine = "dummy_brands_engine.json"
    with open(dummy_config_path_engine, 'w') as f:
        json.dump(dummy_config_content_engine, f, indent=4)

    # Create dummy logo dir and file
    dummy_logos_dir_engine = "logos"
    os.makedirs(dummy_logos_dir_engine, exist_ok=True)
    dummy_logo_path_engine = os.path.join(dummy_logos_dir_engine, "alpha_logo.png")
    # Create a small black square as a dummy logo
    cv2.imwrite(dummy_logo_path_engine, np.zeros((30,30), dtype=np.uint8))
    print(f"Created dummy config {dummy_config_path_engine} and logo {dummy_logo_path_engine}")

    try:
        brand_manager_instance = BrandManager(dummy_config_path_engine)
        scanner_engine_instance = ScannerEngine(brand_manager_instance)

        # Create a dummy image for scanning
        # It should contain text "AlphaText" and the dummy logo (black square)
        dummy_scan_image_path = "dummy_scan_image.png"
        scan_image_height, scan_image_width = 300, 400
        scan_image = np.ones((scan_image_height, scan_image_width), dtype=np.uint8) * 200 # Light gray background

        # Add logo (black square 30x30) at (50,50)
        scan_image[50:50+30, 50:50+30] = 0

        # Add text (Pillow needed for this part of test setup)
        try:
            from PIL import Image, ImageDraw, ImageFont
            pil_img = Image.fromarray(scan_image)
            pil_img = pil_img.convert("RGB") # OCR might work better with RGB
            draw = ImageDraw.Draw(pil_img)
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 18)
            except IOError:
                font = ImageFont.load_default()
            draw.text((100, 150), "This image contains AlphaText for BrandAlpha.", fill=(0,0,0), font=font)
            pil_img.save(dummy_scan_image_path) # Save as PNG
            print(f"Created dummy scan image: {dummy_scan_image_path}")

            results = scanner_engine_instance.scan_image(dummy_scan_image_path)
            print("\nScan Results from Engine:")
            if results:
                for res_item in results:
                    print(f" - {res_item}")
            else:
                print("No detections.")

        except ImportError:
            print("Pillow is not installed. Cannot create text on dummy scan image for engine test.")
        except pytesseract.TesseractNotFoundError: # OCRScanner init might raise this
             print("Tesseract not found by OCRScanner. Engine test will skip OCR.")
             # If OCRScanner init failed, self.ocr_scanner is None, so scan_image should still run logo part.
             results_no_ocr = scanner_engine_instance.scan_image(dummy_scan_image_path) # Test this path
             print("\nScan Results (OCR Disabled):")
             if results_no_ocr:
                for res_item in results_no_ocr:
                    print(f" - {res_item}")
             else:
                print("No detections (OCR Disabled).")

        except Exception as e_inner:
            print(f"Error during ScannerEngine direct test image processing: {e_inner}")

    except pytesseract.TesseractNotFoundError:
         print("Tesseract not found. ScannerEngine test cannot fully proceed for OCR.")
    except Exception as e_outer:
        print(f"Error initializing ScannerEngine or BrandManager for test: {e_outer}")
    finally:
        # Clean up dummy files
        if os.path.exists(dummy_config_path_engine):
            os.remove(dummy_config_path_engine)
        if os.path.exists(dummy_logo_path_engine):
            os.remove(dummy_logo_path_engine)
        if os.path.exists(dummy_logos_dir_engine): # remove dir if empty, or use shutil.rmtree if it could have other files
            try:
                os.rmdir(dummy_logos_dir_engine)
            except OSError:
                print(f"Could not remove dummy logos directory {dummy_logos_dir_engine} (may not be empty or permission issue).")

        if os.path.exists(dummy_scan_image_path):
            os.remove(dummy_scan_image_path)
        print("Cleaned up ScannerEngine test dummy files.")
