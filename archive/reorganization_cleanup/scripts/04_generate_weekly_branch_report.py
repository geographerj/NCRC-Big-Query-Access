"""
Generate weekly branch changes report comparing current week to baseline data
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fdic_branch_changes_report import create_excel_report, load_baseline_data, get_branch_changes_web, load_from_csv

def setup_baseline_from_csvs(reports_dir):
    """Save the existing CSV files as baseline data"""
    baseline_file = reports_dir / "BASELINE_branch_changes.csv"
    
    closings_file = reports_dir / "Branch_Office_Closings_10_31_2025.csv"
    openings_file = reports_dir / "Branch_Office_Openings_10_31_2025.csv"
    
    if not closings_file.exists() or not openings_file.exists():
        print(f"ERROR: Baseline CSV files not found")
        print(f"  Expected: {closings_file}")
        print(f"  Expected: {openings_file}")
        return False
    
    print("\nSetting up baseline data from CSV files...")
    
    # Load and combine baseline CSVs
    df_closings = pd.read_csv(closings_file)
    df_openings = pd.read_csv(openings_file)
    
    # Add event code
    df_closings['Event_Code'] = '711'
    df_openings['Event_Code'] = '721'
    
    # Combine
    df_baseline = pd.concat([df_closings, df_openings], ignore_index=True)
    
    # Save as baseline
    df_baseline.to_csv(baseline_file, index=False)
    print(f"  Baseline saved: {baseline_file} ({len(df_baseline)} records)")
    
    return True

def fetch_weekly_data(start_date, end_date, reports_dir):
    """Fetch data for the report week"""
    print(f"\nFetching data for report week: {start_date.date()} to {end_date.date()}")
    
    # Try to fetch from web
    df_web = get_branch_changes_web(start_date, end_date, use_effective_date=False)
    
    if len(df_web) > 0:
        print(f"  Successfully fetched {len(df_web)} records from FDIC website")
        return df_web
    
    # If web fetch fails, check for CSV files with the report week dates
    print("  Web fetch returned no data - checking for CSV files...")
    
    # Look for CSV files that might have been manually exported
    csv_files = list(reports_dir.glob("*.csv"))
    csv_files = [f for f in csv_files if "Branch_Office" in f.name and f.name != "BASELINE_branch_changes.csv"]
    
    if csv_files:
        print(f"  Found {len(csv_files)} potential CSV file(s)")
        print("  NOTE: Please export new CSV files from FDIC for the report week")
        print("  or use --csv-closings and --csv-openings arguments")
    
    return pd.DataFrame()

def combine_csvs_for_week(closings_file, openings_file):
    """Combine opening and closing CSV files for the report week"""
    print(f"\nLoading CSV files for report week...")
    print(f"  Closings: {closings_file}")
    print(f"  Openings: {openings_file}")
    
    if not closings_file.exists() or not openings_file.exists():
        print("ERROR: CSV files not found")
        return pd.DataFrame()
    
    df_closings = pd.read_csv(closings_file)
    df_openings = pd.read_csv(openings_file)
    
    print(f"  Closings file: {len(df_closings)} records")
    print(f"  Openings file: {len(df_openings)} records")
    
    # Check if files are identical (they might be the same export)
    if len(df_closings) == len(df_openings):
        # Use the closings file and filter by CHANGECODE
        if 'CHANGECODE' in df_closings.columns:
            print(f"  Note: Both files appear identical. Using CHANGECODE column to separate events.")
            # Convert CHANGECODE to string for comparison (may be numeric)
            df_closings['CHANGECODE'] = df_closings['CHANGECODE'].astype(str)
            # Get closings (711) and openings (721) from the data
            actual_closings = df_closings[df_closings['CHANGECODE'] == '711'].copy()
            actual_openings = df_closings[df_closings['CHANGECODE'] == '721'].copy()
            
            print(f"  Actual closings (CHANGECODE 711): {len(actual_closings)} records")
            print(f"  Actual openings (CHANGECODE 721): {len(actual_openings)} records")
            
            # Set Event_Code based on CHANGECODE
            actual_closings['Event_Code'] = '711'
            actual_openings['Event_Code'] = '721'
            
            # Combine
            df_combined = pd.concat([actual_closings, actual_openings], ignore_index=True)
            print(f"  Combined: {len(df_combined)} total records")
            return df_combined
        else:
            # Fallback: assume filename indicates content
            df_closings['Event_Code'] = '711'
            df_openings['Event_Code'] = '721'
            # Only use closings file if they're identical
            print(f"  Warning: Files appear identical but no CHANGECODE column. Using closings file only.")
            return df_closings
    
    # If files are different, use them as provided
    # Use CHANGECODE if available, otherwise assume by filename
    if 'CHANGECODE' in df_closings.columns:
        df_closings['CHANGECODE'] = df_closings['CHANGECODE'].astype(str)
        df_closings = df_closings[df_closings['CHANGECODE'] == '711'].copy()
    df_closings['Event_Code'] = '711'
    
    if 'CHANGECODE' in df_openings.columns:
        df_openings['CHANGECODE'] = df_openings['CHANGECODE'].astype(str)
        df_openings = df_openings[df_openings['CHANGECODE'] == '721'].copy()
    df_openings['Event_Code'] = '721'
    
    # Combine
    df_combined = pd.concat([df_closings, df_openings], ignore_index=True)
    
    print(f"  Combined: {len(df_combined)} total records")
    
    return df_combined

def filter_by_date_range(df, start_date, end_date):
    """Filter DataFrame by PROCDATE, falling back to EFFDATE if needed"""
    if len(df) == 0:
        return df
    
    filtered = False
    
    # Try PROCDATE first
    if 'PROCDATE' in df.columns:
        df['PROCDATE'] = pd.to_datetime(df['PROCDATE'], errors='coerce')
        mask = (df['PROCDATE'] >= start_date) & (df['PROCDATE'] <= end_date)
        df_filtered = df[mask].copy()
        
        if len(df_filtered) > 0:
            print(f"  Filtered by PROCDATE: {len(df_filtered)} records")
            return df_filtered
        else:
            print(f"  No records with PROCDATE in range ({start_date.date()} to {end_date.date()})")
    
    # Try EFFDATE as fallback
    if 'EFFDATE' in df.columns:
        df['EFFDATE'] = pd.to_datetime(df['EFFDATE'], errors='coerce')
        mask = (df['EFFDATE'] >= start_date) & (df['EFFDATE'] <= end_date)
        df_filtered = df[mask].copy()
        
        if len(df_filtered) > 0:
            print(f"  Filtered by EFFDATE: {len(df_filtered)} records")
            return df_filtered
    
    # If no filtering worked, return all data with a warning
    print(f"  WARNING: Could not filter by date range - showing all {len(df)} records")
    return df

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate weekly FDIC branch changes report')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD), defaults to last week Sunday')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD), defaults to last week Saturday')
    parser.add_argument('--csv-closings', type=str, help='Path to closings CSV file for report week')
    parser.add_argument('--csv-openings', type=str, help='Path to openings CSV file for report week')
    parser.add_argument('--setup-baseline', action='store_true', help='Set up baseline from existing CSV files')
    
    args = parser.parse_args()
    
    reports_dir = Path(r"C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis\Weekly BankFind Branch Changes Reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Calculate date range (last week: Sunday to Saturday)
    if args.start_date and args.end_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    else:
        # Default to last week (Sunday to Saturday)
        today = datetime.now()
        # Find last Saturday
        days_since_saturday = (today.weekday() + 2) % 7
        if days_since_saturday == 0:
            days_since_saturday = 7
        last_saturday = today - timedelta(days=days_since_saturday)
        end_date = last_saturday
        start_date = last_saturday - timedelta(days=6)  # Previous Sunday
    
    print("="*80)
    print("WEEKLY FDIC BRANCH CHANGES REPORT GENERATOR")
    print("="*80)
    print(f"\nReport Period: {start_date.date()} to {end_date.date()}")
    
    # Setup baseline if requested or if it doesn't exist
    baseline_file = reports_dir / "BASELINE_branch_changes.csv"
    if args.setup_baseline or not baseline_file.exists():
        if not setup_baseline_from_csvs(reports_dir):
            print("\nERROR: Failed to set up baseline data")
            return
    
    # Load baseline data
    baseline_data = load_baseline_data()
    if baseline_data is None or len(baseline_data) == 0:
        print("\nWARNING: No baseline data available - trend analysis will be limited")
    
    # Get data for the report week
    if args.csv_closings and args.csv_openings:
        # Use provided CSV files
        df_week = combine_csvs_for_week(
            Path(args.csv_closings),
            Path(args.csv_openings)
        )
    else:
        # Try to fetch from web
        df_week = fetch_weekly_data(start_date, end_date, reports_dir)
        
        if len(df_week) == 0:
            print("\n" + "="*80)
            print("ERROR: No data available for report week")
            print("="*80)
            print("\nPlease either:")
            print("  1. Export CSV files from FDIC for the report week and use --csv-closings and --csv-openings")
            print("  2. Ensure the FDIC website is accessible and try again")
            return
    
    # Filter by date range
    df_week = filter_by_date_range(df_week, start_date, end_date)
    
    if len(df_week) == 0:
        print("\nWARNING: No records found for the report week after filtering")
        print("The report will be generated but will show no data for this week")
    
    # Generate output filename
    output_file = reports_dir / f"Branch_Changes_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.xlsx"
    
    # Create Excel report
    print("\n" + "="*80)
    print("GENERATING EXCEL REPORT")
    print("="*80)
    
    create_excel_report(
        df_week,
        str(output_file),
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        baseline_data
    )
    
    print("\n" + "="*80)
    print("REPORT COMPLETE!")
    print("="*80)
    print(f"\nReport saved to: {output_file}")
    print(f"\nReport includes:")
    print(f"  • {len(df_week)} records for the report week")
    if baseline_data is not None:
        print(f"  • {len(baseline_data)} baseline records for trend analysis")

if __name__ == "__main__":
    main()

