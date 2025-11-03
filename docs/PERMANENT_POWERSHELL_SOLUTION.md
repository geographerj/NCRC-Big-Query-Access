# Permanent Solution for PowerShell Wrapper Issues

## The Problem

Even with Command Prompt set as the default terminal, Cursor may still use a PowerShell wrapper that fails with paths containing apostrophes.

## Best Permanent Solutions

### ✅ Solution 1: Double-Click Python Scripts (SIMPEST)

**Created:** `organize_pnc_files_DIRECT.py` - Self-contained script you can double-click.

**How to use:**
1. Navigate to `c:\DREAM` in File Explorer
2. Double-click `organize_pnc_files_DIRECT.py`
3. Script runs directly, bypassing Cursor's terminal entirely

**Why it works:**
- Windows executes Python directly (no Cursor terminal wrapper)
- Self-contained - no imports needed
- Uses `pathlib` to handle apostrophe paths
- Shows results in a console window

---

### ✅ Solution 2: Use External Command Prompt

**Steps:**
1. Open Windows Command Prompt (outside Cursor)
2. Navigate to: `cd c:\DREAM`
3. Run: `python organize_pnc_onedrive_files.py`

**Why it works:**
- Completely bypasses Cursor's terminal wrapper
- Command Prompt handles paths correctly
- No PowerShell interference

---

### ✅ Solution 3: Use Python Launcher via File Explorer

**Steps:**
1. Right-click `organize_pnc_files_DIRECT.py` in File Explorer
2. Select "Open with" → Python
3. Or ensure `.py` files are associated with Python (default on Windows)

**Why it works:**
- Windows handles the execution directly
- No IDE terminal wrapper involved

---

### ✅ Solution 4: Create Batch File Wrapper

Create `RUN_ORGANIZE.bat`:
```batch
@echo off
cd /d c:\DREAM
python organize_pnc_files_DIRECT.py
pause
```

**Why it works:**
- Batch files run in cmd.exe directly
- Bypasses Cursor terminal
- Can be double-clicked

---

## Recommended Approach

**For immediate use:**
1. Double-click `organize_pnc_files_DIRECT.py` in File Explorer
2. This bypasses all terminal wrapper issues

**For future scripts:**
1. Use the pattern in `organize_pnc_files_DIRECT.py`:
   - Self-contained code (no complex imports)
   - Uses `pathlib.Path` for all paths
   - Add `input("Press Enter...")` at end for double-click usage
2. Or use external Command Prompt for all Python scripts

---

## Files Created

- ✅ `organize_pnc_files_DIRECT.py` - Self-contained, double-clickable version
- ✅ `utils/run_python_script.py` - Utility launcher (works once terminal works)
- ✅ `execute_organize_files.py` - Uses importlib pattern
- ✅ `docs/PERMANENT_POWERSHELL_SOLUTION.md` - This guide

---

## Technical Details

The issue: Cursor's terminal wrapper (even with Command Prompt) may use PowerShell for Base64 encoding/decoding of commands, which fails with apostrophes.

Solutions that work:
1. **Double-click Python files** - Windows executes directly, no wrapper
2. **External Command Prompt** - No wrapper at all
3. **Batch files** - Run in cmd.exe directly
4. **Subprocess with shell=False** - Bypasses shell interpretation (once Python can run)

---

## Test Your Fix

1. Double-click `organize_pnc_files_DIRECT.py`
2. Should see console window with file movement progress
3. Files will be moved to merger folder

---

## Going Forward

**Best practice:** For scripts that need to run reliably:
1. Make them self-contained (like `organize_pnc_files_DIRECT.py`)
2. Use `pathlib.Path` for all paths
3. Add `input("Press Enter...")` at end if double-clicking
4. Test by double-clicking in File Explorer first

