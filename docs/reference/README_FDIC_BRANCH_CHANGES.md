# FDIC Branch Changes Weekly Report

This script generates weekly reports on bank branch openings and closings from the FDIC Office Structure Changes Report (OSCR).

## Setup

1. **Install required dependencies:**
```bash
pip install requests beautifulsoup4 pandas openpyxl
```

2. **Add to requirements.txt:**
```bash
echo "requests>=2.31.0" >> requirements.txt
echo "beautifulsoup4>=4.12.0" >> requirements.txt
```

## Usage

### Automatic Web Scraping (If Available)

```bash
# Weekly report (last 7 days)
python scripts/fdic_branch_changes_report.py

# Custom date range
python scripts/fdic_branch_changes_report.py --start-date 2024-10-01 --end-date 2024-10-31

# Specific event codes (711=closings, 721=openings)
python scripts/fdic_branch_changes_report.py --event-codes 711 721
```

### Manual CSV Export Method (Recommended)

Since the FDIC website may not have a direct API, the most reliable method is:

1. **Visit FDIC OSCR website:**
   - Go to: https://banks.data.fdic.gov/bankfind-suite/oscr
   - Set parameters:
     - **Start Date**: (e.g., 10/31/2024)
     - **End Date**: (e.g., 10/31/2025)
     - **Event Code**: `711 OR 721` (for both openings and closings)
     - **Search Date**: Process Date (PROCDATE)
   - Click Search

2. **Export data:**
   - If export option is available, download as CSV
   - Or copy table data and save as CSV

3. **Generate Excel report:**
```bash
python scripts/fdic_branch_changes_report.py --csv-file <downloaded_file>.csv
```

## Weekly Automation

### Windows Task Scheduler

1. Create a batch file `run_fdic_report.bat`:
```batch
@echo off
cd C:\DREAM
python scripts\fdic_branch_changes_report.py
```

2. Schedule in Task Scheduler:
   - Create Basic Task
   - Trigger: Weekly (every Monday)
   - Action: Start Program → Select batch file

### Linux/Mac Cron

Add to crontab (`crontab -e`):
```bash
# Run every Monday at 9 AM
0 9 * * 1 cd /path/to/DREAM && python scripts/fdic_branch_changes_report.py
```

## Output

The script generates an Excel file with:

- **Summary Sheet**: Statistics and overview
- **Branch Closings Sheet**: All branch closing events (Event Code 711)
- **Branch Openings Sheet**: All branch opening events (Event Code 721)

Each sheet includes:
- All branch details from FDIC data
- Formatted headers
- Auto-sized columns
- Frozen header row

Reports are saved to: `reports/branch_changes/`

## Event Codes

- **711**: Branch Closing
- **721**: Branch Opening

For other event codes, see FDIC documentation.

## Troubleshooting

If automatic scraping doesn't work:

1. **Check FDIC website structure** - The website may have changed
2. **Use manual CSV export** - Most reliable method
3. **Check API documentation** - Visit https://api.fdic.gov/banks/docs/
4. **Verify date range** - Ensure there are actual branch changes in the period

## References

- FDIC OSCR: https://banks.data.fdic.gov/bankfind-suite/oscr
- FDIC API Docs: https://api.fdic.gov/banks/docs/

