"""
Interactive Script to Setup New Member Report

Prompts user for required information:
- Filters (loan type, purpose, etc.)
- Location (CBSA, counties, etc.)
- Years
- Subject lender (LEI)
- Member organization
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import argparse


def prompt_for_filters() -> dict:
    """Prompt user for loan filters"""
    print("\n" + "="*80)
    print("LOAN FILTERS")
    print("="*80)
    
    filters = {
        "standard_hmda_filters": True,
        "loan_purpose": None,
        "occupancy_type": "1",
        "reverse_mortgage": "exclude",
        "construction_method": "1",
        "total_units": [1, 2, 3, 4],
        "action_taken": "1"
    }
    
    # Loan purpose
    print("\nLoan Purpose:")
    print("  1 = Home Purchase only")
    print("  2 = (blank = all loan purposes)")
    purpose = input("  Enter loan purpose (1 for home purchase, Enter for all): ").strip()
    filters["loan_purpose"] = purpose if purpose else None
    
    # Confirm standard filters
    print("\nStandard HMDA Filters:")
    print("  - Owner-occupied (occupancy_type = '1')")
    print("  - Reverse mortgages excluded")
    print("  - Site-built (construction_method = '1')")
    print("  - 1-4 units")
    print("  - Originations only (action_taken = '1')")
    confirm = input("  Use standard filters? (Y/n): ").strip().lower()
    if confirm == 'n':
        filters["standard_hmda_filters"] = False
        print("\n  Custom filter configuration required - edit config file manually")
    
    return filters


def prompt_for_location() -> dict:
    """Prompt user for geographic location"""
    print("\n" + "="*80)
    print("GEOGRAPHIC SCOPE")
    print("="*80)
    
    print("\nLocation Type:")
    print("  1 = CBSA (Metro Area)")
    print("  2 = County codes")
    print("  3 = Custom SQL filter")
    
    loc_type = input("  Enter location type (1-3): ").strip()
    
    geography = {"type": "cbsa", "cbsa_codes": [], "county_codes": [], "custom_filter": None}
    
    if loc_type == "1":
        geography["type"] = "cbsa"
        print("\nCBSA Codes:")
        print("  Enter CBSA codes separated by commas (e.g., 35620, 16980)")
        print("  Or enter CBSA names separated by commas")
        cbsa_input = input("  CBSA codes or names: ").strip()
        
        if cbsa_input:
            # Try to determine if codes or names
            items = [x.strip() for x in cbsa_input.split(',')]
            # If all numeric, treat as codes
            if all(item.isdigit() for item in items):
                geography["cbsa_codes"] = items
            else:
                geography["cbsa_names"] = items
    
    elif loc_type == "2":
        geography["type"] = "county"
        print("\nCounty Codes (GEOID5 format):")
        print("  Enter 5-digit county codes separated by commas (e.g., 36047, 36061)")
        county_input = input("  County codes: ").strip()
        
        if county_input:
            geography["county_codes"] = [x.strip() for x in county_input.split(',')]
    
    elif loc_type == "3":
        geography["type"] = "custom"
        print("\nCustom SQL Filter:")
        print("  Enter SQL WHERE clause fragment (e.g., c.cbsa_name LIKE '%New York%')")
        custom_filter = input("  Custom filter: ").strip()
        geography["custom_filter"] = custom_filter if custom_filter else None
    
    return geography


def prompt_for_years() -> list:
    """Prompt user for years to analyze"""
    print("\n" + "="*80)
    print("TIME PERIOD")
    print("="*80)
    
    print("\nYears to Analyze:")
    print("  Enter years separated by commas (e.g., 2018,2019,2020,2021,2022,2023,2024)")
    print("  Or enter range (e.g., 2018-2024)")
    
    years_input = input("  Years: ").strip()
    
    years = []
    if '-' in years_input:
        # Range format
        start, end = years_input.split('-')
        years = list(range(int(start.strip()), int(end.strip()) + 1))
    else:
        # Comma-separated
        years = [int(y.strip()) for y in years_input.split(',') if y.strip().isdigit()]
    
    if not years:
        # Default
        print("  Using default years: 2018-2024")
        years = list(range(2018, 2025))
    
    return sorted(years)


def prompt_for_lender() -> dict:
    """Prompt user for subject lender"""
    print("\n" + "="*80)
    print("SUBJECT LENDER")
    print("="*80)
    
    print("\nLender Identifier:")
    print("  1 = LEI (Legal Entity Identifier) - Preferred")
    print("  2 = RSSD ID")
    print("  3 = Lender Name (requires crosswalk)")
    
    id_type = input("  Enter identifier type (1-3): ").strip()
    
    lender = {"lei": None, "name": None, "rssd": None}
    
    if id_type == "1":
        lei = input("  Enter LEI: ").strip()
        lender["lei"] = lei if lei else None
    
    elif id_type == "2":
        rssd = input("  Enter RSSD ID: ").strip()
        lender["rssd"] = rssd if rssd else None
    
    elif id_type == "3":
        name = input("  Enter Lender Name: ").strip()
        lender["name"] = name if name else None
    
    return lender


def prompt_for_metadata() -> dict:
    """Prompt user for report metadata"""
    print("\n" + "="*80)
    print("REPORT METADATA")
    print("="*80)
    
    report_title = input("\n  Report Title: ").strip()
    if not report_title:
        report_title = "HMDA Fair Lending Analysis"
    
    member_org = input("  Member Organization: ").strip()
    
    report_id = input("  Report ID (e.g., MEMBER_001): ").strip()
    if not report_id:
        report_id = f"MEMBER_{datetime.now().strftime('%Y%m%d')}"
    
    analyst = input("  Analyst Name (Enter for default): ").strip()
    if not analyst:
        analyst = "NCRC Research"
    
    description = input("  Description (optional): ").strip()
    
    return {
        "report_title": report_title,
        "member_organization": member_org,
        "report_id": report_id,
        "report_date": datetime.now().strftime('%Y-%m-%d'),
        "analyst": analyst,
        "description": description
    }


def create_config_file(output_path: str, config: dict):
    """Save configuration to JSON file"""
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"\n✓ Configuration saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Interactive setup for new member report')
    parser.add_argument('--output', type=str, default=None,
                       help='Output config file path (default: configs/[report_id].json)')
    parser.add_argument('--non-interactive', action='store_true',
                       help='Skip prompts and use template')
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("NCRC MEMBER REPORT SETUP")
    print("="*80)
    print("\nThis script will prompt you for the required information to generate")
    print("a member report. Please have ready:")
    print("  - Geographic scope (CBSA codes, county codes, or custom filter)")
    print("  - Years to analyze")
    print("  - Subject lender identifier (LEI preferred)")
    print("  - Loan filters (typically home purchase, standard HMDA filters)")
    
    if args.non_interactive:
        print("\nNon-interactive mode: Using template")
        config = {
            "report_metadata": {
                "report_title": "HMDA Fair Lending Analysis",
                "member_organization": "Member Organization",
                "report_id": f"MEMBER_{datetime.now().strftime('%Y%m%d')}",
                "report_date": datetime.now().strftime('%Y-%m-%d'),
                "analyst": "NCRC Research",
                "description": "Custom report generated for member request"
            },
            "geography": {"type": "cbsa", "cbsa_codes": []},
            "subject_lender": {"lei": None},
            "loan_filters": {
                "standard_hmda_filters": True,
                "loan_purpose": "1",
                "action_taken": "1"
            },
            "report_metadata": {"years": [2018, 2019, 2020, 2021, 2022, 2023, 2024]}
        }
    else:
        # Prompt for information
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
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        report_id = config["report_metadata"].get("report_id", "MEMBER_REPORT")
        config_dir = Path(__file__).parent.parent / "configs"
        config_dir.mkdir(exist_ok=True)
        output_path = config_dir / f"{report_id}.json"
    
    # Save configuration
    create_config_file(str(output_path), config)
    
    print("\n" + "="*80)
    print("SETUP COMPLETE")
    print("="*80)
    print(f"\nConfiguration file created: {output_path}")
    print("\nNext steps:")
    print(f"  1. Review the configuration file if needed")
    print(f"  2. Run: python scripts/generate_member_report.py --config {output_path}")
    print("\n" + "="*80)


if __name__ == '__main__':
    main()

