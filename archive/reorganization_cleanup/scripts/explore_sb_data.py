"""
Explore Small Business (SB) Dataset in BigQuery
"""
import sys
import os
import pandas as pd
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

def explore_sb_dataset():
    """Explore the SB dataset structure"""
    print("\n" + "="*80)
    print("EXPLORING SMALL BUSINESS (SB) DATASET")
    print("="*80)
    
    creds_path = os.path.join(base_dir, "config", "credentials", "hdma1-242116-74024e2eb88f.json")
    
    if os.path.exists(creds_path):
        client = create_client(key_path=creds_path)
    else:
        client = create_client()
    
    # Check what tables exist (simplified)
    print("\n1. Checking available tables...")
    print("   Querying disclosure and lenders tables directly...")
    
    # Check disclosure table structure by sampling
    print("\n2. Checking disclosure table structure...")
    query = """
    SELECT *
    FROM `hdma1-242116.sb.disclosure`
    LIMIT 1
    """
    disclosure_sample = client.execute_query(query)
    print(f"\nDisclosure table columns ({len(disclosure_sample.columns)}):")
    for col in disclosure_sample.columns:
        print(f"  - {col}")
    
    # Check lenders table structure by sampling
    print("\n3. Checking lenders table structure...")
    query = """
    SELECT *
    FROM `hdma1-242116.sb.lenders`
    LIMIT 1
    """
    lenders_sample = client.execute_query(query)
    print(f"\nLenders table columns ({len(lenders_sample.columns)}):")
    for col in lenders_sample.columns:
        print(f"  - {col}")
    
    # Sample disclosure data
    print("\n4. Sampling disclosure data...")
    query = """
    SELECT *
    FROM `hdma1-242116.sb.disclosure`
    LIMIT 3
    """
    disclosure_sample2 = client.execute_query(query)
    print(f"\nSample disclosure rows:")
    print(disclosure_sample2.head().to_string())
    
    # Sample lenders data
    print("\n5. Sampling lenders data...")
    query = """
    SELECT *
    FROM `hdma1-242116.sb.lenders`
    LIMIT 3
    """
    lenders_sample2 = client.execute_query(query)
    print(f"\nSample lenders rows:")
    print(lenders_sample2.head().to_string())
    
    # Check join relationship - lenders table uses sb_resid to match disclosure.respondent_id
    print("\n6. Checking join relationship...")
    query = """
    SELECT 
        d.respondent_id,
        l.sb_lender as lender_name,
        l.sb_rssd as rssd,
        COUNT(*) as disclosure_count
    FROM `hdma1-242116.sb.disclosure` d
    LEFT JOIN `hdma1-242116.sb.lenders` l
        ON d.respondent_id = l.sb_resid
    GROUP BY d.respondent_id, l.sb_lender, l.sb_rssd
    ORDER BY disclosure_count DESC
    LIMIT 20
    """
    join_sample = client.execute_query(query)
    print(f"\nTop lenders by disclosure count:")
    print(join_sample.head(10).to_string())
    
    # Look for Fifth Third and Comerica
    print("\n7. Searching for Fifth Third and Comerica...")
    query = """
    SELECT 
        l.sb_resid as respondent_id,
        l.sb_lender as lender_name,
        l.sb_rssd as rssd,
        COUNT(DISTINCT d.year) as years,
        COUNT(*) as total_records
    FROM `hdma1-242116.sb.disclosure` d
    LEFT JOIN `hdma1-242116.sb.lenders` l
        ON d.respondent_id = l.sb_resid
    WHERE UPPER(l.sb_lender) LIKE '%FIFTH%THIRD%'
       OR UPPER(l.sb_lender) LIKE '%COMERICA%'
       OR l.sb_rssd = '723112'
       OR l.sb_rssd = '60143'
    GROUP BY l.sb_resid, l.sb_lender, l.sb_rssd
    ORDER BY l.sb_lender
    """
    bank_search = client.execute_query(query)
    if len(bank_search) > 0:
        print(f"\nFound {len(bank_search)} matches:")
        print(bank_search.to_string())
    else:
        print("\nNo matches found with RSSD or name search")
        
        # Try broader search
        query = """
        SELECT DISTINCT
            l.sb_resid as respondent_id,
            l.sb_lender as lender_name,
            l.sb_rssd as rssd
        FROM `hdma1-242116.sb.lenders` l
        WHERE l.sb_rssd = '723112'
           OR l.sb_rssd = '60143'
           OR UPPER(l.sb_lender) LIKE '%THIRD%'
           OR UPPER(l.sb_lender) LIKE '%COMERICA%'
        LIMIT 10
        """
        broader_search = client.execute_query(query)
        print(f"\nBroader search results:")
        print(broader_search.to_string())
    
    # Check what years are available
    print("\n8. Checking available reporting years...")
    query = """
    SELECT 
        year,
        COUNT(DISTINCT respondent_id) as lenders,
        COUNT(*) as total_records
    FROM `hdma1-242116.sb.disclosure`
    WHERE year IS NOT NULL
    GROUP BY year
    ORDER BY year DESC
    """
    periods = client.execute_query(query)
    print(f"\nReporting periods by year:")
    print(periods.to_string())
    
    print("\n" + "="*80)
    print("EXPLORATION COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    explore_sb_dataset()

