import sys
import os
import datetime
import subprocess # Added for screenshot capture
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import QTimer, QDateTime
from .nudity_filter import NudityFilter # Import the filter using relative import
import cv2 # For saving the blurred image if needed

class BrandCenturyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Brand Century Screenshotter")
        self.setGeometry(100, 100, 400, 200)  # x, y, width, height

        self.screenshot_timer = QTimer(self)
        self.screenshot_timer.timeout.connect(self.capture_and_save_screenshot) # Connect the timer

        self.is_capturing = False
        self.screenshot_interval = 5000  # Default to 5 seconds (in milliseconds)

        # Define base directories
        self.base_project_dir = os.path.abspath("BrandCentury")
        self.screenshots_base_dir = os.path.join(self.base_project_dir, "Screenshots")
        self.originals_base_dir = os.path.join(self.base_project_dir, "Originals")
        self.blurred_base_dir = os.path.join(self.base_project_dir, "BlurredScreenshots")

        # Initialize NudityFilter
        self.nudity_filter = NudityFilter()

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Controls Layout
        controls_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Capturing")
        self.start_button.clicked.connect(self.start_capture)
        controls_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Capturing")
        self.stop_button.clicked.connect(self.stop_capture)
        self.stop_button.setEnabled(False)
        controls_layout.addWidget(self.stop_button)

        main_layout.addLayout(controls_layout)

        # Interval Layout
        interval_layout = QHBoxLayout()
        interval_label = QLabel("Interval:")
        interval_layout.addWidget(interval_label)

        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["1 Second", "2 Seconds", "5 Seconds"])
        self.interval_combo.setCurrentText("5 Seconds") # Default
        self.interval_combo.currentIndexChanged.connect(self.update_interval)
        interval_layout.addWidget(self.interval_combo)
        interval_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        main_layout.addLayout(interval_layout)

        # Status Layout
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Idle")
        status_layout.addWidget(self.status_label)
        status_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        main_layout.addLayout(status_layout)

        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(main_layout)

    def start_capture(self):
        self.is_capturing = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.interval_combo.setEnabled(False)
        self.status_label.setText(f"Status: Capturing every {self.interval_combo.currentText()}...")
        self.screenshot_timer.start(self.screenshot_interval)
        # Perform an immediate capture on start, if desired (optional, not explicitly in plan but common)
        # self.capture_and_save_screenshot()
        print(f"Capture started. Interval: {self.screenshot_interval}ms")

    def stop_capture(self):
        self.is_capturing = False
        self.screenshot_timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.interval_combo.setEnabled(True)
        self.status_label.setText("Status: Idle. Stopped.")
        print("Capture stopped.") # Placeholder

    def update_interval(self):
        selected_text = self.interval_combo.currentText()
        if "1 Second" in selected_text:
            self.screenshot_interval = 1000
        elif "2 Seconds" in selected_text:
            self.screenshot_interval = 2000
        elif "5 Seconds" in selected_text:
            self.screenshot_interval = 5000

        if self.is_capturing:
            self.screenshot_timer.stop()
            self.screenshot_timer.start(self.screenshot_interval)
            self.status_label.setText(f"Status: Capturing every {selected_text}...")
        print(f"Interval updated to: {self.screenshot_interval}ms")

    # Placeholder for screenshot functionality - will be implemented in 1.3 and 1.4
    def capture_screenshot_os_native(self, filepath):
        """
        Captures the primary display using macOS native 'screencapture' command.
        Saves the screenshot to the given filepath.
        Returns True on success, False on failure.
        """
        try:
            # -C: Capture the screen, not a window
            # -x: Do not play sounds
            # -m: Capture the main monitor only (if multiple displays)
            # The filepath is the last argument
            subprocess.run(["screencapture", "-C", "-x", "-m", filepath], check=True)
            print(f"Screenshot saved to {filepath}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error capturing screenshot: {e}")
            self.status_label.setText("Status: Error capturing screen!")
            return False
        except FileNotFoundError:
            print("Error: 'screencapture' utility not found. Is this running on macOS?")
            self.status_label.setText("Status: 'screencapture' not found!")
            # Stop trying if the command isn't there
            if self.is_capturing:
                self.stop_capture()
            return False

    def _get_timestamped_filepath(self, base_dir):
        """
        Generates a timestamped filepath within a daily subdirectory of base_dir.
        Ensures the daily subdirectory exists.
        e.g., <base_dir>/YYYY-MM-DD/YYYYMMDD_HHMMSS.png
        """
        now = QDateTime.currentDateTime()
        current_date_str = now.toString("yyyy-MM-dd")
        timestamp_filename = now.toString("yyyyMMdd_HHmmss") + ".png"

        # Ensure the specific base_dir (e.g., BrandCentury/Screenshots) exists
        # This is generally good, though the startup code also creates them.
        os.makedirs(base_dir, exist_ok=True)

        daily_dir = os.path.join(base_dir, current_date_str)

        try:
            os.makedirs(daily_dir, exist_ok=True) # Ensure daily subdir (e.g., <base_dir>/2023-01-01) exists
        except OSError as e:
            print(f"Error creating directory {daily_dir}: {e}")
            self.status_label.setText(f"Status: Error creating dir {current_date_str}")
            if self.is_capturing:
                self.stop_capture()
            return None # Propagate error

        return os.path.join(daily_dir, timestamp_filename)

    def capture_and_save_screenshot(self):
        # 1. Define path for the original screenshot (raw capture)
        # For initial capture, we can use a temporary path or save directly to "Originals" if nudity check is fast.
        # Let's create a temporary file name first.
        now = QDateTime.currentDateTime()
        temp_filename = f"temp_capture_{now.toString('yyyyMMdd_HHmmss_zzz')}.png"
        temp_filepath = os.path.join(self.base_project_dir, temp_filename) # Store temp in project root or a temp subfolder

        # 2. Capture screenshot to this temporary path
        if not self.capture_screenshot_os_native(temp_filepath):
            self.status_label.setText("Status: Screen capture failed.")
            # Consider deleting temp_filepath if it was partially created or empty
            if os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except OSError:
                    pass # Ignore if removal fails
            return

        # 3. Perform nudity detection on the captured image
        try:
            detected_boxes = self.nudity_filter.detect_nudity(temp_filepath)
        except Exception as e: # Catch errors from NudeDetector loading or detection
            print(f"Error during nudity detection process: {e}")
            self.status_label.setText("Status: Nudity detection error.")
            # Save the original screenshot to the main screenshot path as a fallback
            # so data isn't lost, or handle as an error case without saving.
            # For now, let's try to save it to the 'Screenshots' (unprocessed) path.
            fallback_path = self._get_timestamped_filepath(self.screenshots_base_dir) # Corrected call
            if fallback_path:
                try:
                    os.rename(temp_filepath, fallback_path)
                    display_path = os.path.join("...", os.path.basename(os.path.dirname(fallback_path)), os.path.basename(fallback_path))
                    self.status_label.setText(f"Status: Nudity err, saved to {display_path}")
                except OSError as rename_err:
                    print(f"Error moving temp file to fallback: {rename_err}")
                    if os.path.exists(temp_filepath): os.remove(temp_filepath) # cleanup temp
            else: # if fallback path generation failed
                if os.path.exists(temp_filepath): os.remove(temp_filepath) # cleanup temp
            return

        # 4. Process based on detection results
        final_saved_path = None
        status_message_suffix = ""

        if detected_boxes:
            # Nudity detected - blur the image
            print(f"Nudity detected in {temp_filepath}. Blurring...")
            blurred_image_matrix = self.nudity_filter.blur_regions(temp_filepath, detected_boxes)

            if blurred_image_matrix is not None:
                # Save original to "Originals" directory
                original_save_path = self._get_timestamped_filepath(self.originals_base_dir) # Corrected call
                if original_save_path:
                    try:
                        os.rename(temp_filepath, original_save_path) # Move the original
                        print(f"Original saved to {original_save_path}")
                    except OSError as e:
                        print(f"Error moving temp file to originals: {e}")
                        # If move fails, original is still in temp_filepath. Decide on cleanup.
                        # For now, we'll try to remove temp_filepath if blurred saving succeeds.

                # Save blurred image to "BlurredScreenshots" directory
                blurred_save_path = self._get_timestamped_filepath(self.blurred_base_dir) # Corrected call
                if blurred_save_path:
                    try:
                        cv2.imwrite(blurred_save_path, blurred_image_matrix)
                        final_saved_path = blurred_save_path
                        status_message_suffix = " (blurred)"
                        print(f"Blurred image saved to {blurred_save_path}")
                        if original_save_path and os.path.exists(temp_filepath): # If original move failed but blur saved
                            os.remove(temp_filepath) # remove the temp copy
                    except Exception as e:
                        print(f"Error saving blurred image: {e}")
                        self.status_label.setText("Status: Error saving blurred image.")
                        # Original might be in temp_filepath or moved to originals_save_path
                        # if original_save_path exists and temp_filepath doesn't, original is safe.
                        # if temp_filepath still exists, it's the original.
                        if not original_save_path and os.path.exists(temp_filepath): # if original wasn't moved yet
                             os.remove(temp_filepath) # remove temp to avoid confusion
                else: # blurred_save_path generation failed
                    self.status_label.setText("Status: Error creating path for blurred img.")
                    if os.path.exists(temp_filepath): os.remove(temp_filepath)

            else: # Blurring failed
                print(f"Blurring failed for {temp_filepath}.")
                self.status_label.setText("Status: Blurring failed.")
                # Save original to "Screenshots" as fallback
                fallback_path = self._get_timestamped_filepath(self.screenshots_base_dir) # Corrected call
                if fallback_path:
                    try:
                        os.rename(temp_filepath, fallback_path)
                        final_saved_path = fallback_path
                    except OSError as e:
                        print(f"Error moving temp file to fallback after blur fail: {e}")
                        if os.path.exists(temp_filepath): os.remove(temp_filepath)
                else:
                    if os.path.exists(temp_filepath): os.remove(temp_filepath)
        else:
            # No nudity detected - save original to "Screenshots" directory
            print(f"No nudity detected in {temp_filepath}. Saving as is.")
            regular_save_path = self._get_timestamped_filepath(self.screenshots_base_dir) # Corrected call
            if regular_save_path:
                try:
                    os.rename(temp_filepath, regular_save_path) # Move the original
                    final_saved_path = regular_save_path
                except OSError as e:
                    print(f"Error moving temp file to screenshots: {e}")
                    if os.path.exists(temp_filepath): os.remove(temp_filepath) # cleanup temp
            else: # regular_save_path generation failed
                if os.path.exists(temp_filepath): os.remove(temp_filepath) # cleanup temp

        # Update status label
        if final_saved_path:
            display_path = os.path.join("...", os.path.basename(os.path.dirname(final_saved_path)), os.path.basename(final_saved_path))
            self.status_label.setText(f"Status: Saved to {display_path}{status_message_suffix}")
        elif not self.is_capturing : # If something went wrong and we are not capturing anymore
            pass # Status already set by error condition or stop_capture
        elif self.is_capturing and not final_saved_path and self.status_label.text().startswith("Status: Capturing"):
            # If capture is ongoing but this specific save failed without specific error message
            self.status_label.setText("Status: Error saving last screenshot.")

        # Cleanup temp file if it somehow still exists and wasn't moved/deleted
        if os.path.exists(temp_filepath) and temp_filepath != final_saved_path : # final_saved_path could be temp_filepath if rename failed but we treat it as saved
            try:
                if not (detected_boxes and blurred_image_matrix is None and final_saved_path and final_saved_path == temp_filepath) : # Avoid deleting if it became the fallback
                    os.remove(temp_filepath)
            except OSError as e:
                print(f"Final cleanup error for temp file {temp_filepath}: {e}")


if __name__ == '__main__':
    # Ensure base directories exist at startup
    project_dirs = [
        os.path.abspath("BrandCentury/Screenshots"),
        os.path.abspath("BrandCentury/Originals"),
        os.path.abspath("BrandCentury/BlurredScreenshots")
    ]
    for p_dir in project_dirs:
        os.makedirs(p_dir, exist_ok=True)

    app = QApplication(sys.argv)
    main_window = BrandCenturyApp()
    main_window.show()
    sys.exit(app.exec())
