"""
Query SOD tables directly to find name matches for Fifth Third and Comerica.
No encoding issues - just prints simple output.
"""

import sys
import os
import pandas as pd

# Handle module imports
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

create_client = bigquery_client.create_client

# Credentials path
creds_path = os.path.join(base_dir, "config", "credentials", "hdma1-242116-74024e2eb88f.json")

def query_sod_names(search_term, year=2024, table='sod25'):
    """Query SOD table for institution names matching search term"""
    if os.path.exists(creds_path):
        client = create_client(key_path=creds_path)
    else:
        client = create_client()
    
    table_map = {
        'sod': 'hdma1-242116.branches.sod',
        'sod25': 'hdma1-242116.branches.sod25',
        'sod_legacy': 'hdma1-242116.branches.sod_legacy'
    }
    
    sql_table = table_map.get(table.lower(), 'hdma1-242116.branches.sod25')
    
    query = f"""
    SELECT DISTINCT
        institution_name,
        COUNT(DISTINCT uninumbr) as branch_count,
        SUM(deposits) as total_deposits,
        MIN(year) as first_year,
        MAX(year) as last_year
    FROM `{sql_table}`
    WHERE UPPER(institution_name) LIKE UPPER('%{search_term}%')
      AND year = {year}
    GROUP BY institution_name
    ORDER BY branch_count DESC
    """
    
    try:
        df = client.execute_query(query)
        return df
    except Exception as e:
        print(f"Error querying {table}: {str(e)}")
        return pd.DataFrame()

def main():
    print("\n" + "="*80)
    print("FINDING SOD NAME MATCHES")
    print("="*80)
    
    # Try all tables
    tables_to_check = ['sod25', 'sod', 'sod_legacy']
    
    print("\n" + "="*80)
    print("FIFTH THIRD BANK - POTENTIAL SOD MATCHES")
    print("="*80)
    print("\nHMDA Name: Fifth Third Bank")
    print("\nSearching SOD tables for names containing 'FIFTH THIRD'...\n")
    
    fifth_third_matches = []
    
    for table in tables_to_check:
        print(f"\nTable: {table}")
        print("-" * 80)
        df = query_sod_names('FIFTH THIRD', year=2024, table=table)
        
        if len(df) > 0:
            for idx, row in df.iterrows():
                name = row['institution_name']
                branches = int(row['branch_count'])
                deposits = float(row['total_deposits'])
                print(f"  {name}")
                print(f"    Branches: {branches:,} | Deposits: ${deposits:,.0f}")
                fifth_third_matches.append({
                    'table': table,
                    'name': name,
                    'branches': branches,
                    'deposits': deposits
                })
        else:
            print("  (No matches found)")
    
    print("\n" + "="*80)
    print("COMERICA BANK - POTENTIAL SOD MATCHES")
    print("="*80)
    print("\nHMDA Name: Comerica Bank")
    print("\nSearching SOD tables for names containing 'COMERICA'...\n")
    
    comerica_matches = []
    
    for table in tables_to_check:
        print(f"\nTable: {table}")
        print("-" * 80)
        df = query_sod_names('COMERICA', year=2024, table=table)
        
        if len(df) > 0:
            for idx, row in df.iterrows():
                name = row['institution_name']
                branches = int(row['branch_count'])
                deposits = float(row['total_deposits'])
                print(f"  {name}")
                print(f"    Branches: {branches:,} | Deposits: ${deposits:,.0f}")
                comerica_matches.append({
                    'table': table,
                    'name': name,
                    'branches': branches,
                    'deposits': deposits
                })
        else:
            print("  (No matches found)")
    
    # Summary for user confirmation
    print("\n" + "="*80)
    print("LIKELY MATCHES - PLEASE CONFIRM")
    print("="*80)
    
    print("\nFIFTH THIRD BANK:")
    print("  HMDA Name: 'Fifth Third Bank'")
    if fifth_third_matches:
        # Pick the one with most branches (most likely to be correct)
        best_match = max(fifth_third_matches, key=lambda x: x['branches'])
        print(f"\n  LIKELY MATCH: '{best_match['name']}'")
        print(f"    Table: {best_match['table']}")
        print(f"    Branches: {best_match['branches']:,}")
        print(f"\n  Other candidates:")
        for match in sorted(fifth_third_matches, key=lambda x: x['branches'], reverse=True)[:5]:
            if match['name'] != best_match['name']:
                print(f"    - '{match['name']}' ({match['table']}, {match['branches']} branches)")
    else:
        print("\n  No matches found - please search manually")
    
    print("\nCOMERICA BANK:")
    print("  HMDA Name: 'Comerica Bank'")
    if comerica_matches:
        best_match = max(comerica_matches, key=lambda x: x['branches'])
        print(f"\n  LIKELY MATCH: '{best_match['name']}'")
        print(f"    Table: {best_match['table']}")
        print(f"    Branches: {best_match['branches']:,}")
        print(f"\n  Other candidates:")
        for match in sorted(comerica_matches, key=lambda x: x['branches'], reverse=True)[:5]:
            if match['name'] != best_match['name']:
                print(f"    - '{match['name']}' ({match['table']}, {match['branches']} branches)")
    else:
        print("\n  No matches found - please search manually")
    
    print("\n" + "="*80)
    print("\nPlease confirm which SOD names are correct!")

if __name__ == "__main__":
    main()

