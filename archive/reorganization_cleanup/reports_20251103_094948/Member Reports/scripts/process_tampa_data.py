"""
Process Tampa market data for report generation

Calculates the 6 standard metrics:
1. Black homebuyer share
2. Hispanic homebuyer share
3. Asian homebuyer share
4. LMIB lending share
5. LMICT lending share
6. MMCT lending share
"""

import pandas as pd
import numpy as np
from pathlib import Path

def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the 6 standard metrics from raw data
    
    Note: For borrower demographics, denominator is loans WITH demographic data
    For geographic metrics (LMICT, MMCT), denominator is all originations
    """
    results = []
    
    for _, row in df.iterrows():
        total = row['total_originations']
        with_demo = row['loans_with_demographics']
        
        # Borrower demographics (denominator = loans with demographic data)
        black_pct = (row.get('black_loans', 0) / with_demo * 100) if with_demo > 0 else 0
        hispanic_pct = (row.get('hispanic_loans', 0) / with_demo * 100) if with_demo > 0 else 0
        asian_pct = (row.get('asian_loans', 0) / with_demo * 100) if with_demo > 0 else 0
        white_pct = (row.get('white_loans', 0) / with_demo * 100) if with_demo > 0 else 0
        native_american_pct = (row.get('native_american_loans', 0) / with_demo * 100) if with_demo > 0 else 0
        hopi_pct = (row.get('hopi_loans', 0) / with_demo * 100) if with_demo > 0 else 0
        
        # Geographic metrics (denominator = all originations)
        lmib_pct = (row['lmib_loans'] / total * 100) if total > 0 else 0
        lmict_pct = (row['lmict_loans'] / total * 100) if total > 0 else 0
        mmct_pct = (row['mmct_loans'] / total * 100) if total > 0 else 0
        
        result = {
            'activity_year': row['activity_year'],
            'lei': row.get('lei', 'Market'),
            'total_originations': total,
            'loans_with_demographics': with_demo,
            'missing_demographic_pct': ((total - with_demo) / total * 100) if total > 0 else 0,
            # Percentages (with demographic data as denominator for race/ethnicity)
            'black_homebuyer_share': black_pct,
            'hispanic_homebuyer_share': hispanic_pct,
            'asian_homebuyer_share': asian_pct,
            'white_homebuyer_share': white_pct,
            'native_american_homebuyer_share': native_american_pct,
            'hopi_homebuyer_share': hopi_pct,
            # Percentages (all originations as denominator for geographic metrics)
            'lmib_share': lmib_pct,
            'lmict_share': lmict_pct,
            'mmct_share': mmct_pct,
            # Counts
            'black_loans': row.get('black_loans', 0),
            'hispanic_loans': row.get('hispanic_loans', 0),
            'asian_loans': row.get('asian_loans', 0),
            'white_loans': row.get('white_loans', 0),
            'native_american_loans': row.get('native_american_loans', 0),
            'hopi_loans': row.get('hopi_loans', 0),
            'lmib_loans': row['lmib_loans'],
            'lmict_loans': row['lmict_loans'],
            'mmct_loans': row['mmct_loans']
        }
        
        results.append(result)
    
    return pd.DataFrame(results)


def process_market_data():
    """Process Tampa market data"""
    data_dir = Path("Member Reports/data/raw")
    
    # Load market data
    market_data = pd.read_csv(data_dir / "tampa_market_data.csv")
    
    # Filter to market overview only
    market_df = market_data[market_data['analysis_type'] == 'Market'].copy()
    
    # Calculate metrics
    market_metrics = calculate_metrics(market_df)
    
    # Save processed data
    output_dir = Path("Member Reports/data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    market_metrics.to_csv(output_dir / "tampa_market_metrics.csv", index=False)
    
    print(f"\nMarket metrics calculated:")
    print(f"  Years: {sorted(market_metrics['activity_year'].unique())}")
    print(f"\nSample metrics (2024):")
    # Try both string and int
    sample_2024_row = market_metrics[
        (market_metrics['activity_year'] == '2024') | 
        (market_metrics['activity_year'] == 2024)
    ]
    if len(sample_2024_row) > 0:
        sample_2024 = sample_2024_row.iloc[0]
        print(f"  Total originations: {sample_2024['total_originations']:,}")
        print(f"  Black homebuyer share: {sample_2024['black_homebuyer_share']:.1f}%")
        print(f"  Hispanic homebuyer share: {sample_2024['hispanic_homebuyer_share']:.1f}%")
        print(f"  Asian homebuyer share: {sample_2024['asian_homebuyer_share']:.1f}%")
        print(f"  LMIB share: {sample_2024['lmib_share']:.1f}%")
        print(f"  LMICT share: {sample_2024['lmict_share']:.1f}%")
        print(f"  MMCT share: {sample_2024['mmct_share']:.1f}%")
    else:
        print("  2024 data not found")
    
    return market_metrics


def process_top_lenders():
    """Process top 10 lenders data"""
    data_dir = Path("Member Reports/data/raw")
    
    # Load data
    market_data = pd.read_csv(data_dir / "tampa_market_data.csv")
    top_lenders = pd.read_csv(data_dir / "tampa_top_lenders_2024.csv")
    
    # Get top 10 LEIs
    top_10_leis = top_lenders['lei'].tolist()
    
    # Filter lender data to top 10
    lender_df = market_data[market_data['analysis_type'] == 'Lender'].copy()
    top_10_data = lender_df[lender_df['lei'].isin(top_10_leis)].copy()
    
    # Calculate metrics for each lender-year
    top_10_metrics = calculate_metrics(top_10_data)
    
    # Merge with lender names/LEIs for easier reading
    top_10_metrics = top_10_metrics.merge(
        top_lenders[['lei', 'total_originations_2024']].rename(columns={'total_originations_2024': 'rank_2024'}),
        on='lei',
        how='left'
    )
    top_10_metrics = top_10_metrics.sort_values(['rank_2024', 'activity_year'], ascending=[False, True])
    
    # Save processed data
    output_dir = Path("Member Reports/data/processed")
    top_10_metrics.to_csv(output_dir / "tampa_top_10_lenders_metrics.csv", index=False)
    
    print(f"\nTop 10 lender metrics calculated:")
    print(f"  {len(top_10_metrics)} lender-year rows")
    print(f"  {len(top_10_metrics['lei'].unique())} unique lenders")
    
    return top_10_metrics


if __name__ == '__main__':
    print("Processing Tampa market data...")
    market_metrics = process_market_data()
    top_10_metrics = process_top_lenders()
    
    print("\n" + "="*80)
    print("DATA PROCESSING COMPLETE")
    print("="*80)
    print("\nProcessed files:")
    print("  - tampa_market_metrics.csv")
    print("  - tampa_top_10_lenders_metrics.csv")
    print("\nReady for report generation!")

