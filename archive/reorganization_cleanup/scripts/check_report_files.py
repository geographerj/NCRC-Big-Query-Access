"""Check what CSV files are available for the weekly report"""

from pathlib import Path
import pandas as pd
from datetime import datetime

reports_dir = Path(r"C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis\Weekly BankFind Branch Changes Reports")

print("="*80)
print("CHECKING AVAILABLE CSV FILES")
print("="*80)

csv_files = list(reports_dir.glob("*.csv"))
print(f"\nFound {len(csv_files)} CSV file(s):")
for f in sorted(csv_files):
    print(f"  • {f.name}")

# Check baseline
baseline_file = reports_dir / "BASELINE_branch_changes.csv"
if baseline_file.exists():
    df = pd.read_csv(baseline_file)
    if 'PROCDATE' in df.columns:
        df['PROCDATE'] = pd.to_datetime(df['PROCDATE'], errors='coerce')
        proc_dates = df['PROCDATE'].dropna()
        if len(proc_dates) > 0:
            print(f"\nBaseline data date range:")
            print(f"  PROCDATE: {proc_dates.min()} to {proc_dates.max()}")
            print(f"  Total records: {len(df)}")

print("\n" + "="*80)
print("TO GENERATE THE WEEKLY REPORT:")
print("="*80)
print("\nYou need to export NEW CSV files from FDIC for the report week (Oct 19-25, 2025).")
print("\nSteps:")
print("1. Go to: https://banks.data.fdic.gov/bankfind-suite/oscr")
print("2. Set date range to: 10/19/2025 to 10/25/2025")
print("3. Set Search Date to: PROCDATE (Process Date)")
print("4. Search for Event Code: 711 (closings) and export CSV")
print("5. Search for Event Code: 721 (openings) and export CSV")
print("\nThen run:")
print("  python scripts/generate_weekly_branch_report.py \\")
print("    --csv-closings \"path/to/closings.csv\" \\")
print("    --csv-openings \"path/to/openings.csv\"")

