"""
Quick script to find LEI from the Lenders_and_LEI_Numbers.csv file.
Faster than querying BigQuery!
"""

import pandas as pd
import os
import sys

def find_lei_in_file(bank_name: str, csv_path: str = None):
    """
    Find LEI for a bank from the crosswalk file.
    
    Args:
        bank_name: Bank name to search for
        csv_path: Path to Lenders_and_LEI_Numbers.csv (auto-detected if None)
    """
    if csv_path is None:
        # Try to find the file
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "reference", "Lenders_and_LEI_Numbers.csv"),
            "data/reference/Lenders_and_LEI_Numbers.csv",
            "../data/reference/Lenders_and_LEI_Numbers.csv",
            "Lenders_and_LEI_Numbers.csv"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                csv_path = path
                break
        
        if csv_path is None or not os.path.exists(csv_path):
            print(f"ERROR: Could not find Lenders_and_LEI_Numbers.csv")
            print(f"Tried: {possible_paths}")
            return None
    
    # Load the file
    df = pd.read_csv(csv_path)
    
    # Search for bank name
    mask = df['Respondent Name'].str.contains(bank_name, case=False, na=False)
    results = df[mask].copy()
    
    if len(results) == 0:
        print(f"\nNo matches found for '{bank_name}'")
        return None
    
    print(f"\n{'='*80}")
    print(f"Found {len(results)} match(es) for '{bank_name}':")
    print(f"{'='*80}\n")
    
    for idx, row in results.iterrows():
        print(f"LEI: {row['Lei']}")
        print(f"Name: {row['Respondent Name']}")
        if 'Assets' in row and pd.notna(row['Assets']) and row['Assets'] > 0:
            print(f"Assets: ${row['Assets']:,.0f}")
        print()
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Find bank LEI from crosswalk file")
    parser.add_argument("bank_name", help="Bank name to search for")
    
    args = parser.parse_args()
    
    find_lei_in_file(args.bank_name)

