"""
Branch-HMDA Joining Utilities

Utilities for joining branch (SOD) data with HMDA lending data using GEOID.
GEOID in SOD matches census_tract in HMDA, enabling tract-level analysis.
"""

import pandas as pd
from typing import Optional, Dict


def prepare_hmda_tract_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare HMDA DataFrame census_tract column to match SOD GEOID format.
    
    HMDA census_tract may be stored as string with or without decimals.
    GEOID format may vary - this function standardizes for matching.
    
    Args:
        df: HMDA DataFrame with census_tract column
        
    Returns:
        DataFrame with standardized tract column
    """
    df = df.copy()
    
    # Find census tract column
    tract_col = None
    for col in df.columns:
        if 'tract' in col.lower() or col.lower() == 'geoid':
            tract_col = col
            break
    
    if tract_col is None:
        raise ValueError("No census_tract or GEOID column found in HMDA data")
    
    # Convert to string and remove decimals if present (GEOID is typically integer-like)
    df[f'{tract_col}_geoid'] = df[tract_col].astype(str).str.replace('.', '').str.strip()
    
    # Pad with zeros if needed (tracts are typically 11 digits)
    # But don't assume - just standardize format
    df[f'{tract_col}_geoid'] = df[f'{tract_col}_geoid'].str.zfill(11)
    
    return df


def join_branches_with_hmda(
    branches_df: pd.DataFrame,
    hmda_df: pd.DataFrame,
    how: str = 'left'
) -> pd.DataFrame:
    """
    Join branch (SOD) data with HMDA lending data using GEOID.
    
    GEOID in SOD matches census_tract in HMDA.
    
    Args:
        branches_df: SOD branch DataFrame (must have 'geoid' column)
        hmda_df: HMDA lending DataFrame (must have 'census_tract' or similar)
        how: Type of join ('left', 'right', 'inner', 'outer')
    
    Returns:
        Joined DataFrame
    """
    # Prepare HMDA tract column
    hmda_prepared = prepare_hmda_tract_column(hmda_df)
    
    # Find the prepared GEOID column in HMDA
    hmda_geoid_col = None
    for col in hmda_prepared.columns:
        if col.endswith('_geoid'):
            hmda_geoid_col = col
            break
    
    if hmda_geoid_col is None:
        raise ValueError("Could not create GEOID column from HMDA census_tract")
    
    # Prepare branch GEOID (ensure string format)
    branches_df = branches_df.copy()
    branches_df['geoid'] = branches_df['geoid'].astype(str).str.replace('.', '').str.strip().str.zfill(11)
    
    # Perform join
    joined = branches_df.merge(
        hmda_prepared,
        left_on='geoid',
        right_on=hmda_geoid_col,
        how=how,
        suffixes=('_branch', '_hmda')
    )
    
    return joined


def analyze_branch_lending_alignment(
    branches_df: pd.DataFrame,
    hmda_df: pd.DataFrame,
    lender_name: str = None
) -> pd.DataFrame:
    """
    Analyze alignment between branch presence and lending by tract.
    
    Creates summary showing:
    - Tracts with branches AND lending
    - Tracts with branches but NO lending (red flag)
    - Tracts with lending but NO branches
    - Tracts with neither
    
    Args:
        branches_df: SOD branch DataFrame
        hmda_df: HMDA lending DataFrame
        lender_name: Optional lender name for filtering
        
    Returns:
        DataFrame with alignment analysis
    """
    # Filter by lender if specified
    if lender_name:
        branches_df = branches_df[
            branches_df['institution_name'].str.contains(lender_name, case=False, na=False)
        ]
        # HMDA filtering would be by respondent_name or LEI
    
    # Join datasets
    joined = join_branches_with_hmda(branches_df, hmda_df, how='outer')
    
    # Create alignment categories
    joined['has_branch'] = joined['uninumbr'].notna()
    joined['has_lending'] = joined['lei'].notna()  # Or other HMDA identifier
    
    # Count by tract
    alignment = joined.groupby('geoid').agg({
        'has_branch': 'any',
        'has_lending': 'any',
        'cbsa_code_branch': 'first',
        'cbsa_code_hmda': 'first',
        'br_lmi': 'first',
        'cr_minority': 'first'
    }).reset_index()
    
    # Create alignment category
    def categorize(row):
        if row['has_branch'] and row['has_lending']:
            return 'Branch and Lending'
        elif row['has_branch'] and not row['has_lending']:
            return 'Branch Only (Red Flag)'
        elif not row['has_branch'] and row['has_lending']:
            return 'Lending Only'
        else:
            return 'Neither'
    
    alignment['alignment_category'] = alignment.apply(categorize, axis=1)
    
    # Get CBSA (prefer branch CBSA, fallback to HMDA)
    alignment['cbsa_code'] = alignment['cbsa_code_branch'].fillna(alignment['cbsa_code_hmda'])
    
    return alignment


def get_branch_closures_in_lmi_minority_tracts(
    branches_prev: pd.DataFrame,
    branches_current: pd.DataFrame
) -> pd.DataFrame:
    """
    Identify branch closures that occurred in LMI or minority tracts.
    
    Compares two time periods to find closed branches.
    
    Args:
        branches_prev: SOD branch DataFrame from previous period
        branches_current: SOD branch DataFrame from current period
        
    Returns:
        DataFrame of closed branches with LMI/minority flags
    """
    # Find branches that exist in prev but not in current
    prev_uninumbr = set(branches_prev['uninumbr'].unique())
    current_uninumbr = set(branches_current['uninumbr'].unique())
    
    closed_uninumbr = prev_uninumbr - current_uninumbr
    
    # Get details of closed branches
    closed = branches_prev[branches_prev['uninumbr'].isin(closed_uninumbr)].copy()
    
    # Add summary flags
    closed['closed_in_lmi'] = closed['br_lmi'] == 1
    closed['closed_in_minority'] = closed['cr_minority'] == 1
    closed['closed_in_lmi_minority'] = (closed['br_lmi'] == 1) & (closed['cr_minority'] == 1)
    
    return closed.sort_values(['closed_in_lmi_minority', 'closed_in_minority', 'closed_in_lmi'], ascending=False)

