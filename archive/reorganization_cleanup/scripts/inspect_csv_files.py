"""Inspect CSV files to understand the data structure"""

import pandas as pd
from pathlib import Path
from datetime import datetime

reports_dir = Path(r"C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis\Weekly BankFind Branch Changes Reports")

print("="*80)
print("INSPECTING CSV FILES")
print("="*80)

# Check closings file
closings_file = reports_dir / "Branch_Office_Closings_10_31_2025 (1).csv"
print(f"\n1. CLOSINGS FILE: {closings_file.name}")
if closings_file.exists():
    df_closings = pd.read_csv(closings_file)
    print(f"   Total records: {len(df_closings)}")
    if 'CHANGECODE' in df_closings.columns:
        print(f"   CHANGECODE values: {df_closings['CHANGECODE'].unique()}")
        print(f"   CHANGECODE counts:\n{df_closings['CHANGECODE'].value_counts()}")
    if 'PROCDATE' in df_closings.columns:
        df_closings['PROCDATE'] = pd.to_datetime(df_closings['PROCDATE'], errors='coerce')
        print(f"   PROCDATE range: {df_closings['PROCDATE'].min()} to {df_closings['PROCDATE'].max()}")
        mask = (df_closings['PROCDATE'] >= datetime(2025,10,19)) & (df_closings['PROCDATE'] <= datetime(2025,10,25))
        print(f"   Records with PROCDATE Oct 19-25: {mask.sum()}")
    if 'EFFDATE' in df_closings.columns:
        df_closings['EFFDATE'] = pd.to_datetime(df_closings['EFFDATE'], errors='coerce')
        print(f"   EFFDATE range: {df_closings['EFFDATE'].min()} to {df_closings['EFFDATE'].max()}")

# Check openings file
openings_file = reports_dir / "Branch_Office_Openings_10_31_2025.csv"
print(f"\n2. OPENINGS FILE: {openings_file.name}")
if openings_file.exists():
    df_openings = pd.read_csv(openings_file)
    print(f"   Total records: {len(df_openings)}")
    if 'CHANGECODE' in df_openings.columns:
        print(f"   CHANGECODE values: {df_openings['CHANGECODE'].unique()}")
        print(f"   CHANGECODE counts:\n{df_openings['CHANGECODE'].value_counts()}")
    if 'PROCDATE' in df_openings.columns:
        df_openings['PROCDATE'] = pd.to_datetime(df_openings['PROCDATE'], errors='coerce')
        print(f"   PROCDATE range: {df_openings['PROCDATE'].min()} to {df_openings['PROCDATE'].max()}")
        mask = (df_openings['PROCDATE'] >= datetime(2025,10,19)) & (df_openings['PROCDATE'] <= datetime(2025,10,25))
        print(f"   Records with PROCDATE Oct 19-25: {mask.sum()}")
    if 'EFFDATE' in df_openings.columns:
        df_openings['EFFDATE'] = pd.to_datetime(df_openings['EFFDATE'], errors='coerce')
        print(f"   EFFDATE range: {df_openings['EFFDATE'].min()} to {df_openings['EFFDATE'].max()}")

# Check if they're the same
print("\n3. COMPARISON:")
if closings_file.exists() and openings_file.exists():
    print(f"   Same number of records? {len(df_closings) == len(df_openings)}")
    if len(df_closings) == len(df_openings):
        # Check if they're identical
        if 'INSTNAME' in df_closings.columns and 'INSTNAME' in df_openings.columns:
            print(f"   First 5 bank names in closings: {df_closings['INSTNAME'].head(5).tolist()}")
            print(f"   First 5 bank names in openings: {df_openings['INSTNAME'].head(5).tolist()}")

