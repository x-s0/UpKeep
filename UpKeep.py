# UpKeep - Version 1.6
# Copyright (c) 2025 x-so
# Licensed under the MIT License (see LICENSE for details)

import tkinter as tk
from tkinter import ttk, filedialog
import subprocess
import threading
import os
import json

class UpKeepApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x580")
        
        # Ensure folders exist
        self.scripts_folder = "scripts"
        self.reports_folder = "reports"
        self.settings_folder = "settings"
        os.makedirs(self.scripts_folder, exist_ok=True)
        os.makedirs(self.reports_folder, exist_ok=True)
        os.makedirs(self.settings_folder, exist_ok=True)
        
        # Load settings (default to dark mode)
        self.settings_file = os.path.join(self.settings_folder, "settings.json")
        self.load_settings()
        if not hasattr(self, 'current_theme'):  # If no settings file exists, default to dark
            self.current_theme = 'dark'
            self.show_extra_buttons = False
            self.extra_button_configs = {f"Extra {i}": None for i in range(1, 11)}
            self.save_settings()
        
        # Apply initial theme
        self.root.configure(bg=self.themes[self.current_theme]["bg"])
        self.root.overrideredirect(True)

        # Style configuration
        self.style = ttk.Style()
        self.update_style()
        self.style.layout("TNotebook", [])
        self.style.configure("TNotebook", background=self.themes[self.current_theme]["bg"], borderwidth=0)
        self.style.configure("TNotebook.Tab", padding=[10, 2], font=("Arial", 10))

        # Custom title bar
        self.title_bar = tk.Frame(self.root, bg=self.themes[self.current_theme]["title_bg"], height=30)
        self.title_bar.pack(fill="x")
        
        self.title_label = tk.Label(self.title_bar, text="UpKeep", fg=self.themes[self.current_theme]["title_fg"], 
                                  bg=self.themes[self.current_theme]["title_bg"], font=("Arial", 12))
        self.title_label.pack(side="left", padx=10)
        
        self.settings_button = tk.Button(self.title_bar, text="⚙", command=self.open_settings,
                                       bg=self.themes[self.current_theme]["title_bg"], fg=self.themes[self.current_theme]["title_fg"],
                                       bd=0, font=("Arial", 12))
        self.settings_button.pack(side="right", padx=5)
        
        self.close_button = tk.Button(self.title_bar, text="✕", command=self.root.quit,
                                    bg=self.themes[self.current_theme]["title_bg"], fg=self.themes[self.current_theme]["title_fg"], 
                                    bd=0, font=("Arial", 12), activebackground="#ff4444")
        self.close_button.pack(side="right", padx=5)
        
        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.do_drag)
        self.title_label.bind("<Button-1>", self.start_drag)
        self.title_label.bind("<B1-Motion>", self.do_drag)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tools_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tools_frame, text="Tools")

        self.files_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.files_frame, text="UpEditor")
        
        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="Patch Notes")

        self.setup_tools_tab()
        self.setup_files_tab()
        self.setup_info_tab()

    def setup_tools_tab(self):
        self.button_frame_left = ttk.Frame(self.tools_frame, padding=10)
        self.button_frame_left.pack(side="left", fill="y")

        self.button_frame_right = ttk.Frame(self.tools_frame, padding=10)

        self.output_frame = ttk.Frame(self.tools_frame, padding=10)
        self.output_frame.pack(side="right", fill="both", expand=True)

        self.create_button(self.button_frame_left, "Flush DNS", "flushdns.bat")
        self.create_button(self.button_frame_left, "Renew IP", "iprenew.bat")
        self.create_button(self.button_frame_left, "Network Info", "netinfo.bat")
        self.create_button(self.button_frame_left, "Check Disk", "checkdisk.bat")
        self.create_button(self.button_frame_left, "SFC Scan", "sfcscan.bat")
        self.create_button(self.button_frame_left, "Reset Winsock", "winsockreset.bat")
        self.create_button(self.button_frame_left, "Clean Temp", "cleantemp.bat")
        self.create_button(self.button_frame_left, "Reboot", "reboot.bat")
        self.create_button(self.button_frame_left, "Diagnostic Report", "diagnostic.bat")
        self.create_button(self.button_frame_left, "View Report", None, self.view_latest_report)
        self.create_button(self.button_frame_left, "App Info", "appinfo.bat")

        self.output_text = tk.Text(self.output_frame, height=15, width=70,
                                 bg=self.themes[self.current_theme]["text_bg"], 
                                 fg=self.themes[self.current_theme]["text_fg"],
                                 font=("Consolas", 9))
        self.output_text.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.output_text)
        scrollbar.pack(side="right", fill="y")
        self.output_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.output_text.yview)

        self.clear_frame = ttk.Frame(self.output_frame)
        self.clear_frame.pack(side="bottom", fill="x", pady=(5, 0))

        self.clear_button = ttk.Button(self.clear_frame, text="Clear Output", 
                                     command=self.clear_output, width=15)
        self.clear_button.pack(side="right", padx=(0, 5))

        self.update_extra_buttons()

    def setup_files_tab(self):
        self.file_list_frame = ttk.Frame(self.files_frame, padding=10)
        self.file_list_frame.pack(side="left", fill="y")

        self.editor_frame = ttk.Frame(self.files_frame, padding=10)
        self.editor_frame.pack(side="right", fill="both", expand=True)

        self.file_listbox = tk.Listbox(self.file_list_frame, bg=self.themes[self.current_theme]["text_bg"],
                                     fg=self.themes[self.current_theme]["text_fg"], font=("Arial", 10),
                                     width=30, height=20)
        self.file_listbox.pack(fill="y", expand=True)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)

        self.update_file_list()

        self.editor_text = tk.Text(self.editor_frame, height=15, width=70,
                                 bg=self.themes[self.current_theme]["text_bg"],
                                 fg=self.themes[self.current_theme]["text_fg"],
                                 font=("Consolas", 9), undo=True)
        self.editor_text.pack(fill="both", expand=True)

        editor_scrollbar = ttk.Scrollbar(self.editor_text)
        editor_scrollbar.pack(side="right", fill="y")
        self.editor_text.config(yscrollcommand=editor_scrollbar.set)
        editor_scrollbar.config(command=self.editor_text.yview)

        self.editor_button_frame = ttk.Frame(self.editor_frame)
        self.editor_button_frame.pack(side="bottom", fill="x", pady=(5, 0))

        self.save_button = ttk.Button(self.editor_button_frame, text="Save", command=self.save_script)
        self.save_button.pack(side="left", padx=5)

        self.new_script_button = ttk.Button(self.editor_button_frame, text="New Script", command=self.new_script)
        self.new_script_button.pack(side="left", padx=5)

        self.open_script_button = ttk.Button(self.editor_button_frame, text="Open", command=self.open_script)
        self.open_script_button.pack(side="left", padx=5)

    def setup_info_tab(self):
        # Create a frame for the patch notes content
        self.info_content_frame = ttk.Frame(self.info_frame, padding=10)
        self.info_content_frame.pack(fill="both", expand=True)

        # Create a Text widget for patch notes
        self.patch_notes_text = tk.Text(
            self.info_content_frame,
            height=20,
            width=80,
            bg=self.themes[self.current_theme]["text_bg"],
            fg=self.themes[self.current_theme]["text_fg"],
            font=("Consolas", 10),
            wrap="word",
            borderwidth=0,
            relief="flat"
        )
        self.patch_notes_text.pack(fill="both", expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.patch_notes_text)
        scrollbar.pack(side="right", fill="y")
        self.patch_notes_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.patch_notes_text.yview)

        # Define the patch notes file path
        self.patch_notes_file = "patch_notes.txt"

        # Check if patch_notes.txt exists, create it with default content if not
        if not os.path.exists(self.patch_notes_file):
            default_content = (
                "It look's like the Patch Notes file either didn't download correctly or was downloaded at all.\n"
                "No need to worry!\n"
                "The file is in the github repo (/docs/patchnotes-vx.x.md)\n"
            )
            with open(self.patch_notes_file, 'w', encoding='utf-8') as f:
                f.write(default_content)

        # Read content from patch_notes.txt
        try:
            with open(self.patch_notes_file, 'r', encoding='utf-8') as f:
                patch_notes_content = f.read()
            self.patch_notes_text.insert("end", patch_notes_content)
        except Exception as e:
            self.patch_notes_text.insert("end", f"Error reading {self.patch_notes_file}: {str(e)}\n")

        # Make the text read-only
        self.patch_notes_text.config(state="disabled")

    # Theme definitions
    themes = {
        "light": {
            "bg": "#f0f0f0",
            "title_bg": "#2d2d2d",
            "title_fg": "white",
            "text_bg": "white",
            "text_fg": "black"
        },
        "dark": {
            "bg": "#1e1e1e",
            "title_bg": "#333333",
            "title_fg": "white",
            "text_bg": "#252526",
            "text_fg": "#d4d4d4"
        }
    }

    def load_settings(self):
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                self.current_theme = settings.get('theme', 'dark')
                self.show_extra_buttons = settings.get('extra_buttons', False)
                self.extra_button_configs = settings.get('extra_button_configs', {f"Extra {i}": None for i in range(1, 11)})
        except (FileNotFoundError, json.JSONDecodeError):
            self.current_theme = 'dark'
            self.show_extra_buttons = False
            self.extra_button_configs = {f"Extra {i}": None for i in range(1, 11)}
            self.save_settings()

    def save_settings(self):
        settings = {
            'theme': self.current_theme,
            'extra_buttons': self.show_extra_buttons,
            'extra_button_configs': self.extra_button_configs
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)

    def toggle_theme(self):
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme()
        self.save_settings()

    def apply_theme(self):
        self.root.configure(bg=self.themes[self.current_theme]["bg"])
        self.title_bar.configure(bg=self.themes[self.current_theme]["title_bg"])
        self.title_label.configure(bg=self.themes[self.current_theme]["title_bg"],
                                 fg=self.themes[self.current_theme]["title_fg"])
        self.close_button.configure(bg=self.themes[self.current_theme]["title_bg"],
                                  fg=self.themes[self.current_theme]["title_fg"])
        self.settings_button.configure(bg=self.themes[self.current_theme]["title_bg"],
                                     fg=self.themes[self.current_theme]["title_fg"])
        self.output_text.configure(bg=self.themes[self.current_theme]["text_bg"],
                                 fg=self.themes[self.current_theme]["text_fg"])
        self.file_listbox.configure(bg=self.themes[self.current_theme]["text_bg"],
                                  fg=self.themes[self.current_theme]["text_fg"])
        self.editor_text.configure(bg=self.themes[self.current_theme]["text_bg"],
                                 fg=self.themes[self.current_theme]["text_fg"])
        self.patch_notes_text.configure(bg=self.themes[self.current_theme]["text_bg"],
                                       fg=self.themes[self.current_theme]["text_fg"])  # Update patch notes theme
        self.style.configure("TNotebook", background=self.themes[self.current_theme]["bg"])
        self.style.configure("TNotebook.Tab", background=self.themes[self.current_theme]["title_bg"],
                           foreground=self.themes[self.current_theme]["title_fg"])
        self.update_style()
        if hasattr(self, 'settings_window') and self.settings_window.winfo_exists():
            self.settings_window.configure(bg=self.themes[self.current_theme]["bg"])
            self.settings_frame.configure(bg=self.themes[self.current_theme]["bg"])
            self.theme_button.configure(bg=self.themes[self.current_theme]["title_bg"],
                                      fg=self.themes[self.current_theme]["title_fg"])

    def update_style(self):
        if self.current_theme == "light":
            self.style.theme_use('default')
        else:
            self.style.theme_use('clam')
        self.style.configure("TButton", padding=6, font=("Arial", 10))

    def open_settings(self):
        if hasattr(self, 'settings_window') and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return

        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.geometry("400x600")
        self.settings_window.overrideredirect(True)
        self.settings_window.configure(bg=self.themes[self.current_theme]["bg"])

        settings_title_bar = tk.Frame(self.settings_window, bg=self.themes[self.current_theme]["title_bg"], height=30)
        settings_title_bar.pack(fill="x")
        
        tk.Label(settings_title_bar, text="Settings", fg=self.themes[self.current_theme]["title_fg"],
                bg=self.themes[self.current_theme]["title_bg"], font=("Arial", 12)).pack(side="left", padx=10)
        
        tk.Button(settings_title_bar, text="✕", command=self.settings_window.destroy,
                 bg=self.themes[self.current_theme]["title_bg"], fg=self.themes[self.current_theme]["title_fg"],
                 bd=0, font=("Arial", 12), activebackground="#ff4444").pack(side="right", padx=5)

        settings_title_bar.bind("<Button-1>", lambda e: self.start_drag(e, self.settings_window))
        settings_title_bar.bind("<B1-Motion>", lambda e: self.do_drag(e, self.settings_window))

        self.settings_frame = tk.Frame(self.settings_window, bg=self.themes[self.current_theme]["bg"])
        self.settings_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.theme_button = tk.Button(self.settings_frame, text="Toggle Theme", command=self.toggle_theme,
                                    bg=self.themes[self.current_theme]["title_bg"], fg=self.themes[self.current_theme]["title_fg"],
                                    font=("Arial", 10))
        self.theme_button.pack(pady=5)

        self.extra_buttons_var = tk.BooleanVar(value=self.show_extra_buttons)
        tk.Checkbutton(self.settings_frame, text="Dev Mode", variable=self.extra_buttons_var,
                      command=self.toggle_extra_buttons, bg=self.themes[self.current_theme]["bg"],
                      fg=self.themes[self.current_theme]["text_fg"], font=("Arial", 10),
                      selectcolor=self.themes[self.current_theme]["text_bg"]).pack(pady=5)

        tk.Label(self.settings_frame, text="Extra Button Configuration", bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["text_fg"], font=("Arial", 10, "bold")).pack(pady=(10, 5))

        self.button_entries = {}
        self.button_script_vars = {}
        script_options = ["None"] + [f for f in os.listdir(self.scripts_folder) if f.lower().endswith('.bat')]

        for i in range(1, 11):
            frame = tk.Frame(self.settings_frame, bg=self.themes[self.current_theme]["bg"])
            frame.pack(fill="x", pady=2)

            default_name = list(self.extra_button_configs.keys())[i-1]
            tk.Label(frame, text=f"Button {i} Name:", bg=self.themes[self.current_theme]["bg"],
                    fg=self.themes[self.current_theme]["text_fg"], font=("Arial", 10)).pack(side="left")
            entry = tk.Entry(frame, bg=self.themes[self.current_theme]["text_bg"],
                           fg=self.themes[self.current_theme]["text_fg"], font=("Arial", 10))
            entry.insert(0, default_name)
            entry.pack(side="left", padx=5)
            self.button_entries[f"Extra {i}"] = entry

            tk.Label(frame, text="Script:", bg=self.themes[self.current_theme]["bg"],
                    fg=self.themes[self.current_theme]["text_fg"], font=("Arial", 10)).pack(side="left")
            var = tk.StringVar(value=self.extra_button_configs.get(default_name, "None"))
            option_menu = ttk.OptionMenu(frame, var, var.get(), *script_options,
                                       command=lambda val, idx=i: self.update_button_script(idx, val))
            option_menu.pack(side="left", padx=5)
            self.button_script_vars[f"Extra {i}"] = var

        tk.Button(self.settings_frame, text="Apply Changes", command=self.apply_button_changes,
                 bg=self.themes[self.current_theme]["title_bg"], fg=self.themes[self.current_theme]["title_fg"],
                 font=("Arial", 10)).pack(pady=10)

    def toggle_extra_buttons(self):
        self.show_extra_buttons = self.extra_buttons_var.get()
        self.update_extra_buttons()
        self.save_settings()

    def update_extra_buttons(self):
        for widget in self.button_frame_right.winfo_children():
            widget.destroy()
        if self.button_frame_right.winfo_ismapped():
            self.button_frame_right.pack_forget()
        if self.show_extra_buttons:
            self.button_frame_right.pack(side="left", fill="y")
            for name, script in self.extra_button_configs.items():
                if script and script != "None":
                    self.create_button(self.button_frame_right, name, script)
                else:
                    self.create_button(self.button_frame_right, name, None,
                                     lambda n=name: self.output_text.insert("end", f"{n} clicked (no script assigned)\n"))

    def update_button_script(self, index, script):
        old_name = f"Extra {index}"
        new_name = self.button_entries[old_name].get()
        self.extra_button_configs[new_name] = script
        if old_name != new_name and old_name in self.extra_button_configs:
            del self.extra_button_configs[old_name]

    def apply_button_changes(self):
        for old_name, entry in self.button_entries.items():
            new_name = entry.get()
            script = self.button_script_vars[old_name].get()
            if new_name and new_name != old_name:
                self.extra_button_configs[new_name] = script
                if old_name in self.extra_button_configs:
                    del self.extra_button_configs[old_name]
            else:
                self.extra_button_configs[old_name] = script
        self.update_extra_buttons()
        self.save_settings()

    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        scripts_dir = os.path.join(os.getcwd(), self.scripts_folder)
        if os.path.exists(scripts_dir):
            for file in os.listdir(scripts_dir):
                if os.path.isfile(os.path.join(scripts_dir, file)) and file.lower().endswith('.bat'):
                    self.file_listbox.insert(tk.END, file)

    def on_file_select(self, event):
        selection = self.file_listbox.curselection()
        if not selection:
            return
        file_name = self.file_listbox.get(selection[0])
        full_path = os.path.join(os.getcwd(), self.scripts_folder, file_name)
        self.editor_text.delete("1.0", tk.END)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                self.editor_text.insert("end", f.read())
            self.current_script = file_name
        except Exception as e:
            self.editor_text.insert("end", f"Error reading {file_name}: {str(e)}\n")
            self.current_script = None

    def save_script(self):
        if not hasattr(self, 'current_script') or not self.current_script:
            self.new_script()
            return
        full_path = os.path.join(self.scripts_folder, self.current_script)
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(self.editor_text.get("1.0", tk.END))
            self.output_text.insert("end", f"Saved {self.current_script}\n")
            self.update_file_list()
        except Exception as e:
            self.output_text.insert("end", f"Error saving {self.current_script}: {str(e)}\n")

    def new_script(self):
        new_window = tk.Toplevel(self.root)
        new_window.geometry("300x150")
        new_window.overrideredirect(True)
        new_window.configure(bg=self.themes[self.current_theme]["bg"])

        title_bar = tk.Frame(new_window, bg=self.themes[self.current_theme]["title_bg"], height=30)
        title_bar.pack(fill="x")
        tk.Label(title_bar, text="New Script", fg=self.themes[self.current_theme]["title_fg"],
                bg=self.themes[self.current_theme]["title_bg"], font=("Arial", 12)).pack(side="left", padx=10)
        tk.Button(title_bar, text="✕", command=new_window.destroy,
                 bg=self.themes[self.current_theme]["title_bg"], fg=self.themes[self.current_theme]["title_fg"],
                 bd=0, font=("Arial", 12), activebackground="#ff4444").pack(side="right", padx=5)
        title_bar.bind("<Button-1>", lambda e: self.start_drag(e, new_window))
        title_bar.bind("<B1-Motion>", lambda e: self.do_drag(e, new_window))

        frame = tk.Frame(new_window, bg=self.themes[self.current_theme]["bg"])
        frame.pack(pady=10, padx=10, fill="both", expand=True)

        tk.Label(frame, text="Script Name:", bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["text_fg"], font=("Arial", 10)).pack(pady=5)
        name_entry = tk.Entry(frame, bg=self.themes[self.current_theme]["text_bg"],
                            fg=self.themes[self.current_theme]["text_fg"], font=("Arial", 10))
        name_entry.pack(pady=5)
        name_entry.insert(0, "new_script.bat")

        def create():
            name = name_entry.get()
            if not name.lower().endswith('.bat'):
                name += '.bat'
            full_path = os.path.join(self.scripts_folder, name)
            if os.path.exists(full_path):
                self.output_text.insert("end", f"Error: {name} already exists!\n")
            else:
                try:
                    template = (
                        "@echo off\n"
                        "REM Simple Batch Script Template\n"
                        "echo Starting script...\n"
                        "REM Add your commands below\n"
                        "echo Example command executed\n"
                        "pause\n"
                        "echo Script finished\n"
                    )
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(template)
                    self.update_file_list()
                    self.file_listbox.select_set(self.file_listbox.size() - 1)
                    self.on_file_select(None)
                    self.output_text.insert("end", f"Created {name} with template\n")
                except Exception as e:
                    self.output_text.insert("end", f"Error creating {name}: {str(e)}\n")
            new_window.destroy()

        tk.Button(frame, text="Create", command=create,
                 bg=self.themes[self.current_theme]["title_bg"], fg=self.themes[self.current_theme]["title_fg"],
                 font=("Arial", 10)).pack(pady=5)

    def open_script(self):
        file_path = filedialog.askopenfilename(
            initialdir=self.scripts_folder,
            title="Open Batch Script",
            filetypes=(("Batch files", "*.bat"), ("All files", "*.*"))
        )
        if file_path:
            file_name = os.path.basename(file_path)
            self.editor_text.delete("1.0", tk.END)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.editor_text.insert("end", f.read())
                self.current_script = file_name
                self.update_file_list()
                for i in range(self.file_listbox.size()):
                    if self.file_listbox.get(i) == file_name:
                        self.file_listbox.select_clear(0, tk.END)
                        self.file_listbox.select_set(i)
                        break
                self.output_text.insert("end", f"Opened {file_name}\n")
            except Exception as e:
                self.editor_text.insert("end", f"Error opening {file_name}: {str(e)}\n")
                self.current_script = None

    def start_drag(self, event, window=None):
        window = window or self.root
        self.x = event.x
        self.y = event.y

    def do_drag(self, event, window=None):
        window = window or self.root
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = window.winfo_x() + deltax
        y = window.winfo_y() + deltay
        window.geometry(f"+{x}+{y}")

    def create_button(self, frame, text, script_path, command=None):
        if command is None and script_path:
            full_path = os.path.join(self.scripts_folder, script_path)
            command = lambda: self.run_script(full_path)
        btn = ttk.Button(frame, text=text, command=command, width=15)
        btn.pack(pady=5)

    def run_script(self, script_path):
        if not os.path.exists(script_path):
            self.output_text.insert("end", f"Error: {script_path} not found!\n")
            return
        self.output_text.insert("end", f"Running {os.path.basename(script_path)}...\n")
        thread = threading.Thread(target=self.execute_script, args=(script_path,))
        thread.start()

    def execute_script(self, script_path):
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
        self.output_text.delete("1.0", "end")

def main():
    root = tk.Tk()
    app = UpKeepApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
