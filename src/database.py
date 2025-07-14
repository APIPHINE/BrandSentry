import sqlite3
import json
import os

DB_FILE = "brand_sentry.db"
CAPTURES_DIR = "captures"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    # Ensure the captures directory exists
    os.makedirs(CAPTURES_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initializes the database and creates/alters the scans table."""
    conn = get_db_connection()
    with conn:
        # Create table if it doesn't exist
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                screenshot_path TEXT NOT NULL,
                blurred_screenshot_path TEXT,
                status TEXT NOT NULL DEFAULT 'new',
                detected_brands TEXT
            )
        """)
        # Add the new thumbnail_path column if it doesn't exist
        try:
            conn.execute("ALTER TABLE scans ADD COLUMN thumbnail_path TEXT")
            print("Upgraded database: Added 'thumbnail_path' column.")
        except sqlite3.OperationalError as e:
            # This error occurs if the column already exists, which is fine.
            if "duplicate column name" not in str(e):
                raise
    print("Database initialized.")

def add_scan_result(screenshot_path, blurred_path, thumbnail_path, brands):
    """
    Adds a new scan result to the database.

    Args:
        screenshot_path (str): Path to the original screenshot.
        blurred_path (str): Path to the blurred screenshot, or None.
        thumbnail_path (str): Path to the thumbnail image.
        brands (list): A list of brand detection dictionaries.
    """
    conn = get_db_connection()
    with conn:
        conn.execute(
            """
            INSERT INTO scans (screenshot_path, blurred_screenshot_path, thumbnail_path, detected_brands, status)
            VALUES (?, ?, ?, ?, 'new')
            """,
            (screenshot_path, blurred_path, thumbnail_path, json.dumps(brands))
        )
    print(f"Added scan result for {screenshot_path} to the database.")

def get_scans_by_status(status="all"):
    """
    Retrieves scans from the database based on their status.

    Args:
        status (str): The status to filter by ('new', 'cleared', 'infringement').
                      If 'all', retrieves all scans.

    Returns:
        A list of rows, where each row is a dictionary-like object.
    """
    conn = get_db_connection()
    if status.lower() == 'all':
        cursor = conn.execute("SELECT * FROM scans ORDER BY timestamp DESC")
    else:
        cursor = conn.execute("SELECT * FROM scans WHERE status = ? ORDER BY timestamp DESC", (status,))

    scans = cursor.fetchall()
    conn.close()
    return scans

def update_scan_status(scan_id, new_status):
    """
    Updates the status of a specific scan.

    Args:
        scan_id (int): The ID of the scan to update.
        new_status (str): The new status ('cleared' or 'infringement').
    """
    conn = get_db_connection()
    with conn:
        conn.execute("UPDATE scans SET status = ? WHERE id = ?", (new_status, scan_id))
    print(f"Updated status for scan ID {scan_id} to '{new_status}'.")


if __name__ == '__main__':
    # --- Example Usage and Testing ---
    print("Running database module tests...")
    # Clean up old db file for a fresh test
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    initialize_database()

    # Test adding a scan
    add_scan_result("captures/test1.png", None, [{'label': 'nike'}])
    add_scan_result("captures/test2.png", "captures/test2_blurred.png", [{'label': 'adidas'}])

    # Test retrieving scans
    all_scans = get_scans_by_status('all')
    new_scans = get_scans_by_status('new')
    cleared_scans = get_scans_by_status('cleared')

    assert len(all_scans) == 2
    assert len(new_scans) == 2
    assert len(cleared_scans) == 0
    print("Assertion passed: Correct number of initial scans retrieved.")

    # Test updating a scan
    scan_id_to_update = new_scans[0]['id']
    update_scan_status(scan_id_to_update, 'cleared')

    # Test retrieving again
    all_scans = get_scans_by_status('all')
    new_scans = get_scans_by_status('new')
    cleared_scans = get_scans_by_status('cleared')

    assert len(all_scans) == 2
    assert len(new_scans) == 1
    assert len(cleared_scans) == 1
    assert cleared_scans[0]['id'] == scan_id_to_update
    print("Assertion passed: Status update and retrieval are correct.")

    print("Database module tests passed successfully.")
