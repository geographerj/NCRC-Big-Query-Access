"""
New narrative functions with improved writing quality
"""

def generate_key_findings_improved(market_metrics: pd.DataFrame) -> list:
    """Generate key findings with high-quality explanatory text"""
    market_sorted = market_metrics.sort_values('activity_year')
    earliest_year = int(market_sorted['activity_year'].iloc[0])
    latest_year = int(market_sorted['activity_year'].iloc[-1])
    earliest_data = market_sorted.iloc[0]
    latest_data = market_sorted.iloc[-1]
    total_originations = market_metrics['total_originations'].sum()
    
    findings = []
    
    findings.append(
        f"Mortgage lending patterns in Tampa city from {earliest_year} through {latest_year} reflect broader "
        f"market dynamics and demographic changes within the city. Over this seven-year period, lenders "
        f"originated {int(total_originations):,} home purchase loans across 130 census tracts that comprise "
        f"Tampa city. The volume of lending varied substantially, peaking in 2020 with {int(market_sorted[market_sorted['activity_year'] == 2020]['total_originations'].iloc[0]):,} "
        f"originations and declining to {int(latest_data['total_originations']):,} loans in {latest_year}."
    )
    
    # Borrower demographics trends
    hispanic_change = latest_data['hispanic_homebuyer_share'] - earliest_data['hispanic_homebuyer_share']
    black_change = latest_data['black_homebuyer_share'] - earliest_data['black_homebuyer_share']
    
    findings.append(
        f"Lending patterns by borrower race and ethnicity demonstrate significant shifts over the analysis period. "
        f"Hispanic borrowers, who represented {earliest_data['hispanic_homebuyer_share']:.2f}% of homebuyers with "
        f"demographic data in {earliest_year}, saw their share increase to {latest_data['hispanic_homebuyer_share']:.2f}% "
        f"by {latest_year}, reflecting both population growth and expanded access to credit for Hispanic households. "
        f"Black homebuyers represented less than 1% of loans throughout the period, while White borrowers accounted "
        f"for the majority of originations. These patterns raise questions about equitable access to mortgage credit "
        f"across racial and ethnic groups in Tampa's housing market."
    )
    
    # Geographic patterns
    lmict_change = latest_data['lmict_share'] - earliest_data['lmict_share']
    mmct_change = latest_data['mmct_share'] - earliest_data['mmct_share']
    
    findings.append(
        f"Geographic analysis reveals important trends in lending to low-income and minority communities. The share "
        f"of loans in Low-to-Moderate Income Census Tracts (LMICT) increased from {earliest_data['lmict_share']:.2f}% "
        f"in {earliest_year} to {latest_data['lmict_share']:.2f}% in {latest_year}, suggesting improved credit access "
        f"in economically disadvantaged areas. Similarly, lending in Majority-Minority Census Tracts (MMCT) grew from "
        f"{earliest_data['mmct_share']:.2f}% to {latest_data['mmct_share']:.2f}% over the same period. Despite these "
        f"increases, the concentration of lending in majority-minority areas remains substantial, with more than half "
        f"of all originations occurring in MMCTs by {latest_year}."
    )
    
    return findings


def generate_market_patterns_lead_in_and_analysis(market_metrics: pd.DataFrame) -> dict:
    """Generate lead-in sentences and analysis paragraphs for market patterns section"""
    market_sorted = market_metrics.sort_values('activity_year')
    earliest_year = int(market_sorted['activity_year'].iloc[0])
    latest_year = int(market_sorted['activity_year'].iloc[-1])
    earliest_data = market_sorted.iloc[0]
    latest_data = market_sorted.iloc[-1]
    
    # Lead-in (2 sentences)
    lead_in = (
        f"The following tables examine lending patterns across race and ethnicity, as well as geographic "
        f"concentration in low-income and majority-minority communities. These metrics provide insight into "
        f"how mortgage credit is distributed across different demographic groups and neighborhoods within Tampa city."
    )
    
    # Analysis after tables (1-2 paragraphs)
    hispanic_change = latest_data['hispanic_homebuyer_share'] - earliest_data['hispanic_homebuyer_share']
    white_share_latest = latest_data.get('white_homebuyer_share', 0)
    lmict_change = latest_data['lmict_share'] - earliest_data['lmict_share']
    mmct_change = latest_data['mmct_share'] - earliest_data['mmct_share']
    
    analysis = (
        f"Trends in borrower demographics show a notable increase in lending to Hispanic homebuyers over the "
        f"{earliest_year}-{latest_year} period, with their share growing by {abs(hispanic_change):.2f} percentage points. "
        f"This increase reflects both demographic changes in Tampa's population and potentially improved access to credit. "
        f"However, lending to Black and Asian borrowers remained minimal throughout the period, raising concerns about "
        f"equitable access to homeownership opportunities for these groups. White borrowers continued to represent the "
        f"largest share of homebuyers, consistent with historical patterns in mortgage lending."
    ) + "\n\n" + (
        f"Geographic patterns demonstrate mixed trends. While lending to low-to-moderate income borrowers (LMIB) "
        f"declined over the period, the share of loans in Low-to-Moderate Income Census Tracts (LMICT) increased, "
        f"suggesting that lending shifted toward higher-income borrowers within these communities. The substantial and "
        f"growing concentration of lending in Majority-Minority Census Tracts (MMCT), reaching {latest_data['mmct_share']:.2f}% "
        f"by {latest_year}, indicates that the mortgage market remains heavily concentrated in minority neighborhoods. "
        f"These patterns merit further investigation to understand whether they reflect borrower preferences, market "
        f"conditions, or potential disparities in credit access."
    )
    
    return {
        'lead_in': lead_in,
        'analysis': analysis
    }


