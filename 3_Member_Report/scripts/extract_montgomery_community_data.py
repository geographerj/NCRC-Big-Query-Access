"""
Extract data from Montgomery County community profile PDF
Based on extract_community_profile_data.py but adapted for Montgomery
"""

import sys
from pathlib import Path
import pdfplumber
import re
import json


def extract_montgomery_community_data(pdf_path: str) -> dict:
    """
    Extract demographic, income, and housing data from Montgomery County community profile PDF
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary with extracted community data
    """
    community_data = {
        "community_name": "Montgomery County, MD (County)",
        "profile_year": "2022",
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
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            
            print(f"Extracted text from {len(pdf.pages)} pages")
            
            # Extract demographics (similar patterns as Tampa)
            demo_patterns = {
                'hispanic_percentage': [
                    r'[Hh]ispanic.*?(\d+\.?\d*)\s*%',
                    r'[Ll]atino.*?(\d+\.?\d*)\s*%',
                    r'Hispanic.*?(\d+\.?\d*)',
                ],
                'black_percentage': [
                    r'[Bb]lack.*?(\d+\.?\d*)\s*%',
                    r'[Aa]frican\s+[Aa]merican.*?(\d+\.?\d*)\s*%',
                ],
                'white_percentage': [
                    r'[Ww]hite.*?(\d+\.?\d*)\s*%',
                ],
                'asian_percentage': [
                    r'[Aa]sian.*?(\d+\.?\d*)\s*%',
                ]
            }
            
            for demo_key, patterns in demo_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, full_text)
                    if match:
                        try:
                            pct = float(match.group(1))
                            if 0 <= pct <= 100 and demo_key not in community_data['demographics']:
                                community_data['demographics'][demo_key] = pct
                                break
                        except ValueError:
                            continue
            
            # Extract income data
            income_patterns = {
                'median_household_income': [
                    r'[Mm]edian\s+[Hh]ousehold\s+[Ii]ncome.*?\$?([\d,]+)',
                    r'[Mm]edian.*?[Ii]ncome.*?\$?([\d,]+)',
                ],
                'poverty_rate': [
                    r'[Pp]overty.*?(\d+\.?\d*)\s*%',
                    r'[Bb]elow\s+[Pp]overty.*?(\d+\.?\d*)\s*%',
                ]
            }
            
            for income_key, patterns in income_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, full_text)
                    if match:
                        try:
                            if income_key == 'median_household_income':
                                val = int(match.group(1).replace(',', ''))
                                if val > 0:
                                    community_data['income'][income_key] = val
                                    break
                            else:
                                val = float(match.group(1))
                                if 0 <= val <= 100:
                                    community_data['income'][income_key] = val
                                    break
                        except ValueError:
                            continue
            
            # Extract housing data
            housing_patterns = {
                'homeownership_rate': [
                    r'[Hh]omeownership.*?(\d+\.?\d*)\s*%',
                    r'[Oo]wn.*?[Oo]ccupied.*?(\d+\.?\d*)\s*%',
                ]
            }
            
            for housing_key, patterns in housing_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, full_text)
                    if match:
                        try:
                            val = float(match.group(1))
                            if 0 <= val <= 100:
                                community_data['housing'][housing_key] = val
                                break
                        except ValueError:
                            continue
            
            print(f"Extracted data from community profile:")
            print(f"  Demographics: {len(community_data['demographics'])} categories found")
            print(f"  Income data: {'Found' if community_data['income'] else 'Not found'}")
            print(f"  Housing data: {'Found' if community_data['housing'] else 'Not found'}")
            
    except Exception as e:
        print(f"Error extracting data from PDF: {e}")
        import traceback
        traceback.print_exc()
    
    return community_data


if __name__ == "__main__":
    # Extract data from Montgomery community profile
    member_reports_dir = Path(__file__).parent.parent
    pdf_path = member_reports_dir / "supporting_files" / "Community Profile of Montgomery, MD (County, 2022).pdf"
    
    print(f"Extracting data from: {pdf_path}")
    
    community_data = extract_montgomery_community_data(str(pdf_path))
    
    # Save to JSON
    output_path = member_reports_dir / "data" / "processed" / "montgomery_community_profile_data.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(community_data, f, indent=2)
    
    print(f"\nData saved to: {output_path}")

