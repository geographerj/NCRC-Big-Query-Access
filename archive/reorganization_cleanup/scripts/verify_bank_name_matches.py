"""
Bank Name Matching Verification Tool

This script helps match bank names between HMDA and SOD datasets.
Since there's no reliable join column, we must match by name with manual verification.

Usage:
    python verify_bank_name_matches.py
    
    This will:
    1. Get unique bank names from your HMDA data
    2. Get unique bank names from SOD data
    3. Find potential matches
    4. Create an Excel file for you to verify matches
    5. Save verified matches to a crosswalk file
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Handle spaces in module path
import importlib.util
spec = importlib.util.spec_from_file_location(
    "bigquery_client",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "Lending and Branch Analysis", "utils", "bigquery_client.py")
)
bigquery_client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bigquery_client)

spec2 = importlib.util.spec_from_file_location(
    "branch_matching",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "Lending and Branch Analysis", "utils", "branch_matching.py")
)
branch_matching = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(branch_matching)

spec3 = importlib.util.spec_from_file_location(
    "branch_queries",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "Lending and Branch Analysis", "queries", "branch_queries.py")
)
branch_queries = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(branch_queries)

# Use the modules
create_client = bigquery_client.create_client
find_potential_matches = branch_matching.find_potential_matches
create_verification_worksheet = branch_matching.create_verification_worksheet


def get_hmda_bank_names(year: int = 2024, top_n: int = 100) -> pd.DataFrame:
    """
    Get unique bank names from HMDA data.
    
    Args:
        year: Year to query
        top_n: Number of top lenders by volume to include
        
    Returns:
        DataFrame with bank names from HMDA
    """
    print(f"\n{'='*80}")
    print("Getting bank names from HMDA data...")
    print(f"{'='*80}")
    
    client = create_client()
    
    query = f"""
    SELECT DISTINCT
        respondent_name,
        lei,
        COUNT(*) as loan_count,
        COUNTIF(action_taken = '1') as originations
    FROM `hdma1-242116.hmda.hmda`
    WHERE activity_year = {year}
      AND respondent_name IS NOT NULL
      AND respondent_name != ''
    GROUP BY respondent_name, lei
    ORDER BY originations DESC
    LIMIT {top_n}
    """
    
    df = client.execute_query(query)
    
    print(f"Found {len(df)} unique banks in HMDA for {year}")
    print(f"Top 5 by originations:")
    for idx, row in df.head().iterrows():
        print(f"  {row['respondent_name']} ({row['originations']:,} originations)")
    
    return df


def get_sod_bank_names(year: int = 2024, sod_table: str = 'sod') -> pd.DataFrame:
    """
    Get unique bank names from SOD data.
    
    Args:
        year: Year to query
        sod_table: Which SOD table ('sod', 'sod25', 'sod_legacy')
        
    Returns:
        DataFrame with bank names from SOD
    """
    print(f"\n{'='*80}")
    print(f"Getting bank names from SOD data ({sod_table})...")
    print(f"{'='*80}")
    
    client = create_client()
    
    table_map = {
        'sod': 'hdma1-242116.branches.sod',
        'sod25': 'hdma1-242116.branches.sod25',
        'sod_legacy': 'hdma1-242116.branches.sod_legacy'
    }
    
    table = table_map.get(sod_table.lower(), 'hdma1-242116.branches.sod')
    
    query = f"""
    SELECT DISTINCT
        institution_name,
        COUNT(DISTINCT uninumbr) as branch_count,
        SUM(deposits) as total_deposits
    FROM `{table}`
    WHERE year = {year}
      AND institution_name IS NOT NULL
      AND institution_name != ''
    GROUP BY institution_name
    ORDER BY branch_count DESC
    """
    
    df = client.execute_query(query)
    
    print(f"Found {len(df)} unique banks in SOD for {year}")
    print(f"Top 5 by branch count:")
    for idx, row in df.head().iterrows():
        print(f"  {row['institution_name']} ({row['branch_count']:,} branches)")
    
    return df


def main():
    """Main workflow for bank name matching"""
    
    print("\n" + "="*80)
    print("BANK NAME MATCHING VERIFICATION TOOL")
    print("="*80)
    print("\nThis tool helps you match bank names between HMDA and SOD datasets.")
    print("Since names differ (e.g., 'Wells Fargo' vs 'Wells Fargo Bank'),")
    print("you'll need to verify matches manually.\n")
    
    # Configuration
    year = 2024  # Year to analyze
    top_n_hmda = 50  # Top N lenders from HMDA to match
    
    print(f"Configuration:")
    print(f"  Year: {year}")
    print(f"  Top {top_n_hmda} lenders from HMDA")
    
    # Ask user which SOD table to use
    print("\nWhich SOD table do you want to use?")
    print("  1. sod (default)")
    print("  2. sod25")
    print("  3. sod_legacy")
    choice = input("Enter choice (1-3) [1]: ").strip() or "1"
    
    sod_table_map = {'1': 'sod', '2': 'sod25', '3': 'sod_legacy'}
    sod_table = sod_table_map.get(choice, 'sod')
    
    print(f"\nUsing SOD table: {sod_table}\n")
    
    # Get data
    hmda_df = get_hmda_bank_names(year=year, top_n=top_n_hmda)
    sod_df = get_sod_bank_names(year=year, sod_table=sod_table)
    
    # Find potential matches
    print(f"\n{'='*80}")
    print("Finding potential matches...")
    print(f"{'='*80}")
    
    hmda_names = hmda_df['respondent_name'].unique().tolist()
    sod_names = sod_df['institution_name'].unique().tolist()
    
    matches_df = find_potential_matches(
        hmda_names=hmda_names,
        sod_names=sod_names,
        threshold=0.7  # 70% similarity minimum
    )
    
    print(f"\nFound {len(matches_df)} potential matches")
    print(f"\nTop matches by similarity:")
    for idx, row in matches_df.head(10).iterrows():
        print(f"  {row['similarity']:.2%} - '{row['hmda_name']}' <-> '{row['sod_name']}'")
    
    # Create verification worksheet
    output_dir = Path("data/reference")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    verification_file = output_dir / f"bank_name_matches_to_verify_{year}.xlsx"
    
    print(f"\n{'='*80}")
    print(f"Creating verification worksheet...")
    print(f"{'='*80}")
    
    create_verification_worksheet(matches_df, str(verification_file))
    
    print(f"\n{'='*80}")
    print("NEXT STEPS:")
    print(f"{'='*80}")
    print(f"1. Open the file: {verification_file}")
    print(f"2. Review each potential match")
    print(f"3. Mark 'is_match' column with Y/Yes/True/1 if the names refer to the same bank")
    print(f"4. Mark with N/No/False/0 if they're different banks")
    print(f"5. Save the file")
    print(f"6. Run this script again to save verified matches to crosswalk file")
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()

