"""
Herfindahl-Hirschman Index (HHI) Analysis for Bank Mergers

Calculates market concentration using HHI for lending markets.
Based on DOJ Antitrust Division methodology:
https://www.justice.gov/atr/herfindahl-hirschman-index

HHI Formula:
- Square each firm's market share (as percentage)
- Sum the squared shares
- Range: 0 (perfectly competitive) to 10,000 (monopoly)

Market Concentration Thresholds:
- HHI < 1,000: Unconcentrated
- 1,000 ≤ HHI ≤ 1,800: Moderately concentrated
- HHI > 1,800: Highly concentrated

Merger Analysis:
- Increase in HHI > 100 points in highly concentrated markets
  is presumed likely to enhance market power
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple


def calculate_hhi(
    market_shares: pd.Series,
    as_percentages: bool = False
) -> float:
    """
    Calculate Herfindahl-Hirschman Index for a market.
    
    Args:
        market_shares: Series of market shares (0-100 if as_percentages=True, else 0-1)
        as_percentages: If True, market_shares are 0-100. If False, they're 0-1.
    
    Returns:
        HHI value (0 to 10,000)
        
    Example:
        >>> shares = pd.Series([30, 30, 20, 20])  # Percentages
        >>> hhi = calculate_hhi(shares, as_percentages=True)
        >>> print(hhi)  # 2600.0
    """
    if as_percentages:
        # Market shares are already percentages (0-100)
        shares = market_shares / 100.0
    else:
        # Market shares are proportions (0-1)
        shares = market_shares
    
    # Square each share and sum
    hhi = (shares ** 2).sum()
    
    # Convert to 0-10,000 scale (standard HHI scale)
    hhi_scaled = hhi * 10000
    
    return hhi_scaled


def calculate_market_shares(
    df: pd.DataFrame,
    market_column: str,
    firm_column: str,
    volume_column: str
) -> pd.DataFrame:
    """
    Calculate market shares for each firm in each market.
    
    Args:
        df: DataFrame with lending data
        market_column: Column identifying markets (e.g., 'cbsa_code', 'county_code')
        firm_column: Column identifying firms/lenders (e.g., 'lei', 'respondent_name')
        volume_column: Column with volume metric (e.g., 'originations', 'loan_amount')
    
    Returns:
        DataFrame with market shares by market and firm
    """
    # Calculate total volume by market
    market_totals = df.groupby(market_column)[volume_column].sum().reset_index()
    market_totals = market_totals.rename(columns={volume_column: 'market_total'})
    
    # Calculate volume by market and firm
    firm_volumes = df.groupby([market_column, firm_column])[volume_column].sum().reset_index()
    firm_volumes = firm_volumes.rename(columns={volume_column: 'firm_volume'})
    
    # Merge to calculate shares
    shares = firm_volumes.merge(market_totals, on=market_column, how='left')
    shares['market_share'] = (shares['firm_volume'] / shares['market_total']) * 100  # As percentage
    
    return shares


def calculate_hhi_by_market(
    df: pd.DataFrame,
    market_column: str,
    firm_column: str,
    volume_column: str
) -> pd.DataFrame:
    """
    Calculate HHI for each market (e.g., each CBSA).
    
    Args:
        df: DataFrame with lending data
        market_column: Column identifying markets (e.g., 'cbsa_code')
        firm_column: Column identifying firms/lenders (e.g., 'lei')
        volume_column: Column with volume metric (e.g., 'originations')
    
    Returns:
        DataFrame with HHI for each market
    """
    # Calculate market shares
    shares = calculate_market_shares(df, market_column, firm_column, volume_column)
    
    # Calculate HHI for each market
    hhi_by_market = shares.groupby(market_column).apply(
        lambda x: calculate_hhi(x['market_share'], as_percentages=True)
    ).reset_index()
    hhi_by_market.columns = [market_column, 'hhi']
    
    # Add market concentration category
    hhi_by_market['concentration_category'] = hhi_by_market['hhi'].apply(categorize_market_concentration)
    
    # Add number of firms
    firm_counts = shares.groupby(market_column)[firm_column].nunique().reset_index()
    firm_counts.columns = [market_column, 'number_of_firms']
    hhi_by_market = hhi_by_market.merge(firm_counts, on=market_column, how='left')
    
    # Add market totals
    market_totals = shares.groupby(market_column).agg({
        'firm_volume': 'sum'
    }).reset_index()
    market_totals.columns = [market_column, 'market_total_volume']
    hhi_by_market = hhi_by_market.merge(market_totals, on=market_column, how='left')
    
    return hhi_by_market.sort_values('hhi', ascending=False)


def categorize_market_concentration(hhi: float) -> str:
    """
    Categorize market concentration based on HHI.
    
    Based on DOJ Antitrust Guidelines:
    - HHI < 1,000: Unconcentrated
    - 1,000 ≤ HHI ≤ 1,800: Moderately concentrated
    - HHI > 1,800: Highly concentrated
    
    Args:
        hhi: HHI value (0-10,000)
    
    Returns:
        Concentration category string
    """
    if hhi < 1000:
        return "Unconcentrated"
    elif hhi <= 1800:
        return "Moderately Concentrated"
    else:
        return "Highly Concentrated"


def calculate_merger_hhi_change(
    pre_merger_df: pd.DataFrame,
    post_merger_df: pd.DataFrame,
    market_column: str,
    firm_column: str,
    volume_column: str,
    merging_firms: List[str]
) -> pd.DataFrame:
    """
    Calculate HHI change from a merger.
    
    Args:
        pre_merger_df: Lending data before merger
        post_merger_df: Lending data after merger
        market_column: Column identifying markets
        firm_column: Column identifying firms
        volume_column: Column with volume metric
        merging_firms: List of firm identifiers that are merging
    
    Returns:
        DataFrame with HHI before, after, and change for each market
    """
    # Calculate pre-merger HHI
    pre_hhi = calculate_hhi_by_market(pre_merger_df, market_column, firm_column, volume_column)
    pre_hhi = pre_hhi.rename(columns={'hhi': 'hhi_pre_merger', 'concentration_category': 'category_pre'})
    
    # Calculate post-merger HHI (merging firms should be treated as one)
    post_df = post_merger_df.copy()
    
    # If merging firms are separate in post-merger data, combine them
    if firm_column in post_df.columns:
        # Replace firm identifiers with combined identifier
        combined_firm_id = '+'.join(sorted(merging_firms))
        post_df.loc[post_df[firm_column].isin(merging_firms), firm_column] = combined_firm_id
        
        # Aggregate volumes for combined firm
        firm_grouped = post_df.groupby([market_column, firm_column])[volume_column].sum().reset_index()
        post_df = post_df.groupby([market_column, firm_column]).agg({
            volume_column: 'sum'
        }).reset_index()
    
    post_hhi = calculate_hhi_by_market(post_df, market_column, firm_column, volume_column)
    post_hhi = post_hhi.rename(columns={'hhi': 'hhi_post_merger', 'concentration_category': 'category_post'})
    
    # Merge and calculate change
    merged = pre_hhi.merge(post_hhi, on=market_column, how='outer')
    merged['hhi_change'] = merged['hhi_post_merger'] - merged['hhi_pre_merger']
    
    # Flag markets where merger raises antitrust concerns
    merged['antitrust_concern'] = (
        (merged['hhi_pre_merger'] > 1800) & 
        (merged['hhi_change'] > 100)
    )
    
    return merged.sort_values('hhi_change', ascending=False)


def calculate_top_firm_shares(
    shares_df: pd.DataFrame,
    market_column: str,
    top_n: int = 4
) -> pd.DataFrame:
    """
    Calculate market shares for top N firms in each market.
    
    Useful for identifying dominant firms and calculating C4 (4-firm concentration).
    
    Args:
        shares_df: DataFrame with market shares (from calculate_market_shares)
        market_column: Column identifying markets
        top_n: Number of top firms to include
    
    Returns:
        DataFrame with top N firms and their shares per market
    """
    # Sort by market share descending
    shares_sorted = shares_df.sort_values([market_column, 'market_share'], ascending=[True, False])
    
    # Get top N firms per market
    top_firms = shares_sorted.groupby(market_column).head(top_n)
    
    # Calculate C4 (4-firm concentration ratio)
    if top_n >= 4:
        c4 = shares_sorted.groupby(market_column).head(4).groupby(market_column)['market_share'].sum().reset_index()
        c4.columns = [market_column, 'c4_concentration_ratio']
        top_firms = top_firms.merge(c4, on=market_column, how='left')
    
    return top_firms


def analyze_lending_market_concentration(
    hmda_df: pd.DataFrame,
    market_level: str = 'cbsa',
    volume_metric: str = 'originations',
    year: Optional[int] = None
) -> Dict:
    """
    Comprehensive HHI analysis of lending markets.
    
    Args:
        hmda_df: HMDA lending DataFrame
        market_level: 'cbsa', 'county', or 'tract'
        volume_metric: 'originations', 'loan_amount', or column name
        year: Optional year filter
    
    Returns:
        Dictionary with:
        - hhi_by_market: HHI for each market
        - market_shares: Shares for each lender in each market
        - top_firms: Top 4 firms by market
        - summary_stats: Summary statistics
    """
    # Prepare data
    df = hmda_df.copy()
    
    if year:
        df = df[df['activity_year'] == year]
    
    # Set market and volume columns
    market_map = {
        'cbsa': 'cbsa_code',
        'county': 'county_code',
        'tract': 'census_tract'
    }
    
    market_col = market_map.get(market_level.lower(), 'cbsa_code')
    
    # Handle volume metric
    if volume_metric == 'originations':
        # Create originations column if needed
        if 'originations' not in df.columns:
            if 'action_taken' in df.columns:
                df['originations'] = (df['action_taken'] == '1').astype(int)
            else:
                raise ValueError("Cannot calculate originations - missing action_taken column")
        volume_col = 'originations'
    else:
        volume_col = volume_metric
    
    # Calculate market shares
    shares = calculate_market_shares(df, market_col, 'lei', volume_col)
    
    # Calculate HHI
    hhi = calculate_hhi_by_market(df, market_col, 'lei', volume_col)
    
    # Top firms
    top_firms = calculate_top_firm_shares(shares, market_col, top_n=4)
    
    # Summary statistics
    summary = {
        'total_markets': len(hhi),
        'highly_concentrated_markets': len(hhi[hhi['hhi'] > 1800]),
        'moderately_concentrated_markets': len(hhi[(hhi['hhi'] >= 1000) & (hhi['hhi'] <= 1800)]),
        'unconcentrated_markets': len(hhi[hhi['hhi'] < 1000]),
        'avg_hhi': hhi['hhi'].mean(),
        'median_hhi': hhi['hhi'].median(),
        'max_hhi': hhi['hhi'].max(),
        'min_hhi': hhi['hhi'].min()
    }
    
    return {
        'hhi_by_market': hhi,
        'market_shares': shares,
        'top_firms': top_firms,
        'summary_stats': pd.Series(summary)
    }


def create_hhi_report(
    analysis_results: Dict,
    output_path: Optional[str] = None
) -> pd.ExcelWriter:
    """
    Create Excel report with HHI analysis results.
    
    Args:
        analysis_results: Output from analyze_lending_market_concentration
        output_path: Path to save Excel file
    
    Returns:
        ExcelWriter object (call .save() to write file)
    """
    if output_path is None:
        output_path = "hhi_analysis_report.xlsx"
    
    writer = pd.ExcelWriter(output_path, engine='openpyxl')
    
    # Sheet 1: HHI by Market
    analysis_results['hhi_by_market'].to_excel(writer, sheet_name='HHI by Market', index=False)
    
    # Sheet 2: Market Shares
    analysis_results['market_shares'].to_excel(writer, sheet_name='Market Shares', index=False)
    
    # Sheet 3: Top Firms
    analysis_results['top_firms'].to_excel(writer, sheet_name='Top 4 Firms', index=False)
    
    # Sheet 4: Summary
    analysis_results['summary_stats'].to_excel(writer, sheet_name='Summary Statistics', index=True)
    
    return writer

