"""
Create Baseline Report for FDIC Branch Changes

Generates a baseline report covering the past year of branch closures
to establish historical patterns for trend analysis.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# Import the main report functions
sys.path.insert(0, str(Path(__file__).parent))
from fdic_branch_changes_report import (
    get_branch_changes_web,
    create_excel_report,
    load_from_csv
)

def main():
    """Create baseline report for past year"""
    print("="*80)
    print("FDIC BRANCH CHANGES - BASELINE REPORT GENERATOR")
    print("="*80)
    
    # Calculate date range: One year ago to today
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    print(f"\nGenerating baseline report:")
    print(f"  Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"  This covers the past year of branch changes")
    
    # Set output file location
    reports_dir = Path(r"C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis\Weekly BankFind Branch Changes Reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    baseline_file = reports_dir / f"BASELINE_Branch_Changes_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.xlsx"
    
    print(f"\nOutput file: {baseline_file}")
    
    # Try to fetch data
    print("\nNote: This will attempt to fetch data from FDIC website.")
    print("Due to JavaScript requirements, you may need to:")
    print("1. Manually export CSV from FDIC website for the full year")
    print("2. Run: python scripts/create_baseline_report.py --csv-file <exported_file>.csv")
    
    # Check for CSV file argument
    import argparse
    parser = argparse.ArgumentParser(description='Create Baseline Branch Changes Report')
    parser.add_argument('--csv-file', help='Load data from CSV file')
    
    args = parser.parse_args()
    
    if args.csv_file:
        df = load_from_csv(args.csv_file)
    else:
        # Try web scraping (may not work)
        df = get_branch_changes_web(start_date, end_date, ['711', '721'], use_effective_date=False)
    
    if len(df) > 0:
        # Create baseline report
        # For baseline, we'll also create a CSV version for easy loading
        baseline_csv = reports_dir / f"BASELINE_branch_changes.csv"
        df.to_csv(baseline_csv, index=False)
        print(f"\nBaseline CSV saved: {baseline_csv}")
        print("  (This will be used for trend analysis in weekly reports)")
        
        # Also create Excel report
        create_excel_report(
            df, 
            str(baseline_file),
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'),
            baseline_data=None  # This IS the baseline
        )
        
        print("\n" + "="*80)
        print("BASELINE REPORT COMPLETE!")
        print("="*80)
        print(f"\nBaseline report saved to: {baseline_file}")
        print("\nThis baseline will be used for trend analysis in weekly reports.")
    else:
        print("\n" + "="*80)
        print("NO DATA RETRIEVED")
        print("="*80)
        print("\nTo create baseline report:")
        print("1. Visit: https://banks.data.fdic.gov/bankfind-suite/oscr")
        print(f"2. Set date range: {start_date.strftime('%m/%d/%Y')} to {end_date.strftime('%m/%d/%Y')}")
        print("3. Event Code: 711 OR 721")
        print("4. Search Date: Process Date")
        print("5. Export as CSV")
        print(f"6. Run: python scripts/create_baseline_report.py --csv-file <exported_file>.csv")

if __name__ == "__main__":
    main()

