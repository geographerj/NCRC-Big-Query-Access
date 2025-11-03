"""
Check SOD table year ranges and record counts.
Helps determine which SOD table to use for analysis.
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

def check_table_years(table_name: str):
    """Check year distribution for a SOD table"""
    if os.path.exists(creds_path):
        client = create_client(key_path=creds_path)
    else:
        client = create_client()
    
    table_map = {
        'sod': 'hdma1-242116.branches.sod',
        'sod25': 'hdma1-242116.branches.sod25',
        'sod_legacy': 'hdma1-242116.branches.sod_legacy'
    }
    
    sql_table = table_map.get(table_name.lower(), table_name)
    
    query = f"""
    SELECT 
        year,
        COUNT(*) as total_records,
        COUNT(DISTINCT uninumbr) as unique_branches,
        COUNT(DISTINCT rssd) as unique_institutions
    FROM `{sql_table}`
    GROUP BY year
    ORDER BY year
    """
    
    try:
        df = client.execute_query(query)
        return df
    except Exception as e:
        print(f"Error querying {table_name}: {str(e)}")
        return pd.DataFrame()

def main():
    print("\n" + "="*80)
    print("CHECKING SOD TABLE YEAR DISTRIBUTIONS")
    print("="*80)
    
    tables = ['sod25', 'sod', 'sod_legacy']
    
    all_results = {}
    
    for table in tables:
        print(f"\n{'='*80}")
        print(f"Table: {table}")
        print(f"{'='*80}\n")
        
        df = check_table_years(table)
        
        if len(df) > 0:
            print(df.to_string(index=False))
            print(f"\nSummary for {table}:")
            print(f"  Years available: {df['year'].min()} to {df['year'].max()}")
            print(f"  Total years: {len(df)}")
            print(f"  Total records (all years): {df['total_records'].sum():,}")
            print(f"  Total unique branches: {df['unique_branches'].sum():,}")
            print(f"  Total unique institutions: {df['unique_institutions'].max():,}")
            
            # Check if has 2017-2025
            years = set(df['year'].unique())
            needed_years = set(range(2017, 2026))
            has_needed = needed_years.issubset(years)
            
            if has_needed:
                print(f"  HAS 2017-2025 DATA: YES")
            else:
                missing = needed_years - years
                if missing:
                    print(f"  HAS 2017-2025 DATA: NO (missing years: {sorted(missing)})")
            
            all_results[table] = df
        else:
            print("  No data found or error occurred")
            all_results[table] = pd.DataFrame()
    
    # Summary comparison
    print("\n" + "="*80)
    print("SUMMARY COMPARISON")
    print("="*80)
    print("\nWhich table has 2017-2025 data?")
    print("-" * 80)
    
    for table, df in all_results.items():
        if len(df) > 0:
            years = set(df['year'].unique())
            has_2017_2025 = all(year in years for year in range(2017, 2026))
            
            if has_2017_2025:
                print(f"{table:12s}: YES - Has 2017-2025 (recommended)")
            else:
                year_range = f"{df['year'].min()}-{df['year'].max()}"
                print(f"{table:12s}: NO  - Years: {year_range}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

