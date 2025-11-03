"""
Process FDIC CSV files (separate openings and closings) and combine into weekly report
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fdic_branch_changes_report import create_excel_report, load_baseline_data

def combine_fdic_csvs(closings_file, openings_file, start_date, end_date):
    """Combine separate opening and closing CSV files into one DataFrame"""
    
    print(f"\nLoading FDIC CSV files...")
    print(f"  Closings: {closings_file}")
    print(f"  Openings: {openings_file}")
    
    # Load both files
    df_closings = pd.read_csv(closings_file)
    df_openings = pd.read_csv(openings_file)
    
    print(f"  Closings: {len(df_closings)} records")
    print(f"  Openings: {len(df_openings)} records")
    
    # Add event code column to identify type
    df_closings['Event_Code'] = '711'  # Closing
    df_openings['Event_Code'] = '721'  # Opening
    
    # Combine
    df_combined = pd.concat([df_closings, df_openings], ignore_index=True)
    
    print(f"  Combined: {len(df_combined)} total records (before date filter)")
    
    # Filter by PROCDATE (Process Date) to match the report week
    # If no records found, try filtering by EFFDATE (Effective Date) instead
    filtered = False
    if 'PROCDATE' in df_combined.columns:
        # Convert PROCDATE to datetime
        df_combined['PROCDATE'] = pd.to_datetime(df_combined['PROCDATE'], errors='coerce')
        
        # Filter to only include records processed during the report week
        mask = (df_combined['PROCDATE'] >= start_date) & (df_combined['PROCDATE'] <= end_date)
        df_filtered = df_combined[mask].copy()
        
        if len(df_filtered) > 0:
            df_combined = df_filtered
            filtered = True
            print(f"  After filtering by PROCDATE ({start_date.date()} to {end_date.date()}): {len(df_combined)} records")
        else:
            # Try EFFDATE instead
            print(f"  No records with PROCDATE in range ({start_date.date()} to {end_date.date()})")
            if 'EFFDATE' in df_combined.columns:
                df_combined['EFFDATE'] = pd.to_datetime(df_combined['EFFDATE'], errors='coerce')
                mask = (df_combined['EFFDATE'] >= start_date) & (df_combined['EFFDATE'] <= end_date)
                df_filtered = df_combined[mask].copy()
                if len(df_filtered) > 0:
                    df_combined = df_filtered
                    filtered = True
                    print(f"  Filtering by EFFDATE instead: {len(df_combined)} records")
                else:
                    print(f"  Also no records with EFFDATE in range - showing all data ({len(df_combined)} records)")
            else:
                print(f"  EFFDATE column not found - showing all data ({len(df_combined)} records)")
    else:
        print("  WARNING: PROCDATE column not found - showing all data")
    
    if not filtered:
        # Show date ranges for debugging
        if 'PROCDATE' in df_combined.columns:
            proc_dates = pd.to_datetime(df_combined.get('PROCDATE', pd.Series()), errors='coerce')
            if len(proc_dates.dropna()) > 0:
                print(f"  PROCDATE range in data: {proc_dates.min()} to {proc_dates.max()}")
        if 'EFFDATE' in df_combined.columns:
            eff_dates = pd.to_datetime(df_combined.get('EFFDATE', pd.Series()), errors='coerce')
            if len(eff_dates.dropna()) > 0:
                print(f"  EFFDATE range in data: {eff_dates.min()} to {eff_dates.max()}")
    
    return df_combined

def main():
    reports_dir = Path(r"C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis\Weekly BankFind Branch Changes Reports")
    
    # Find CSV files
    closings_file = reports_dir / "Branch_Office_Closings_10_31_2025.csv"
    openings_file = reports_dir / "Branch_Office_Openings_10_31_2025.csv"
    
    if not closings_file.exists() or not openings_file.exists():
        print("ERROR: CSV files not found")
        print(f"  Expected: {closings_file}")
        print(f"  Expected: {openings_file}")
        return
    
    # Date range for last week (Oct 19-25, 2025)
    start_date = datetime(2025, 10, 19)  # Sunday
    end_date = datetime(2025, 10, 25)   # Saturday
    
    print("="*80)
    print("PROCESSING FDIC BRANCH CHANGES DATA")
    print("="*80)
    
    # Combine the CSV files
    df = combine_fdic_csvs(closings_file, openings_file, start_date, end_date)
    
    if len(df) == 0:
        print("\nNo data to process")
        return
    
    # Load baseline if available
    baseline_data = load_baseline_data()
    
    # Generate output filename
    output_file = reports_dir / f"Branch_Changes_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.xlsx"
    
    # Create Excel report
    create_excel_report(
        df,
        str(output_file),
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        baseline_data
    )
    
    print("\n" + "="*80)
    print("REPORT COMPLETE!")
    print("="*80)
    print(f"\nReport saved to: {output_file}")

if __name__ == "__main__":
    main()

