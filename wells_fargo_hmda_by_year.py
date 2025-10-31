"""
Query Wells Fargo HMDA Records by Year

This script queries the HMDA dataset to count the number of records
from Wells Fargo for each year.
"""

from google.cloud import bigquery
import pandas as pd


def main():
    print("="*80)
    print("WELLS FARGO HMDA RECORDS BY YEAR")
    print("="*80)
    print()
    
    key_path = "hdma1-242116-74024e2eb88f.json"
    project_id = "hdma1-242116"
    
    # Correct Wells Fargo LEI from lenders18 table
    wells_fargo_lei = "KB1H1DSPRFMYMCUFXT09"
    
    print("Connecting to BigQuery...")
    client = bigquery.Client.from_service_account_json(key_path, project=project_id)
    print("? Connected")
    print()
    
    query = f"""
    SELECT 
        activity_year,
        COUNT(*) as total_records,
        COUNTIF(action_taken = '1') as originations,
        COUNTIF(action_taken = '3') as denials,
        COUNTIF(action_taken = '2') as approved_not_accepted,
        COUNTIF(action_taken = '4') as withdrawn,
        COUNTIF(action_taken = '5') as incomplete,
        COUNT(DISTINCT state_code) as states_with_activity,
        COUNT(DISTINCT CONCAT(state_code, county_code)) as counties_with_activity,
        COUNT(DISTINCT census_tract) as tracts_with_activity,
        SUM(CASE WHEN action_taken = '1' THEN loan_amount ELSE 0 END) as total_originated_amount,
        AVG(CASE WHEN action_taken = '1' THEN loan_amount ELSE NULL END) as avg_originated_amount,
        COUNTIF(loan_purpose = '1') as home_purchase_count,
        COUNTIF(loan_purpose = '2') as home_improvement_count,
        COUNTIF(loan_purpose IN ('31', '32')) as refinancing_count
    FROM `hdma1-242116.hmda.hmda`
    WHERE lei = '{wells_fargo_lei}'
    GROUP BY activity_year
    ORDER BY activity_year
    """
    
    print(f"Querying Wells Fargo HMDA records...")
    print(f"LEI: {wells_fargo_lei}")
    print(f"Institution: Wells Fargo Bank")
    print()
    print("Running query (this may take a minute)...")
    
    query_job = client.query(query)
    results = query_job.result()
    df = results.to_dataframe()
    
    print(f"? Query completed: {len(df)} rows returned")
    print()
    
    if len(df) > 0:
        print("="*80)
        print("RESULTS: Wells Fargo HMDA Records by Year")
        print("="*80)
        print()
        print(df.to_string(index=False))
        print()
        
        # Save to CSV
        output_path = "wells_fargo_hmda_by_year.csv"
        df.to_csv(output_path, index=False)
        print(f"? Results saved to: {output_path}")
        print()
        
        # Print summary
        print("="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Years with data: {len(df)}")
        print(f"Year range: {df['activity_year'].min()} - {df['activity_year'].max()}")
        print(f"Total records across all years: {int(df['total_records'].sum()):,}")
        print(f"Total originations across all years: {int(df['originations'].sum()):,}")
        if df['total_originated_amount'].sum() > 0:
            print(f"Total originated amount: ${df['total_originated_amount'].sum():,.0f}")
        print()
    else:
        print("? No data found for Wells Fargo")

if __name__ == "__main__":
    main()
