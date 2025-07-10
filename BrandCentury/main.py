import sys
import os
import datetime
import subprocess # Added for screenshot capture
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import QTimer, QDateTime

class BrandCenturyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Brand Century Screenshotter")
        self.setGeometry(100, 100, 400, 200)  # x, y, width, height

        self.screenshot_timer = QTimer(self)
        self.screenshot_timer.timeout.connect(self.capture_and_save_screenshot) # Connect the timer

        self.is_capturing = False
        self.screenshot_interval = 5000  # Default to 5 seconds (in milliseconds)
        self.screenshots_base_dir = os.path.abspath("BrandCentury/Screenshots") # Use absolute path

        # Ensure base screenshots directory exists (already done at startup of script)
        # os.makedirs(self.screenshots_base_dir, exist_ok=True) # This is fine here, or can be in main part

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

    def get_screenshot_filepath(self):
        """
        Generates a filepath for the new screenshot.
        Ensures the daily subdirectory exists.
        e.g., BrandCentury/Screenshots/YYYY-MM-DD/YYYYMMDD_HHMMSS.png
        """
        now = QDateTime.currentDateTime()
        current_date_str = now.toString("yyyy-MM-dd")
        timestamp_filename = now.toString("yyyyMMdd_HHmmss") + ".png"

        daily_screenshot_dir = os.path.join(self.screenshots_base_dir, current_date_str)

        # Create the daily directory if it doesn't exist
        try:
            os.makedirs(daily_screenshot_dir, exist_ok=True)
        except OSError as e:
            print(f"Error creating directory {daily_screenshot_dir}: {e}")
            self.status_label.setText(f"Status: Error creating dir {current_date_str}")
            # Potentially stop capture if we can't create directories
            if self.is_capturing:
                self.stop_capture()
            return None

        return os.path.join(daily_screenshot_dir, timestamp_filename)

    def capture_and_save_screenshot(self): # This will be implemented in 1.4 and 1.5 fully
        filepath = self.get_screenshot_filepath()
        if not filepath:
            # Error already handled and message shown by get_screenshot_filepath
            return

        if self.capture_screenshot_os_native(filepath):
            # Display only part of the path for brevity in status
            display_path = os.path.join("...", os.path.basename(os.path.dirname(filepath)), os.path.basename(filepath))
            self.status_label.setText(f"Status: Saved to {display_path}")
        # If capture_screenshot_os_native fails, it sets its own error status.


if __name__ == '__main__':
    # Ensure base screenshots directory exists at startup
    # This was moved from __init__ to ensure it's created before app runs if main.py is moved
    # and also to align with where BrandCentury/Screenshots is first mentioned in plan.
    # However, the initial `mkdir -p BrandCentury/Screenshots` in bash setup already handles this.
    # For robustness, we can ensure it here too.
    base_screenshots_dir = os.path.abspath("BrandCentury/Screenshots")
    os.makedirs(base_screenshots_dir, exist_ok=True)

    app = QApplication(sys.argv)
    main_window = BrandCenturyApp()
    main_window.show()
    sys.exit(app.exec())
