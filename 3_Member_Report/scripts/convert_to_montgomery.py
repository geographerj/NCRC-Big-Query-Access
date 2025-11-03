"""Convert Tampa script to Montgomery script"""

import re

# Read Tampa script
with open('create_tampa_report.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replacements - location references
replacements = [
    ('Tampa', 'Montgomery County'),
    ('TAMPA', 'MONTGOMERY'),
    ('tampa', 'montgomery'),
    ('Tampa, Florida', 'Montgomery County, Maryland'),
    ('Tampa city', 'Montgomery County'),
    ('Tampa_FL', 'Montgomery_MD'),
    ('Tampa, FL', 'Montgomery County, MD'),
    ('Community Profile of Tampa, FL (City, 2020)', 'Community Profile of Montgomery, MD (County, 2022)'),
    ('tampa_community_profile_data.json', 'montgomery_community_profile_data.json'),
    ('tampa_market_report.json', 'montgomery_market_report.json'),
    ('tampa_market_metrics.csv', 'montgomery_market_metrics.csv'),
    ('tampa_top_10_lenders_metrics.csv', 'montgomery_top_10_lenders_metrics.csv'),
    ('tampa_top_lenders_2024.csv', 'montgomery_top_lenders_2024.csv'),
    ('tampa_market_data.csv', 'montgomery_market_data.csv'),
    ('130 census tracts', 'all census tracts within'),
    ('130 census tracts within the city boundaries', 'all census tracts within Montgomery County'),
    ('Tampa\'s', 'Montgomery County\'s'),
]

for old, new in replacements:
    content = content.replace(old, new)

# Replace load_tampa_data function
old_load_func = r'def load_tampa_data\(\):.*?return market_metrics, top_10_metrics, top_lenders'
new_load_func = '''def query_and_process_montgomery_data():
    """Query Montgomery County data from BigQuery and process it"""
    from queries.montgomery_market_query import build_montgomery_market_query
    try:
        sys.path.insert(0, str(member_reports_dir.parent / "Lending and Branch Analysis" / "utils"))
        from bigquery_client import create_client
        
        client = create_client()
        county_code = '24031'  # Montgomery County, MD
        years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
        
        print(f"Querying BigQuery for Montgomery County, MD (county code: {county_code})...")
        query = build_montgomery_market_query(county_code, years)
        raw_data = client.execute_query(query)
        print(f"  Retrieved {len(raw_data)} rows")
        
        # Process data
        market_data = raw_data[raw_data['analysis_type'] == 'Market'].copy()
        lender_data = raw_data[raw_data['analysis_type'] == 'Lender'].copy()
        
        # Calculate market metrics
        market_metrics = []
        for year in sorted(market_data['activity_year'].unique()):
            year_data = market_data[market_data['activity_year'] == year].iloc[0]
            total = year_data['total_originations']
            demo = year_data['loans_with_demographics']
            market_metrics.append({
                'activity_year': str(year),
                'total_originations': total,
                'loans_with_demographics': demo,
                'black_homebuyer_share': (year_data['black_loans'] / demo * 100) if demo > 0 else 0,
                'hispanic_homebuyer_share': (year_data['hispanic_loans'] / demo * 100) if demo > 0 else 0,
                'asian_homebuyer_share': (year_data['asian_loans'] / demo * 100) if demo > 0 else 0,
                'white_homebuyer_share': (year_data['white_loans'] / demo * 100) if demo > 0 else 0,
                'native_american_homebuyer_share': (year_data['native_american_loans'] / demo * 100) if demo > 0 else 0,
                'hopi_homebuyer_share': (year_data['hopi_loans'] / demo * 100) if demo > 0 else 0,
                'lmib_share': (year_data['lmib_loans'] / total * 100) if total > 0 else 0,
                'lmict_share': (year_data['lmict_loans'] / total * 100) if total > 0 else 0,
                'mmct_share': (year_data['mmct_loans'] / total * 100) if total > 0 else 0
            })
        market_metrics_df = pd.DataFrame(market_metrics)
        
        # Calculate lender metrics
        lender_metrics = []
        for (lei, year), group in lender_data.groupby(['lei', 'activity_year']):
            y = group.iloc[0]
            t = y['total_originations']
            d = y['loans_with_demographics']
            lender_metrics.append({
                'lei': lei,
                'activity_year': str(year),
                'total_originations': t,
                'loans_with_demographics': d,
                'black_homebuyer_share': (y['black_loans'] / d * 100) if d > 0 else 0,
                'hispanic_homebuyer_share': (y['hispanic_loans'] / d * 100) if d > 0 else 0,
                'asian_homebuyer_share': (y['asian_loans'] / d * 100) if d > 0 else 0,
                'white_homebuyer_share': (y['white_loans'] / d * 100) if d > 0 else 0,
                'native_american_homebuyer_share': (y['native_american_loans'] / d * 100) if d > 0 else 0,
                'hopi_homebuyer_share': (y['hopi_loans'] / d * 100) if d > 0 else 0,
                'lmib_share': (y['lmib_loans'] / t * 100) if t > 0 else 0,
                'lmict_share': (y['lmict_loans'] / t * 100) if t > 0 else 0,
                'mmct_share': (y['mmct_loans'] / t * 100) if t > 0 else 0
            })
        lender_metrics_df = pd.DataFrame(lender_metrics)
        
        # Get top 10 lenders by 2024 volume
        top_10_lenders = lender_data[lender_data['activity_year'] == '2024'].nlargest(10, 'total_originations')[['lei', 'total_originations']].copy()
        top_10_lenders = top_10_lenders.rename(columns={'total_originations': 'total_originations_2024'})
        top_10_lenders['respondent_name'] = None
        
        return market_metrics_df, lender_metrics_df, top_10_lenders
    except Exception as e:
        print(f"Error querying/processing data: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None'''

content = re.sub(old_load_func, new_load_func, content, flags=re.DOTALL)

# Update main function
content = content.replace('market_metrics, top_10_metrics, top_lenders = load_tampa_data()',
                         'market_metrics, top_10_metrics, top_lenders = query_and_process_montgomery_data()')
content = content.replace('Loading processed data...', 'Querying and processing HMDA data...')

# Update methodology
content = content.replace(
    'The analysis focuses on Tampa city, Florida, defined as 130 census tracts within the \ncity boundaries. Census tracts were identified from the Community Profile of Tampa, FL (City, 2020).',
    'The analysis focuses on Montgomery County, Maryland, encompassing all census tracts within the county. Geographic scope was identified from the Community Profile of Montgomery, MD (County, 2022).'
)

# Update generate_lender_lead_in
content = content.replace('lead_in = f"{lender_name} is one of the top lenders in the Tampa market."',
                         'lead_in = f"{lender_name} is one of the top lenders in the Montgomery County market."')

# Update methodology text
content = content.replace('Mortgage Lending in Tampa, Florida', 'Mortgage Lending in Montgomery County, Maryland')

# Write Montgomery script
with open('create_montgomery_report.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Created create_montgomery_report.py")

