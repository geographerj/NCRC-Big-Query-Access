"""
Generate Tampa Market Report

This script generates the complete market overview report for Tampa city.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add paths
member_reports_dir = Path(__file__).parent.parent
sys.path.insert(0, str(member_reports_dir))
sys.path.insert(0, str(member_reports_dir.parent / "Lending and Branch Analysis" / "utils"))

from queries.tampa_market_query import build_tampa_market_query, build_top_lenders_2024_query
from bigquery_client import create_client
import pandas as pd

# Tampa census tracts
TAMPA_TRACTS = [
    '12057990000', '12057013604', '12057007300', '12057011008', '12057980100', '12057010215', 
    '12057005302', '12057011019', '12057011017', '12057003700', '12057980500', '12057980600', 
    '12057013501', '12057011605', '12057012001', '12057007200', '12057002600', '12057010900', 
    '12057010211', '12057011708', '12057010216', '12057012002', '12057011016', '12057014400', 
    '12057011010', '12057011304', '12057005401', '12057004602', '12057005900', '12057010212', 
    '12057003600', '12057001300', '12057010210', '12057011013', '12057006900', '12057000102', 
    '12057000101', '12057011802', '12057006000', '12057006700', '12057011712', '12057001001', 
    '12057000800', '12057005800', '12057000500', '12057001002', '12057011018', '12057002500', 
    '12057006400', '12057001700', '12101032112', '12057013503', '12057004800', '12057011205', 
    '12101032113', '12057002400', '12057001400', '12057001800', '12057007001', '12057007102', 
    '12057002701', '12057011909', '12057003800', '12057014200', '12057011911', '12057010501', 
    '12057011206', '12057006802', '12057005101', '12057000202', '12057006600', '12057000401', 
    '12057006801', '12057001900', '12057000402', '12057007103', '12057005000', '12057010805', 
    '12057004500', '12057004700', '12057000301', '12057004601', '12057002800', '12057006300', 
    '12057005700', '12057000902', '12057006200', '12057001100', '12057006101', '12057011910', 
    '12057006103', '12057003500', '12057002300', '12057001500', '12057006501', '12057001200', 
    '12057011907', '12057000601', '12057003000', '12057007002', '12057000602', '12057003400', 
    '12057010816', '12057002200', '12057002900', '12057010809', '12057003100', '12057002000', 
    '12057001600', '12057002100', '12057002702', '12057005102', '12057000701', '12057000302', 
    '12057004200', '12057004901', '12057005500', '12057000702', '12057000201', '12057005301', 
    '12057004400', '12057006503', '12057000901', '12057004300', '12057003200', '12057003300', 
    '12057004902', '12057011905', '12057006504', '12057004100'
]

YEARS = [2018, 2019, 2020, 2021, 2022, 2023, 2024]


def main():
    print("\n" + "="*80)
    print("TAMPA MARKET REPORT GENERATION")
    print("="*80)
    print(f"\nGeography: Tampa City (130 census tracts)")
    print(f"Years: {YEARS[0]}-{YEARS[-1]}")
    print(f"Loan Type: Home Purchase Originations Only")
    print(f"Analysis: Market Overview + Top 10 Lenders (2024)")
    
    # Connect to BigQuery
    print("\n" + "="*80)
    print("STEP 1: CONNECTING TO BIGQUERY")
    print("="*80)
    
    creds_path = member_reports_dir.parent / "config" / "credentials" / "hdma1-242116-74024e2eb88f.json"
    if not creds_path.exists():
        creds_path = None
    
    client = create_client(key_path=str(creds_path) if creds_path else None)
    
    # Query market data
    print("\n" + "="*80)
    print("STEP 2: QUERYING MARKET DATA")
    print("="*80)
    
    market_query = build_tampa_market_query(TAMPA_TRACTS, YEARS)
    print(f"Query length: {len(market_query)} characters")
    
    print("\nExecuting query...")
    market_data = client.execute_query(market_query)
    print(f"Retrieved {len(market_data):,} rows")
    
    # Query top lenders
    print("\n" + "="*80)
    print("STEP 3: IDENTIFYING TOP 10 LENDERS (2024)")
    print("="*80)
    
    top_lenders_query = build_top_lenders_2024_query(TAMPA_TRACTS)
    top_lenders = client.execute_query(top_lenders_query)
    print(f"Found {len(top_lenders)} top lenders")
    
    # Merge lender names from crosswalk
    try:
        crosswalk_path = member_reports_dir.parent / "data" / "reference" / "Lenders_and_LEI_Numbers.csv"
        if crosswalk_path.exists():
            lender_crosswalk = pd.read_csv(crosswalk_path)
            lender_crosswalk = lender_crosswalk.rename(columns={'Lei': 'lei', 'Respondent Name': 'respondent_name'})
            top_lenders = top_lenders.merge(
                lender_crosswalk[['lei', 'respondent_name']],
                on='lei',
                how='left'
            )
            print(f"  Merged lender names for {top_lenders['respondent_name'].notna().sum()} lenders")
        else:
            print("  Warning: Lender crosswalk not found, will use LEI only")
            top_lenders['respondent_name'] = None
    except Exception as e:
        print(f"  Warning: Could not merge lender names: {e}")
        top_lenders['respondent_name'] = None
    
    # Save raw data
    output_dir = member_reports_dir / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    market_data.to_csv(output_dir / "tampa_market_data.csv", index=False)
    top_lenders.to_csv(output_dir / "tampa_top_lenders_2024.csv", index=False)
    
    print(f"\nRaw data saved:")
    print(f"  - {output_dir / 'tampa_market_data.csv'}")
    print(f"  - {output_dir / 'tampa_top_lenders_2024.csv'}")
    
    print("\n" + "="*80)
    print("STEP 4: PROCESSING DATA")
    print("="*80)
    
    # Process market data
    market_df = market_data[market_data['analysis_type'] == 'Market'].copy()
    lender_df = market_data[market_data['analysis_type'] == 'Lender'].copy()
    
    print(f"\nMarket data: {len(market_df)} year rows")
    print(f"Lender data: {len(lender_df)} lender-year rows")
    
    # Get top 10 LEIs
    top_10_leis = top_lenders['lei'].tolist()
    print(f"\nTop 10 lenders by 2024 volume:")
    for i, row in top_lenders.iterrows():
        print(f"  {i+1}. LEI {row['lei']}: {row['total_originations_2024']:,} originations")
    
    # Filter lender data to top 10
    top_10_data = lender_df[lender_df['lei'].isin(top_10_leis)].copy()
    print(f"\nTop 10 lender data: {len(top_10_data)} lender-year rows")
    
    print("\n" + "="*80)
    print("DATA READY FOR REPORT GENERATION")
    print("="*80)
    print("\nNext: Process data and generate PDF/Excel reports")
    print("\nMarket metrics calculated:")
    print("  - Black homebuyer share")
    print("  - Hispanic homebuyer share")
    print("  - Asian homebuyer share")
    print("  - LMIB lending share")
    print("  - LMICT lending share")
    print("  - MMCT lending share")
    
    return market_df, top_10_data, top_lenders


if __name__ == '__main__':
    market_df, top_10_data, top_lenders = main()

