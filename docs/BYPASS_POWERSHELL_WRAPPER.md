# Bypassing PowerShell Wrapper Issues

## Problem
When running Python scripts through Cursor's terminal, PowerShell wrapper errors occur, especially with paths containing apostrophes (e.g., `OneDrive - Nat'l Community...`).

## Permanent Solution

### Method 1: Use the Python Launcher Utility (Recommended)

We've created `utils/run_python_script.py` that uses `subprocess` with `shell=False` to bypass PowerShell entirely.

**Usage:**
```bash
python utils/run_python_script.py <script_name.py> [args...]
```

**Example:**
```bash
python utils/run_python_script.py organize_pnc_onedrive_files.py
```

This launcher:
- Uses `subprocess.run()` with `shell=False` to bypass PowerShell wrapper
- Properly handles paths with apostrophes using `pathlib.Path`
- Shows output in real-time
- Returns proper exit codes

### Method 2: Run Scripts Directly from Command Prompt

Open **Command Prompt** (not PowerShell) and run:
```cmd
cd c:\DREAM
python script_name.py
```

### Method 3: Double-Click Python Scripts (Windows)

If Python is properly associated with `.py` files:
1. Navigate to `c:\DREAM` in File Explorer
2. Double-click the `.py` file to execute it

## Best Practices

1. **Always use `pathlib.Path` for paths** - Never put paths with apostrophes in strings that go through shell
2. **Use `shell=False` in subprocess calls** - This bypasses PowerShell wrapper
3. **Test with `utils/test_apostrophe_path.py`** - Verify your path handling works

## Testing

Run the test script to verify path handling:
```bash
python utils/run_python_script.py utils/test_apostrophe_path.py
```

Or directly:
```bash
python utils/test_apostrophe_path.py
```

## Files Using This Pattern

- `scripts/goal_setting_analysis_main.py` - Uses `load_module_from_path()` function
- `utils/run_python_script.py` - Generic launcher for any Python script
- `organize_pnc_onedrive_files.py` - Uses `pathlib.Path` for OneDrive path

## Technical Details

The PowerShell wrapper fails because it tries to parse command strings that contain special characters. By using:
- `subprocess.run()` with `shell=False` - Direct process execution, no shell interpretation
- `pathlib.Path` objects - Handles paths correctly regardless of special characters
- Raw strings (`r"..."`) for paths - Prevents escape sequence issues

