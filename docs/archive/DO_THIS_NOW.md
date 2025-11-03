# Do This Now - Quick Path to Report

## Step 1: Run SQL in BigQuery (5 minutes)

1. Open: https://console.cloud.google.com/bigquery
2. Click "Compose new query"
3. Open file: `FIFTH_THIRD_REDLINING_FULL_QUERY.sql`
4. Copy ALL the SQL
5. Paste into BigQuery
6. Click "Run"
7. Wait 5-15 minutes
8. Click "Save results" → "CSV (local file)"
9. Save as: `fifth_third_report.csv` in your Desktop\DREAM Analysis folder

## Step 2: Generate Excel (1 minute)

Open your PowerShell/CMD terminal (not Cursor's):

```powershell
cd "C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis"
python ncrc_worst_lenders_analysis_v4.py fifth_third_report.csv
```

## Done! ✅

You'll get an Excel file with your complete report.

The terminal issue is preventing me from running it for you, but you have all the working code ready to go!


