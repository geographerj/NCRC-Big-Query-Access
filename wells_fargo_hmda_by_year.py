"""
Query Wells Fargo HMDA Records by Year

This script queries the HMDA dataset to count the number of records
from Wells Fargo for each year.

Usage:
    python wells_fargo_hmda_by_year.py
    
    Or specify custom key path:
    python wells_fargo_hmda_by_year.py --key-path "path/to/key.json"
"""

import sys
import os
from google.cloud import bigquery
import pandas as pd
import argparse


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
        COUNTIF(action_taken = '2') as approved_not_accepted,
        COUNTIF(action_taken = '4') as withdrawn,
        COUNTIF(action_taken = '5') as incomplete,
        COUNT(DISTINCT state_code) as states_with_activity,
        COUNT(DISTINCT CONCAT(state_code, county_code)) as counties_with_activity,
        COUNT(DISTINCT census_tract) as tracts_with_activity,
        SUM(CASE WHEN action_taken = '1' THEN loan_amount ELSE 0 END) as total_originated_amount,
        AVG(CASE WHEN action_taken = '1' THEN loan_amount ELSE NULL END) as avg_originated_amount,
        -- Loan purpose breakdown
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
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Query Wells Fargo HMDA records by year')
    parser.add_argument('--key-path', 
                       default='hdma1-242116-74024e2eb88f.json',
                       help='Path to BigQuery service account key file')
    parser.add_argument('--output', 
                       default='wells_fargo_hmda_by_year.csv',
                       help='Output CSV file path')
    args = parser.parse_args()
    
    print("="*80)
    print("WELLS FARGO HMDA RECORDS BY YEAR")
    print("="*80)
    print()
    
    # Create BigQuery client
    print("Connecting to BigQuery...")
    
    key_path = args.key_path
    project_id = "hdma1-242116"
    
    # Check if key file exists
    if not os.path.exists(key_path):
        print(f"? Error: Service account key file not found: {key_path}")
        print()
        print("Please provide the correct path to your key file:")
        print("  Windows example:")
        print('    python wells_fargo_hmda_by_year.py --key-path "C:\\Users\\...\\hdma1-242116-74024e2eb88f.json"')
        print("  Mac/Linux example:")
        print('    python wells_fargo_hmda_by_year.py --key-path "/path/to/hdma1-242116-74024e2eb88f.json"')
        return 1
    
    try:
        client = bigquery.Client.from_service_account_json(key_path, project=project_id)
        print(f"? Connected to BigQuery project: {project_id}")
        print(f"  Using key file: {key_path}")
        print()
    except Exception as e:
        print(f"? Error connecting to BigQuery: {e}")
        return 1
    
    # Get query
    query = get_wells_fargo_records_by_year()
    
    print("Executing query for Wells Fargo HMDA records by year...")
    print("LEI: 549300RHCGHM14LPTW53")
    print()
    
    # Execute query
    try:
        print("Running query... (this may take a minute)")
        query_job = client.query(query)
        results = query_job.result()
        df = results.to_dataframe()
        print(f"? Query completed: {len(df):,} rows returned")
    except Exception as e:
        print(f"? Error executing query: {e}")
        return 1
    
    # Display results
    print()
    print("="*80)
    print("RESULTS: Wells Fargo HMDA Records by Year")
    print("="*80)
    print()
    
    # Format the dataframe for display
    display_df = df.copy()
    
    # Format numeric columns with commas
    numeric_cols = ['total_records', 'originations', 'denials', 
                    'approved_not_accepted', 'withdrawn', 'incomplete',
                    'states_with_activity', 'counties_with_activity', 
                    'tracts_with_activity', 'home_purchase_count',
                    'home_improvement_count', 'refinancing_count']
    
    for col in numeric_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
    
    # Format amount columns
    if 'total_originated_amount' in display_df.columns:
        display_df['total_originated_amount'] = display_df['total_originated_amount'].apply(
            lambda x: f"${x:,.0f}" if pd.notna(x) else ""
        )
    if 'avg_originated_amount' in display_df.columns:
        display_df['avg_originated_amount'] = display_df['avg_originated_amount'].apply(
            lambda x: f"${x:,.0f}" if pd.notna(x) else ""
        )
    
    print(display_df.to_string(index=False))
    print()
    
    # Save to CSV (original unformatted data)
    output_path = args.output
    df.to_csv(output_path, index=False)
    print(f"? Exported {len(df):,} rows to: {output_path}")
    print()
    
    # Print summary statistics
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
        print("This could mean:")
        print("1. Wells Fargo uses a different LEI in the dataset")
        print("2. The HMDA table is empty or inaccessible")
        print()
        print("Try running the query to find Wells Fargo's LEI:")
        print("  See wells_fargo_find_lei.sql")
    print()
    
    return 0


if __name__ == "__main__":
    exit(main())
