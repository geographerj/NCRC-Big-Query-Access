# GitHub Actions Weekly Branch Report

This workflow automatically runs every Friday to generate the FDIC Branch Changes report for the previous week.

## How It Works

1. **Schedule**: Runs every Friday at 9:00 AM UTC
2. **Date Range**: Automatically calculates previous week (Sunday to Saturday)
3. **Process**: Attempts to fetch data from FDIC website
4. **Output**: Generates Excel report and uploads as artifact

## Manual Trigger

You can also trigger the workflow manually from the GitHub Actions tab:

1. Go to **Actions** → **Weekly FDIC Branch Changes Report**
2. Click **Run workflow**
3. Optionally override date range:
   - Leave blank for automatic calculation
   - Or specify `start_date` and `end_date` in YYYY-MM-DD format

## Report Location

- **GitHub Actions**: Reports are saved as artifacts (downloadable for 30 days)
- **Local Runs**: Reports saved to:
  ```
  C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis\Weekly BankFind Branch Changes Reports
  ```

## Important Notes

Since the FDIC website uses JavaScript to load data:

1. **If automated scraping fails**: The workflow will still provide:
   - Correct date range calculation
   - Instructions for manual CSV export
   - Summary in workflow run

2. **Manual CSV Export Method** (Most Reliable):
   - Visit: https://banks.data.fdic.gov/bankfind-suite/oscr
   - Set:
     - **Start Date**: [Previous Sunday]
     - **End Date**: [Previous Saturday]
     - **Event Code**: `711 OR 721`
     - **Search Date**: **Process Date**
   - Export as CSV
   - Run locally: `python scripts/fdic_branch_changes_report.py --csv-file <file>.csv`

## Timezone Adjustments

To change the run time, edit `.github/workflows/weekly_branch_report.yml`:

```yaml
schedule:
  - cron: '0 9 * * 5'  # Friday at 9 AM UTC
```

Cron format: `minute hour day-of-month month day-of-week`

- `0 9 * * 5` = Friday 9:00 AM UTC
- `0 5 * * 5` = Friday 5:00 AM UTC (1:00 AM EDT)
- `0 13 * * 5` = Friday 1:00 PM UTC (9:00 AM EDT)

## Viewing Results

1. Go to **Actions** tab in GitHub
2. Click on the latest workflow run
3. Download the artifact: `branch-changes-report-YYYY-MM-DD`

