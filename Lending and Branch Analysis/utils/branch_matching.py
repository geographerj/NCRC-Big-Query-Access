"""
Branch Data Matching Utilities

Handles matching bank names between HMDA and SOD (Summary of Deposits) datasets.
Since there's no reliable join column (RSSD in SOD but not HMDA), we must match by
bank name with manual verification.

Key constraints:
- Bank names differ between datasets (e.g., "Wells Fargo" vs "Wells Fargo Bank")
- Always require user verification before treating names as matches
- Use uninumbr for deduplication (unique per branch per year)
- Multiple SOD tables overlap - avoid double counting
"""

import pandas as pd
import re
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher


def normalize_bank_name(name: str) -> str:
    """
    Normalize bank name for fuzzy matching.
    
    Removes common suffixes, converts to uppercase, removes extra spaces.
    
    Args:
        name: Bank name string
        
    Returns:
        Normalized bank name
    """
    if pd.isna(name) or not name:
        return ""
    
    # Convert to string and uppercase
    normalized = str(name).upper().strip()
    
    # Remove common suffixes that might differ
    suffixes = [
        r'\s+BANK\s*$',
        r'\s+BANKS?\s*$',
        r'\s+NATIONAL\s+ASSOCIATION\s*$',
        r'\s+N\.A\.\s*$',
        r'\s+NA\s*$',
        r'\s+INC\.?\s*$',
        r'\s+INCORPORATED\s*$',
        r'\s+CORP\.?\s*$',
        r'\s+CORPORATION\s*$',
        r'\s+CO\.?\s*$',
        r'\s+COMPANY\s*$',
    ]
    
    for suffix in suffixes:
        normalized = re.sub(suffix, '', normalized, flags=re.IGNORECASE)
    
    # Remove extra spaces
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized


def fuzzy_match_ratio(name1: str, name2: str) -> float:
    """
    Calculate similarity ratio between two bank names.
    
    Args:
        name1: First bank name
        name2: Second bank name
        
    Returns:
        Similarity ratio (0.0 to 1.0)
    """
    if not name1 or not name2:
        return 0.0
    
    # Normalize both names
    norm1 = normalize_bank_name(name1)
    norm2 = normalize_bank_name(name2)
    
    if not norm1 or not norm2:
        return 0.0
    
    # Use SequenceMatcher for similarity
    return SequenceMatcher(None, norm1, norm2).ratio()


def find_potential_matches(
    hmda_names: List[str],
    sod_names: List[str],
    threshold: float = 0.7
) -> pd.DataFrame:
    """
    Find potential name matches between HMDA and SOD datasets.
    
    Creates a DataFrame with potential matches that need user verification.
    
    Args:
        hmda_names: List of unique bank names from HMDA
        sod_names: List of unique bank names from SOD
        threshold: Minimum similarity ratio to consider (default 0.7)
        
    Returns:
        DataFrame with columns:
        - hmda_name: Name from HMDA
        - sod_name: Potential match from SOD
        - similarity: Similarity ratio (0-1)
        - is_match: Empty - user must fill this in
    """
    matches = []
    
    for hmda_name in hmda_names:
        if pd.isna(hmda_name) or not str(hmda_name).strip():
            continue
            
        best_match = None
        best_score = 0.0
        
        for sod_name in sod_names:
            if pd.isna(sod_name) or not str(sod_name).strip():
                continue
                
            score = fuzzy_match_ratio(str(hmda_name), str(sod_name))
            
            if score >= threshold and score > best_score:
                best_match = sod_name
                best_score = score
        
        if best_match:
            matches.append({
                'hmda_name': hmda_name,
                'sod_name': best_match,
                'similarity': best_score,
                'is_match': ''  # User must verify
            })
    
    df = pd.DataFrame(matches)
    df = df.sort_values('similarity', ascending=False)
    
    return df


