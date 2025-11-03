"""
Extract assessment areas from PDF documents.
Handles different PDF formats (PNC vs FirstBank) and extracts:
- CBSA codes and names
- County names
- State codes
- County codes (GEOIDs) when available
"""

import pdfplumber
from pathlib import Path
import sys
import json
import re
import pandas as pd

def extract_counties_from_text(text, state_code=None):
    """
    Extract county names from text using patterns.
    Counties typically appear as "County Name County, State" or "County Name, State"
    """
    counties = []
    
    # Pattern 1: "County Name County, State" (e.g., "Dallas County, Alabama")
    pattern1 = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+County,\s+([A-Z]{2})'
    matches1 = re.finditer(pattern1, text)
    for match in matches1:
        county_name = match.group(1).strip()
        state = match.group(2).strip()
        counties.append({
            'county_name': county_name,
            'state_code': state,
            'pattern': 'County, State'
        })
    
    # Pattern 2: "County Name, State" (e.g., "Maricopa, Arizona")
    pattern2 = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s+([A-Z]{2}|[A-Z][a-z]+)'
    matches2 = re.finditer(pattern2, text)
    for match in matches2:
        county_name = match.group(1).strip()
        state = match.group(2).strip()
        # Skip if it's obviously not a county
        if county_name.lower() not in ['state', 'county', 'msa', 'cbsa', 'area']:
            counties.append({
                'county_name': county_name,
                'state_code': state if len(state) == 2 else None,
                'state_name': state if len(state) > 2 else None,
                'pattern': 'Name, State'
            })
    
    return counties

def extract_cbsa_codes_from_text(text):
    """Extract CBSA codes from text"""
    # Pattern: 5-digit numbers that are likely CBSA codes
    pattern = r'\b(\d{5})\b'
    matches = re.finditer(pattern, text)
    cbsa_codes = []
    
    for match in matches:
        code = match.group(1)
        # CBSA codes are typically in certain ranges, but accept any 5-digit
        # Could add validation later
        cbsa_codes.append(code)
    
    return list(set(cbsa_codes))  # Remove duplicates

def parse_pnc_assessment_areas(pdf_path):
    """
    Parse PNC Assessment Areas PDF.
    Based on inspection, this appears to contain Small Business loan data by county.
    We need to extract county names and match them to CBSAs.
    """
    print(f"\nParsing PNC Assessment Areas PDF...")
    
    assessment_areas = []
    counties_found = []
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"  Total pages: {len(pdf.pages)}")
        
        # Extract text from all pages
        full_text = ""
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                full_text += "\n" + text
        
        # Look for state headers (e.g., "State: ARIZONA (04)")
        state_pattern = r'State:\s+([A-Z]+)\s+\((\d{2})\)'
        state_matches = re.finditer(state_pattern, full_text)
        
        current_state = None
        current_state_code = None
        
        # Extract counties by state
        for state_match in state_matches:
            state_name = state_match.group(1)
            state_code = state_match.group(2)
            current_state = state_name
            current_state_code = state_code
            
            # Find counties in this section
            # Look for county names in the text following state header
            # Counties often appear in table-like structures
        
        # Alternative: Extract all county patterns
        counties = extract_counties_from_text(full_text)
        
        # Extract CBSA codes
        cbsa_codes = extract_cbsa_codes_from_text(full_text)
        
        print(f"  Found {len(counties)} potential counties")
        print(f"  Found {len(cbsa_codes)} CBSA codes")
        
        # Show sample
        if counties:
            print(f"\n  Sample counties:")
            for county in counties[:10]:
                print(f"    - {county['county_name']}, {county.get('state_code', 'N/A')}")
        
        if cbsa_codes:
            print(f"\n  Sample CBSA codes:")
            for code in cbsa_codes[:10]:
                print(f"    - {code}")
        
        counties_found = counties
    
    return {
        'bank': 'PNC',
        'assessment_areas': assessment_areas,
        'counties': counties_found,
        'cbsa_codes': cbsa_codes,
        'text_length': len(full_text)
    }

def parse_firstbank_assessment_areas(pdf_path):
    """
    Parse FirstBank Assessment Areas PDF.
    Based on inspection, this is a single-page CRA Performance Evaluation document.
    """
    print(f"\nParsing FirstBank Assessment Areas PDF...")
    
    assessment_areas = []
    counties_found = []
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"  Total pages: {len(pdf.pages)}")
        
        # Extract text and tables from first page
        page = pdf.pages[0]
        text = page.extract_text()
        
        # Extract tables
        tables = page.extract_tables()
        
        if tables:
            print(f"  Found {len(tables)} tables")
            
            for table_idx, table in enumerate(tables):
                if table and len(table) > 1:
                    print(f"  Table {table_idx + 1}: {len(table)} rows, {len(table[0])} columns")
                    
                    # Try to find CBSA/county information in table
                    for row in table:
                        row_text = ' '.join([str(cell) if cell else '' for cell in row])
                        if row_text:
                            # Look for CBSA codes
                            cbsa_matches = re.finditer(r'\b(\d{5})\b', row_text)
                            for match in cbsa_matches:
                                code = match.group(1)
                                if code != '99999':  # Skip placeholder
                                    print(f"    Found CBSA code: {code}")
        
        # Extract from text as well
        counties = extract_counties_from_text(text)
        cbsa_codes = extract_cbsa_codes_from_text(text)
        
        print(f"  Found {len(counties)} potential counties")
        print(f"  Found {len(cbsa_codes)} CBSA codes")
        
        if counties:
            print(f"\n  Sample counties:")
            for county in counties[:10]:
                print(f"    - {county['county_name']}, {county.get('state_code', 'N/A')}")
        
        counties_found = counties
    
    return {
        'bank': 'FirstBank',
        'assessment_areas': assessment_areas,
        'counties': counties_found,
        'cbsa_codes': cbsa_codes,
        'text_length': len(text) if text else 0,
        'table_count': len(tables) if tables else 0
    }

def main():
    """Main function - parse both PDFs"""
    if len(sys.argv) < 3:
        print("Usage: python extract_assessment_areas_from_pdfs.py <pnc_pdf> <firstbank_pdf>")
        print("\nExample:")
        print('  python extract_assessment_areas_from_pdfs.py "PNC Assessment Areas.pdf" "Firstbank Assessment Areas 2023.pdf"')
        sys.exit(1)
    
    pnc_pdf = sys.argv[1]
    firstbank_pdf = sys.argv[2]
    
    try:
        pnc_results = parse_pnc_assessment_areas(pnc_pdf)
        firstbank_results = parse_firstbank_assessment_areas(firstbank_pdf)
        
        # Combine results
        combined = {
            'pnc': pnc_results,
            'firstbank': firstbank_results
        }
        
        # Save results
        output_file = Path(pnc_pdf).parent / "assessment_areas_extracted.json"
        with open(output_file, 'w') as f:
            json.dump(combined, f, indent=2)
        
        print(f"\n\nResults saved to: {output_file}")
        print(f"\nNote: County-to-CBSA mapping may need manual review or crosswalk lookup.")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()


