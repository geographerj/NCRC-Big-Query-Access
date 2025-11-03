"""
Test Script: Fifth Third Bank Analysis

This script tests the new utilities by analyzing Fifth Third Bank's lending:
1. Identifies top 10 CBSAs by application volume per year
2. Tests race/ethnicity classification
3. Tests crosswalk merging (CBSA names, lender names)
4. Tests racial share calculations using NCRC methodology
5. Tests HMDA code filtering
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.bigquery_client import create_client
from utils.hmda_crosswalks import merge_hmda_with_crosswalks
from utils.hmda_demographics import apply_demographic_classification, calculate_shares_all_races
from utils.hmda_codes import ORIGINATIONS, HOME_PURCHASE, ALL_RESIDENTIAL, create_filter_where_clause
from queries.hmda_queries import HMDA_TABLE
import pandas as pd

# Fifth Third Bank LEI
FIFTH_THIRD_LEI = 'QFROUN1UWUYU0DVIWD51'

def get_top_cbsas_by_applications(year: int, limit: int = 10):
    """
    Get top CBSAs for Fifth Third Bank by application volume in a given year.
    
    Args:
        year: Year to analyze
        limit: Number of top CBSAs to return
    
    Returns:
        DataFrame with top CBSAs and application counts
    """
    # Use key file from parent directory
    key_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "hdma1-242116-74024e2eb88f.json")
    key_path = os.path.abspath(key_path)
    client = create_client(key_path=key_path)
    
    query = f"""
    SELECT 
        msamd as cbsa_code,
        COUNT(*) as total_applications,
        COUNTIF(action_taken = '1') as originations,
        SUM(CASE WHEN action_taken = '1' THEN loan_amount END) as total_loan_amount
    FROM `{HMDA_TABLE}`
    WHERE activity_year = '{year}'
      AND lei = '{FIFTH_THIRD_LEI}'
      AND msamd IS NOT NULL
      AND msamd != ''
    GROUP BY msamd
    ORDER BY total_applications DESC
    LIMIT {limit}
    """
    
    print(f"\n{'='*80}")
    print(f"Getting top {limit} CBSAs for Fifth Third Bank in {year}")
    print(f"{'='*80}")
    
    df = client.execute_query(query)
    
    # Add CBSA names using crosswalk
    from utils.hmda_crosswalks import load_cbsa_to_county_crosswalk
    cbsa_crosswalk = load_cbsa_to_county_crosswalk()
    cbsa_names = cbsa_crosswalk[['Cbsa Code', 'Cbsa']].drop_duplicates()
    df = df.merge(cbsa_names, left_on='cbsa_code', right_on='Cbsa Code', how='left')
    df = df.drop(columns=['Cbsa Code'])
    df = df.rename(columns={'Cbsa': 'cbsa_name'})
    
    print(f"\nTop {limit} CBSAs by Application Volume:")
    print("-" * 80)
    for idx, row in df.iterrows():
        print(f"{idx+1}. {row['cbsa_name']} ({row['cbsa_code']})")
        print(f"   Applications: {row['total_applications']:,} | Originations: {row['originations']:,}")
    
    return df


def test_race_ethnicity_classification(year: int, cbsa_code: str):
    """
    Test the race/ethnicity classification on a sample of Fifth Third Bank loans.
    
    Args:
        year: Year to analyze
        cbsa_code: CBSA code to filter
    """
    # Use key file from parent directory
    key_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "hdma1-242116-74024e2eb88f.json")
    key_path = os.path.abspath(key_path)
    client = create_client(key_path=key_path)
    
    # Get a sample of originations
    query = f"""
    SELECT 
        lei,
        activity_year,
        cbsa_code,
        census_tract,
        loan_amount,
        action_taken,
        loan_purpose,
        applicant_ethnicity_1,
        applicant_ethnicity_2,
        applicant_ethnicity_3,
        applicant_ethnicity_4,
        applicant_ethnicity_5,
        applicant_race_1,
        applicant_race_2,
        applicant_race_3,
        applicant_race_4,
        applicant_race_5
    FROM `{HMDA_TABLE}`
    WHERE activity_year = {year}
      AND lei = '{FIFTH_THIRD_LEI}'
      AND cbsa_code = '{cbsa_code}'
      AND action_taken = '1'
    LIMIT 1000
    """
    
    print(f"\n{'='*80}")
    print(f"Testing Race/Ethnicity Classification")
    print(f"{'='*80}")
    
    df = client.execute_query(query)
    print(f"\nLoaded {len(df):,} originations")
    
    # Apply demographic classification
    print("\nApplying NCRC demographic classification...")
    df_classified = apply_demographic_classification(df, applicant_prefix='applicant')
    
    print("\nClassification Results:")
    print("-" * 80)
    race_counts = df_classified['applicant_race_category'].value_counts()
    for race, count in race_counts.items():
        pct = (count / len(df_classified)) * 100
        print(f"  {race}: {count:,} ({pct:.1f}%)")
    
    rollup_counts = df_classified['applicant_rollup_category'].value_counts()
    print("\nRollup Categories:")
    for category, count in rollup_counts.items():
        pct = (count / len(df_classified)) * 100
        print(f"  {category}: {count:,} ({pct:.1f}%)")
    
    return df_classified


def test_racial_shares(year: int, cbsa_code: str):
    """
    Test racial share calculations using both methodologies.
    
    Args:
        year: Year to analyze
        cbsa_code: CBSA code to filter
    """
    client = create_client()
    
    # Get originations with counts by race category
    query = f"""
    SELECT 
        COUNT(*) as total_originations
    FROM `{HMDA_TABLE}`
    WHERE activity_year = {year}
      AND lei = '{FIFTH_THIRD_LEI}'
      AND cbsa_code = '{cbsa_code}'
      AND action_taken = '1'
    """
    
    # First, get the raw data
    query_detail = f"""
    SELECT 
        applicant_ethnicity_1,
        applicant_ethnicity_2,
        applicant_ethnicity_3,
        applicant_ethnicity_4,
        applicant_ethnicity_5,
        applicant_race_1,
        applicant_race_2,
        applicant_race_3,
        applicant_race_4,
        applicant_race_5
    FROM `{HMDA_TABLE}`
    WHERE activity_year = {year}
      AND lei = '{FIFTH_THIRD_LEI}'
      AND cbsa_code = '{cbsa_code}'
      AND action_taken = '1'
    """
    
    print(f"\n{'='*80}")
    print(f"Testing Racial Share Calculations")
    print(f"{'='*80}")
    
    df = client.execute_query(query_detail)
    print(f"\nLoaded {len(df):,} originations")
    
    # Apply classification
    df_classified = apply_demographic_classification(df, applicant_prefix='applicant')
    
    # Prepare data for share calculation
    df_shares = df_classified.groupby('applicant_race_category').size().reset_index(name='total_originations')
    
    print("\nCalculating shares using NCRC methodology (excluding missing)...")
    shares_ncrc = calculate_shares_all_races(
        df_shares,
        total_column='total_originations',
        race_column='applicant_race_category',
        include_missing_in_denominator=False  # NCRC method
    )
    
    print("\nRacial Shares (NCRC Method - Excluding Missing):")
    print("-" * 80)
    for _, row in shares_ncrc.iterrows():
        print(f"  {row['race_category']}: {row['share_percent']:.2f}% ({row['loan_count']:,} loans)")
    
    return shares_ncrc


def test_crosswalk_merging(year: int, cbsa_code: str):
    """
    Test merging HMDA data with crosswalks.
    
    Args:
        year: Year to analyze
        cbsa_code: CBSA code to filter
    """
    # Use key file from parent directory
    key_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "hdma1-242116-74024e2eb88f.json")
    key_path = os.path.abspath(key_path)
    client = create_client(key_path=key_path)
    
    query = f"""
    SELECT 
        lei,
        activity_year,
        cbsa_code,
        census_tract,
        loan_amount,
        action_taken,
        loan_purpose
    FROM `{HMDA_TABLE}`
    WHERE activity_year = {year}
      AND lei = '{FIFTH_THIRD_LEI}'
      AND cbsa_code = '{cbsa_code}'
      AND action_taken = '1'
    LIMIT 100
    """
    
    print(f"\n{'='*80}")
    print(f"Testing Crosswalk Merging")
    print(f"{'='*80}")
    
    df = client.execute_query(query)
    print(f"\nLoaded {len(df):,} originations")
    print(f"Columns before merge: {list(df.columns)}")
    
    # Merge with crosswalks
    df_merged = merge_hmda_with_crosswalks(df, merge_cbsa=True, merge_lender_names=True)
    
    print(f"\nColumns after merge: {list(df_merged.columns)}")
    print(f"\nSample merged data:")
    print("-" * 80)
    if 'cbsa_name' in df_merged.columns:
        print(f"CBSA Name: {df_merged['cbsa_name'].iloc[0]}")
    if 'respondent_name' in df_merged.columns:
        print(f"Lender Name: {df_merged['respondent_name'].iloc[0]}")
    
    return df_merged


def main():
    """Run all tests for Fifth Third Bank"""
    
    print("\n" + "="*80)
    print("FIFTH THIRD BANK ANALYSIS - Testing New Utilities")
    print("="*80)
    
    # Use 2024 as test year
    test_year = 2024
    
    # Step 1: Get top CBSAs
    top_cbsas = get_top_cbsas_by_applications(test_year, limit=10)
    
    if len(top_cbsas) == 0:
        print("\n⚠ No data found for Fifth Third Bank. Check LEI and year.")
        return
    
    # Step 2: Test on first CBSA
    test_cbsa = top_cbsas.iloc[0]
    test_cbsa_code = test_cbsa['cbsa_code']
    test_cbsa_name = test_cbsa.get('cbsa_name', test_cbsa_code)
    
    print(f"\n{'='*80}")
    print(f"Testing on: {test_cbsa_name} ({test_cbsa_code})")
    print(f"{'='*80}")
    
    # Step 3: Test crosswalk merging
    df_merged = test_crosswalk_merging(test_year, test_cbsa_code)
    
    # Step 4: Test race/ethnicity classification
    df_classified = test_race_ethnicity_classification(test_year, test_cbsa_code)
    
    # Step 5: Test racial share calculations
    shares = test_racial_shares(test_year, test_cbsa_code)
    
    # Step 6: Save results
    output_dir = "Lending and Branch Analysis/data"
    os.makedirs(output_dir, exist_ok=True)
    
    df_merged.to_csv(f"{output_dir}/fifth_third_test_merged.csv", index=False)
    df_classified.to_csv(f"{output_dir}/fifth_third_test_classified.csv", index=False)
    shares.to_csv(f"{output_dir}/fifth_third_test_shares.csv", index=False)
    top_cbsas.to_csv(f"{output_dir}/fifth_third_top_cbsas.csv", index=False)
    
    print(f"\n{'='*80}")
    print("✓ All tests completed!")
    print(f"✓ Results saved to: {output_dir}/")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()