def load_verified_matches(crosswalk_path: str) -> Dict[str, str]:
    """
    Load previously verified bank name matches from a crosswalk file.
    
    Crosswalk file should have columns:
    - hmda_name: Bank name as it appears in HMDA
    - sod_name: Bank name as it appears in SOD
    
    Args:
        crosswalk_path: Path to CSV file with verified matches
        
    Returns:
        Dictionary mapping HMDA names to SOD names
    """
    try:
        df = pd.read_csv(crosswalk_path)
        
        # Handle various column name formats
        hmda_col = None
        sod_col = None
        
        for col in df.columns:
            if 'hmda' in col.lower():
                hmda_col = col
            if 'sod' in col.lower():
                sod_col = col
        
        if not hmda_col or not sod_col:
            raise ValueError("Crosswalk must have columns for HMDA and SOD names")
        
        # Create mapping dictionary
        mapping = {}
        for _, row in df.iterrows():
            hmda_name = str(row[hmda_col]).strip()
            sod_name = str(row[sod_col]).strip()
            if hmda_name and sod_name:
                mapping[hmda_name] = sod_name
        
        return mapping
        
    except Exception as e:
        print(f"Warning: Could not load verified matches from {crosswalk_path}: {e}")
        return {}


def save_verified_matches(
    matches_df: pd.DataFrame,
    output_path: str,
    verified_only: bool = True
):
    """
    Save verified bank name matches to a crosswalk file.
    
    Args:
        matches_df: DataFrame with matches (must have 'hmda_name', 'sod_name', 'is_match')
        output_path: Path to save CSV file
        verified_only: If True, only save rows where is_match is True/Yes
    """
    # Filter to verified matches if requested
    if verified_only:
        # Handle various true values
        matches_df = matches_df[
            matches_df['is_match'].astype(str).str.upper().isin(['TRUE', 'YES', 'Y', '1', 'X', '✓'])
        ].copy()
    
    # Select relevant columns
    output_df = matches_df[['hmda_name', 'sod_name']].copy()
    output_df = output_df.drop_duplicates()
    
    output_df.to_csv(output_path, index=False)
    print(f"✓ Saved {len(output_df)} verified matches to {output_path}")


def create_verification_worksheet(
    matches_df: pd.DataFrame,
    output_path: str
):
    """
    Create an Excel file for manual verification of bank name matches.
    
    Creates a file with checkboxes or columns for user to mark which matches are correct.
    
    Args:
        matches_df: DataFrame with potential matches
        output_path: Path to save Excel file
    """
    # Create a copy for user verification
    verify_df = matches_df.copy()
    
    # Add columns for verification
    verify_df['is_match'] = ''  # User fills: Y/N/Yes/No/True/False
    verify_df['notes'] = ''  # User can add notes
    
    # Sort by similarity (highest first)
    verify_df = verify_df.sort_values('similarity', ascending=False)
    
    # Save to Excel
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        verify_df.to_excel(writer, sheet_name='Verify Matches', index=False)
        
        # Get workbook and worksheet for formatting
        workbook = writer.book
        worksheet = writer.sheets['Verify Matches']
        
        # Add header note
        worksheet.insert_rows(1)
        worksheet.merge_cells('A1:D1')
        cell = worksheet['A1']
        cell.value = 'INSTRUCTIONS: Mark is_match column with Y/Yes/True/1 if names are the same bank, N/No/False/0 if different'
        cell.font = {'bold': True, 'size': 11}
        cell.fill = {'patternType': 'solid', 'fgColor': 'FFFF00'}  # Yellow
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"✓ Created verification worksheet: {output_path}")
    print(f"  Please review and mark matches, then save the file.")


def deduplicate_branches(df: pd.DataFrame, year_col: str = 'year', unique_col: str = 'uninumbr') -> pd.DataFrame:
    """
    Remove duplicate branches using uninumbr (unique per branch per year).
    
    Args:
        df: DataFrame with branch data
        year_col: Name of year column
        unique_col: Name of unique identifier column (uninumbr)
        
    Returns:
        DataFrame with duplicates removed
    """
    if unique_col not in df.columns or year_col not in df.columns:
        print(f"Warning: Cannot deduplicate - missing {unique_col} or {year_col} column")
        return df
    
    # Count duplicates
    duplicate_mask = df.duplicated(subset=[year_col, unique_col], keep=False)
    duplicate_count = duplicate_mask.sum()
    
    if duplicate_count > 0:
        print(f"Found {duplicate_count} duplicate branches (same uninumbr + year)")
        # Keep first occurrence
        df = df.drop_duplicates(subset=[year_col, unique_col], keep='first')
        print(f"Removed duplicates, {len(df)} unique branches remaining")
    else:
        print(f"No duplicates found ({len(df)} branches)")
    
    return df

