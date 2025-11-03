# Final Instructions: Fifth Third Redlining Report

## Everything is Ready!

I've created all the files you need. The SQL query is complete and ready to run.

## Step 1: Run SQL Query in BigQuery

**File**: `FIFTH_THIRD_REDLINING_FULL_QUERY.sql`

1. Open Google Cloud Console: https://console.cloud.google.com/bigquery
2. Click "Compose new query"
3. Copy entire contents of `FIFTH_THIRD_REDLINING_FULL_QUERY.sql`
4. Paste into BigQuery
5. Click "Run"
6. Wait for results (5-15 minutes depending on data size)
7. Click "Save results" → "CSV (local file)"
8. Save as: `fifth_third_redlining_report.csv`

## Step 2: Generate Excel Report

**Use your regular PowerShell/CMD terminal** (not Cursor's broken one):

1. Open Windows Terminal, PowerShell, or CMD
2. Navigate to your project:
   ```
   cd "C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis"
   ```
3. Run Excel generator:
   ```
   python ncrc_worst_lenders_analysis_v4.py fifth_third_redlining_report.csv
   ```

## Done! ✅

You'll get an Excel file with:
- Fifth Third Bank vs Peer comparisons
- 8 tract demographic metrics (MMCT, Black, Hispanic, Combined at 50% and 80%)
- Years 2018-2024
- Top 10 CBSAs by originations
- Conditional formatting (red/yellow/green)
- Statistical significance indicators

## What You're Getting

**Metrics**:
- MMCT 50% and 80% (Majority Minority Census Tracts)
- Black Tract 50% and 80%
- Hispanic Tract 50% and 80%
- Black+Hispanic Tract 50% and 80%

**Analysis**:
- Subject Bank: Fifth Third Bank
- Peer Banks: Lenders with 50%-200% of Fifth Third's volume
- Geographic Focus: Top 10 CBSAs by home purchase originations
- Time Period: 2018-2024
- Filters: Owner-occupied, site-built, 1-4 unit, exclude reverse mortgages

**Excel Output**:
- Years as columns
- Metrics as rows
- Color-coded gaps (red=bad, green=good)
- Asterisks for statistical significance

## SQL Query Summary

The query:
1. Finds top 10 CBSAs by Fifth Third home purchase originations
2. Joins HMDA data with tract demographics from geo.black_hispanic_majority
3. Applies standard filters
4. Calculates metrics for subject bank vs peers
5. Outputs all columns needed for Excel generator

**File is ready**: Just copy/paste into BigQuery and run!


