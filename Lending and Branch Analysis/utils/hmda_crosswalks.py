"""
HMDA Crosswalk Utilities

Functions for loading and merging HMDA data with crosswalk files
(e.g., CBSA names, lender names, geographic identifiers).
"""

import pandas as pd
import os
from typing import Optional
from .crosswalk_utils import load_crosswalk


def load_cbsa_to_county_crosswalk(crosswalk_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load CBSA to County crosswalk file.
    
    Args:
        crosswalk_path: Path to CBSA to County CSV file (defaults to common location)
    
    Returns:
        DataFrame with CBSA to County mapping
    """
    if crosswalk_path is None:
        # Try common locations
        script_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(script_dir)), "CBSA_to_County_Mapping.csv"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))), "CBSA_to_County_Mapping.csv"),
            "CBSA_to_County_Mapping.csv",
            "../CBSA_to_County_Mapping.csv",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                crosswalk_path = path
                break
        
        if crosswalk_path is None:
            raise FileNotFoundError("CBSA to County crosswalk not found. Please provide path.")
    
    df = load_crosswalk(crosswalk_path, dtype={'Cbsa Code': str, 'Geoid5': str})
    return df


def load_lender_name_crosswalk(crosswalk_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load lender LEI to name crosswalk file.
    
    Args:
        crosswalk_path: Path to lender crosswalk CSV file (defaults to common location)
    
    Returns:
        DataFrame with LEI to lender name mapping
    """
    if crosswalk_path is None:
        # Try common locations
        script_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(script_dir)), "Lenders_and_LEI_Numbers.csv"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))), "Lenders_and_LEI_Numbers.csv"),
            "Lenders_and_LEI_Numbers.csv",
            "../Lenders_and_LEI_Numbers.csv",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                crosswalk_path = path
                break
        
        if crosswalk_path is None:
            raise FileNotFoundError("Lender LEI crosswalk not found. Please provide path.")
    
    df = load_crosswalk(crosswalk_path, dtype={'Lei': str})
    
    # Standardize column names to lowercase
    if 'Lei' in df.columns:
        df = df.rename(columns={'Lei': 'lei'})
    if 'Respondent Name' in df.columns:
        df = df.rename(columns={'Respondent Name': 'respondent_name'})
    
    return df


def merge_hmda_with_crosswalks(
    df: pd.DataFrame,
    merge_cbsa: bool = True,
    merge_lender_names: bool = True
) -> pd.DataFrame:
    """
    Merge HMDA DataFrame with crosswalk files.
    
    Args:
        df: HMDA DataFrame
        merge_cbsa: Whether to merge CBSA names
        merge_lender_names: Whether to merge lender names
    
    Returns:
        DataFrame with merged crosswalk information
    """
    df_merged = df.copy()
    
    # Merge CBSA names if requested
    if merge_cbsa:
        # Check if we have a cbsa_code column
        cbsa_columns = [col for col in df.columns if 'cbsa' in col.lower() or 'msamd' in col.lower()]
        if cbsa_columns:
            cbsa_col = cbsa_columns[0]  # Use first CBSA-related column found
            try:
                cbsa_crosswalk = load_cbsa_to_county_crosswalk()
                
                # Get unique CBSA codes and names
                cbsa_names = cbsa_crosswalk[['Cbsa Code', 'Cbsa']].drop_duplicates()
                
                # Determine the join column in the crosswalk
                df_merged = df_merged.merge(
                    cbsa_names,
                    left_on=cbsa_col,
                    right_on='Cbsa Code',
                    how='left'
                )
                df_merged = df_merged.drop(columns=['Cbsa Code'])
                df_merged = df_merged.rename(columns={'Cbsa': 'cbsa_name'})
                
                print(f"✓ Merged CBSA names (found {df_merged['cbsa_name'].notna().sum():,} matches)")
            except Exception as e:
                print(f"⚠ Could not merge CBSA names: {e}")
    
    # Merge lender names if requested
    if merge_lender_names:
        # Check if we have a lei column
        if 'lei' in df.columns:
            try:
                lender_crosswalk = load_lender_name_crosswalk()
                
                df_merged = df_merged.merge(
                    lender_crosswalk[['lei', 'respondent_name']],
                    on='lei',
                    how='left'
                )
                
                print(f"✓ Merged lender names (found {df_merged['respondent_name'].notna().sum():,} matches)")
            except Exception as e:
                print(f"⚠ Could not merge lender names: {e}")
    
    return df_merged

