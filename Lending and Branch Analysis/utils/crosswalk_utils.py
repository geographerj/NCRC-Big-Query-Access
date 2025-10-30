"""
Crosswalk File Utilities

Helper functions for loading, saving, and working with crosswalk files
(e.g., CBSA to County, ZIP to Census Tract, etc.)
"""

import pandas as pd
import os
from typing import Optional, Dict, List, Tuple


def load_crosswalk(file_path: str, dtype: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """
    Load a crosswalk file (CSV)
    
    Args:
        file_path: Path to crosswalk CSV file
        dtype: Optional dict specifying data types for columns (useful for preserving leading zeros in codes)
    
    Returns:
        DataFrame with crosswalk data
    """
    print(f"Loading crosswalk from: {file_path}")
    
    if dtype is None:
        # Default: treat code columns as strings to preserve leading zeros
        df = pd.read_csv(file_path, dtype=str)
    else:
        df = pd.read_csv(file_path, dtype=dtype)
    
    print(f"  Loaded {len(df):,} rows")
    print(f"  Columns: {list(df.columns)}")
    
    return df


def save_crosswalk(df: pd.DataFrame, output_path: str, index: bool = False):
    """
    Save a crosswalk DataFrame to CSV
    
    This is how you can create crosswalk files to share with me!
    
    Args:
        df: DataFrame to save
        output_path: Path where CSV will be saved
        index: Whether to include index column (usually False for crosswalks)
    
    Example:
        # Create a simple crosswalk
        crosswalk = pd.DataFrame({
            'cbsa_code': ['33860', '19300'],
            'cbsa_name': ['Montgomery AL', 'Daphne-Fairhope-Foley AL'],
            'county_code': ['01001', '01003']
        })
        
        # Save it
        save_crosswalk(crosswalk, 'data/my_crosswalk.csv')
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_csv(output_path, index=index)
    print(f"✓ Saved crosswalk to: {output_path}")
    print(f"  Rows: {len(df):,}")
    print(f"  Columns: {list(df.columns)}")


def merge_with_crosswalk(
    df: pd.DataFrame,
    crosswalk: pd.DataFrame,
    left_on: str,
    right_on: str,
    how: str = 'left'
) -> pd.DataFrame:
    """
    Merge a DataFrame with a crosswalk file
    
    Args:
        df: Main DataFrame to merge
        crosswalk: Crosswalk DataFrame
        left_on: Column name in df to join on
        right_on: Column name in crosswalk to join on
        how: Type of join ('left', 'right', 'inner', 'outer')
    
    Returns:
        Merged DataFrame
    """
    result = df.merge(crosswalk, left_on=left_on, right_on=right_on, how=how)
    print(f"  Merged {len(df):,} rows with crosswalk")
    print(f"  Result: {len(result):,} rows")
    return result


def validate_crosswalk(df: pd.DataFrame, key_column: str) -> Tuple[bool, List[str]]:
    """
    Validate a crosswalk file for common issues
    
    Args:
        df: Crosswalk DataFrame
        key_column: Primary key column to check for duplicates
    
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Check for duplicates in key column
    duplicates = df[df.duplicated(subset=[key_column], keep=False)]
    if len(duplicates) > 0:
        issues.append(f"Found {len(duplicates)} duplicate rows in key column '{key_column}'")
    
    # Check for missing values in key column
    missing = df[key_column].isna().sum()
    if missing > 0:
        issues.append(f"Found {missing} missing values in key column '{key_column}'")
    
    is_valid = len(issues) == 0
    
    if is_valid:
        print(f"✓ Crosswalk validation passed")
    else:
        print(f"⚠ Crosswalk validation found {len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")
    
    return is_valid, issues


# Example crosswalk loader for common files
def load_cbsa_to_county(crosswalk_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load CBSA to County crosswalk
    
    Args:
        crosswalk_path: Path to CBSA to County crosswalk (defaults to common location)
    
    Returns:
        DataFrame with CBSA to County mapping
    """
    if crosswalk_path is None:
        # Try common locations
        possible_paths = [
            "../CBSA_to_County_Mapping.csv",
            "CBSA_to_County_Mapping.csv",
            "../../CBSA_to_County_Mapping.csv"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                crosswalk_path = path
                break
        
        if crosswalk_path is None:
            raise FileNotFoundError("CBSA to County crosswalk not found. Please provide path.")
    
    df = load_crosswalk(crosswalk_path, dtype={'cbsa_code': str, 'Geoid5': str})
    return df

