"""
Load RSSD crosswalk from SharePoint file.
RSSD enables reliable matching between HMDA (by LEI) and SOD (by RSSD).

Workflow:
1. Download the SharePoint Excel file
2. Save it locally (e.g., data/reference/LEI_to_RSSD.xlsx or .csv)
3. This script loads it and creates a mapping
"""

import pandas as pd
import os
from typing import Dict, Optional


def load_rssd_crosswalk(crosswalk_path: str) -> pd.DataFrame:
    """
    Load LEI to RSSD crosswalk from Excel or CSV file.
    
    Args:
        crosswalk_path: Path to Excel (.xlsx) or CSV file
        
    Returns:
        DataFrame with LEI and RSSD columns
    """
    if not os.path.exists(crosswalk_path):
        raise FileNotFoundError(f"Crosswalk file not found: {crosswalk_path}")
    
    # Try to load as Excel first
    if crosswalk_path.endswith('.xlsx') or crosswalk_path.endswith('.xls'):
        df = pd.read_excel(crosswalk_path)
    else:
        # Assume CSV
        df = pd.read_csv(crosswalk_path)
    
    # Try to find LEI and RSSD columns (case-insensitive)
    lei_col = None
    rssd_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'lei' in col_lower:
            lei_col = col
        if 'rssd' in col_lower or 'rss' in col_lower or 'rss-id' in col_lower or 'rss_id' in col_lower:
            rssd_col = col
    
    if lei_col is None:
        raise ValueError("Could not find LEI column in crosswalk file")
    if rssd_col is None:
        raise ValueError("Could not find RSSD/RSS-ID column in crosswalk file")
    
    # Create clean mapping
    mapping = df[[lei_col, rssd_col]].copy()
    mapping.columns = ['lei', 'rssd']
    
    # Remove any rows with missing values
    mapping = mapping.dropna(subset=['lei', 'rssd'])
    
    # Convert RSSD to string (some may have leading zeros)
    mapping['rssd'] = mapping['rssd'].astype(str).str.strip()
    mapping['lei'] = mapping['lei'].astype(str).str.strip()
    
    # Remove duplicates
    mapping = mapping.drop_duplicates(subset=['lei'])
    
    print(f"Loaded {len(mapping)} LEI->RSSD mappings")
    print(f"Columns found: LEI='{lei_col}', RSSD='{rssd_col}'")
    
    return mapping


def create_lei_rssd_dict(crosswalk_path: str) -> Dict[str, str]:
    """
    Create a simple dictionary mapping LEI to RSSD.
    
    Args:
        crosswalk_path: Path to crosswalk file
        
    Returns:
        Dictionary mapping LEI -> RSSD
    """
    df = load_rssd_crosswalk(crosswalk_path)
    return dict(zip(df['lei'], df['rssd']))


def find_rssd_for_bank(lei: str, crosswalk_path: str) -> Optional[str]:
    """
    Find RSSD for a bank given its LEI.
    
    Args:
        lei: Bank's LEI
        crosswalk_path: Path to crosswalk file
        
    Returns:
        RSSD if found, None otherwise
    """
    mapping = create_lei_rssd_dict(crosswalk_path)
    return mapping.get(lei.upper())


if __name__ == "__main__":
    import sys
    
    # Try common locations
    possible_paths = [
        "data/reference/LEI_to_RSSD.xlsx",
        "data/reference/LEI_to_RSSD.csv",
        "data/reference/RSSD_Crosswalk.xlsx",
        "data/reference/RSSD_Crosswalk.csv",
    ]
    
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        # Try to find file
        for p in possible_paths:
            if os.path.exists(p):
                path = p
                break
        else:
            print("ERROR: RSSD crosswalk file not found.")
            print(f"Please download the SharePoint file and save it as one of:")
            for p in possible_paths:
                print(f"  {p}")
            print("\nOr provide path as argument:")
            print("  python load_rssd_crosswalk.py path/to/file.xlsx")
            sys.exit(1)
    
    try:
        mapping = load_rssd_crosswalk(path)
        print(f"\nSample mappings:")
        print(mapping.head(10))
        
        # Test with Fifth Third and Comerica
        print("\n" + "="*80)
        print("TESTING WITH FIFTH THIRD AND COMERICA")
        print("="*80)
        
        fifth_third_lei = "QFROUN1UWUYU0DVIWD51"
        comerica_lei = "70WY0ID1N53Q4254VH70"
        
        lei_to_rssd = create_lei_rssd_dict(path)
        
        ft_rssd = lei_to_rssd.get(fifth_third_lei)
        com_rssd = lei_to_rssd.get(comerica_lei)
        
        print(f"\nFifth Third Bank:")
        print(f"  LEI: {fifth_third_lei}")
        print(f"  RSSD: {ft_rssd if ft_rssd else 'NOT FOUND'}")
        
        print(f"\nComerica Bank:")
        print(f"  LEI: {comerica_lei}")
        print(f"  RSSD: {com_rssd if com_rssd else 'NOT FOUND'}")
        
    except Exception as e:
        print(f"ERROR: {e}")

