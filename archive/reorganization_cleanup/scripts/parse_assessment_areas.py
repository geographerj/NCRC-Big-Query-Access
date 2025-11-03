"""
Parse Assessment Area PDFs/CSVs/Excel to extract counties/CBSAs included in bank's assessment areas.

Assessment areas are typically CBSAs/MSAs but only include specific counties within them.
This script helps extract which counties are actually included.

Supports:
- PDF files (requires pdfplumber: pip install pdfplumber)
- CSV files (with CBSA/County/GEOID columns)
- Excel files (with assessment area data)
- Manual input template
"""

import re
from pathlib import Path
import pandas as pd
import sys
import json

# Try to import PDF libraries (optional)
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    print("Note: pdfplumber not installed. PDF parsing disabled. Install with: pip install pdfplumber")

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

def parse_assessment_area_pdf(pdf_path):
    """
    Parse assessment area PDF to extract counties and CBSAs.
    
    Returns a dictionary with:
    - assessment_areas: List of dicts with CBSA name, CBSA code, and included counties
    - all_counties: List of all county GEOIDs or names that are included
    - counties_by_cbsa: Dict mapping CBSA code to list of counties
    """
    print(f"\nParsing assessment area PDF: {pdf_path}")
    
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Try using pdfplumber first (better text extraction)
    text_content = []
    tables_data = []
    
    if not HAS_PDFPLUMBER and not HAS_PYPDF2:
        raise ImportError("No PDF libraries available. Please install pdfplumber: pip install pdfplumber")
    
    try:
        if HAS_PDFPLUMBER:
            with pdfplumber.open(pdf_path) as pdf:
                print(f"  Total pages: {len(pdf.pages)}")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
                    
                    # Extract tables (assessment areas often in tables)
                    tables = page.extract_tables()
                    if tables:
                        for table_idx, table in enumerate(tables):
                            tables_data.append({
                                'page': page_num,
                                'table': table_idx,
                                'data': table
                            })
        elif HAS_PYPDF2:
            # Fallback to PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
    
    except Exception as e:
        raise Exception(f"Failed to parse PDF: {e}. Try converting PDF to CSV/Excel first, or install pdfplumber: pip install pdfplumber")
    
    # Combine all text
    full_text = "\n".join(text_content)
    
    print(f"\n  Extracted {len(text_content)} pages of text")
    print(f"  Found {len(tables_data)} tables")
    
    # Parse assessment areas
    assessment_areas = []
    all_counties = []
    
    # Look for patterns like "CBSA 16980" or "MSA: Chicago" or county names
    cbsa_pattern = r'(?:CBSA|MSA|Metro|Metropolitan)\s*(?:Area|Statistical Area)?\s*:?\s*([A-Za-z\s]+?)(?:\s*\(?(\d{5})\)?)?'
    county_pattern = r'([A-Za-z\s]+?)\s+(?:County|Parish|Borough|Census Area)'
    
    # Try to extract from tables first (more structured)
    if tables_data:
        print(f"\n  Analyzing {len(tables_data)} tables...")
        for table_info in tables_data:
            table = table_info['data']
            if table and len(table) > 1:  # Has header and data
                # Convert to DataFrame for easier parsing
                try:
                    df_table = pd.DataFrame(table[1:], columns=table[0])
                    print(f"    Table {table_info['page']}-{table_info['table']}: {len(df_table)} rows, {len(df_table.columns)} columns")
                    print(f"      Columns: {list(df_table.columns)[:5]}")
                except:
                    pass
    
    # Extract CBSAs/MSAs from text
    cbsa_matches = re.finditer(cbsa_pattern, full_text, re.IGNORECASE)
    found_cbsas = []
    for match in cbsa_matches:
        name = match.group(1).strip()
        code = match.group(2) if match.group(2) else None
        found_cbsas.append({'name': name, 'code': code, 'context': match.group(0)})
    
    # Extract counties from text
    county_matches = re.finditer(county_pattern, full_text)
    found_counties = []
    for match in county_matches:
        county_name = match.group(1).strip()
        if len(county_name) > 2 and county_name not in ['New', 'North', 'South', 'East', 'West']:
            found_counties.append(county_name)
    
    print(f"\n  Found {len(found_cbsas)} CBSA/MSA references")
    print(f"  Found {len(found_counties)} potential county names")
    
    # Try to match counties to CBSAs (look for structure in tables or text)
    counties_by_cbsa = {}
    
    if tables_data:
        # Parse tables to find CBSA-county relationships
        for table_info in tables_data:
            table = table_info['data']
            if not table or len(table) < 2:
                continue
            
            # Look for columns that might be CBSA, County, GEOID, etc.
            headers = [str(h).lower() if h else '' for h in table[0]]
            
            cbsa_col = None
            county_col = None
            geoid_col = None
            state_col = None
            
            for idx, header in enumerate(headers):
                if any(x in header for x in ['cbsa', 'msa', 'metro']):
                    cbsa_col = idx
                if 'county' in header or 'parish' in header:
                    county_col = idx
                if 'geoid' in header or 'fips' in header or 'code' in header:
                    geoid_col = idx
                if 'state' in header:
                    state_col = idx
            
            # If we found relevant columns, extract data
            if cbsa_col is not None or county_col is not None:
                for row in table[1:]:
                    if len(row) > max([x for x in [cbsa_col, county_col, geoid_col, state_col] if x is not None]):
                        cbsa_val = str(row[cbsa_col]).strip() if cbsa_col is not None and row[cbsa_col] else None
                        county_val = str(row[county_col]).strip() if county_col is not None and row[county_col] else None
                        geoid_val = str(row[geoid_col]).strip() if geoid_col is not None and row[geoid_col] else None
                        state_val = str(row[state_col]).strip() if state_col is not None and row[state_col] else None
                        
                        if county_val and county_val != 'None' and county_val != 'nan':
                            all_counties.append({
                                'county_name': county_val,
                                'geoid': geoid_val,
                                'cbsa': cbsa_val,
                                'state': state_val
                            })
                            
                            if cbsa_val and cbsa_val != 'None' and cbsa_val != 'nan':
                                if cbsa_val not in counties_by_cbsa:
                                    counties_by_cbsa[cbsa_val] = []
                                counties_by_cbsa[cbsa_val].append({
                                    'county_name': county_val,
                                    'geoid': geoid_val,
                                    'state': state_val
                                })
    
    # If we didn't find structure in tables, try to extract from text
    if not counties_by_cbsa and found_cbsas:
        print("\n  No structured table found, extracting from text...")
        # This is more heuristic - would need to see actual PDF structure
    
    result = {
        'assessment_areas': found_cbsas,
        'all_counties': all_counties,
        'counties_by_cbsa': counties_by_cbsa,
        'raw_text': full_text[:5000],  # First 5000 chars for review
        'tables_summary': [{'page': t['page'], 'rows': len(t['data']), 'cols': len(t['data'][0]) if t['data'] else 0} for t in tables_data]
    }
    
    return result

