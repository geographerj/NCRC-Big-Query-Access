"""
Interactive Member Report Generator

Generates reports after prompting user for required information.
"""

import sys
import os
from pathlib import Path

# Import the setup and generation scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.setup_new_report import (
    prompt_for_metadata,
    prompt_for_location,
    prompt_for_years,
    prompt_for_lender,
    prompt_for_filters,
    create_config_file
)

# Import generation script functions
from scripts.generate_member_report import (
    load_config,
    query_hmda_data,
    generate_reports
)


def main():
    """Interactive report generation"""
    print("\n" + "="*80)
    print("NCRC MEMBER REPORT GENERATOR")
    print("="*80)
    print("\nThis script will:")
    print("  1. Prompt you for filters, location, and years")
    print("  2. Query data from BigQuery")
    print("  3. Generate PDF and Excel reports")
    
    # Step 1: Collect information
    print("\n" + "="*80)
    print("STEP 1: COLLECT REPORT PARAMETERS")
    print("="*80)
    
    metadata = prompt_for_metadata()
    geography = prompt_for_location()
    years = prompt_for_years()
    lender = prompt_for_lender()
    filters = prompt_for_filters()
    
    # Build configuration
    metadata["years"] = years
    metadata["date_range"] = {
        "start_year": min(years),
        "end_year": max(years)
    }
    
    config = {
        "report_metadata": metadata,
        "geography": geography,
        "subject_lender": lender,
        "loan_filters": filters,
        "metrics": {
            "borrower_demographics": {
                "enabled": True,
                "include": ["hispanic", "black", "asian"]
            },
            "income_metrics": {
                "enabled": True,
                "include": ["lmib_percentage", "lmict_percentage"]
            },
            "redlining": {
                "enabled": True,
                "include": ["mmct_50", "mmct_80"]
            }
        },
        "peer_definition": {
            "enabled": False,
            "method": "all_other_lenders"
        },
        "analysis_options": {
            "group_by_loan_purpose": False,
            "show_time_series": True,
            "show_peer_comparison": True,
            "statistical_significance": True,
            "significance_level": 0.05
        },
        "output": {
            "format": "both",
            "output_directory": "outputs/excel",
            "include_methods_sheet": True,
            "include_raw_data": True
        },
        "data_sources": {
            "hmda_table": "hdma1-242116.hmda.hmda",
            "geo_table": "hdma1-242116.geo.black_hispanic_majority",
            "cbsa_crosswalk": "hdma1-242116.geo.cbsa_to_county"
        }
    }
    
    # Save config temporarily
    temp_config_path = Path("configs") / f"{metadata['report_id']}_temp.json"
    temp_config_path.parent.mkdir(exist_ok=True)
    create_config_file(str(temp_config_path), config)
    
    # Step 2: Confirm before proceeding
    print("\n" + "="*80)
    print("CONFIGURATION SUMMARY")
    print("="*80)
    print(f"  Report Title: {metadata['report_title']}")
    print(f"  Member Organization: {metadata.get('member_organization', 'N/A')}")
    print(f"  Geography: {geography['type']} - {geography.get('cbsa_codes', geography.get('county_codes', 'See config'))}")
    print(f"  Years: {', '.join(map(str, years))}")
    print(f"  Subject Lender: {lender.get('lei') or lender.get('rssd') or lender.get('name') or 'All Lenders'}")
    print(f"  Loan Filters: {'Home Purchase' if filters.get('loan_purpose') == '1' else 'All Loans'}")
    
    confirm = input("\nProceed with report generation? (Y/n): ").strip().lower()
    if confirm == 'n':
        print("\nReport generation cancelled.")
        return
    
    # Step 3: Generate report
    print("\n" + "="*80)
    print("STEP 2: GENERATING REPORT")
    print("="*80)
    
    try:
        # Import BigQuery client
        from utils.bigquery_client import create_client
        import pandas as pd
        
        # Connect to BigQuery
        print("\nConnecting to BigQuery...")
        creds_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                  'config', 'credentials', 'hdma1-242116-74024e2eb88f.json')
        if not os.path.exists(creds_path):
            creds_path = None
        
        client = create_client(key_path=creds_path)
        
        # Query data
        hmda_data = query_hmda_data(config, client)
        
        # Save raw data
        raw_data_path = os.path.join('data', 'raw', f"{metadata['report_id']}_raw.csv")
        os.makedirs(os.path.dirname(raw_data_path), exist_ok=True)
        hmda_data.to_csv(raw_data_path, index=False)
        print(f"\n✓ Raw data saved: {raw_data_path}")
        
        # Generate reports
        output_dir = config['output']['output_directory']
        os.makedirs(output_dir, exist_ok=True)
        
        pdf_path, excel_path = generate_reports(config, hmda_data, output_dir)
        
        print("\n" + "="*80)
        print("REPORT GENERATION COMPLETE!")
        print("="*80)
        print(f"\nPDF Report: {pdf_path}")
        print(f"Excel Report: {excel_path}")
        print(f"Raw Data: {raw_data_path}")
        print(f"Configuration: {temp_config_path}")
        
    except Exception as e:
        print(f"\n❌ Error during report generation: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Clean up temp config or ask to keep
    keep_config = input("\nKeep configuration file? (Y/n): ").strip().lower()
    if keep_config != 'n':
        final_config_path = Path("configs") / f"{metadata['report_id']}.json"
        temp_config_path.rename(final_config_path)
        print(f"✓ Configuration saved to: {final_config_path}")
    else:
        temp_config_path.unlink()
        print("✓ Temporary configuration file removed")


if __name__ == '__main__':
    main()

