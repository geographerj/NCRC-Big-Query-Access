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
    """
    
    HMDA_TABLE = "hdma1-242116.hmda.hmda"
    wells_fargo_lei = "549300RHCGHM14LPTW53"
    
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
    
    key_path = "hdma1-242116-74024e2eb88f.json"
    project_id = "hdma1-242116"
    
    print("Connecting to BigQuery...")
    try:
        client = bigquery.Client.from_service_account_json(key_path, project=project_id)
        print(f"? Connected to BigQuery project: {project_id}")
        print()
    except Exception as e:
        print(f"? Error connecting to BigQuery: {e}")
        return 1
    
    query = get_wells_fargo_records_by_year()
    
    print("Executing query for Wells Fargo HMDA records by year...")
    print("LEI: 549300RHCGHM14LPTW53")
    print()
    
    try:
        print("Running query... (this may take a minute)")
        query_job = client.query(query)
        results = query_job.result()
        df = results.to_dataframe()
        print(f"? Query completed: {len(df):,} rows returned")
    except Exception as e:
        print(f"? Error executing query: {e}")
        return 1
    
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
    
    # Print summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    if len(df) > 0:
        print(f"Total years with data: {len(df)}")
        print(f"Year range: {int(df['activity_year'].min())} - {int(df['activity_year'].max())}")
        print(f"Total records across all years: {int(df['total_records'].sum()):,}")
        print(f"Total originations across all years: {int(df['originations'].sum()):,}")
        print(f"Total originated amount: ${df['total_originated_amount'].sum():,.0f}")
    else:
        print("No data found for Wells Fargo LEI: 549300RHCGHM14LPTW53")
    print()
    
    return 0


if __name__ == "__main__":
    exit(main())
