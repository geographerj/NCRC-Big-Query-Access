"""
Extract Tampa city census tracts from community profile PDF
"""

import pdfplumber
import re

def extract_tampa_tracts(pdf_path):
    """Extract census tract numbers from Tampa community profile"""
    tracts = []
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Reading PDF: {len(pdf.pages)} pages\n")
        
        for page_num, page in enumerate(pdf.pages, 1):
            # Extract tables
            tables = page.extract_tables()
            if tables:
                print(f"Page {page_num}: Found {len(tables)} tables")
                
                for table_idx, table in enumerate(tables):
                    if table and len(table) > 0:
                        # Print table structure to help identify tract table
                        print(f"  Table {table_idx + 1}: {len(table)} rows x {len(table[0]) if table[0] else 0} cols")
                        
                        # Look for tract identifiers in all cells
                        for row_idx, row in enumerate(table):
                            for col_idx, cell in enumerate(row):
                                if cell:
                                    cell_text = str(cell).strip()
                                    
                                    # Look for 11-digit GEOID (12057XXXXXX for Hillsborough County, FL)
                                    geoid_matches = re.findall(r'\b12057\d{6}\b', cell_text)
                                    for match in geoid_matches:
                                        if match not in tracts:
                                            tracts.append(match)
                                            print(f"    Found: {match}")
                                    
                                    # Look for tract number patterns that might need county prefix
                                    tract_num_matches = re.findall(r'\b(\d{4,6}(?:\.\d{2})?)\b', cell_text)
                                    for match in tract_num_matches:
                                        # If it's a 6-digit number, likely a tract
                                        if len(match.replace('.', '')) == 6 and match not in tracts:
                                            full_tract = f"12057{match.replace('.', '')}"
                                            if full_tract not in tracts:
                                                tracts.append(full_tract)
                                                print(f"    Found: {full_tract}")
            
            # Also check text for tract patterns
            text = page.extract_text()
            if text:
                # Look for GEOID patterns
                geoid_matches = re.findall(r'\b12057\d{6}\b', text)
                for match in geoid_matches:
                    if match not in tracts:
                        tracts.append(match)
                        print(f"  Found in text: {match}")
    
    return sorted(tracts)

if __name__ == '__main__':
    pdf_path = r"C:\DREAM\Member Reports\supporting_files\Community Profile of Tampa, FL (City, 2020).pdf"
    tracts = extract_tampa_tracts(pdf_path)
    
    print(f"\n{'='*60}")
    print(f"FOUND {len(tracts)} CENSUS TRACTS")
    print(f"{'='*60}")
    
    if tracts:
        print("\nFirst 20 tracts:")
        for tract in tracts[:20]:
            print(f"  {tract}")
        if len(tracts) > 20:
            print(f"  ... and {len(tracts) - 20} more")
        
        # Save to file
        output_file = r"C:\DREAM\Member Reports\data\processed\tampa_census_tracts.txt"
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            for tract in tracts:
                f.write(f"{tract}\n")
        print(f"\nSaved all {len(tracts)} tracts to: {output_file}")
        
        # Also create JSON list for config
        import json
        json_file = r"C:\DREAM\Member Reports\data\processed\tampa_census_tracts.json"
        with open(json_file, 'w') as f:
            json.dump(tracts, f, indent=2)
        print(f"Saved JSON list to: {json_file}")
    else:
        print("\nNo tracts found.")
        print("The PDF may list tracts in a format that needs manual extraction.")
        print("Please check the PDF or provide tract numbers manually.")
