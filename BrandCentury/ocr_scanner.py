import pytesseract
from PIL import Image # Pillow for image opening, pytesseract can work with it
import os

class OCRScanner:
    def __init__(self):
        """
        Initializes the OCRScanner.
        Checks if Tesseract is installed and accessible.
        """
        try:
            # You can specify the Tesseract command path if it's not in PATH
            # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' # Example path
            version = pytesseract.get_tesseract_version()
            print(f"OCRScanner: Tesseract version {version} found.")
        except pytesseract.TesseractNotFoundError:
            print("OCRScanner Error: Tesseract is not installed or not found in your PATH.")
            print("Please install Tesseract OCR and ensure it's in your system's PATH.")
            # Depending on desired behavior, could raise an exception here to halt
            # or allow the program to continue with OCR functionality disabled.
            raise # For now, let's make it critical if Tesseract isn't found.
        except Exception as e:
            print(f"OCRScanner Error: An unexpected error occurred during Tesseract version check: {e}")
            raise


    def extract_text(self, image_path):
        """
        Extracts text from the given image file path.

        :param image_path: Path to the image file.
        :return: A string containing all recognized text, or an empty string if an error occurs or no text is found.
        """
        if not os.path.exists(image_path):
            print(f"OCRScanner: Image path not found: {image_path}")
            return ""

        try:
            # Use Pillow to open the image, then pass to pytesseract
            # This provides more robust image handling than letting pytesseract open directly sometimes.
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            if text:
                print(f"OCRScanner: Extracted text from {image_path}.")
            else:
                print(f"OCRScanner: No text found in {image_path}.")
            return text.strip()
        except pytesseract.TesseractError as te:
            # This can happen if Tesseract encounters an issue with the image or its own process
            print(f"OCRScanner: Tesseract error while processing {image_path}: {te}")
            return ""
        except Exception as e:
            print(f"OCRScanner: Failed to extract text from {image_path}. Error: {e}")
            return ""

    def spot_keywords_in_text(self, text_to_search, keyword_to_brand_map):
        """
        Finds which brands' keywords appear in the given text.

        :param text_to_search: The text string (e.g., from OCR).
        :param keyword_to_brand_map: A dictionary mapping lowercase keywords to lists of brand names.
                                     (e.g., from BrandManager.get_keyword_map())
        :return: A list of unique brand names whose keywords were found.
        """
        found_brands = set()
        text_to_search_lower = text_to_search.lower()

        for keyword, brand_names in keyword_to_brand_map.items():
            # keyword is already lowercase from BrandManager
            if keyword in text_to_search_lower:
                for brand_name in brand_names:
                    found_brands.add(brand_name)

        if found_brands:
            print(f"OCRScanner: Spotted keywords for brands: {list(found_brands)}")
        else:
            print("OCRScanner: No defined keywords spotted in text.")

        return list(found_brands)

# Example Usage (for testing this module directly)
if __name__ == '__main__':
    print("OCR Scanner Module - Direct Test")

    # This test requires Tesseract to be installed and a sample image.
    # It also needs a dummy BrandManager output for keyword spotting.

    try:
        ocr_scanner_instance = OCRScanner() # This will check for Tesseract

        # Create a dummy image for testing (Pillow can create a simple one)
        # This is a very basic image, real OCR performance varies greatly.
        try:
            from PIL import Image, ImageDraw, ImageFont
            dummy_image_path = "dummy_ocr_test_image.png"
            img = Image.new('RGB', (400, 100), color = (255, 255, 255))
            d = ImageDraw.Draw(img)
            try:
                # Try to use a common font, fallback if not found
                font = ImageFont.truetype("DejaVuSans.ttf", 20)
            except IOError:
                font = ImageFont.load_default() # Default PIL font

            d.text((10,10), "Hello World, this is BrandAlpha.", fill=(0,0,0), font=font)
            d.text((10,40), "Another keyword: Product B from Beta.", fill=(0,0,0), font=font)
            img.save(dummy_image_path)
            print(f"Created dummy image: {dummy_image_path}")

            extracted_text = ocr_scanner_instance.extract_text(dummy_image_path)
            print(f"\nExtracted Text:\n---\n{extracted_text}\n---")

            # Dummy keyword map (similar to what BrandManager would provide)
            dummy_keyword_map = {
                "brandalpha": ["BrandAlpha"],
                "product a": ["BrandAlpha"],
                "beta": ["BrandBeta"],
                "product b": ["BrandBeta"]
            }

            found_brands = ocr_scanner_instance.spot_keywords_in_text(extracted_text, dummy_keyword_map)
            print(f"\nBrands found based on keywords: {found_brands}")

            os.remove(dummy_image_path)
            print(f"Removed {dummy_image_path}")

        except ImportError:
            print("Pillow is not installed, cannot create dummy image for OCR test.")
        except pytesseract.TesseractNotFoundError:
            print("Tesseract not found, skipping OCR part of the test.")
        except Exception as e:
            print(f"Error during OCR direct test: {e}")
            if os.path.exists(dummy_image_path):
                 os.remove(dummy_image_path)


    except pytesseract.TesseractNotFoundError:
        print("Tesseract not found. OCRScanner tests cannot proceed.")
    except Exception as e:
        print(f"Could not initialize OCRScanner for testing: {e}")
