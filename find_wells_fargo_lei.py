"""
Find Wells Fargo's LEI in the HMDA dataset
"""

from google.cloud import bigquery
import pandas as pd

def main():
    print("="*80)
    print("FINDING WELLS FARGO LEI IN HMDA DATASET")
    print("="*80)
    print()
    
    key_path = "hdma1-242116-74024e2eb88f.json"
    project_id = "hdma1-242116"
    
    print("Connecting to BigQuery...")
    client = bigquery.Client.from_service_account_json(key_path, project=project_id)
    print("✓ Connected")
    print()
    
    # Search for Wells Fargo
    query = """
    SELECT DISTINCT 
        lei, 
        respondent_name,
        COUNT(*) as total_records,
        MIN(activity_year) as first_year,
        MAX(activity_year) as last_year
    FROM `hdma1-242116.hmda.hmda`
    WHERE LOWER(respondent_name) LIKE '%wells%fargo%'
       OR LOWER(respondent_name) LIKE '%wellsfargo%'
    GROUP BY lei, respondent_name
    ORDER BY total_records DESC
    LIMIT 20
    """
    
    print("Searching for Wells Fargo in HMDA dataset...")
    print()
    
    query_job = client.query(query)
    results = query_job.result()
    df = results.to_dataframe()
    
    if len(df) > 0:
        print(f"Found {len(df)} Wells Fargo entities:")
        print()
        print(df.to_string(index=False))
        print()
        
        # Save results
        df.to_csv("wells_fargo_leis.csv", index=False)
        print("✓ Saved to wells_fargo_leis.csv")
    else:
        print("❌ No Wells Fargo entities found in HMDA dataset")
        print()
        print("Trying broader search...")
        
        # Try broader search
        query2 = """
        SELECT DISTINCT 
            lei, 
            respondent_name,
            COUNT(*) as total_records
        FROM `hdma1-242116.hmda.hmda`
        WHERE LOWER(respondent_name) LIKE '%wells%'
        GROUP BY lei, respondent_name
        ORDER BY total_records DESC
        LIMIT 50
        """
        
        query_job2 = client.query(query2)
        results2 = query_job2.result()
        df2 = results2.to_dataframe()
        
        print(f"Found {len(df2)} entities with 'wells' in name:")
        print()
        print(df2.to_string(index=False))

if __name__ == "__main__":
    main()
