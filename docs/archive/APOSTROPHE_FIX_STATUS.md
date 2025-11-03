# Apostrophe Path Fix - Status & Testing Guide

## Issue Summary

The OneDrive path contains an apostrophe:
```
C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis
```

This breaks Cursor's PowerShell terminal wrapper when it tries to escape quotes for Base64 encoding.

## Solution Implemented: Symbolic Link

A symbolic link (junction) was created to provide a simple path without apostrophes:
```
C:\DREAM -> C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis
```

## Current Status

✅ **Symbolic link created**: `C:\DREAM` exists (based on workspace path)  
⚠️ **Terminal still has issues**: PowerShell wrapper still failing (seen in test commands)

## How to Verify the Fix is Working

### Step 1: Check if Symbolic Link Exists

**Option A: From File Explorer**
1. Open File Explorer
2. Navigate to `C:\`
3. Look for `DREAM` folder
4. Right-click → Properties
5. Should show "Type: Junction" or similar

**Option B: From Command Prompt** (outside Cursor)
1. Open Command Prompt (not Cursor terminal)
2. Run:
   ```cmd
   dir C:\DREAM
   ```
3. Should list your project files

**Option C: Check if it links to OneDrive**
```cmd
dir /A:L C:\DREAM
```
Should show it's a symbolic link pointing to your OneDrive path.

### Step 2: Verify You're Using C:\DREAM in Cursor

1. In Cursor, check the bottom status bar - it should show:
   ```
   C:\DREAM
   ```
   NOT:
   ```
   C:\Users\edite\OneDrive - Nat'l Community...
   ```

2. If it shows the OneDrive path:
   - Close Cursor
   - File → Open Folder
   - Select `C:\DREAM` (NOT the OneDrive path)

### Step 3: Test Terminal Commands

**In Cursor Terminal, try:**
```cmd
python --version
```

**Expected Results:**
- ✅ **Success**: Python version prints → Fix is working!
- ❌ **PowerShell error**: "Missing terminator" or "Missing '('" → Still has issues

**If PowerShell errors occur:**
1. Change terminal to Command Prompt:
   - `Ctrl+,` (Settings)
   - Search: `terminal default profile windows`
   - Set to: **Command Prompt**
   - Close and reopen terminal

2. Or use external terminal:
   - Open Command Prompt outside Cursor
   - `cd C:\DREAM`
   - `python --version`

## Testing Scripts

### Test Script 1: TEST_APOSTROPHE_FIX.bat

Run from Command Prompt (outside Cursor):
```cmd
cd C:\DREAM
TEST_APOSTROPHE_FIX.bat
```

This will:
- Check if you're in `C:\DREAM`
- Verify symbolic link exists
- Test Python commands
- Check path for apostrophes

### Test Script 2: TEST_PATH_ISSUE.bat

Run from Command Prompt:
```cmd
cd C:\DREAM
TEST_PATH_ISSUE.bat
```

Tests basic Python functionality.

### Test Script 3: Run a Real Python Script

Try running a project script:
```cmd
cd C:\DREAM
python scripts\fifth_third_cba_report.py --help
```

If this works without errors, the fix is successful!

## Troubleshooting

### Problem: "C:\DREAM does not exist"

**Solution**: Create the symbolic link
1. Right-click `CREATE_SYMBOLIC_LINK.bat`
2. "Run as administrator"
3. Follow prompts
4. Close and reopen Cursor
5. Open `C:\DREAM` in Cursor

### Problem: "Still getting PowerShell errors in Cursor"

**Solution 1**: Change default terminal (quick fix)
1. `Ctrl+,` → Settings
2. Search: `terminal default profile windows`
3. Change to: **Command Prompt**
4. Restart terminal

**Solution 2**: Use external terminal
- Open Command Prompt outside Cursor
- All commands will work from there

### Problem: "Cursor still shows OneDrive path"

**Solution**: 
1. Close Cursor completely
2. File → Open Folder
3. Navigate to and select: `C:\DREAM`
4. NOT the OneDrive path

### Problem: "Files not syncing to OneDrive"

**Solution**: 
- Symbolic links should sync automatically
- Check OneDrive sync status
- If issues persist, the symbolic link might need to be recreated

## Verification Checklist

- [ ] `C:\DREAM` exists (check File Explorer or `dir C:\DREAM`)
- [ ] Cursor workspace shows `C:\DREAM` in status bar
- [ ] `python --version` works in Cursor terminal (or Command Prompt works)
- [ ] Can run Python scripts without path errors
- [ ] Files sync to OneDrive correctly
- [ ] No apostrophe in working directory path

## Success Indicators

✅ **Full Success**: 
- Cursor terminal works perfectly
- All Python commands execute
- No PowerShell errors
- Files sync to OneDrive

⚠️ **Partial Success**:
- Symbolic link exists
- Can use external Command Prompt
- Need to use Command Prompt instead of PowerShell in Cursor

❌ **Still Broken**:
- PowerShell errors persist even with Command Prompt
- Symbolic link doesn't exist
- Files not accessible

## Next Steps After Verification

Once verified working:

1. ✅ Document that you're using `C:\DREAM` path
2. ✅ Update any batch files if they reference old path
3. ✅ Test running a full analysis script
4. ✅ Verify OneDrive sync is working

## Need Help?

If issues persist:
1. Check if `CREATE_SYMBOLIC_LINK.bat` was run as Administrator
2. Try Solution 2: Change terminal to Command Prompt
3. Use external Command Prompt for all operations
4. Verify OneDrive path is correct in `CREATE_SYMBOLIC_LINK.bat`

---

**Last Updated**: Check current status by running test scripts above.

