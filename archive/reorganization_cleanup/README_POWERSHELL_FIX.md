# Permanent Fix for PowerShell Wrapper Issues

## The Problem

Cursor's PowerShell wrapper fails when project path contains apostrophes (like `Nat'l`), causing ALL terminal commands to fail with parsing errors.

## Permanent Solutions (Ranked by Effectiveness)

### ✅ Solution 1: Python Script Launcher (RECOMMENDED - No System Changes)

Use `utils/run_python_script.py` which bypasses PowerShell entirely by using `subprocess` with `shell=False`.

**Usage:**
```bash
python utils/run_python_script.py <script_name.py> [args...]
```

**Example:**
```bash
python utils/run_python_script.py organize_pnc_onedrive_files.py
```

**Why it works:**
- Uses `subprocess.run()` with `shell=False` - Direct process execution, no shell interpretation
- Bypasses PowerShell wrapper completely
- Works for ALL Python scripts

**Setup:** Already created in `utils/run_python_script.py` - ready to use!

---

### ✅ Solution 2: Change Cursor's Default Terminal (QUICK FIX)

Change Cursor's integrated terminal from PowerShell to Command Prompt.

**Steps:**
1. Open Cursor Settings (`Ctrl+,`)
2. Search for: `terminal default profile windows`
3. Set: **Terminal › Integrated › Default Profile: Windows** → **Command Prompt**
4. Close and reopen terminal
5. Test: `python --version`

**Why it works:**
- Command Prompt handles special characters better than PowerShell
- No quote escaping issues
- Immediate effect

---

### ✅ Solution 3: Create Symbolic Link (PERMANENT SYSTEM FIX)

Create a junction point from `C:\DREAM` to your OneDrive path. Cursor sees a simple path without apostrophes.

**Steps:**
1. Open **Command Prompt as Administrator** (Right-click → Run as Administrator)
2. Create junction:
   ```cmd
   mklink /J "C:\DREAM" "C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis"
   ```
3. In Cursor, close current folder and open `C:\DREAM`
4. Test: `python --version`

**Why it works:**
- Cursor sees path as `C:\DREAM` (no apostrophe)
- Files still sync to OneDrive automatically
- Permanent solution

**Note:** You're already using `C:\DREAM` as your workspace! The junction may already exist.

---

## Quick Reference

### For Scripts Going Forward

**Option A: Use the launcher (recommended)**
```bash
python utils/run_python_script.py script_name.py
```

**Option B: Use importlib pattern** (like in `goal_setting_analysis_main.py`)
```python
import importlib.util
def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
```

**Option C: Use subprocess directly in scripts**
```python
import subprocess
subprocess.run([sys.executable, 'script.py'], shell=False)
```

---

## Testing

Test your fix:
```bash
python utils/test_apostrophe_path.py
```

Or using the launcher:
```bash
python utils/run_python_script.py utils/test_apostrophe_path.py
```

---

## Best Practice Going Forward

1. **Always use `pathlib.Path`** for paths with special characters
2. **Use `subprocess` with `shell=False`** when executing scripts programmatically
3. **Document in scripts** that they use `utils/run_python_script.py` if needed
4. **Test new scripts** with the launcher first

---

## Files Created

- `utils/run_python_script.py` - Generic Python script launcher
- `utils/test_apostrophe_path.py` - Test script for path handling
- `docs/BYPASS_POWERSHELL_WRAPPER.md` - Detailed technical documentation
- This file (`README_POWERSHELL_FIX.md`) - Quick reference guide

