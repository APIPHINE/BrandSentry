import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

from .database import get_scans_by_status, update_scan_status

class ResultsViewer(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Scan Results")
        self.geometry("800x600")

        # --- Frames ---
        self.filter_frame = ttk.Frame(self, padding="5")
        self.filter_frame.pack(fill=tk.X)

        # Using a Canvas and a Frame for a scrollable area
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # --- Filter Buttons ---
        self.current_filter = tk.StringVar(value="new")

        ttk.Radiobutton(self.filter_frame, text="New", variable=self.current_filter, value="new", command=self.refresh_scans).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(self.filter_frame, text="Cleared", variable=self.current_filter, value="cleared", command=self.refresh_scans).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(self.filter_frame, text="Infringement", variable=self.current_filter, value="infringement", command=self.refresh_scans).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(self.filter_frame, text="All", variable=self.current_filter, value="all", command=self.refresh_scans).pack(side=tk.LEFT, padx=5)

        self.refresh_scans()

    def refresh_scans(self):
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        status = self.current_filter.get()
        scans = get_scans_by_status(status)

        if not scans:
            ttk.Label(self.scrollable_frame, text=f"No scans with status '{status}' found.").pack(pady=10)
            return

        for scan in scans:
            self.create_scan_widget(scan)

    def create_scan_widget(self, scan_data):
        item_frame = ttk.Labelframe(self.scrollable_frame, text=f"ID: {scan_data['id']} - Status: {scan_data['status']}", padding="10")
        item_frame.pack(padx=10, pady=5, fill=tk.X)

        # --- Thumbnail Display ---
        thumbnail_path = scan_data.get('thumbnail_path')
        if thumbnail_path and os.path.exists(thumbnail_path):
            try:
                img = Image.open(thumbnail_path)
                photo = ImageTk.PhotoImage(img)
                img_label = ttk.Label(item_frame, image=photo)
                img_label.image = photo # Keep a reference!
                img_label.pack(side=tk.LEFT, padx=5)
            except Exception as e:
                print(f"Could not load thumbnail {thumbnail_path}: {e}")
                # Display a placeholder if the image fails to load
                ttk.Label(item_frame, text="[Image Error]").pack(side=tk.LEFT, padx=5)
        else:
            # Display a placeholder if no thumbnail is available
            ttk.Label(item_frame, text="[No Thumbnail]").pack(side=tk.LEFT, padx=5)

        # --- Info and Action Buttons ---
        info_frame = ttk.Frame(item_frame)
        info_frame.pack(side=tk.LEFT, padx=10)

        ttk.Label(info_frame, text=f"Timestamp: {scan_data['timestamp']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Brands: {scan_data['detected_brands']}").pack(anchor=tk.W)

        button_frame = ttk.Frame(item_frame)
        button_frame.pack(side=tk.RIGHT, padx=10)

        # Don't show "Clear" button if already cleared
        if scan_data['status'] != 'cleared':
            clear_btn = ttk.Button(button_frame, text="Clear", command=lambda: self.update_status(scan_data['id'], 'cleared'))
            clear_btn.pack(pady=2)

        # Don't show "Mark" button if already an infringement
        if scan_data['status'] != 'infringement':
            infringe_btn = ttk.Button(button_frame, text="Mark as Infringement", command=lambda: self.update_status(scan_data['id'], 'infringement'))
            infringe_btn.pack(pady=2)

    def update_status(self, scan_id, new_status):
        update_scan_status(scan_id, new_status)
        self.refresh_scans()
