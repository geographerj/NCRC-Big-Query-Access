"""
Quick script to find a bank's LEI from HMDA data.
"""

import sys
import os
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Handle module imports with spaces in path
import importlib.util

def load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

bigquery_client = load_module(
    "bigquery_client",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "Lending and Branch Analysis", "utils", "bigquery_client.py")
)

create_client = bigquery_client.create_client


def find_bank_lei(bank_name: str, year: int = 2024):
    """
    Find LEI and other identifiers for a bank.
    
    Args:
        bank_name: Name to search for (partial match)
        year: Year to search
    """
    # Try to find credentials in the config folder
    creds_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "config", "credentials", "hdma1-242116-74024e2eb88f.json"
    )
    
    if os.path.exists(creds_path):
        client = create_client(key_path=creds_path)
    else:
        client = create_client()
    
    query = f"""
    SELECT DISTINCT
        lei,
        respondent_name,
        COUNTIF(action_taken = '1') as originations,
        SUM(CASE WHEN action_taken = '1' THEN loan_amount END) as total_loan_amount,
        COUNT(DISTINCT cbsa_code) as cbsas_served
    FROM `hdma1-242116.hmda.hmda`
    WHERE activity_year = {year}
      AND UPPER(respondent_name) LIKE UPPER('%{bank_name}%')
    GROUP BY lei, respondent_name
    ORDER BY originations DESC
    LIMIT 20
    """
    
    df = client.execute_query(query)
    
    print(f"\n{'='*80}")
    print(f"Search Results for: '{bank_name}'")
    print(f"{'='*80}\n")
    
    if len(df) == 0:
        print("No results found. Try a different search term.")
        return None
    
    for idx, row in df.iterrows():
        print(f"Option {idx + 1}:")
        print(f"  LEI: {row['lei']}")
        print(f"  Name: {row['respondent_name']}")
        print(f"  Originations ({year}): {row['originations']:,}")
        print(f"  Loan Volume: ${row['total_loan_amount']:,.0f}")
        print(f"  CBSAs Served: {row['cbsas_served']}")
        print()
    
    return df


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Find bank LEI from HMDA data")
    parser.add_argument("bank_name", help="Bank name to search for")
    parser.add_argument("--year", type=int, default=2024, help="Year to search (default: 2024)")
    
    args = parser.parse_args()
    
    find_bank_lei(args.bank_name, args.year)
    
    print("\nUsage in merger analysis:")
    print(f"  bank_lei = 'LEI_FROM_ABOVE'")
    print(f"  bank_sod_name = 'Verify SOD name manually!'")

