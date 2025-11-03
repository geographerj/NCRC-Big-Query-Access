"""
Validate Worst Lenders Redlining Data v2
Checks data quality, year coverage, and 2022-2024 qualification thresholds
"""

import pandas as pd
import sys

def validate_data(input_file):
    """Validate the v2 query output data"""
    print("="*80)
    print("WORST LENDERS DATA VALIDATION v2")
    print("="*80)
    
    # Load data
    print(f"\nLoading data from: {input_file}")
    df = pd.read_csv(input_file, dtype={'county_code': str, 'cbsa_code': str})
    df['activity_year'] = df['activity_year'].astype(int)
    
    print(f"\nBasic Statistics:")
    print(f"  Total rows: {len(df):,}")
    print(f"  Unique banks: {df['lender_name'].nunique()}")
    print(f"  Unique CBSAs: {df['cbsa_code'].nunique()}")
    print(f"  Unique counties: {df['county_code'].nunique()}")
    
    # Check year coverage
    print(f"\nYear Coverage:")
    years_present = sorted(df['activity_year'].unique())
    print(f"  Years present: {years_present}")
    expected_years = list(range(2018, 2025))
    missing_years = [y for y in expected_years if y not in years_present]
    if missing_years:
        print(f"  WARNING: Missing years: {missing_years}")
    else:
        print(f"  OK: All years 2018-2024 present")
    
    # Check 2022-2024 data
    print(f"\n2022-2024 Data (Scoring Period):")
    scoring_data = df[df['activity_year'].isin([2022, 2023, 2024])].copy()
    print(f"  Rows in 2022-2024: {len(scoring_data):,}")
    print(f"  Banks with data in 2022-2024: {scoring_data['lender_name'].nunique()}")
    
    # Check for banks with ≥500 applications in 2022-2024 (qualification threshold)
    print(f"\nBank Qualification Check (>=500 apps in CBSA, 2022-2024):")
    
    # Filter to scoring years and count applications by bank/CBSA
    scoring_applications = scoring_data[
        scoring_data['kind'] == 'Application'
    ].copy()
    
    bank_cbsa_counts = scoring_applications.groupby(['lender_name', 'cbsa_code']).agg({
        'subject_total_count': 'sum'
    }).reset_index()
    
    qualified_combos = bank_cbsa_counts[bank_cbsa_counts['subject_total_count'] >= 500]
    
    print(f"  Bank-CBSA combinations with >=500 apps in 2022-2024: {len(qualified_combos)}")
    print(f"  Unique banks meeting threshold: {qualified_combos['lender_name'].nunique()}")
    print(f"  Unique CBSAs with qualified banks: {qualified_combos['cbsa_code'].nunique()}")
    
    # Show banks with low counts (potential issues)
    low_counts = bank_cbsa_counts[bank_cbsa_counts['subject_total_count'] < 500]
    if len(low_counts) > 0:
        print(f"\n  WARNING: Bank-CBSA combinations below threshold:")
        print(f"     (These should not appear in output if qualification worked correctly)")
        print(f"     Total below-threshold combos: {len(low_counts)}")
        print(f"     Sample (first 10):")
        for idx, row in low_counts.head(10).iterrows():
            print(f"       {row['lender_name']} in CBSA {row['cbsa_code']}: {row['subject_total_count']:.0f} apps")
    
    # Check data completeness
    print(f"\nData Completeness:")
    
    # Check for missing peer data (should have some, but not necessarily all)
    rows_with_peer_data = df[df['peer_total_count'] > 0]
    rows_without_peer_data = df[df['peer_total_count'] == 0]
    
    print(f"  Rows with peer data: {len(rows_with_peer_data):,} ({len(rows_with_peer_data)/len(df)*100:.1f}%)")
    print(f"  Rows without peer data: {len(rows_without_peer_data):,} ({len(rows_without_peer_data)/len(df)*100:.1f}%)")
    
    # Check by year
    print(f"\n  Peer data by year:")
    for year in sorted(df['activity_year'].unique()):
        year_data = df[df['activity_year'] == year]
        with_peers = len(year_data[year_data['peer_total_count'] > 0])
        print(f"    {year}: {with_peers:,}/{len(year_data):,} rows have peer data ({with_peers/len(year_data)*100:.1f}%)")
    
    # Check metric columns
    print(f"\nMetric Columns Check:")
    expected_metric_cols = [
        'subject_mmct_50', 'subject_mmct_80',
        'peer_mmct_50', 'peer_mmct_80',
        'subject_black_tract_50', 'subject_black_tract_80',
        'peer_black_tract_50', 'peer_black_tract_80',
        'subject_hispanic_tract_50', 'subject_hispanic_tract_80',
        'peer_hispanic_tract_50', 'peer_hispanic_tract_80',
        'subject_black_hispanic_tract_50', 'subject_black_hispanic_tract_80',
        'peer_black_hispanic_tract_50', 'peer_black_hispanic_tract_80'
    ]
    
    missing_cols = [col for col in expected_metric_cols if col not in df.columns]
    if missing_cols:
        print(f"  WARNING: Missing columns: {missing_cols}")
    else:
        print(f"  OK: All expected metric columns present")
    
    # Check for null values in key columns
    print(f"\nNull Value Check:")
    key_cols = ['lender_name', 'cbsa_code', 'activity_year', 'subject_total_count']
    for col in key_cols:
        null_count = df[col].isna().sum()
        if null_count > 0:
            print(f"  WARNING: {col}: {null_count:,} null values")
        else:
            print(f"  OK: {col}: No null values")
    
    # Sample data quality checks
    print(f"\nData Quality Checks:")
    
    # Check for negative counts (only numeric columns)
    count_cols = [col for col in df.columns if 'count' in col.lower() and df[col].dtype in ['int64', 'float64']]
    negative_counts = False
    for col in count_cols:
        if (df[col] < 0).any():
            print(f"  WARNING: {col}: Has negative values")
            negative_counts = True
    if not negative_counts:
        print(f"  OK: No negative counts found")
    
    # Check year distribution
    print(f"\nYear Distribution:")
    year_counts = df.groupby('activity_year').size()
    for year in sorted(year_counts.index):
        print(f"  {year}: {year_counts[year]:,} rows")
    
    # Check bank distribution in 2022-2024
    print(f"\nTop Banks by 2022-2024 Applications:")
    scoring_apps_by_bank = scoring_applications.groupby('lender_name')['subject_total_count'].sum().sort_values(ascending=False)
    for bank, count in scoring_apps_by_bank.head(10).items():
        print(f"  {bank}: {count:,.0f} applications")
    
    # Summary
    print(f"\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    issues = []
    if missing_years:
        issues.append(f"Missing years: {missing_years}")
    if len(qualified_combos) == 0:
        issues.append("No banks meet >=500 apps threshold in 2022-2024")
    if missing_cols:
        issues.append(f"Missing columns: {missing_cols}")
    
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("OK: Data validation passed!")
        print(f"\n  - All years 2018-2024 present")
        print(f"  - {qualified_combos['lender_name'].nunique()} banks qualify for analysis")
        print(f"  - Data structure looks correct")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    input_file = r"C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis\data\raw\bq-results-20251101-204726-1762030073826.csv"
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    
    try:
        validate_data(input_file)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

