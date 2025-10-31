"""
Query Wells Fargo HMDA Records by Year

This script queries the HMDA dataset to count the number of records
from Wells Fargo for each year.
"""

import sys
import os
from google.cloud import bigquery
import pandas as pd


def get_wells_fargo_records_by_year():
    """
    Query HMDA dataset for Wells Fargo records by year
    
    Wells Fargo's LEI: 549300RHCGHM14LPTW53
    (This is the most common LEI used for Wells Fargo Bank, N.A.)
    """
    
    # HMDA table reference
    HMDA_TABLE = "hdma1-242116.hmda.hmda"
    
    # Wells Fargo LEI
    wells_fargo_lei = "549300RHCGHM14LPTW53"
    
    query = f"""
    SELECT 
        activity_year,
        COUNT(*) as total_records,
        COUNTIF(action_taken = '1') as originations,
        COUNTIF(action_taken = '3') as denials,
        COUNT(DISTINCT state_code) as states_with_activity,
        COUNT(DISTINCT census_tract) as tracts_with_activity,
        SUM(CASE WHEN action_taken = '1' THEN loan_amount ELSE 0 END) as total_originated_amount
    FROM `{HMDA_TABLE}`
    WHERE lei = '{wells_fargo_lei}'
    GROUP BY activity_year
    ORDER BY activity_year
    """
    
    return query


def main():
    """Execute the query and display/save results"""
    print("="*80)
    print("WELLS FARGO HMDA RECORDS BY YEAR")
    print("="*80)
    print()
    
    # Create BigQuery client
    print("Connecting to BigQuery...")
    
    # Try multiple credential methods
    key_path = "hdma1-242116-74024e2eb88f.json"
    project_id = "hdma1-242116"
    
    if os.path.exists(key_path):
        print(f"Using service account key: {key_path}")
        client = bigquery.Client.from_service_account_json(key_path, project=project_id)
    else:
        print("Service account key not found. Trying Application Default Credentials...")
        try:
            client = bigquery.Client(project=project_id)
        except Exception as e:
            print(f"Error: Could not authenticate with BigQuery")
            print(f"Details: {e}")
            print()
            print("Please ensure you have:")
            print("1. Service account key file: hdma1-242116-74024e2eb88f.json")
            print("   OR")
            print("2. Application Default Credentials configured")
            return
    
    print(f"? Connected to BigQuery project: {project_id}")
    print()
    
    # Get query
    query = get_wells_fargo_records_by_year()
    
    print("Executing query for Wells Fargo HMDA records by year...")
    print("LEI: 549300RHCGHM14LPTW53")
    print()
    
    # Execute query
    print(f"Executing query...")
    query_job = client.query(query)
    results = query_job.result()
    df = results.to_dataframe()
    print(f"? Query completed: {len(df):,} rows returned")
    
    # Display results
    print()
    print("="*80)
    print("RESULTS: Wells Fargo HMDA Records by Year")
    print("="*80)
    print()
    print(df.to_string(index=False))
    print()
    
    # Save to CSV
    output_path = "wells_fargo_hmda_by_year.csv"
    df.to_csv(output_path, index=False)
    print(f"? Exported {len(df):,} rows to: {output_path}")
    print()
    
    # Print summary statistics
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total years with data: {len(df)}")
    print(f"Year range: {df['activity_year'].min()} - {df['activity_year'].max()}")
    print(f"Total records across all years: {df['total_records'].sum():,}")
    print(f"Total originations across all years: {df['originations'].sum():,}")
    print()


if __name__ == "__main__":
    main()
