"""
Extract data from community profile PDF for use in reports
"""

import sys
from pathlib import Path
import pdfplumber
import re
import json

def extract_tampa_community_data(pdf_path: str) -> dict:
    """
    Extract demographic, income, and housing data from Tampa community profile PDF
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary with extracted community data
    """
    community_data = {
        "community_name": "Tampa, FL (City)",
        "profile_year": "2020",
        "demographics": {},
        "income": {},
        "housing": {},
        "trends": {}
    }
    
    if not Path(pdf_path).exists():
        print(f"PDF file not found: {pdf_path}")
        return community_data
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() or ""
            
            # Try to extract tables
            tables = []
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
            
            # Extract population data
            # Look for patterns like "Total Population: 123,456" or "Population: 123,456"
            pop_patterns = [
                r'Total\s+Population[:\s]+([\d,]+)',
                r'Population[:\s]+([\d,]+)',
                r'([\d,]+)\s+total\s+population',
            ]
            for pattern in pop_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    pop_str = match.group(1).replace(',', '')
                    try:
                        community_data['demographics']['total_population'] = int(pop_str)
                        break
                    except ValueError:
                        continue
            
            # Extract demographic percentages
            # Look for patterns like "Black: 25.3%" or "Black/African American: 25.3%"
            demo_patterns = {
                'black_percentage': [
                    r'Black[^\d]*:?\s*([\d.]+)\s*%',
                    r'Black/African\s+American[^\d]*:?\s*([\d.]+)\s*%',
                ],
                'hispanic_percentage': [
                    r'Hispanic[^\d]*:?\s*([\d.]+)\s*%',
                    r'Latino[^\d]*:?\s*([\d.]+)\s*%',
                ],
                'white_percentage': [
                    r'White[^\d]*:?\s*([\d.]+)\s*%',
                    r'White\s+\(non-Hispanic\)[^\d]*:?\s*([\d.]+)\s*%',
                ],
                'asian_percentage': [
                    r'Asian[^\d]*:?\s*([\d.]+)\s*%',
                ],
            }
            
            for demo_key, patterns in demo_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, full_text, re.IGNORECASE)
                    if match:
                        try:
                            pct = float(match.group(1))
                            if 0 <= pct <= 100:
                                community_data['demographics'][demo_key] = pct
                                break
                        except ValueError:
                            continue
            
            # Extract income data
            # Look for "Median Household Income: $45,678" or similar
            income_patterns = [
                r'Median\s+Household\s+Income[:\s$]+([\d,]+)',
                r'Median\s+Income[:\s$]+([\d,]+)',
            ]
            for pattern in income_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    inc_str = match.group(1).replace(',', '').replace('$', '')
                    try:
                        community_data['income']['median_household_income'] = int(inc_str)
                        break
                    except ValueError:
                        continue
            
            # Extract poverty rate
            poverty_patterns = [
                r'Poverty\s+Rate[:\s]+([\d.]+)\s*%',
                r'Poverty[:\s]+([\d.]+)\s*%',
            ]
            for pattern in poverty_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    try:
                        pct = float(match.group(1))
                        if 0 <= pct <= 100:
                            community_data['income']['poverty_rate'] = pct
                            break
                    except ValueError:
                        continue
            
            # Extract homeownership rate
            homeownership_patterns = [
                r'Homeownership\s+Rate[:\s]+([\d.]+)\s*%',
                r'Homeownership[:\s]+([\d.]+)\s*%',
            ]
            for pattern in homeownership_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    try:
                        pct = float(match.group(1))
                        if 0 <= pct <= 100:
                            community_data['housing']['homeownership_rate'] = pct
                            break
                    except ValueError:
                        continue
            
            # Extract median home value
            home_value_patterns = [
                r'Median\s+Home\s+Value[:\s$]+([\d,]+)',
                r'Median\s+Housing\s+Value[:\s$]+([\d,]+)',
            ]
            for pattern in home_value_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    val_str = match.group(1).replace(',', '').replace('$', '')
                    try:
                        community_data['housing']['median_home_value'] = int(val_str)
                        break
                    except ValueError:
                        continue
            
            # Try to extract from tables if available
            for table in tables:
                if table and len(table) > 0:
                    # Look for demographic data in tables
                    for row in table:
                        if row:
                            row_text = ' '.join([str(cell) if cell else '' for cell in row])
                            # Check for demographic categories
                            for demo_key, patterns in demo_patterns.items():
                                for pattern in patterns:
                                    match = re.search(pattern, row_text, re.IGNORECASE)
                                    if match:
                                        try:
                                            pct = float(match.group(1))
                                            if 0 <= pct <= 100 and demo_key not in community_data['demographics']:
                                                community_data['demographics'][demo_key] = pct
                                                break
                                        except ValueError:
                                            continue
            
            print(f"Extracted data from community profile:")
            print(f"  Population: {community_data['demographics'].get('total_population', 'Not found')}")
            print(f"  Demographics: {len([k for k in community_data['demographics'].keys() if k != 'total_population'])} categories found")
            print(f"  Income data: {'Found' if community_data['income'] else 'Not found'}")
            print(f"  Housing data: {'Found' if community_data['housing'] else 'Not found'}")
            
    except Exception as e:
        print(f"Error extracting data from PDF: {e}")
        import traceback
        traceback.print_exc()
    
    return community_data


if __name__ == "__main__":
    # Extract data from Tampa community profile
    pdf_path = Path("Member Reports/supporting_files/Community Profile of Tampa, FL (City, 2020).pdf")
    if not pdf_path.exists():
        pdf_path = Path("supporting_files/Community Profile of Tampa, FL (City, 2020).pdf")
    
    data = extract_tampa_community_data(str(pdf_path))
    
    # Save to JSON file
    output_path = Path("Member Reports/data/processed/tampa_community_profile_data.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nData saved to: {output_path}")

