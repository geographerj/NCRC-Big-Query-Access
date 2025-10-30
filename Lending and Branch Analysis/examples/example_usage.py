"""
Example Usage of Lending and Branch Analysis Utilities

This script demonstrates how to:
1. Connect to BigQuery
2. Execute queries
3. Save results to CSV
4. Work with crosswalk files
5. Share data with the AI assistant
"""

import sys
import os

# Add parent directory to path to import utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils import create_client, save_crosswalk, load_crosswalk
from queries import hmda_queries, branch_queries


def example_basic_query():
    """Example: Execute a basic query and save results"""
    print("="*80)
    print("EXAMPLE 1: Basic Query Execution")
    print("="*80)
    
    # Create BigQuery client
    client = create_client()
    
    # Get a query from query templates
    query = hmda_queries.get_lender_activity_by_year(year=2024, lender_lei=None)
    
    # Execute query and save to CSV
    output_path = "data/lender_activity_2024.csv"
    df = client.query_to_csv(query, output_path)
    
    print(f"\n✓ Results saved to: {output_path}")
    print(f"  Preview:")
    print(df.head())
    return df


def example_cbsa_analysis():
    """Example: Analyze lending patterns for a specific CBSA"""
    print("\n" + "="*80)
    print("EXAMPLE 2: CBSA Lending Analysis")
    print("="*80)
    
    client = create_client()
    
    # Query for a specific CBSA (example: Montgomery, AL)
    cbsa_code = "33860"
    query = hmda_queries.get_cbsa_lending_patterns(cbsa_code=cbsa_code, year=2024)
    
    output_path = "data/montgomery_al_lending_2024.csv"
    df = client.query_to_csv(query, output_path)
    
    print(f"\n✓ Results saved to: {output_path}")
    return df


def example_crosswalk_usage():
    """Example: Working with crosswalk files"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Crosswalk File Usage")
    print("="*80)
    
    # Load existing crosswalk
    try:
        crosswalk = load_crosswalk("../CBSA_to_County_Mapping.csv")
        print(f"\n✓ Loaded crosswalk with {len(crosswalk):,} rows")
        print(f"  Columns: {list(crosswalk.columns)}")
    except FileNotFoundError:
        print("  Crosswalk file not found - this is okay for the example")
        # Create a simple example crosswalk
        import pandas as pd
        crosswalk = pd.DataFrame({
            'cbsa_code': ['33860', '19300'],
            'cbsa_name': ['Montgomery AL', 'Daphne-Fairhope-Foley AL'],
            'county_code': ['01001', '01003']
        })
        print("  Created example crosswalk")
    
    # Save a crosswalk (this is how you share crosswalks with me!-->)
    output_path = "data/example_crosswalk.csv"
    save_crosswalk(crosswalk, output_path)
    
    print(f"\n✓ Example crosswalk saved to: {output_path}")
    print("\n  TIP: You can create any crosswalk file and save it like this.")
    print("       Then share the CSV file with me, and I can load it!")


def example_branch_analysis():
    """Example: Branch data analysis"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Branch Analysis")
    print("="*80)
    
    client = create_client()
    
    # Get branch data for a CBSA
    cbsa_code = "33860"
    query = branch_queries.get_branches_by_cbsa(cbsa_code=cbsa_code, year=2024)
    
    output_path = "data/montgomery_branches_2024.csv"
    df = client.query_to_csv(query, output_path)
    
    print(f"\n✓ Results saved to: {output_path}")
    return df


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("LENDING AND BRANCH ANALYSIS - EXAMPLE USAGE")
    print("="*80)
    print("\nThis script demonstrates how to use the utilities to query BigQuery")
    print("and save data that can be shared with the AI assistant.")
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    try:
        # Run examples (comment out any you don't want to run)
        example_basic_query()
        example_cbsa_analysis()
        example_crosswalk_usage()
        example_branch_analysis()
        
        print("\n" + "="*80)
        print("ALL EXAMPLES COMPLETED!")
        print("="*80)
        print("\n✓ Check the 'data/' directory for CSV files")
        print("✓ You can share these CSV files with the AI assistant")
        print("✓ The assistant can load them and help with analysis")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

