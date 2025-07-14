import os
import cv2
import numpy as np

def load_images_from_folder(folder):
    """
    Loads all images from a specified folder.

    Args:
        folder (str): The path to the folder containing images.

    Returns:
        A dictionary mapping filenames to the loaded images (as numpy arrays).
    """
    images = {}
    for filename in os.listdir(folder):
        # Check for common image file extensions
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            img = cv2.imread(os.path.join(folder, filename))
            if img is not None:
                images[filename] = img
    return images

def parse_annotations(annotation_path, images):
    """
    Parses annotation files to extract bounding box and label information.

    **Note:** This is a placeholder function and needs to be adapted based
    on the actual annotation format of the chosen dataset (e.g., XML, JSON, CSV).

    Assumed format: A simple CSV file per image named `image_filename.csv`
    with columns: `label,xmin,ymin,xmax,ymax`

    Args:
        annotation_path (str): The path to the folder containing annotations.
        images (dict): A dictionary of loaded images, keyed by filename.

    Returns:
        A dictionary mapping image filenames to a list of annotations, where
        each annotation is a dictionary with 'label' and 'bbox' (bounding box).
    """
    annotations = {}
    for filename in images.keys():
        # Assumes annotation filename matches image filename but with a .txt extension
        # e.g., 'logo1.png' has an annotation file 'logo1.txt'
        base_filename, _ = os.path.splitext(filename)
        annotation_file = os.path.join(annotation_path, base_filename + '.txt')

        if not os.path.exists(annotation_file):
            print(f"Warning: Annotation file not found for {filename}")
            continue

        image_annotations = []
        with open(annotation_file, 'r') as f:
            # This part is highly dependent on the dataset's annotation format.
            # The following is a placeholder for a simple format.
            # For example, for YOLO format: class_id center_x center_y width height
            # For VOC (XML) or COCO (JSON), a different parser would be needed.
            for line in f.readlines():
                parts = line.strip().split()
                if len(parts) >= 5:
                    label = parts[0]
                    # Assuming bounding box is in xmin, ymin, xmax, ymax format
                    bbox = [int(p) for p in parts[1:5]]
                    image_annotations.append({'label': label, 'bbox': bbox})

        annotations[filename] = image_annotations
    return annotations

def preprocess_data(image_folder, annotation_folder):
    """
    Main function to load and preprocess the data.

    Args:
        image_folder (str): Path to the folder with images.
        annotation_folder (str): Path to the folder with annotations.

    Returns:
        A tuple of (images, annotations).
    """
    print("Loading images...")
    images = load_images_from_folder(image_folder)
    print(f"Loaded {len(images)} images.")

    print("Parsing annotations...")
    annotations = parse_annotations(annotation_folder, images)
    print(f"Found annotations for {len(annotations)} images.")

    # Further preprocessing steps could go here, for example:
    # - Resizing images to a consistent size
    # - Normalizing pixel values
    # - Data augmentation (flipping, rotating, etc.)

    return images, annotations

if __name__ == '__main__':
    # Example usage (replace with actual paths when dataset is available)
    # This assumes a directory structure like:
    # /data/
    #   /images/
    #     logo1.png
    #     logo2.jpg
    #   /annotations/
    #     logo1.txt
    #     logo2.txt

    # Create dummy directories and files for testing
    if not os.path.exists('dummy_data/images'):
        os.makedirs('dummy_data/images')
    if not os.path.exists('dummy_data/annotations'):
        os.makedirs('dummy_data/annotations')

    # Create a dummy image and annotation
    dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite('dummy_data/images/test_logo.png', dummy_image)
    with open('dummy_data/annotations/test_logo.txt', 'w') as f:
        f.write('nike 10 10 50 50\n')
        f.write('adidas 60 60 90 90\n')

    print("Running preprocessing script with dummy data...")
    images, annotations = preprocess_data('dummy_data/images', 'dummy_data/annotations')

    # Print out the results for verification
    for filename, data in annotations.items():
        print(f"\nAnnotations for {filename}:")
        for ann in data:
            print(f"  Label: {ann['label']}, BBox: {ann['bbox']}")

    print("\nPreprocessing script finished.")
