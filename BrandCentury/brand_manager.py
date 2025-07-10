import json
import os

class BrandManager:
    def __init__(self, config_filepath):
        self.config_filepath = config_filepath
        self.brands_data = []
        self._keyword_to_brand_map = {}  # {keyword_lowercase: [brand_name1, brand_name2]}
        self._logo_to_brand_map = {}  # {logo_path: brand_name}

        if not os.path.exists(config_filepath):
            print(f"Warning: Brand configuration file not found at {config_filepath}")
            # Potentially create a dummy empty one or raise an error
            # For now, it will just result in empty maps and data.
            return

        self._load_config()

    def _load_config(self):
        try:
            with open(self.config_filepath, 'r') as f:
                self.brands_data = json.load(f)

            # Populate helper maps
            for brand_entry in self.brands_data:
                brand_name = brand_entry.get("name")
                if not brand_name:
                    print(f"Warning: Brand entry missing 'name': {brand_entry}")
                    continue

                # Keywords
                for keyword in brand_entry.get("keywords", []):
                    kw_lower = keyword.lower()
                    if kw_lower not in self._keyword_to_brand_map:
                        self._keyword_to_brand_map[kw_lower] = []
                    if brand_name not in self._keyword_to_brand_map[kw_lower]: # Avoid duplicates if same keyword for same brand
                        self._keyword_to_brand_map[kw_lower].append(brand_name)

                # Logo templates
                for logo_path in brand_entry.get("logo_templates", []):
                    # It's possible multiple brands might somehow reference the same logo file,
                    # but typically one logo file path maps to one brand.
                    # If a logo path is already mapped, this will overwrite. Consider if this is desired.
                    # For now, let's assume a logo path is unique per brand or the last one wins.
                    # A more robust system might check for conflicts or support multiple brands per logo.
                    if logo_path in self._logo_to_brand_map:
                         print(f"Warning: Logo path '{logo_path}' redefined for brand '{brand_name}'. Previous was '{self._logo_to_brand_map[logo_path]}'.")
                    self._logo_to_brand_map[logo_path] = brand_name

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {self.config_filepath}: {e}")
            self.brands_data = [] # Reset on error
        except Exception as e:
            print(f"Error loading brand configuration from {self.config_filepath}: {e}")
            self.brands_data = [] # Reset on error

    def get_all_brands(self):
        """Returns all loaded brand data as a list of dictionaries."""
        return self.brands_data

    def get_brand_by_name(self, name):
        """Returns data for a specific brand by name, or None if not found."""
        for brand_entry in self.brands_data:
            if brand_entry.get("name") == name:
                return brand_entry
        return None

    def get_keyword_map(self):
        """
        Returns a dictionary mapping keywords (lowercase) to a list of brand names.
        e.g., {'keyword1': ['BrandA', 'BrandB'], 'keyword2': ['BrandA']}
        """
        return self._keyword_to_brand_map

    def get_logo_map(self):
        """
        Returns a dictionary mapping logo template file paths to brand names.
        e.g., {'logos/logoA.png': 'BrandA', 'logos/logoB.png': 'BrandB'}
        """
        return self._logo_to_brand_map

# Example Usage (for testing this module directly)
if __name__ == '__main__':
    # Assume a dummy brands.json exists in the same directory for this test
    dummy_config_content = [
        {
            "name": "BrandAlpha",
            "keywords": ["Alpha", "Product A", "AlphaTest"],
            "logo_templates": ["logos/alpha_logo.png", "logos/alpha_icon.png"]
        },
        {
            "name": "BrandBeta",
            "keywords": ["Beta", "Product B", "betatest"],
            "logo_templates": ["logos/beta_logo.png"]
        },
        {
            "name": "BrandGamma",
            "keywords": ["gamma", "alphatest"] # "alphatest" also in BrandAlpha
        }
    ]
    dummy_config_path = "dummy_brands.json"
    with open(dummy_config_path, 'w') as f:
        json.dump(dummy_config_content, f, indent=4)

    print(f"Created {dummy_config_path} for testing.")

    # Test with the dummy file
    brand_manager = BrandManager(dummy_config_path)

    print("\nAll Brands Data:")
    for brand in brand_manager.get_all_brands():
        print(brand)

    print("\nBrandAlpha details:")
    print(brand_manager.get_brand_by_name("BrandAlpha"))

    print("\nKeyword Map:")
    print(brand_manager.get_keyword_map())

    print("\nLogo Map:")
    print(brand_manager.get_logo_map())

    # Clean up dummy file
    os.remove(dummy_config_path)
    print(f"\nRemoved {dummy_config_path}.")
