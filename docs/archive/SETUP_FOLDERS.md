# Manual Folder Setup Instructions

Since Cursor's terminal has issues, follow these manual steps:

## Step 1: Create Folders Manually

**Option A: Using File Explorer**
1. Navigate to: `C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis`
2. Right-click → New → Folder
3. Create these three folders:
   - `data`
   - `reports`
   - `scripts`

**Option B: Using Command Prompt (outside Cursor)**
1. Open Command Prompt (Windows Key + R, type `cmd`)
2. Navigate to your project:
   ```
   cd "C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis"
   ```
3. Run these commands:
   ```
   mkdir data
   mkdir reports
   mkdir scripts
   ```

## Step 2: Move Files

### Move CSV Files to `data/` folder:
- Move all `bquxjob_*.csv` files to the `data` folder
- This includes:
  - Redlining CSV files
  - Demographics CSV files

### Move Batch File to `scripts/` folder:
- Move `@@run_excel_generator.bat` (or any batch files) to `scripts/` folder
- OR just use the new `scripts/run_excel_generator.bat` that was created

### Keep at Root:
- `fifth_third_cba_report.py` (stays at root)
- SQL query files (can stay at root, or move to a `SQL` folder if you want)

## Step 3: Test

Run from Command Prompt (outside Cursor):
```
cd "C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis"
python fifth_third_cba_report.py
```

OR use the batch file:
```
scripts\run_excel_generator.bat
```

## Alternative: Let Script Auto-Create Folders

The script automatically creates `reports/` and `data/` folders when you run it, so you only need to create `scripts/` if you want to use the batch file.

If you don't create folders manually, just run the script and it will create them automatically!

