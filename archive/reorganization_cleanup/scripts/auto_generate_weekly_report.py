"""Automatically find newest CSV files and generate weekly report"""

from pathlib import Path
from datetime import datetime, timedelta
import sys

sys.path.insert(0, str(Path(__file__).parent))

from generate_weekly_branch_report import combine_csvs_for_week, filter_by_date_range
from fdic_branch_changes_report import create_excel_report, load_baseline_data

def find_newest_csv_files(reports_dir):
    """Find the newest closings and openings CSV files (excluding baseline)"""
    
    # Get all CSV files except baseline
    csv_files = [f for f in reports_dir.glob("*.csv") 
                 if f.name != "BASELINE_branch_changes.csv"]
    
    # Find closings files
    closings_files = [f for f in csv_files if "closing" in f.name.lower()]
    openings_files = [f for f in csv_files if "opening" in f.name.lower()]
    
    # Sort by modification time, get newest
    if closings_files:
        closings_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        newest_closings = closings_files[0]
    else:
        newest_closings = None
    
    if openings_files:
        openings_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        newest_openings = openings_files[0]
    else:
        newest_openings = None
    
    return newest_closings, newest_openings

def main():
    reports_dir = Path(r"C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis\Weekly BankFind Branch Changes Reports")
    
    # Calculate last week (Sunday to Saturday)
    today = datetime.now()
    days_since_saturday = (today.weekday() + 2) % 7
    if days_since_saturday == 0:
        days_since_saturday = 7
    last_saturday = today - timedelta(days=days_since_saturday)
    end_date = last_saturday
    start_date = last_saturday - timedelta(days=6)  # Previous Sunday
    
    print("="*80)
    print("AUTO-GENERATING WEEKLY FDIC BRANCH CHANGES REPORT")
    print("="*80)
    print(f"\nReport Period: {start_date.date()} to {end_date.date()}")
    
    # Find newest CSV files
    print("\nSearching for newest CSV files...")
    closings_file, openings_file = find_newest_csv_files(reports_dir)
    
    if not closings_file or not openings_file:
        print("\nERROR: Could not find closings and/or openings CSV files")
        print(f"\nFiles in directory:")
        for f in sorted(reports_dir.glob("*.csv")):
            print(f"  • {f.name}")
        return
    
    print(f"  Using closings file: {closings_file.name}")
    print(f"  Using openings file: {openings_file.name}")
    
    # Load baseline
    baseline_data = load_baseline_data()
    if baseline_data is None or len(baseline_data) == 0:
        print("\nWARNING: No baseline data available")
    else:
        print(f"\nLoaded baseline: {len(baseline_data)} records")
    
    # Combine CSV files
    df_week = combine_csvs_for_week(closings_file, openings_file)
    
    if len(df_week) == 0:
        print("\nERROR: No data loaded from CSV files")
        return
    
    # Filter by date range
    print(f"\nFiltering data for report week...")
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
    print(f"  • {len(df_week)} records for the report week ({start_date.date()} to {end_date.date()})")
    if baseline_data is not None:
        print(f"  • {len(baseline_data)} baseline records for trend analysis")

if __name__ == "__main__":
    main()

