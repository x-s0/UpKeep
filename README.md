UpKeep - Version 1.0
=====================================

Overview
--------
UpKeep is an open-source Tkinter-based application designed to help troubleshoot and maintain Windows PCs. It provides a user-friendly interface, diagnostic and repair batch scripts, displaying their output directly in the app. Reports are saved for later review, and the app is customizable for additional functionality.

Features
--------
- Real-time command output display.
- Diagnostic report generation saved to a 'reports' folder.
- Option to view the latest report in Notepad.

Requirements
------------
- Windows operating system (due to .bat file usage).
- Python 3.x installed (with tkinter module, included by default).
- Administrator privileges for some scripts (e.g., SFC Scan, Check Disk).

Installation
------------
1. Download the source files from the repository.
2. Ensure Python 3.x is installed (run `python --version` in Command Prompt to check).
3. All files needs to be in a single directory:
   - `upkeep.py` (main Python script)
   - `scripts` folder (contains all .bat files)
   - `reports` folder (auto-created for diagnostic reports)
4. Install dependencies (none beyond standard Python libraries).

Usage
-----
1. Run the app:
   - Open Command Prompt, navigate to the directory, and type: `python upkeep.py`
   - Or double-click `upkeep.py` if Python is associated with .py files.
   - For scripts requiring admin rights, right-click `upkeep.py` and select "Run as administrator".
2. Use the buttons:
   - Click any button (e.g., "Flush DNS", "Diagnostic Report") to execute its script.
   - Output appears in the text area on the right.
   - "Diagnostic Report" saves a detailed report to the 'reports' folder.
   - "View Report" opens the latest diagnostic report in Notepad.
3. Check results:
   - Scroll through the output to verify script execution.
   - Review saved reports in the 'reports' folder for detailed diagnostics.

Editing and Customization
-------------------------
UpKeep is open-source under the MIT License (see LICENSE). Here’s how to modify it:

### Changing Scripts
- **Location**: All .bat files are in the `scripts` folder.
- **Adding a New Script**:
  1. Create a new .bat file in `scripts` (e.g., `newscript.bat`).
  2. Edit `upkeep.py`, find the `__init__` method, and add a new button:
     ```python
     self.create_button("New Script", "newscript.bat")
     ```
  3. Replace an existing button by updating its name and script path.
- **Editing Existing Scripts**:
  - Open the .bat file in a text editor (e.g., Notepad).
  - Modify scripts as needed. (You could even Contact me about your new scripts and i might implement it in future updates, with credits ofcourse)
  - Save changes; no Python code edits required unless renaming the file.

### Modifying the Interface
- **Buttons**:
  - In `upkeep.py`, edit the `self.create_button` calls in `__init__` to change button text or linked scripts.
  - To add more than 10 buttons, append more `self.create_button` lines (may require resizing the window with `self.root.geometry`).
- **Window Size**: Change `self.root.geometry("700x400")` to adjust width and height (e.g., "800x500").

### Advanced Customization
- **New Features**: Add methods to the `UpKeepApp` class and link them to buttons via `self.create_button("Text", None, self.new_method)`.
- **Folders**: Change `self.scripts_folder` or `self.reports_folder` to different names or paths (update `diagnostic.bat` accordingly).
- **Output**: Enhance `execute_script` to format or filter output (e.g., add timestamps).

### Example: Adding a New Script
1. Create `scripts/reboot.bat`:
   ```batch
   @echo off
   echo Preparing to reboot...
   shutdown /r /t 5
   echo Reboot initiated.
