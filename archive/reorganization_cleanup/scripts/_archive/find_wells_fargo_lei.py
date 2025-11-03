"""
Find Wells Fargo's LEI using the lenders18 table
"""

from google.cloud import bigquery
import pandas as pd

def main():
    print("="*80)
    print("FINDING WELLS FARGO LEI")
    print("="*80)
    print()
    
    key_path = "hdma1-242116-74024e2eb88f.json"
    project_id = "hdma1-242116"
    
    print("Connecting to BigQuery...")
    client = bigquery.Client.from_service_account_json(key_path, project=project_id)
    print("✓ Connected")
    print()
    
    # First, check what columns are in lenders18
    print("Checking lenders18 table schema...")
    table_ref = client.dataset("hmda").table("lenders18")
    table = client.get_table(table_ref)
    
    print("Columns in lenders18:")
    for field in table.schema:
        print(f"  - {field.name} ({field.field_type})")
    print()
    
    # Search for Wells Fargo in lenders18
    query = """
    SELECT *
    FROM `hdma1-242116.hmda.lenders18`
    WHERE LOWER(respondent_name) LIKE '%wells%fargo%'
       OR LOWER(respondent_name) LIKE '%wellsfargo%'
    """
    
    print("Searching for Wells Fargo in lenders18 table...")
    print()
    
    query_job = client.query(query)
    results = query_job.result()
    df = results.to_dataframe()
    
    if len(df) > 0:
        print(f"✓ Found {len(df)} Wells Fargo entries:")
        print()
        print(df.to_string(index=False))
        print()
        
        # Save results
        df.to_csv("wells_fargo_leis.csv", index=False)
        print("✓ Saved to wells_fargo_leis.csv")
        print()
        
        # Get the most common LEI
        if 'lei' in df.columns and len(df) > 0:
            main_lei = df['lei'].iloc[0]
            print("="*80)
            print(f"Main Wells Fargo LEI: {main_lei}")
            print("="*80)
    else:
        print("❌ No Wells Fargo entries found")
        print()
        print("Showing sample of lenders...")
        
        sample_query = """
        SELECT *
        FROM `hdma1-242116.hmda.lenders18`
        LIMIT 10
        """
        
        query_job2 = client.query(sample_query)
        results2 = query_job2.result()
        df2 = results2.to_dataframe()
        print(df2.to_string(index=False))

if __name__ == "__main__":
    main()
