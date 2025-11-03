"""Check the baseline calculation to see why the trend might be wrong"""

import pandas as pd
from pathlib import Path
from datetime import datetime

reports_dir = Path(r"C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis\Weekly BankFind Branch Changes Reports")

print("="*80)
print("CHECKING BASELINE CALCULATION")
print("="*80)

# Load baseline
baseline_file = reports_dir / "BASELINE_branch_changes.csv"
df_baseline = pd.read_csv(baseline_file)

print(f"\nBaseline total records: {len(df_baseline)}")

# Count closings and openings
if 'CHANGECODE' in df_baseline.columns:
    df_baseline['CHANGECODE'] = df_baseline['CHANGECODE'].astype(str)
    baseline_closings = len(df_baseline[df_baseline['CHANGECODE'] == '711'])
    baseline_openings = len(df_baseline[df_baseline['CHANGECODE'] == '721'])
    
    print(f"Baseline closings (711): {baseline_closings}")
    print(f"Baseline openings (721): {baseline_openings}")
    
    # Check PROCDATE range
    if 'PROCDATE' in df_baseline.columns:
        df_baseline['PROCDATE'] = pd.to_datetime(df_baseline['PROCDATE'], errors='coerce')
        valid_dates = df_baseline['PROCDATE'].dropna()
        
        if len(valid_dates) > 0:
            min_date = valid_dates.min()
            max_date = valid_dates.max()
            days_span = (max_date - min_date).days
            baseline_weeks = max(1, days_span / 7.0)
            
            print(f"\nBaseline PROCDATE range:")
            print(f"  Min: {min_date.date()}")
            print(f"  Max: {max_date.date()}")
            print(f"  Days span: {days_span}")
            print(f"  Calculated weeks: {baseline_weeks:.2f}")
            
            avg_weekly_closings = baseline_closings / baseline_weeks
            avg_weekly_openings = baseline_openings / baseline_weeks
            
            print(f"\nBaseline averages:")
            print(f"  Avg weekly closings: {avg_weekly_closings:.2f}")
            print(f"  Avg weekly openings: {avg_weekly_openings:.2f}")
            
            # Current week
            current_closings = 18
            current_openings = 15
            
            print(f"\nCurrent week (Oct 19-25, 2025):")
            print(f"  Closings: {current_closings}")
            print(f"  Openings: {current_openings}")
            
            print(f"\nComparison:")
            print(f"  Closings: {current_closings} vs {avg_weekly_closings:.2f} average")
            print(f"  Difference: {current_closings - avg_weekly_closings:+.2f}")
            print(f"  % Change: {((current_closings - avg_weekly_closings) / avg_weekly_closings * 100) if avg_weekly_closings > 0 else 0:+.1f}%")
            
            # Check if the baseline includes all events or just branch changes
            print(f"\nAll CHANGECODE values in baseline:")
            print(df_baseline['CHANGECODE'].value_counts().head(20))
            
            # Check if we should only count certain date ranges
            print(f"\nBaseline by year (PROCYEAR):")
            if 'PROCYEAR' in df_baseline.columns:
                print(df_baseline['PROCYEAR'].value_counts().sort_index())



