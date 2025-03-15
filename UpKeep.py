# UpKeep - Version 1.1
# Copyright (c) 2025 x-so
# Licensed under the MIT License (see LICENSE for details)

import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import os

class UpKeepApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1000x555")
        self.root.configure(bg="#f0f0f0")
        
        # Remove title bar
        self.root.overrideredirect(True)

        # Ensure folders exist
        self.scripts_folder = "scripts"
        self.reports_folder = "reports"
        os.makedirs(self.scripts_folder, exist_ok=True)
        os.makedirs(self.reports_folder, exist_ok=True)

        # Style configuration
        style = ttk.Style()
        style.configure("TButton", padding=6, font=("Arial", 10))

        # Custom title bar
        self.title_bar = tk.Frame(self.root, bg="#2d2d2d", height=30)
        self.title_bar.pack(fill="x")
        
        # Title text
        self.title_label = tk.Label(self.title_bar, text="UpKeep", fg="white", 
                                  bg="#2d2d2d", font=("Arial", 12))
        self.title_label.pack(side="left", padx=10)
        
        # Close button
        self.close_button = tk.Button(self.title_bar, text="✕", command=self.root.quit,
                                    bg="#2d2d2d", fg="white", bd=0, font=("Arial", 12),
                                    activebackground="#ff4444")
        self.close_button.pack(side="right", padx=5)
        
        # Make window draggable
        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.do_drag)
        self.title_label.bind("<Button-1>", self.start_drag)
        self.title_label.bind("<B1-Motion>", self.do_drag)

        # Main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill="both", expand=True)

        # Button frame (vertical on the left)
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(side="left", fill="y", padx=(0, 10))

        # Output frame (to the right of buttons)
        self.output_frame = ttk.Frame(self.main_frame)
        self.output_frame.pack(side="right", fill="both", expand=True)

        # Buttons
        self.create_button("Flush DNS", "flushdns.bat")
        self.create_button("Renew IP", "iprenew.bat")
        self.create_button("Network Info", "netinfo.bat")
        self.create_button("Check Disk", "checkdisk.bat")
        self.create_button("SFC Scan", "sfcscan.bat")
        self.create_button("Reset Winsock", "winsockreset.bat")
        self.create_button("Clean Temp", "cleantemp.bat")
        self.create_button("Reboot", "reboot.bat")
        self.create_button("Diagnostic Report", "diagnostic.bat")
        self.create_button("View Report", None, self.view_latest_report)
        self.create_button("App Info", "appinfo.bat")

        # Output area
        self.output_text = tk.Text(self.output_frame, height=15, width=70, 
                                 bg="white", font=("Consolas", 9))
        self.output_text.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.output_text)
        scrollbar.pack(side="right", fill="y")
        self.output_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.output_text.yview)

        # Clear button frame
        self.clear_frame = ttk.Frame(self.output_frame)
        self.clear_frame.pack(side="bottom", fill="x", pady=(5, 0))

        # Clear Output button
        self.clear_button = ttk.Button(self.clear_frame, text="Clear Output", 
                                     command=self.clear_output, width=15)
        self.clear_button.pack(side="right", padx=(0, 5))

    def start_drag(self, event):
        """Store initial click position for dragging"""
        self.x = event.x
        self.y = event.y

    def do_drag(self, event):
        """Move window based on drag motion"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def create_button(self, text, script_path, command=None):
        """Create and pack a button with given text and command"""
        if command is None and script_path:
            full_path = os.path.join(self.scripts_folder, script_path)
            command = lambda: self.run_script(full_path)
        btn = ttk.Button(self.button_frame, text=text, command=command, width=15)
        btn.pack(pady=5)

    def run_script(self, script_path):
        """Run the batch script in a separate thread"""
        if not os.path.exists(script_path):
            self.output_text.insert("end", f"Error: {script_path} not found!\n")
            return
        
        self.output_text.insert("end", f"Running {os.path.basename(script_path)}...\n")
        thread = threading.Thread(target=self.execute_script, args=(script_path,))
        thread.start()

    def execute_script(self, script_path):
        """Execute the script and capture output"""
        try:
            process = subprocess.Popen(
                ['cmd.exe', '/c', script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    self.output_text.insert("end", line)
                    self.output_text.see("end")
            
            errors = process.stderr.read()
            if errors:
                self.output_text.insert("end", "Errors:\n" + errors)
            
            process.wait()
            process.stdout.close()
            process.stderr.close()
            
            self.output_text.insert("end", f"Finished running {os.path.basename(script_path)}\n\n")
            self.output_text.see("end")
            
        except Exception as e:
            self.output_text.insert("end", f"Error: {str(e)}\n")

    def view_latest_report(self):
        """Open the latest diagnostic report in Notepad"""
        report_files = [f for f in os.listdir(self.reports_folder) if f.startswith("Diagnostic_Report_") and f.endswith(".txt")]
        if not report_files:
            self.output_text.insert("end", "No diagnostic reports found.\n")
            self.output_text.see("end")
            return
        
        latest_report = max(report_files, key=lambda f: os.path.getctime(os.path.join(self.reports_folder, f)))
        report_path = os.path.join(self.reports_folder, latest_report)
        try:
            subprocess.Popen(['notepad.exe', report_path], creationflags=subprocess.CREATE_NO_WINDOW)
            self.output_text.insert("end", f"Opening {latest_report} in Notepad...\n")
            self.output_text.see("end")
        except Exception as e:
            self.output_text.insert("end", f"Error opening report: {str(e)}\n")
            self.output_text.see("end")

    def clear_output(self):
        """Clear all text in the output area"""
        self.output_text.delete("1.0", "end")

def main():
    root = tk.Tk()
    app = UpKeepApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
