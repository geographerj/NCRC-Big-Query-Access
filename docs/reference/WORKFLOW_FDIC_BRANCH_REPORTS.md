# FDIC Branch Changes Reports - Complete Workflow

## Overview

This workflow generates weekly reports on bank branch openings and closings with trend analysis.

## Step 1: Create Baseline Report (One-Time Setup)

The baseline report establishes historical patterns for the past year of branch closures.

### Instructions:

1. **Visit FDIC OSCR Website:**
   - Go to: https://banks.data.fdic.gov/bankfind-suite/oscr

2. **Set Search Parameters:**
   - **Start Date**: One year ago from today (e.g., if today is Oct 25, 2025, use Oct 25, 2024)
   - **End Date**: Today's date
   - **Event Code**: `711 OR 721` (both openings and closings)
   - **Search Date**: **Process Date** (not Effective Date)

3. **Export Data:**
   - Click Search
   - Export results as CSV
   - Save as `BASELINE_branch_changes.csv` in the reports folder

4. **Generate Baseline Report:**
   ```bash
   python scripts/create_baseline_report.py --csv-file <exported_file>.csv
   ```

5. **Move Baseline File:**
   - The script creates both Excel and CSV versions
   - Ensure `BASELINE_branch_changes.csv` is in:
     ```
     C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis\Weekly BankFind Branch Changes Reports\
     ```

## Step 2: Generate Weekly Report

Run this every Friday for the previous week (Sunday to Saturday).

### Instructions:

1. **Visit FDIC OSCR Website:**
   - Go to: https://banks.data.fdic.gov/bankfind-suite/oscr

2. **Set Search Parameters for Last Week:**
   - **Start Date**: Previous Sunday (e.g., Oct 19, 2025)
   - **End Date**: Previous Saturday (e.g., Oct 25, 2025)
   - **Event Code**: `711 OR 721`
   - **Search Date**: **Process Date**

3. **Export Data:**
   - Export results as CSV

4. **Generate Weekly Report:**
   ```bash
   python scripts/fdic_branch_changes_report.py --csv-file <exported_file>.csv
   ```

   Or use the automatic date calculation:
   ```bash
   python scripts/run_weekly_branch_report.py --test  # For Oct 19-25, 2025
   ```

## Report Structure

Each weekly Excel report contains:

### 1. Notes Sheet
- Explanation of what the report covers
- How it works
- When it runs
- Sheet descriptions
- Data fields
- Contact information

### 2. All Changes Sheet
Shows all branch openings and closings with:
- **Event Type** (Opening/Closing)
- **Bank Name**
- **Branch Address**
- **Service Type**
- **County**
- **State**
- **Effective Date**

### 3. Trend Analysis Sheet
- Current week summary (closings, openings, net change)
- Comparison to baseline (past year average)
- Trend interpretation
- Identifies if current week is part of a trend

## Automation

Once baseline is set up, GitHub Actions will:
- Run automatically every Friday at 9 AM UTC
- Calculate previous week dates (Sunday to Saturday)
- Attempt to fetch data (may require manual CSV export)
- Generate report with trend analysis

## File Locations

- **Baseline Report**: `Weekly BankFind Branch Changes Reports/BASELINE_*.xlsx`
- **Baseline CSV**: `Weekly BankFind Branch Changes Reports/BASELINE_branch_changes.csv`
- **Weekly Reports**: `Weekly BankFind Branch Changes Reports/Branch_Changes_YYYYMMDD_to_YYYYMMDD.xlsx`

## Testing

To test with last week's data:
```bash
python scripts/run_weekly_branch_report.py --test
```

This uses: October 19-25, 2025 (Sunday to Saturday)

