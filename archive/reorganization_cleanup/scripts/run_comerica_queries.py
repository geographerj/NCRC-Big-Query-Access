"""
Run Comerica Bank queries in BigQuery and save results
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
    print("RUNNING COMERICA BANK QUERIES")
    print("="*80)
    
    queries_dir = Path(base_dir) / "queries" / "comerica"
    
    # Run demographics query
    demographics_query = queries_dir / "COMERICA_DEMOGRAPHICS_QUERY.sql"
    if demographics_query.exists():
        run_query(demographics_query, "comerica_demographics.csv")
    else:
        print(f"ERROR: Query file not found: {demographics_query}")
    
    # Run redlining query
    redlining_query = queries_dir / "COMERICA_REDLINING_QUERY.sql"
    if redlining_query.exists():
        run_query(redlining_query, "comerica_redlining.csv")
    else:
        print(f"ERROR: Query file not found: {redlining_query}")
    
    print("\n" + "="*80)
    print("QUERIES COMPLETE!")
    print("="*80)
    print("\nNext steps:")
    print("1. Review the CSV files in data/raw/")
    print("2. Run: python scripts/comerica_cba_report.py")

if __name__ == "__main__":
    main()

