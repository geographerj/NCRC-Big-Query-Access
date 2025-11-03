"""
Show potential SOD name matches for Fifth Third and Comerica.
User will confirm which names are correct matches.
"""

import sys
import os
import pandas as pd

# Handle module imports with spaces in path
import importlib.util

def load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

bigquery_client = load_module(
    "bigquery_client",
    os.path.join(base_dir, "Lending and Branch Analysis", "utils", "bigquery_client.py")
)
branch_matching = load_module(
    "branch_matching",
    os.path.join(base_dir, "Lending and Branch Analysis", "utils", "branch_matching.py")
)

create_client = bigquery_client.create_client
fuzzy_match_ratio = branch_matching.fuzzy_match_ratio

# Credentials path
creds_path = os.path.join(base_dir, "config", "credentials", "hdma1-242116-74024e2eb88f.json")


def get_sod_names_for_bank(hmda_name: str, year: int = 2024, sod_table: str = 'sod25'):
    """
    Get SOD institution names that might match an HMDA bank name.
    """
    if os.path.exists(creds_path):
        client = create_client(key_path=creds_path)
    else:
        client = create_client()
    
    # Query SOD for names similar to HMDA name
    table_map = {
        'sod': 'hdma1-242116.branches.sod',
        'sod25': 'hdma1-242116.branches.sod25',
        'sod_legacy': 'hdma1-242116.branches.sod_legacy'
    }
    
    table = table_map.get(sod_table.lower(), 'hdma1-242116.branches.sod25')
    
    # Get all unique institution names from SOD
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
    
    # Calculate similarity scores
    df['similarity'] = df['institution_name'].apply(
        lambda x: fuzzy_match_ratio(hmda_name, x)
    )
    
    # Filter to reasonable matches and sort by similarity
    matches = df[df['similarity'] >= 0.5].sort_values('similarity', ascending=False)
    
    return matches


def main():
    print("\n" + "="*80)
    print("FINDING SOD NAME MATCHES FOR FIFTH THIRD AND COMERICA")
    print("="*80)
    
    # HMDA names from crosswalk
    fifth_third_hmda = "Fifth Third Bank"
    comerica_hmda = "Comerica Bank"
    
    # Try different SOD tables
    sod_tables = ['sod25', 'sod', 'sod_legacy']
    
    print("\n" + "="*80)
    print("FIFTH THIRD BANK MATCHES")
    print("="*80)
    print(f"\nHMDA Name: '{fifth_third_hmda}'")
    print("\nPotential SOD Matches:")
    print("-" * 80)
    
    all_fifth_third = []
    for table in sod_tables:
        print(f"\nFrom {table}:")
        try:
            matches = get_sod_names_for_bank(fifth_third_hmda, year=2024, sod_table=table)
            if len(matches) > 0:
                for idx, row in matches.head(10).iterrows():
                    print(f"  [{row['similarity']:.1%}] {row['institution_name']}")
                    print(f"      Branches: {row['branch_count']:,}, Deposits: ${row['total_deposits']:,.0f}")
                    all_fifth_third.append({
                        'sod_table': table,
                        'sod_name': row['institution_name'],
                        'similarity': row['similarity'],
                        'branches': row['branch_count'],
                        'deposits': row['total_deposits']
                    })
            else:
                print(f"  No matches found in {table}")
        except Exception as e:
            print(f"  Error querying {table}: {e}")
    
    print("\n" + "="*80)
    print("COMERICA BANK MATCHES")
    print("="*80)
    print(f"\nHMDA Name: '{comerica_hmda}'")
    print("\nPotential SOD Matches:")
    print("-" * 80)
    
    all_comerica = []
    for table in sod_tables:
        print(f"\nFrom {table}:")
        try:
            matches = get_sod_names_for_bank(comerica_hmda, year=2024, sod_table=table)
            if len(matches) > 0:
                for idx, row in matches.head(10).iterrows():
                    print(f"  [{row['similarity']:.1%}] {row['institution_name']}")
                    print(f"      Branches: {row['branch_count']:,}, Deposits: ${row['total_deposits']:,.0f}")
                    all_comerica.append({
                        'sod_table': table,
                        'sod_name': row['institution_name'],
                        'similarity': row['similarity'],
                        'branches': row['branch_count'],
                        'deposits': row['total_deposits']
                    })
            else:
                print(f"  No matches found in {table}")
        except Exception as e:
            print(f"  Error querying {table}: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY - PLEASE CONFIRM:")
    print("="*80)
    
    print("\nFIFTH THIRD BANK:")
    print(f"  HMDA Name: '{fifth_third_hmda}'")
    if all_fifth_third:
        print("  Best SOD Matches:")
        for match in sorted(all_fifth_third, key=lambda x: x['similarity'], reverse=True)[:5]:
            print(f"    - '{match['sod_name']}' (similarity: {match['similarity']:.1%}, table: {match['sod_table']})")
        print("\n  → Which SOD name is correct? (or type 'none' if not found)")
    else:
        print("  → No matches found. Please search manually.")
    
    print("\nCOMERICA BANK:")
    print(f"  HMDA Name: '{comerica_hmda}'")
    if all_comerica:
        print("  Best SOD Matches:")
        for match in sorted(all_comerica, key=lambda x: x['similarity'], reverse=True)[:5]:
            print(f"    - '{match['sod_name']}' (similarity: {match['similarity']:.1%}, table: {match['sod_table']})")
        print("\n  → Which SOD name is correct? (or type 'none' if not found)")
    else:
        print("  → No matches found. Please search manually.")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()

