# Quick Fix: Change Cursor Terminal to Command Prompt

## The Fastest Solution (30 seconds)

### Step 1: Open Cursor Settings
- Press `Ctrl+,` (or File → Preferences → Settings)

### Step 2: Search for Terminal Setting
- Type in search box: `terminal default profile windows`

### Step 3: Change Setting
- Find: **Terminal › Integrated › Default Profile: Windows**
- Change from: `PowerShell`
- Change to: `Command Prompt`

### Step 4: Restart Terminal
- Close any open terminal tabs
- Open new terminal (Ctrl+`)
- Test: `python --version`

## Why This Might Work

Command Prompt (`cmd.exe`) handles path escaping differently than PowerShell and may not have the same Base64 wrapper issues.

## If This Doesn't Work

Use the symbolic link solution (see `CREATE_SYMBOLIC_LINK.bat` or `docs/FIX_APOSTROPHE_PATH_ISSUE.md`).

