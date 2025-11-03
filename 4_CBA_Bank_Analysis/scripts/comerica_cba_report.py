"""
Comerica Bank CBA Borrower Demographics Report Generator

Creates an Excel report with one sheet per CBSA showing borrower demographic metrics.
Same format as Fifth Third report.

Input: CSV from BigQuery with Comerica borrower demographics data
Output: Excel workbook with one sheet per CBSA + Methods sheet
"""

import sys
import os

# Import from Fifth Third script (same logic, different bank)
# We'll reuse the same functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all the functions from fifth_third_cba_report
# Note: Using importlib for numbered module name (02_fifth_third_cba_report.py)
import importlib.util
_ft_path = os.path.join(os.path.dirname(__file__), "02_fifth_third_cba_report.py")
_spec = importlib.util.spec_from_file_location("ft_cba", _ft_path)
_ft_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ft_module)
# Import the needed functions
from ft_cba import (
    load_data,
    add_calculated_metrics,
    create_excel_workbook,
    EXPECTED_YEARS,
    METRIC_GROUPS,
    SIGNIFICANCE_LEVEL
)

def main():
    import argparse
    import glob
    
    parser = argparse.ArgumentParser(
        description='Comerica Bank CBA Combined Report Generator (Redlining + Demographics)'
    )
    parser.add_argument('--input', type=str, 
                       help='Input CSV file from BigQuery (redlining or demographics)')
    parser.add_argument('--input2', type=str,
                       help='Second CSV file from BigQuery to merge (optional)')
    parser.add_argument('--output', type=str, 
                       default='Comerica_CBA_Report.xlsx',
                       help='Output Excel file name')
    
    args = parser.parse_args()
    
    # Set up folder structure
    reports_dir = os.path.join(os.getcwd(), 'reports', 'comerica')
    data_dir = os.path.join(os.getcwd(), 'data', 'raw')
    
    # Create folders if they don't exist
    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    
    print("="*80)
    print("COMERICA BANK CBA COMBINED REPORT GENERATOR")
    print("Combines Redlining (Tract Demographics) + Borrower Demographics")
    print("="*80)
    print(f"Working Directory: {os.getcwd()}")
    print(f"Reports Folder: {reports_dir}")
    print(f"Data Folder: {data_dir}")
    
    # Find input file(s) - prioritize Comerica-specific files
    if args.input:
        if os.path.exists(args.input):
            input_file = args.input
        elif os.path.exists(os.path.join(data_dir, args.input)):
            input_file = os.path.join(data_dir, args.input)
        else:
            print(f"ERROR: Input file not found: {args.input}")
            sys.exit(1)
    else:
        # Look for Comerica files first
        comerica_files = [
            os.path.join(data_dir, 'comerica_demographics.csv'),
            os.path.join(data_dir, 'comerica_redlining.csv')
        ]
        
        # Check which Comerica files exist
        existing_comerica = [f for f in comerica_files if os.path.exists(f)]
        
        if len(existing_comerica) >= 2:
            # Use Comerica files
            input_file = comerica_files[0]  # demographics
            second_file = comerica_files[1]  # redlining
            print(f"Using Comerica data files:")
            print(f"  Input file: {input_file}")
            print(f"  Second file: {second_file}")
        else:
            # Fallback to auto-detect
            csv_files = glob.glob('bquxjob_*.csv') + glob.glob(os.path.join(data_dir, 'bquxjob_*.csv'))
            if len(csv_files) == 0:
                print(f"ERROR: No CSV files found")
                print(f"Looking for: {comerica_files}")
                sys.exit(1)
            
            csv_files.sort(key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, reverse=True)
            input_file = csv_files[0]
            print(f"Auto-detected input file: {input_file}")
    
    # Find second file if not specified and not already set
    if 'second_file' not in locals() or second_file is None:
        if args.input2:
            if os.path.exists(args.input2):
                second_file = args.input2
            elif os.path.exists(os.path.join(data_dir, args.input2)):
                second_file = os.path.join(data_dir, args.input2)
            else:
                print(f"WARNING: Second file not found: {args.input2}")
        else:
            # If we already have comerica files, use them
            if not existing_comerica:
                csv_files = glob.glob('bquxjob_*.csv') + glob.glob(os.path.join(data_dir, 'bquxjob_*.csv'))
                if len(csv_files) >= 2:
                    csv_files.sort(key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, reverse=True)
                    if csv_files[1] != input_file:
                        second_file = csv_files[1]
                        print(f"Auto-detected second file: {second_file}")
    
    # Set output file path
    if args.output:
        if os.path.isabs(args.output):
            output_file = args.output
        else:
            output_file = os.path.join(reports_dir, args.output)
    else:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(reports_dir, f'Comerica_CBA_Report_{timestamp}.xlsx')
    
    # Load and process data
    df = load_data(input_file, second_file)
    df = add_calculated_metrics(df)
    
    # Update methodology text for Comerica
    # (The create_excel_workbook function will use methodology from fifth_third script,
    # but we can override if needed)
    
    # Create Excel workbook
    create_excel_workbook(df, output_file)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print(f"\nOutput file: {output_file}")
    print(f"Saved to: {reports_dir}")

if __name__ == "__main__":
    main()

