"""
Run Small Business (SB) queries in BigQuery and save results
"""
import sys
import os
import pandas as pd
from pathlib import Path
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

def run_query(query_file, output_file):
    """Run a SQL query and save results to CSV"""
    print(f"\n{'='*80}")
    print(f"Running query: {query_file}")
    print(f"{'='*80}")
    
    # Read SQL query
    with open(query_file, 'r', encoding='utf-8') as f:
        query = f.read()
    
    # Connect to BigQuery
    creds_path = os.path.join(base_dir, "config", "credentials", "hdma1-242116-74024e2eb88f.json")
    
    if os.path.exists(creds_path):
        client = create_client(key_path=creds_path)
    else:
        client = create_client()
    
    # Execute query
    print("Executing query in BigQuery...")
    df = client.execute_query(query)
    
    print(f"Query completed: {len(df):,} rows returned")
    
    # Save to CSV
    output_path = Path(base_dir) / "data" / "raw" / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"Saved to: {output_path}")
    
    return df

def main():
    print("\n" + "="*80)
    print("RUNNING SMALL BUSINESS (SB) QUERIES")
    print("="*80)
    
    queries_dir = Path(base_dir) / "queries" / "sb"
    
    # Run Fifth Third SB query
    ft_sb_query = queries_dir / "FIFTH_THIRD_SB_QUERY.sql"
    if ft_sb_query.exists():
        run_query(ft_sb_query, "fifth_third_sb_data.csv")
    else:
        print(f"ERROR: Query file not found: {ft_sb_query}")
    
    # Run Comerica SB query
    com_sb_query = queries_dir / "COMERICA_SB_QUERY.sql"
    if com_sb_query.exists():
        run_query(com_sb_query, "comerica_sb_data.csv")
    else:
        print(f"ERROR: Query file not found: {com_sb_query}")
    
    print("\n" + "="*80)
    print("QUERIES COMPLETE!")
    print("="*80)
    print("\nNext steps:")
    print("1. Run: python scripts/fifth_third_sb_report.py")
    print("2. Run: python scripts/comerica_sb_report.py")

if __name__ == "__main__":
    main()

