import tkinter as tk
from tkinter import ttk
import mss
import cv2
import numpy as np
import time
import threading
import os
from datetime import datetime
from PIL import Image

# Import project modules
from src.nudity.detect import load_nudity_detection_model, detect_and_blur_nudity
from src.database import initialize_database, add_scan_result
from src.viewer import ResultsViewer
from src.config import get_setting

# --- Placeholder Brand Detection ---
def load_brand_model():
    print("Loading brand detection model (placeholder)...")
    def dummy_brand_model(image):
        return [{'label': 'dummy_brand', 'bbox': [10, 10, 80, 80]}]
    return dummy_brand_model

def detect_brands(image, model):
    if model:
        return model(image)
    return []

# --- Core Logic separated for testability ---
class ScreenScanner:
    def __init__(self):
        self.nudity_model = load_nudity_detection_model()
        self.brand_model = load_brand_model()
        self.sct = mss.mss()
        self.captures_dir = "captures"
        self.thumbnails_dir = os.path.join(self.captures_dir, "thumbnails")
        os.makedirs(self.captures_dir, exist_ok=True)
        os.makedirs(self.thumbnails_dir, exist_ok=True)

    def capture_screen(self):
        sct_img = self.sct.grab(self.sct.monitors[1])
        frame = np.array(sct_img)
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    def process_frame(self, frame):
        # 1. Process for nudity and blur if necessary
        # The detect_and_blur_nudity function modifies the frame in place
        blurred_frame = detect_and_blur_nudity(frame.copy(), self.nudity_model)

        # Check if the frame was actually blurred to decide which path to save
        was_blurred = not np.array_equal(frame, blurred_frame)

        # 2. Process for brands
        detected_brands = detect_brands(blurred_frame, self.brand_model)

        # 3. Save results if brands are detected
        if detected_brands:
            now = datetime.now()
            timestamp_str = now.strftime("%Y%m%d_%H%M%S")

            # Save the original and blurred images
            original_filename = f"{timestamp_str}_original.png"
            original_path = os.path.join(self.captures_dir, original_filename)
            cv2.imwrite(original_path, frame)

            # Generate and save thumbnail
            thumbnail_filename = f"{timestamp_str}_thumb.png"
            thumbnail_path = os.path.join(self.thumbnails_dir, thumbnail_filename)
            try:
                with Image.open(original_path) as img:
                    img.thumbnail((150, 150))
                    img.save(thumbnail_path)
            except IOError as e:
                print(f"Error creating thumbnail: {e}")
                thumbnail_path = None # Set path to None if thumbnail fails

            blurred_path = None
            if was_blurred:
                blurred_filename = f"{timestamp_str}_blurred.png"
                blurred_path = os.path.join(self.captures_dir, blurred_filename)
                cv2.imwrite(blurred_path, blurred_frame)

            # Add to database
            add_scan_result(original_path, blurred_path, thumbnail_path, detected_brands)

        return detected_brands

    def close(self):
        self.sct.close()

# --- GUI Application ---
class App:
    def __init__(self, root, scanner):
        self.root = root
        self.scanner = scanner
        self.root.title("Brand Century Scanner")

        # --- State Variables ---
        self.is_scanning = False
        self.scan_interval_seconds = int(get_setting('Settings', 'scan_interval_seconds', fallback=5))
        self.status_text = tk.StringVar(value="Status: Stopped")
        self.scan_thread = None

        # --- UI Elements ---
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.start_stop_button = ttk.Button(self.main_frame, text="Start Scan", command=self.toggle_scan)
        self.start_stop_button.grid(row=0, column=0, padx=5, pady=5)

        self.view_results_button = ttk.Button(self.main_frame, text="View Results", command=self.open_viewer)
        self.view_results_button.grid(row=0, column=1, padx=5, pady=5)

        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_text)
        self.status_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def open_viewer(self):
        # Prevents opening multiple viewer windows
        if not hasattr(self, "viewer_window") or not self.viewer_window.winfo_exists():
            self.viewer_window = ResultsViewer(self.root)
        self.viewer_window.focus()

    def toggle_scan(self):
        if self.is_scanning:
            self.stop_scan()
        else:
            self.start_scan()

    def start_scan(self):
        self.is_scanning = True
        self.status_text.set(f"Status: Scanning every {self.scan_interval_seconds}s")
        self.start_stop_button.config(text="Stop Scan")

        self.scan_thread = threading.Thread(target=self.scan_loop, daemon=True)
        self.scan_thread.start()

    def stop_scan(self):
        self.is_scanning = False
        self.status_text.set("Status: Stopped")
        self.start_stop_button.config(text="Start Scan")

    def scan_loop(self):
        while self.is_scanning:
            frame = self.scanner.capture_screen()
            detected_brands = self.scanner.process_frame(frame)

            if detected_brands:
                print(f"Detected brands: {[b['label'] for b in detected_brands]}")
                # Logic for saving/further scanning is now in process_frame

            time.sleep(self.scan_interval_seconds)

    def on_closing(self):
        self.stop_scan()
        self.scanner.close()
        self.root.destroy()


if __name__ == "__main__":
    # Initialize the database when the app starts
    initialize_database()

    # This part will still fail in a headless environment, but the logic is now testable.
    try:
        root = tk.Tk()
        scanner = ScreenScanner()
        app = App(root, scanner)
        root.mainloop()
    except tk.TclError as e:
        print(f"Tkinter error: {e}")
        print("This is expected in a headless environment.")
        print("The ScreenScanner class can still be tested independently.")
