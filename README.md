# BrandSentry: Brand Century Scanner

BrandSentry is a desktop application designed to periodically scan the screen for brand logos and trademarks. It includes a feature to detect and blur nudity before performing brand detection to ensure user privacy and safety.

**Note:** This project is currently in a development stage. The brand and nudity detection models are placeholders and do not perform real detection.

## Features

*   **Screen Scanning:** Automatically takes screenshots of the primary monitor at a configurable interval.
*   **Nudity Detection & Blurring:** Scans for nudity in screenshots and blurs any detected regions. (Placeholder)
*   **Brand Detection:** Scans the (potentially blurred) image for a list of known brand logos. (Placeholder)
*   **Simple UI:** A basic Tkinter interface to start and stop the scanning process.

## How to Run

### 1. Prerequisites

*   Python 3.8+
*   An environment that supports a GUI (e.g., a standard desktop OS, not a headless server).

### 2. Installation

Clone the repository and install the required Python packages:

```bash
git clone <repository-url>
cd <repository-directory>
pip install -r requirements.txt
```

### 3. Running the Application

To start the application, run the `main.py` script:

```bash
python main.py
```

This will open a small window with a "Start Scan" button. Click it to begin the screen scanning process. Status messages and any detected brand labels (from the placeholder model) will be printed to the console.

## Project Structure

```
.
├── main.py               # Main application entry point (GUI and core logic)
├── requirements.txt      # Python dependencies
├── src/                  # Source code for detection models
│   ├── data/
│   │   └── preprocess.py # Placeholder for data preprocessing
│   ├── nudity/
│   │   └── detect.py     # Placeholder for nudity detection & blurring
│   └── train.py          # Placeholder for brand detection model training
└── tests/                # Unit tests
    └── test_main.py      # Tests for the core scanning logic
```

## Packaging for Distribution (Future Work)

To package this application into a standalone executable for distribution (e.g., on Windows or macOS), a tool like **PyInstaller** could be used.

A basic command to do this would be:

```bash
# Note: This is an example and may require further configuration
pyinstaller --onefile --windowed --name BrandScanner main.py
```

This would create a single executable file in the `dist` directory. However, packaging machine learning models (especially TensorFlow) with PyInstaller can be complex and may require a custom build configuration (a `.spec` file) to ensure all necessary libraries and data files are included.
