# Fixing the Apostrophe Path Issue

## The Problem

Your OneDrive path contains an apostrophe:
```
C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis
```

The `Nat'l` (with apostrophe) likely breaks Cursor's PowerShell wrapper script when it tries to escape quotes for Base64 encoding.

## Solution Options (Without Renaming SharePoint)

### Solution 1: Create a Symbolic Link (RECOMMENDED)

Create a junction/symbolic link to your project using a simple path **without** the apostrophe.

**Steps:**

1. Open Command Prompt as Administrator (Right-click → Run as Administrator)

2. Create a junction point:
   ```cmd
   mklink /J "C:\DREAM" "C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis"
   ```

3. In Cursor, open the folder `C:\DREAM` instead of the original path

4. Test if terminal works:
   ```cmd
   python --version
   ```

**Pros:**
- ✅ One-time setup
- ✅ No need to move files
- ✅ Cursor sees a simple path
- ✅ Files still sync to OneDrive automatically
- ✅ Works for all future projects in this location

**Cons:**
- Requires Admin privileges (one-time)

---

### Solution 2: Change Cursor's Default Terminal to Command Prompt

Command Prompt handles special characters better than PowerShell.

**Steps:**

1. Open Cursor Settings (Ctrl+,)
2. Search for: `terminal default profile windows`
3. Set: **Terminal › Integrated › Default Profile: Windows** to **Command Prompt**
4. Close and reopen terminal
5. Test: `python --version`

**Pros:**
- ✅ No file moving required
- ✅ Quick fix
- ✅ Command Prompt doesn't have the same quote escaping issues

**Cons:**
- ⚠️ Still might have issues (but less likely)

---

### Solution 3: Use SUBST (Temporary Drive Mapping)

Map a drive letter to your path.

**Steps:**

1. Open Command Prompt as Administrator

2. Map drive:
   ```cmd
   subst Z: "C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis"
   ```

3. In Cursor, open folder: `Z:\`

**Pros:**
- ✅ Very simple path: `Z:\`
- ✅ Easy to use

**Cons:**
- ⚠️ Drive mapping is temporary (lost after restart)
- ⚠️ Need to remap each session
- ⚠️ Can conflict with other drive mappings

**To make it permanent:**
Create a batch file that runs on startup:
```batch
@echo off
subst Z: "C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis"
```

---

### Solution 4: Move Project Folder (Not OneDrive)

Move just the `DREAM Analysis` folder to a simpler location, but keep it syncing.

**Steps:**

1. Close Cursor and OneDrive sync

2. Move folder:
   ```cmd
   move "C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis" "C:\Projects\DREAM Analysis"
   ```

3. Create junction back to OneDrive:
   ```cmd
   mklink /J "C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis" "C:\Projects\DREAM Analysis"
   ```

**Pros:**
- ✅ Simple path for Cursor
- ✅ Still syncs to OneDrive

**Cons:**
- ⚠️ More complex setup
- ⚠️ Need to ensure OneDrive syncs the junction correctly

---

## Testing Which Solution Works

### Quick Test: Change Terminal First

1. **Try Solution 2 first** (change to Command Prompt) - Takes 30 seconds
2. If that doesn't work, try **Solution 1** (symbolic link) - Takes 2 minutes

### Verify the Issue

To confirm the apostrophe is the problem:
1. Create a test project in `C:\Test\Project` (no apostrophe)
2. Try running `python --version` in Cursor terminal
3. If it works there, confirms the path is the issue

---

## Recommended Approach

**Start with Solution 2** (Command Prompt) - it's the quickest test.

If that doesn't work, use **Solution 1** (Symbolic Link) - it's the most robust long-term solution.

---

## After Applying a Fix

1. Test the reorganization script:
   ```cmd
   python MOVE_FILES_NOW.py
   ```

2. Verify Python scripts run correctly

3. Update your workflow documentation if needed

