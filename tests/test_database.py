import unittest
import sqlite3
import os
import json
import time

# Add the project root to the path to allow imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import (
    initialize_database,
    add_scan_result,
    get_scans_by_status,
    update_scan_status,
    DB_FILE
)

class TestDatabase(unittest.TestCase):

    def setUp(self):
        """Set up a fresh database for each test."""
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        initialize_database()

    def tearDown(self):
        """Clean up the database file after each test."""
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)

    def test_add_and_get_scans(self):
        """Tests adding scans and retrieving them by status."""
        # --- Arrange ---
        brands1 = [{'label': 'nike'}]
        brands2 = [{'label': 'adidas'}]

        # --- Act ---
        add_scan_result("captures/test1.png", None, "captures/thumbnails/test1.png", brands1)
        time.sleep(0.01) # Ensure timestamps are distinct
        add_scan_result("captures/test2.png", "captures/test2_blurred.png", "captures/thumbnails/test2.png", brands2)

        # --- Assert ---
        all_scans = get_scans_by_status('all')
        new_scans = get_scans_by_status('new')
        cleared_scans = get_scans_by_status('cleared')

        self.assertEqual(len(all_scans), 2)
        self.assertEqual(len(new_scans), 2)
        self.assertEqual(len(cleared_scans), 0)

        # Sort results to make the test deterministic
        new_scans_sorted = sorted(new_scans, key=lambda r: r['screenshot_path'])

        # Check data integrity
        self.assertEqual(new_scans_sorted[0]['screenshot_path'], "captures/test1.png")
        self.assertEqual(new_scans_sorted[0]['thumbnail_path'], "captures/thumbnails/test1.png")
        self.assertEqual(json.loads(new_scans_sorted[0]['detected_brands']), brands1)
        self.assertEqual(new_scans_sorted[1]['screenshot_path'], "captures/test2.png")
        self.assertEqual(json.loads(new_scans_sorted[1]['detected_brands']), brands2)

    def test_update_scan_status(self):
        """Tests updating the status of a scan."""
        # --- Arrange ---
        add_scan_result("captures/test3.png", None, "captures/thumbnails/test3.png", [{'label': 'puma'}])
        new_scan = get_scans_by_status('new')[0]
        scan_id_to_update = new_scan['id']

        # --- Act ---
        update_scan_status(scan_id_to_update, 'cleared')

        # --- Assert ---
        cleared_scans = get_scans_by_status('cleared')
        new_scans_after_update = get_scans_by_status('new')

        self.assertEqual(len(cleared_scans), 1)
        self.assertEqual(len(new_scans_after_update), 0)
        self.assertEqual(cleared_scans[0]['id'], scan_id_to_update)

        # Test updating to 'infringement'
        update_scan_status(scan_id_to_update, 'infringement')
        infringement_scans = get_scans_by_status('infringement')
        self.assertEqual(len(infringement_scans), 1)
        self.assertEqual(infringement_scans[0]['status'], 'infringement')

if __name__ == '__main__':
    unittest.main()