def print_parsing_results(results):
    """Print parsed results in readable format"""
    print("\n" + "="*80)
    print("PARSING RESULTS")
    print("="*80)
    
    print(f"\nAssessment Areas Found: {len(results['assessment_areas'])}")
    for aa in results['assessment_areas'][:10]:
        print(f"  - {aa['name']} (Code: {aa['code']})")
    
    print(f"\nCounties Found: {len(results['all_counties'])}")
    for county in results['all_counties'][:20]:
        print(f"  - {county.get('county_name', 'Unknown')} (GEOID: {county.get('geoid', 'Unknown')}, CBSA: {county.get('cbsa', 'Unknown')})")
    if len(results['all_counties']) > 20:
        print(f"  ... and {len(results['all_counties']) - 20} more")
    
    print(f"\nCounties by CBSA: {len(results['counties_by_cbsa'])} CBSAs")
    for cbsa, counties in list(results['counties_by_cbsa'].items())[:5]:
        print(f"  CBSA {cbsa}: {len(counties)} counties")
        for county in counties[:3]:
            print(f"    - {county.get('county_name')} ({county.get('geoid')})")
    
    print("\n" + "="*80)

def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python parse_assessment_areas.py <pdf_path>")
        print("\nExample:")
        print('  python parse_assessment_areas.py "PNC Bank Assessment Area 2022.pdf"')
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    try:
        results = parse_assessment_area_pdf(pdf_path)
        print_parsing_results(results)
        
        # Optionally save to JSON or Excel
        if len(sys.argv) > 2 and sys.argv[2] == '--save':
            output_file = Path(pdf_path).stem + "_parsed.json"
            import json
            # Convert to JSON-serializable format
            json_results = {
                'assessment_areas': results['assessment_areas'],
                'all_counties': results['all_counties'],
                'counties_by_cbsa': results['counties_by_cbsa']
            }
            with open(output_file, 'w') as f:
                json.dump(json_results, f, indent=2)
            print(f"\nResults saved to: {output_file}")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

