"""
Main Script to Generate Member Reports

Generates both PDF and Excel reports from configuration file.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import argparse

# Add Member Reports directory to path
member_reports_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, member_reports_dir)

# Also add parent directory for Lending and Branch Analysis utils
parent_dir = os.path.dirname(member_reports_dir)
sys.path.insert(0, str(parent_dir))

# Import with proper path handling
import importlib.util

# Load modules dynamically
def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load query builder
queries_module = load_module('member_report_queries', 
                            os.path.join(member_reports_dir, 'queries', 'member_report_queries.py'))
build_member_report_query = queries_module.build_member_report_query

# Load generators
pdf_gen = load_module('pdf_generator',
                     os.path.join(member_reports_dir, 'generators', 'pdf_generator.py'))
PDFReportGenerator = pdf_gen.PDFReportGenerator

excel_gen = load_module('excel_generator',
                       os.path.join(member_reports_dir, 'generators', 'excel_generator.py'))
ExcelReportGenerator = excel_gen.ExcelReportGenerator

data_proc = load_module('data_processor',
                        os.path.join(member_reports_dir, 'generators', 'data_processor.py'))
MemberReportDataProcessor = data_proc.MemberReportDataProcessor

# Load BigQuery client
bq_client = load_module('bigquery_client',
                        os.path.join(member_reports_dir, 'utils', 'bigquery_client.py'))
create_client = bq_client.create_client

import pandas as pd


def load_config(config_path: str) -> dict:
    """Load report configuration from JSON file"""
    with open(config_path, 'r') as f:
        return json.load(f)


def query_hmda_data(config: dict, client) -> 'pd.DataFrame':
    """Query HMDA data from BigQuery"""
    import pandas as pd
    
    query = build_member_report_query(config)
    
    print("Executing BigQuery query...")
    print(f"Query length: {len(query)} characters")
    
    df = client.execute_query(query)
    
    print(f"Query completed: {len(df):,} rows returned")
    return df


def generate_reports(config: dict, hmda_data: 'pd.DataFrame', output_dir: str):
    """Generate both PDF and Excel reports"""
    metadata = config.get('report_metadata', {})
    report_id = metadata.get('report_id', 'MEMBER_REPORT')
    report_title = metadata.get('report_title', 'Member Report')
    member_org = metadata.get('member_organization')
    report_date = metadata.get('report_date', datetime.now().strftime('%Y-%m-%d'))
    
    # Process data
    print("\nProcessing data...")
    processor = MemberReportDataProcessor()
    report_data = processor.process_report_data(hmda_data, config)
    
    # Generate PDF
    print("\nGenerating PDF report...")
    pdf_generator = PDFReportGenerator()
    pdf_path = os.path.join(output_dir, f"{report_id}_Report.pdf")
    pdf_generator.generate_report(
        pdf_path,
        report_title,
        report_data,
        member_org,
        report_date
    )
    print(f"PDF report saved: {pdf_path}")
    
    # Generate Excel
    print("\nGenerating Excel report...")
    excel_generator = ExcelReportGenerator()
    excel_path = os.path.join(output_dir, f"{report_id}_Data.xlsx")
    excel_generator.generate_report(
        excel_path,
        report_title,
        report_data,
        member_org,
        report_date
    )
    print(f"Excel report saved: {excel_path}")
    
    return pdf_path, excel_path


def validate_config(config: dict) -> bool:
    """Validate that required configuration fields are present"""
    required_fields = [
        ('report_metadata', 'years'),
        ('geography', 'type'),
        ('subject_lender', None),  # At least one identifier should be present
    ]
    
    errors = []
    
    # Check metadata
    if 'report_metadata' not in config:
        errors.append("Missing 'report_metadata' section")
    elif 'years' not in config['report_metadata']:
        errors.append("Missing 'years' in report_metadata")
    elif not config['report_metadata']['years']:
        errors.append("'years' list is empty")
    
    # Check geography
    if 'geography' not in config:
        errors.append("Missing 'geography' section")
    elif 'type' not in config['geography']:
        errors.append("Missing 'type' in geography")
    else:
        geo_type = config['geography']['type']
        if geo_type == 'cbsa':
            if not (config['geography'].get('cbsa_codes') or config['geography'].get('cbsa_names')):
                errors.append("Geography type is 'cbsa' but no cbsa_codes or cbsa_names provided")
        elif geo_type == 'county':
            if not config['geography'].get('county_codes'):
                errors.append("Geography type is 'county' but no county_codes provided")
        elif geo_type == 'custom':
            if not config['geography'].get('custom_filter'):
                errors.append("Geography type is 'custom' but no custom_filter provided")
    
    # Check subject lender (at least one identifier)
    if 'subject_lender' not in config:
        errors.append("Missing 'subject_lender' section")
    else:
        lender = config['subject_lender']
        if not (lender.get('lei') or lender.get('rssd') or lender.get('name')):
            errors.append("No lender identifier provided (need lei, rssd, or name)")
    
    if errors:
        print("\n" + "="*80)
        print("CONFIGURATION ERRORS")
        print("="*80)
        for error in errors:
            print(f"  ❌ {error}")
        print("\nPlease run: python scripts/setup_new_report.py")
        print("Or edit your configuration file to fix these issues.")
        return False
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Generate NCRC Member Report')
    parser.add_argument('--config', type=str, required=False,
                       help='Path to configuration JSON file')
    parser.add_argument('--output-dir', type=str, default=None,
                       help='Output directory (default: outputs/excel)')
    parser.add_argument('--query-only', action='store_true',
                       help='Only query data, do not generate reports')
    parser.add_argument('--interactive', action='store_true',
                       help='Run in interactive mode (prompt for all parameters)')
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive:
        # Import and run interactive script
        interactive_script = os.path.join(os.path.dirname(__file__), 'generate_member_report_interactive.py')
        import subprocess
        subprocess.run([sys.executable, interactive_script])
        return
    
    # Check if config provided
    if not args.config:
        print("\n" + "="*80)
        print("CONFIGURATION FILE REQUIRED")
        print("="*80)
        print("\nPlease provide a configuration file:")
        print("  python scripts/generate_member_report.py --config configs/your_config.json")
        print("\nOr run in interactive mode:")
        print("  python scripts/generate_member_report.py --interactive")
        print("\nOr setup a new configuration:")
        print("  python scripts/setup_new_report.py")
        return
    
    # Load configuration
    print("Loading configuration...")
    config = load_config(args.config)
    
    # Validate configuration
    if not validate_config(config):
        return
    
    # Set output directory
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = config.get('output', {}).get('output_directory', 'outputs/excel')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Connect to BigQuery
    print("\nConnecting to BigQuery...")
    creds_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                              'config', 'credentials', 'hdma1-242116-74024e2eb88f.json')
    if not os.path.exists(creds_path):
        creds_path = None  # Use default
    
    client = create_client(key_path=creds_path)
    
    # Query data
    hmda_data = query_hmda_data(config, client)
    
    # Save raw data
    raw_data_path = os.path.join('data', 'raw', f"{config['report_metadata']['report_id']}_raw.csv")
    os.makedirs(os.path.dirname(raw_data_path), exist_ok=True)
    hmda_data.to_csv(raw_data_path, index=False)
    print(f"Raw data saved: {raw_data_path}")
    
    if args.query_only:
        print("\nQuery-only mode: Skipping report generation")
        return
    
    # Generate reports
    pdf_path, excel_path = generate_reports(config, hmda_data, output_dir)
    
    print("\n" + "="*80)
    print("REPORT GENERATION COMPLETE!")
    print("="*80)
    print(f"\nPDF Report: {pdf_path}")
    print(f"Excel Report: {excel_path}")
    print(f"Raw Data: {raw_data_path}")


if __name__ == '__main__':
    main()

