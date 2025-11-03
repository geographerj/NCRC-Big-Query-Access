"""
Create complete Montgomery County market report (PDF + Excel)

Generates report with:
- Introduction
- Key Findings
- Overall Market Patterns
- Top Lender Analysis (top 10)
- Methods and Sources
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import json
import re

# Add paths
member_reports_dir = Path(__file__).parent.parent
sys.path.insert(0, str(member_reports_dir))

# Import generators (using dynamic loading to avoid import errors)
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load generators
try:
    pdf_gen = load_module('pdf_generator',
                         str(member_reports_dir / 'generators' / 'pdf_generator.py'))
    PDFReportGenerator = pdf_gen.PDFReportGenerator
    
    excel_gen = load_module('excel_generator',
                            str(member_reports_dir / 'generators' / 'excel_generator.py'))
    ExcelReportGenerator = excel_gen.ExcelReportGenerator
except Exception as e:
    print(f"Warning: Could not load generators: {e}")
    PDFReportGenerator = None
    ExcelReportGenerator = None


def query_and_process_montgomery_data():
    """Query Montgomery County data from BigQuery and process it"""
    from queries.montgomery_market_query import build_montgomery_market_query
    try:
        sys.path.insert(0, str(member_reports_dir.parent / "Lending and Branch Analysis" / "utils"))
        from bigquery_client import create_client
        
        # Use the service account key file from C:\DREAM
        key_file_path = r"C:\DREAM\hdma1-242116-74024e2eb88f.json"
        client = create_client(key_path=key_file_path)
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
        return None, None, None


def get_lender_info(leis: list):
    """Get lender information from BigQuery lenders18 table"""
    try:
        sys.path.insert(0, str(member_reports_dir.parent / "Lending and Branch Analysis" / "utils"))
        from bigquery_client import create_client
        
        # Use the service account key file from C:\DREAM
        key_file_path = r"C:\DREAM\hdma1-242116-74024e2eb88f.json"
        client = create_client(key_path=key_file_path)
        
        # Format LEIs for SQL IN clause
        leis_str = "', '".join(leis)
        
        query = f"""
        SELECT 
            lei,
            respondent_name,
            type_name,
            assets,
            CAST(REPLACE(COALESCE(assets, '0'), ',', '') AS INT64) as assets_thousands
        FROM `hdma1-242116.hmda.lenders18`
        WHERE lei IN ('{leis_str}')
        """
        
        result = client.execute_query(query)
        
        # Convert assets from thousands to billions for display
        if 'assets_thousands' in result.columns:
            result['assets_billions'] = result['assets_thousands'] / 1000000
        else:
            result['assets_billions'] = None
            
        return result
    except Exception as e:
        print(f"Warning: Could not fetch lender info from BigQuery: {e}")
        return pd.DataFrame()


def create_market_overview_tables(market_metrics: pd.DataFrame) -> dict:
    """Create two tables: race/ethnicity and geographic metrics"""
    # Sort by year
    market_metrics = market_metrics.sort_values('activity_year')
    
    # Get unique years
    years = sorted(market_metrics['activity_year'].unique())
    
    # Table 1: Race/Ethnicity (Originations row + race metrics)
    race_table_rows = []
    
    # Row 1: Number of originations (#,### format)
    originations_row = ['Originations']
    for year in years:
        year_data = market_metrics[market_metrics['activity_year'] == year].iloc[0]
        originations_row.append(f"{int(year_data['total_originations']):,}")
    race_table_rows.append(originations_row)
    
    # Race/ethnicity metrics (remove "Share" and "Homebuyer" from names)
    race_metrics = [
        ('Black %', 'black_homebuyer_share'),
        ('Hispanic %', 'hispanic_homebuyer_share'),
        ('Asian %', 'asian_homebuyer_share'),
        ('White %', 'white_homebuyer_share'),
        ('Native American %', 'native_american_homebuyer_share'),
        ('Hawaiian/Pacific Islander %', 'hopi_homebuyer_share')
    ]
    
    for metric_name, metric_col in race_metrics:
        metric_row = [metric_name]
        for year in years:
            year_data = market_metrics[market_metrics['activity_year'] == year].iloc[0]
            metric_row.append(f"{year_data.get(metric_col, 0):.1f}")
        race_table_rows.append(metric_row)
    
    race_columns = ['Metric'] + [str(year) for year in years]
    race_table = pd.DataFrame(race_table_rows, columns=race_columns)
    
    # Table 2: Geographic metrics (Originations row + geographic metrics)
    geo_table_rows = []
    
    # Row 1: Number of originations
    originations_row = ['Originations']
    for year in years:
        year_data = market_metrics[market_metrics['activity_year'] == year].iloc[0]
        originations_row.append(f"{int(year_data['total_originations']):,}")
    geo_table_rows.append(originations_row)
    
    # Geographic metrics (remove "Share" from names)
    geo_metrics = [
        ('LMIB %', 'lmib_share'),
        ('LMICT %', 'lmict_share'),
        ('MMCT %', 'mmct_share')
    ]
    
    for metric_name, metric_col in geo_metrics:
        metric_row = [metric_name]
        for year in years:
            year_data = market_metrics[market_metrics['activity_year'] == year].iloc[0]
            metric_row.append(f"{year_data[metric_col]:.1f}")
        geo_table_rows.append(metric_row)
    
    geo_columns = ['Metric'] + [str(year) for year in years]
    geo_table = pd.DataFrame(geo_table_rows, columns=geo_columns)
    
    return {
        'race_ethnicity': race_table,
        'geographic': geo_table
    }


def format_lender_name(name: str) -> str:
    """Format lender name - preserve GLEIF capitalization, remove entity suffixes"""
    if pd.isna(name) or name == '':
        return name
    
    name_str = str(name).strip()
    
    # Fix common spacing issues with ordinal numbers (preserve case)
    # Replace "1 ST" with "1st", "2 ND" with "2nd", "3 RD" with "3rd", "4 TH" with "4th", etc.
    name_str = re.sub(r'\b(\d+)\s+(ST|ND|RD|TH)\b', lambda m: f"{m.group(1)}{m.group(2).lower()}", name_str, flags=re.IGNORECASE)
    name_str = re.sub(r'(\d)\s+(ST|ND|RD|TH)\b', lambda m: f"{m.group(1)}{m.group(2).lower()}", name_str, flags=re.IGNORECASE)
    
    # Remove common entity suffixes (case-insensitive)
    # Patterns: ", LLC", ", INC.", ", INC", ", National Association", ", Corporation", ", Corp.", etc.
    # Also handle cases without comma: "Corporation", "Corp", etc.
    entity_suffixes_with_comma = [
        r',\s*LLC\.?$',
        r',\s*INC\.?$',
        r',\s*INCORPORATED\.?$',
        r',\s*CORP\.?$',
        r',\s*CORPORATION\.?$',
        r',\s*NATIONAL ASSOCIATION\.?$',
        r',\s*NA\.?$',
        r',\s*L\.L\.C\.?$',
        r',\s*L\.P\.?$',
        r',\s*LP\.?$',
        r',\s*LTD\.?$',
        r',\s*LIMITED\.?$',
        r',\s*PC\.?$',
        r',\s*P\.C\.?$',
    ]
    
    # Also remove entity words without comma (but be careful - only at end)
    entity_suffixes_without_comma = [
        r'\s+LLC\.?$',
        r'\s+INC\.?$',
        r'\s+INCORPORATED\.?$',
        r'\s+CORP\.?$',
        r'\s+CORPORATION\.?$',
        r'\s+NATIONAL ASSOCIATION\.?$',
        r'\s+NA\.?$',
    ]
    
    # First remove with comma patterns
    for pattern in entity_suffixes_with_comma:
        name_str = re.sub(pattern, '', name_str, flags=re.IGNORECASE)
    
    # Then remove without comma (less aggressive - only at end)
    for pattern in entity_suffixes_without_comma:
        name_str = re.sub(pattern, '', name_str, flags=re.IGNORECASE)
    
    # Fix multiple spaces
    name_str = re.sub(r'\s+', ' ', name_str)
    
    # If name is all caps and longer than 5 chars, convert to Title Case
    # (GLEIF sometimes returns all caps, but we want proper case)
    # However, preserve special cases like "TowneBank" or acronyms
    if name_str.isupper() and len(name_str) > 5:
        # Convert to title case but handle special cases
        # Don't title case if it contains common acronyms that should stay uppercase
        name_str = name_str.title()
    
    # Preserve GLEIF capitalization when it's already in proper case
    return name_str.strip()


def lookup_lender_info_by_lei(lei: str) -> dict:
    """Look up lender information using LEI number via GLEIF API (official source)
    
    Returns:
        Dictionary with:
        - 'name': Legal name of the entity
        - 'headquarters': City, State format (e.g., "Fairfax, Virginia")
        - 'headquarters_address': Full address if available
        - 'country': Country code
        - 'lei_url': Direct link to GLEIF record for this LEI
    """
    try:
        import requests
        
        # Use GLEIF REST API (official Global LEI Index)
        gleif_url = f"https://api.gleif.org/api/v1/lei-records/{lei}"
        
        response = requests.get(gleif_url, timeout=10, headers={'Accept': 'application/vnd.api+json'})
        if response.status_code == 200:
            data = response.json()
            result = {
                'name': '',
                'headquarters': None,
                'headquarters_address': None,
                'country': None,
                'lei_url': f"https://search.gleif.org/#/record/{lei}"
            }
            
            if 'data' in data and 'attributes' in data['data']:
                entity = data['data']['attributes'].get('entity', {})
                
                # Extract legal name
                legal_name = entity.get('legalName', {}).get('name', '')
                if not legal_name:
                    other_entity_names = entity.get('otherEntityNames', [])
                    if other_entity_names and len(other_entity_names) > 0:
                        legal_name = other_entity_names[0].get('name', '')
                
                result['name'] = legal_name
                
                # Extract headquarters address
                hq_address = entity.get('headquartersAddress', {})
                if hq_address:
                    city = hq_address.get('city', '')
                    region = hq_address.get('region', '')
                    country = hq_address.get('country', '')
                    
                    # Format region (convert "US-VA" to "Virginia")
                    if region.startswith('US-'):
                        state_code = region.split('-')[1]
                        # Convert state code to state name (basic mapping)
                        us_states = {
                            'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
                            'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
                            'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
                            'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
                            'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
                            'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
                            'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
                            'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
                            'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
                            'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
                            'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
                            'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
                            'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
                        }
                        state_name = us_states.get(state_code, state_code)
                    else:
                        state_name = region
                    
                    if city and state_name:
                        result['headquarters'] = f"{city}, {state_name}"
                    
                    # Full address
                    address_lines = hq_address.get('addressLines', [])
                    postal_code = hq_address.get('postalCode', '')
                    if address_lines:
                        full_address = ', '.join(filter(None, [', '.join(address_lines), city, state_name, postal_code]))
                        result['headquarters_address'] = full_address
                    
                    result['country'] = country
            
            if result['name']:
                return result
        
        return {}
        
    except ImportError:
        # requests library not available
        return {}
    except Exception as e:
        # Silently fail - will use BigQuery info
        return {}


def lookup_lender_name_by_lei(lei: str) -> str:
    """Look up lender name using LEI number via GLEIF API (backward compatibility wrapper)"""
    info = lookup_lender_info_by_lei(lei)
    return info.get('name', '')


def create_top_lenders_tables(top_10_metrics: pd.DataFrame, top_lenders: pd.DataFrame, lender_info: pd.DataFrame = None) -> dict:
    """Create separate table for each top 10 lender - years as columns, metrics as rows
    
    Returns:
        tuple: (lender_tables_pdf, lender_tables_excel, lender_metadata)
        - lender_tables_pdf: Tables for PDF (without Native American, HoPI, No Data)
        - lender_tables_excel: Tables for Excel (with all metrics including Native American, HoPI, No Data)
        - lender_metadata: Metadata for each lender
    """
    # Get list of top 10 LEIs
    top_10_leis = top_lenders['lei'].tolist()
    
    # Merge lender_info with top_lenders to get respondent_name
    if lender_info is not None and len(lender_info) > 0 and 'respondent_name' in lender_info.columns:
        # Merge lender names into top_lenders
        top_lenders = top_lenders.merge(
            lender_info[['lei', 'respondent_name']],
            on='lei',
            how='left'
        )
        # If respondent_name_y exists (from merge conflict), use it, otherwise use respondent_name_x or respondent_name
        if 'respondent_name_y' in top_lenders.columns:
            top_lenders['respondent_name'] = top_lenders['respondent_name_y'].fillna(top_lenders.get('respondent_name_x', ''))
            top_lenders = top_lenders.drop(columns=['respondent_name_x', 'respondent_name_y'], errors='ignore')
    
    # Filter metrics to ONLY top 10 lenders
    top_10_filtered = top_10_metrics[top_10_metrics['lei'].isin(top_10_leis)].copy()
    
    # Merge with lender names and ranking
    merged = top_10_filtered.merge(
        top_lenders[['lei', 'respondent_name', 'total_originations_2024']].rename(columns={'total_originations_2024': 'rank_2024'}),
        on='lei',
        how='left'
    )
    
    # Sort by rank
    if 'rank_2024' in merged.columns:
        merged = merged.sort_values(['rank_2024'], ascending=[False])
    
    # Create separate table for each lender
    lender_tables_pdf = {}
    lender_tables_excel = {}
    lender_metadata = {}  # Store metadata for each lender
    
    for lei in top_10_leis:
        lender_data = merged[merged['lei'] == lei].sort_values('activity_year')
        
        if len(lender_data) == 0:
            continue
            
        # Always look up lender name from GLEIF first (most accurate source)
        print(f"    Looking up official name for LEI: {lei[:8]}...")
        looked_up_name = lookup_lender_name_by_lei(lei)
        
        if looked_up_name:
            # Use GLEIF official name (most accurate)
            lender_name = format_lender_name(looked_up_name)
            print(f"      Using GLEIF name: {lender_name}")
        else:
            # Fallback to BigQuery name if GLEIF lookup fails
            lender_name_raw = lender_data.iloc[0].get('respondent_name', lei)
            if pd.isna(lender_name_raw) or lender_name_raw == '' or lender_name_raw == lei:
                lender_name = lei
            else:
                lender_name = format_lender_name(lender_name_raw)
                print(f"      Using BigQuery name: {lender_name} (GLEIF lookup failed)")
        
        # Get unique years
        years = sorted(lender_data['activity_year'].unique())
        
        # Create PDF table with years as columns (basic metrics)
        pdf_table_rows = []
        
        # Row 1: Number of originations (#,### format)
        originations_row = ['Originations']
        for year in years:
            year_data = lender_data[lender_data['activity_year'] == year].iloc[0]
            originations_row.append(f"{int(year_data['total_originations']):,}")
        pdf_table_rows.append(originations_row)
        
        # Following rows: Each metric with percentages (##.## format) - PDF version (basic metrics)
        pdf_metrics = [
            ('Black %', 'black_homebuyer_share'),
            ('Hispanic %', 'hispanic_homebuyer_share'),
            ('Asian %', 'asian_homebuyer_share'),
            ('LMIB %', 'lmib_share'),
            ('LMICT %', 'lmict_share'),
            ('MMCT %', 'mmct_share')
        ]
        
        for metric_name, metric_col in pdf_metrics:
            metric_row = [metric_name]
            for year in years:
                year_data = lender_data[lender_data['activity_year'] == year].iloc[0]
                metric_row.append(f"{year_data[metric_col]:.1f}")
            pdf_table_rows.append(metric_row)
        
        # Create Excel table with additional metrics
        excel_table_rows = pdf_table_rows.copy()
        
        # Add Native American, HoPI, and No Data metrics for Excel
        excel_metrics = [
            ('Native American %', 'native_american_homebuyer_share'),
            ('Hawaiian/Pacific Islander %', 'hopi_homebuyer_share')
        ]
        
        for metric_name, metric_col in excel_metrics:
            metric_row = [metric_name]
            for year in years:
                year_data = lender_data[lender_data['activity_year'] == year].iloc[0]
                metric_row.append(f"{year_data[metric_col]:.1f}")
            excel_table_rows.append(metric_row)
        
        # Add No Data loans row (count, not percentage)
        no_data_row = ['No Data Loans']
        for year in years:
            year_data = lender_data[lender_data['activity_year'] == year].iloc[0]
            total = year_data['total_originations']
            with_demo = year_data.get('loans_with_demographics', 0)
            no_data_count = total - with_demo
            no_data_row.append(f"{int(no_data_count):,}")
        excel_table_rows.append(no_data_row)
        
        # Create DataFrames with years as column headers
        columns = ['Metric'] + [str(year) for year in years]
        lender_tables_pdf[lender_name] = pd.DataFrame(pdf_table_rows, columns=columns)
        lender_tables_excel[lender_name] = pd.DataFrame(excel_table_rows, columns=columns)
        
        # Store metadata for this lender
        lender_metadata[lender_name] = {
            'lei': lei,
            'lender_data': lender_data
        }
    
    return lender_tables_pdf, lender_tables_excel, lender_metadata


def generate_key_findings(market_metrics: pd.DataFrame) -> list:
    """Generate key findings focusing on trends over time"""
    market_sorted = market_metrics.sort_values('activity_year')
    earliest_year = int(market_sorted['activity_year'].iloc[0])
    latest_year = int(market_sorted['activity_year'].iloc[-1])
    earliest_data = market_sorted.iloc[0]
    latest_data = market_sorted.iloc[-1]
    total_originations = market_metrics['total_originations'].sum()
    
    findings = []
    
    # Overall volume
    findings.append(
        f"Lenders originated {int(total_originations):,} home purchase loans in Montgomery County from {earliest_year} through {latest_year}."
    )
    
    # Hispanic lending trend - dramatic expansion
    hispanic_earliest = earliest_data['hispanic_homebuyer_share']
    hispanic_latest = latest_data['hispanic_homebuyer_share']
    hispanic_change = hispanic_latest - hispanic_earliest
    if abs(hispanic_change) > 5:
        findings.append(
            f"Hispanic borrowers experienced a significant expansion in lending share, increasing from {hispanic_earliest:.1f}% in {earliest_year} to {hispanic_latest:.1f}% in {latest_year}, representing a {abs(hispanic_change):.1f} percentage point increase over the period."
        )
    
    # Black lending - stagnation
    black_earliest = earliest_data['black_homebuyer_share']
    black_latest = latest_data['black_homebuyer_share']
    black_change = black_latest - black_earliest
    if abs(black_change) < 2:
        findings.append(
            f"Lending to Black borrowers remained relatively stagnant over the period, with Black borrowers representing {black_latest:.1f}% of borrowers in {latest_year}, compared to {black_earliest:.1f}% in {earliest_year}."
        )
    
    # LMICT lending - expansion
    lmict_earliest = earliest_data['lmict_share']
    lmict_latest = latest_data['lmict_share']
    lmict_change = lmict_latest - lmict_earliest
    if abs(lmict_change) > 5:
        direction = "expanded" if lmict_change > 0 else "declined"
        findings.append(
            f"Lending in Low-to-Moderate Income Census Tracts (LMICT) {direction} over the period, with LMICT receiving {lmict_latest:.1f}% of all originations in {latest_year}, up from {lmict_earliest:.1f}% in {earliest_year}."
        )
    
    # LMIB lending - decline
    lmib_earliest = earliest_data['lmib_share']
    lmib_latest = latest_data['lmib_share']
    lmib_change = lmib_latest - lmib_earliest
    if lmib_change < -2:
        findings.append(
            f"Lending to Low-to-Moderate Income Borrowers (LMIB) declined over the period, with LMIB representing {lmib_latest:.1f}% of all originations in {latest_year}, down from {lmib_earliest:.1f}% in {earliest_year}."
        )
    
    # MMCT (with note about 2020 census boundary change)
    mmct_earliest = earliest_data['mmct_share']
    mmct_latest = latest_data['mmct_share']
    mmct_change = mmct_latest - mmct_earliest
    if abs(mmct_change) > 5:
        findings.append(
            f"Lending in Majority-Minority Census Tracts (MMCT) expanded from {mmct_earliest:.1f}% in {earliest_year} to {mmct_latest:.1f}% in {latest_year}. "
            f"This increase should be interpreted in the context of the 2020 census boundary changes, which created approximately 30% more majority-minority census tracts nationally. "
            f"However, these boundary changes did not take effect in HMDA data until 2022."
        )
    
    return findings


def load_community_profile_data() -> dict:
    """Load community profile data - try Census API first, then fall back to JSON file"""
    # Try Census API first (includes current + 2020/2010 comparison data)
    try:
        sys.path.insert(0, str(member_reports_dir / 'utils'))
        from census_api_client import get_census_data_for_county
        
        # Montgomery County, MD: state FIPS = 24, county FIPS = 031
        print("  Attempting to fetch data from Census API...")
        census_data = get_census_data_for_county(
            county_fips='031',
            state_fips='24',
            include_comparison_years=True,  # Get 2020, 2010, and 2000 data for comparison
            include_2000=True  # Include 2000 for long-term trend analysis
        )
        
        if census_data and census_data.get('demographics'):
            print("  ✓ Loaded current data from Census API")
            if census_data.get('comparison_years'):
                print(f"  ✓ Loaded comparison data: {', '.join(census_data['comparison_years'].keys())}")
            return census_data
    except Exception as e:
        print(f"  Could not load from Census API: {e}")
        print("  Falling back to JSON file...")
    
    # Fall back to JSON file
    profile_path = member_reports_dir / "data" / "processed" / "montgomery_community_profile_data.json"
    if profile_path.exists():
        try:
            with open(profile_path, 'r') as f:
                data = json.load(f)
                print("  Loaded data from JSON file (no comparison years available)")
                return data
        except Exception as e:
            print(f"  Warning: Could not load community profile data: {e}")
    
    return {}


def generate_introduction(community_data: dict = None) -> str:
    """Generate introduction section with community profile context"""
    intro = "This report examines mortgage lending patterns in Montgomery County, Maryland from 2018 through 2024, focusing on home purchase originations within Montgomery County. The analysis encompasses all census tracts within the county and evaluates lending outcomes by borrower demographics and geographic characteristics, using standard fair lending metrics.\n\n"
    
    # Add community profile context if available
    if community_data:
        demographics = community_data.get('demographics', {})
        income = community_data.get('income', {})
        
        demo_parts = []
        if demographics.get('total_population'):
            pop = demographics['total_population']
            if pop > 1000:  # Sanity check - avoid small numbers that might be errors
                # Determine data source citation
                profile_year = community_data.get('profile_year', '2022')
                if 'ACS' in str(profile_year) or 'Census' in str(profile_year):
                    citation = "According to U.S. Census Bureau data"
                else:
                    citation = "According to the Community Profile of Montgomery, MD (County, 2022)"
                demo_parts.append(f"{citation}, Montgomery County has a population of approximately {pop:,}")
        
        demo_percentages = []
        if demographics.get('hispanic_percentage'):
            demo_percentages.append(f"{demographics['hispanic_percentage']:.1f}% Hispanic or Latino")
        if demographics.get('black_percentage'):
            demo_percentages.append(f"{demographics['black_percentage']:.1f}% Black or African American")
        if demographics.get('white_percentage'):
            demo_percentages.append(f"{demographics['white_percentage']:.1f}% White")
        if demographics.get('asian_percentage'):
            demo_percentages.append(f"{demographics['asian_percentage']:.1f}% Asian")
        
        if demo_percentages:
            if demo_parts:
                intro += f"{demo_parts[0]}, with {', '.join(demo_percentages)}. "
            else:
                # Determine citation based on data source
                profile_year = community_data.get('profile_year', '2022')
                if 'ACS' in str(profile_year) or 'Census' in str(profile_year):
                    citation = "According to U.S. Census Bureau American Community Survey data"
                else:
                    citation = "According to the Community Profile of Montgomery, MD (County, 2022)"
                intro += f"{citation}, the county's population is {', '.join(demo_percentages)}. "
        
        if income.get('median_household_income'):
            median_income = income['median_household_income']
            intro += f"The community profile reports a median household income of ${median_income:,}. "
        
        # Add demographic trend context
        trends = community_data.get('trends', {})
        if trends.get('demographic_shifts'):
            intro += f"Demographic trends show {', '.join(trends['demographic_shifts'])}. "
        elif demographics.get('hispanic_percentage') and demographics.get('hispanic_percentage', 0) > 25:
            intro += "The community profile documents significant growth in the Hispanic and Latino population over recent years, reflecting broader demographic shifts across Maryland. "
    
    if not community_data or not community_data.get('demographics'):
        # Fallback if no community profile data
        intro += "Montgomery County is a diverse metropolitan area with a growing population that reflects broader demographic trends in Maryland. The county has experienced significant growth in Hispanic and Latino residents over the past decade, while maintaining a substantial White population and smaller but important Black, Asian, and other racial and ethnic communities. "
    
    intro += "Demographic shifts in Montgomery County mirror state and national patterns, with increasing diversity contributing to changes in housing demand and mortgage lending patterns.\n\n"
    intro += "The report presents a market-wide overview of lending patterns, followed by a detailed analysis of the top 10 lenders ranked by 2024 home purchase origination volume. Each lender's performance is evaluated across the full 2018-2024 period to assess trends and patterns in fair lending outcomes."
    
    return intro.strip()


def analyze_demographic_trends(community_data: dict) -> dict:
    """Analyze long-term demographic trends from 2000, 2010, 2020, and current ACS data
    
    Returns:
        Dictionary with trend analysis for each demographic group
    """
    trends = {
        'hispanic_trend': None,
        'black_trend': None,
        'asian_trend': None,
        'white_trend': None
    }
    
    if not community_data or not community_data.get('comparison_years'):
        return trends
    
    current = community_data.get('demographics', {})
    census_2020 = community_data.get('comparison_years', {}).get('2020', {}).get('demographics', {})
    census_2010 = community_data.get('comparison_years', {}).get('2010', {}).get('demographics', {})
    census_2000 = community_data.get('comparison_years', {}).get('2000', {}).get('demographics', {})
    
    # Analyze Hispanic trends
    if census_2000 and census_2010 and census_2020 and current:
        hispanic_2000 = census_2000.get('hispanic_percentage', 0)
        hispanic_2010 = census_2010.get('hispanic_percentage', 0)
        hispanic_2020 = census_2020.get('hispanic_percentage', 0)
        hispanic_current = current.get('hispanic_percentage', 0)
        
        if hispanic_2000 and hispanic_current:
            change_2000_to_current = hispanic_current - hispanic_2000
            if change_2000_to_current > 5:
                trends['hispanic_trend'] = {
                    'direction': 'rising',
                    'change': change_2000_to_current,
                    '2000': hispanic_2000,
                    '2010': hispanic_2010,
                    '2020': hispanic_2020,
                    'current': hispanic_current
                }
    
    # Analyze Black/African American trends
    if census_2000 and census_2010 and census_2020 and current:
        black_2000 = census_2000.get('black_percentage', 0)
        black_2010 = census_2010.get('black_percentage', 0)
        black_2020 = census_2020.get('black_percentage', 0)
        black_current = current.get('black_percentage', 0)
        
        if black_2000 and black_current:
            change_2000_to_current = black_current - black_2000
            # Stagnation: little change over 20+ years
            if abs(change_2000_to_current) < 3:
                trends['black_trend'] = {
                    'direction': 'stagnant',
                    'change': change_2000_to_current,
                    '2000': black_2000,
                    '2010': black_2010,
                    '2020': black_2020,
                    'current': black_current
                }
    
    # Analyze Asian trends
    if census_2000 and census_2010 and census_2020 and current:
        asian_2000 = census_2000.get('asian_percentage', 0)
        asian_2010 = census_2010.get('asian_percentage', 0)
        asian_2020 = census_2020.get('asian_percentage', 0)
        asian_current = current.get('asian_percentage', 0)
        
        if asian_2000 and asian_current:
            change_2000_to_current = asian_current - asian_2000
            if change_2000_to_current > 3:
                trends['asian_trend'] = {
                    'direction': 'rising',
                    'change': change_2000_to_current,
                    '2000': asian_2000,
                    '2010': asian_2010,
                    '2020': asian_2020,
                    'current': asian_current
                }
    
    # Analyze White trends
    if census_2000 and census_2010 and census_2020 and current:
        white_2000 = census_2000.get('white_percentage', 0)
        white_2010 = census_2010.get('white_percentage', 0)
        white_2020 = census_2020.get('white_percentage', 0)
        white_current = current.get('white_percentage', 0)
        
        if white_2000 and white_current:
            change_2000_to_current = white_current - white_2000
            if change_2000_to_current < -5:
                trends['white_trend'] = {
                    'direction': 'declining',
                    'change': change_2000_to_current,
                    '2000': white_2000,
                    '2010': white_2010,
                    '2020': white_2020,
                    'current': white_current
                }
    
    return trends


def generate_market_patterns_narrative(market_metrics: pd.DataFrame, community_data: dict = None) -> dict:
    """Generate lead-in and analysis for market patterns section"""
    market_sorted = market_metrics.sort_values('activity_year')
    earliest_year = int(market_sorted['activity_year'].iloc[0])
    latest_year = int(market_sorted['activity_year'].iloc[-1])
    earliest_data = market_sorted.iloc[0]
    latest_data = market_sorted.iloc[-1]
    
    # Lead-in with community profile context
    if community_data and community_data.get('demographics'):
        demographics = community_data['demographics']
        demo_parts = []
        if demographics.get('hispanic_percentage'):
            demo_parts.append(f"{demographics['hispanic_percentage']:.1f}% Hispanic or Latino")
        if demographics.get('black_percentage'):
            demo_parts.append(f"{demographics['black_percentage']:.1f}% Black or African American")
        if demographics.get('white_percentage'):
            demo_parts.append(f"{demographics['white_percentage']:.1f}% White")
        if demographics.get('asian_percentage'):
            demo_parts.append(f"{demographics['asian_percentage']:.1f}% Asian")
        
        if demo_parts:
            # Determine citation based on data source
            profile_year = community_data.get('profile_year', '2022')
            if 'ACS' in str(profile_year) or 'Census' in str(profile_year):
                citation = "According to U.S. Census Bureau American Community Survey data"
            else:
                citation = "According to the Community Profile of Montgomery, MD (County, 2022)"
            lead_in = (
                f"{citation}, Montgomery County's population is composed of "
                f"{', '.join(demo_parts)}. The following tables examine how mortgage lending patterns align with these "
                f"demographic characteristics, as well as geographic concentration in low-income and majority-minority communities."
            )
        else:
            lead_in = (
                f"The following tables examine lending patterns across race and ethnicity, as well as geographic "
                f"concentration in low-income and majority-minority communities. These metrics provide insight into "
                f"how mortgage credit is distributed across different demographic groups and neighborhoods within Montgomery County."
            )
    else:
        lead_in = (
            f"The following tables examine lending patterns across race and ethnicity, as well as geographic "
            f"concentration in low-income and majority-minority communities. These metrics provide insight into "
                f"how mortgage credit is distributed across different demographic groups and neighborhoods within Montgomery County."
        )
    
    # Analyze long-term demographic trends from Census data (2000, 2010, 2020, current)
    demographic_trends = analyze_demographic_trends(community_data) if community_data else {}
    
    # Analysis after tables - plain English narrative
    hispanic_change = latest_data['hispanic_homebuyer_share'] - earliest_data['hispanic_homebuyer_share']
    black_change = latest_data['black_homebuyer_share'] - earliest_data['black_homebuyer_share']
    lmict_change = latest_data['lmict_share'] - earliest_data['lmict_share']
    mmct_change = latest_data['mmct_share'] - earliest_data['mmct_share']
    lmib_change = latest_data['lmib_share'] - earliest_data['lmib_share']
    
    # Build analysis in plain English with community profile context and historical trends
    analysis_parts = []
    
    # Add demographic trend context paragraph at the beginning
    trend_paragraphs = []
    if demographic_trends.get('hispanic_trend'):
        ht = demographic_trends['hispanic_trend']
        trend_paragraphs.append(
            f"Census data shows that Montgomery County's Hispanic and Latino population has grown substantially over the past two decades, "
            f"increasing from {ht['2000']:.1f}% in 2000 to {ht['2010']:.1f}% in 2010, {ht['2020']:.1f}% in 2020, and "
            f"{ht['current']:.1f}% in the most recent American Community Survey data. This {ht['change']:.1f} percentage point increase "
            f"since 2000 reflects the rising influence of Hispanic residents in the county's demographic composition."
        )
    
    if demographic_trends.get('asian_trend'):
        at = demographic_trends['asian_trend']
        trend_paragraphs.append(
            f"Similarly, the Asian population has experienced notable growth, rising from {at['2000']:.1f}% in 2000 to "
            f"{at['2010']:.1f}% in 2010, {at['2020']:.1f}% in 2020, and {at['current']:.1f}% in recent ACS data. "
            f"This represents a {at['change']:.1f} percentage point increase since 2000, demonstrating the expanding presence "
            f"of Asian communities in Montgomery County."
        )
    
    if demographic_trends.get('black_trend'):
        bt = demographic_trends['black_trend']
        trend_paragraphs.append(
            f"In contrast, the Black or African American population has remained relatively stable over this period, "
            f"comprising {bt['2000']:.1f}% in 2000, {bt['2010']:.1f}% in 2010, {bt['2020']:.1f}% in 2020, and "
            f"{bt['current']:.1f}% in recent data. This long-term stagnation in the Black population share highlights "
            f"persistent demographic patterns that may influence lending outcomes."
        )
    
    if demographic_trends.get('white_trend'):
        wt = demographic_trends['white_trend']
        trend_paragraphs.append(
            f"Meanwhile, the White population share has declined from {wt['2000']:.1f}% in 2000 to {wt['2010']:.1f}% in 2010, "
            f"{wt['2020']:.1f}% in 2020, and {wt['current']:.1f}% in recent ACS data, representing a "
            f"{abs(wt['change']):.1f} percentage point decrease over the period."
        )
    
    if trend_paragraphs:
        analysis_parts.extend(trend_paragraphs)
        analysis_parts.append("")  # Empty line for spacing
    
    # Get community demographics for comparison
    comm_hispanic = None
    comm_black = None
    comm_white = None
    comm_asian = None
    poverty_rate = None
    
    if community_data and community_data.get('demographics'):
        comm_hispanic = community_data['demographics'].get('hispanic_percentage')
        comm_black = community_data['demographics'].get('black_percentage')
        comm_white = community_data['demographics'].get('white_percentage')
        comm_asian = community_data['demographics'].get('asian_percentage')
    if community_data and community_data.get('income'):
        poverty_rate = community_data['income'].get('poverty_rate')
    
    lending_hispanic = latest_data['hispanic_homebuyer_share']
    black_latest = latest_data['black_homebuyer_share']
    white_share_latest = latest_data.get('white_homebuyer_share', 0)
    
    # Hispanic lending - compare to demographics and national trends
    if abs(hispanic_change) > 5:
        analysis_parts.append(
            f"Lending to Hispanic borrowers expanded significantly over the period. This growth reflects Montgomery County's "
            f"increasingly diverse population and suggests improved access to mortgage credit for Hispanic families."
        )
        
        if comm_hispanic:
            gap = lending_hispanic - comm_hispanic
            if abs(gap) > 10:  # Only cite specific gap if very large
                if gap < 0:
                    analysis_parts.append(
                        f"However, the share of loans going to Hispanic borrowers remains below their representation "
                        f"in the community's population. According to the Community Profile of Montgomery, MD (County, 2022), "
                        f"Hispanic and Latino residents make up a larger portion of Montgomery County's population than their share "
                        f"of mortgage lending, indicating continued room for improvement in credit access."
                    )
                else:
                    analysis_parts.append(
                        f"This lending share now exceeds the Hispanic population share in Montgomery County, reflecting strong "
                        f"access to mortgage credit relative to the community's demographics. This aligns with national "
                        f"trends where Hispanic borrowers have achieved representation in mortgage lending that matches or "
                        f"exceeds their share of the population (see NCRC's 2025 Mortgage Market Series, Part 1)."
                    )
            elif gap > 0:
                analysis_parts.append(
                    f"This lending pattern now aligns with or exceeds the Hispanic population share in Montgomery County, "
                    f"showing that mortgage credit access for Hispanic borrowers has improved over time. This mirrors "
                    f"national patterns where Hispanic borrower participation in mortgage lending has expanded significantly."
                )
        else:
            analysis_parts.append(
                f"This expansion likely reflects both demographic changes in Montgomery County's population and improved "
                f"access to credit for Hispanic borrowers seeking homeownership, consistent with broader national "
                f"trends in Hispanic mortgage lending."
            )
    
    # Black lending - compare to demographics, highlight concerns
    if abs(black_change) < 2:
        analysis_parts.append(
            f"In contrast, lending to Black borrowers remained essentially unchanged throughout the period, "
            f"raising questions about equitable access to homeownership opportunities."
        )
        
        if comm_black:
            black_gap = black_latest - comm_black
            if abs(black_gap) > 10:  # Only cite specific gap if very large
                analysis_parts.append(
                    f"The share of loans going to Black borrowers falls well below their representation in Montgomery County's population. "
                    f"The Community Profile of Montgomery, MD (County, 2022) shows that Black residents make up a substantially "
                    f"larger portion of the county's population than their share of mortgage lending would suggest. "
                    f"This gap between population demographics and lending patterns warrants attention and reflects a persistent "
                    f"national pattern where Black borrower participation in mortgage lending remains well below population "
                    f"representation (see NCRC's 2025 Mortgage Market Series, Part 1 and Part 2)."
                )
            elif black_gap < 0:
                analysis_parts.append(
                    f"Black borrowers receive a smaller share of loans than their representation in the community's population, "
                    f"suggesting that barriers to credit access may persist despite overall lending growth in the market. "
                    f"This aligns with national trends showing stagnant Black borrower participation in mortgage lending."
                )
            else:
                analysis_parts.append(
                    f"While lending to Black borrowers has not increased, the current share is roughly aligned with "
                    f"their representation in Montgomery County's population."
                )
        else:
            analysis_parts.append(
                f"This stagnation is concerning given the importance of homeownership for wealth building, "
                f"and suggests that efforts to expand credit access may not have reached Black borrowers equally. "
                f"This pattern reflects broader national challenges in expanding mortgage credit access for Black borrowers."
            )
    
    # White lending - brief mention if significant gap
    if comm_white and white_share_latest > 0:
        white_gap = white_share_latest - comm_white
        if abs(white_gap) > 10:  # Only mention if very large gap
            if white_gap > 0:
                analysis_parts.append(
                    f"White borrowers continue to receive a larger share of mortgage loans than their representation "
                    f"in the community's population, a pattern that has been consistent in mortgage lending historically."
                )
    
    # Geographic patterns - plain English
    geo_analysis = []
    
    # Get housing tenure data for context
    homeownership_rate = None
    if community_data and community_data.get('housing'):
        homeownership_rate = community_data['housing'].get('homeownership_rate')
    
    # LMIB - focus on the concern
    if lmib_change < -2:
        geo_analysis.append(
            f"Lending to low- and moderate-income borrowers declined over the period. This trend is concerning "
            f"because it suggests that households earning below the area median income may be finding it "
            f"increasingly difficult to access mortgage credit. This decline mirrors national patterns where "
            f"low- and moderate-income lending has fallen to historically low levels, reflecting severe "
            f"affordability challenges in the housing market."
        )
        if poverty_rate:
            geo_analysis.append(
                f"Given that Montgomery County has a significant portion of residents living below the poverty line, "
                f"this decline in lending to lower-income borrowers may limit opportunities for wealth building "
                f"through homeownership. Nationally, lending to low- and moderate-income borrowers reached "
                f"its lowest level since 2018 in 2024, indicating this is a systemic challenge across markets "
                f"(see NCRC's 2025 Mortgage Market Series, Part 1)."
            )
    
    # LMICT - explain what this means, highlight displacement concern
    if abs(lmict_change) > 5:
        direction = "expanded" if lmict_change > 0 else "declined"
        geo_analysis.append(
            f"Lending in lower-income neighborhoods {direction} over the period. These communities, where median "
            f"household incomes fall below 80% of the area median, are places where mortgage credit can be especially "
            f"important for community stability and economic opportunity."
        )
        
        # If both LMIB declined AND LMICT expanded, this is concerning
        if lmib_change < -2 and lmict_change > 5:
            geo_analysis.append(
                f"However, this expansion in lending to lower-income neighborhoods is particularly concerning when "
                f"viewed alongside the decline in lending to lower-income borrowers. This pattern suggests that "
                f"higher-income borrowers are purchasing homes in lower-income areas, which could lead to rising "
                f"housing costs and displacement of existing residents, especially renters."
            )
            
            if homeownership_rate:
                renter_rate = 100 - homeownership_rate
                geo_analysis.append(
                    f"According to the Community Profile of Montgomery, MD (County, 2022), approximately {renter_rate:.0f}% of "
                    f"Montgomery County households are renters. This means that many residents in lower-income neighborhoods "
                    f"may be particularly vulnerable to displacement if housing costs increase due to higher-income "
                    f"buyers entering the market."
                )
            else:
                geo_analysis.append(
                    f"This pattern raises concerns about displacement, as residents in these neighborhoods—many of "
                    f"whom are renters—may face rising housing costs and pressure to move as higher-income buyers "
                    f"enter the market."
                )
        elif lmict_change > 0:
            geo_analysis.append(
                f"The increase in lending to these neighborhoods helps ensure that residents in lower-income areas "
                f"have access to credit opportunities, though it is important to monitor whether this lending "
                f"benefits existing community residents or primarily serves higher-income newcomers."
            )
    
    # MMCT - explain context
    if abs(mmct_change) > 5:
        geo_analysis.append(
            f"Lending in majority-minority neighborhoods expanded significantly over the period. These are neighborhoods "
            f"where residents of color make up more than half the population."
        )
        if comm_black or comm_hispanic:
            geo_analysis.append(
                f"Given Montgomery County's diverse population, this increase in lending to majority-minority areas reflects "
                f"both the city's demographic composition and potentially improved credit access in communities "
                f"that have historically faced lending challenges."
            )
        geo_analysis.append(
            f"It is important to note that the 2020 census redrew boundaries and created approximately 30% more "
            f"majority-minority census tracts nationally. However, these boundary changes did not take effect in HMDA data "
            f"until 2022. This means that some of the apparent increase in lending to these areas after 2022 reflects how "
            f"neighborhoods were reclassified, not just changes in lending patterns."
        )
    
    if geo_analysis:
        analysis_parts.extend(geo_analysis)
    
    # Closing observation
    analysis_parts.append(
        f"These lending patterns reflect a complex mix of factors including demographic changes, market conditions, "
        f"lender practices, and borrower preferences. Understanding how these factors interact can help identify "
        f"opportunities to expand equitable access to mortgage credit throughout Montgomery County's diverse communities."
    )
    
    # Join paragraphs with double newlines for proper paragraph breaks
    analysis = "\n\n".join([para.strip() for para in analysis_parts if para.strip()])
    
    return {
        'lead_in': lead_in,
        'analysis': analysis
    }


def generate_top_lenders_narrative(top_lenders: pd.DataFrame, market_metrics: pd.DataFrame) -> str:
    """Generate narrative for Top Lender Analysis"""
    total_top10 = int(top_lenders['total_originations_2024'].sum())
    
    # Calculate market total for 2024 to get market share
    market_2024 = market_metrics[
        (market_metrics['activity_year'] == '2024') | (market_metrics['activity_year'] == 2024)
    ]
    market_total_2024 = market_2024['total_originations'].iloc[0] if len(market_2024) > 0 else total_top10
    market_share = (total_top10 / market_total_2024 * 100) if market_total_2024 > 0 else 0
    
    narrative = f"""
The top 10 lenders by 2024 home purchase origination volume originated {total_top10:,} loans, 
representing {market_share:.1f}% of all home purchase originations in Montgomery County that year. 
Analysis of these lenders across the 2018-2024 period reveals varying patterns in lending 
to minority borrowers and in minority and low-income communities.
    """.strip()
    
    return narrative


def check_lender_cba(lender_name: str) -> bool:
    """
    Check if a lender has a Community Benefits Agreement (CBA) with NCRC
    
    Args:
        lender_name: Name of the lender to check
    
    Returns:
        True if lender has a CBA, False otherwise
    """
    # Known CBA lenders (case-insensitive matching)
    cba_lenders = [
        'truist',  # Truist Financial Corporation
        'pnc',  # PNC Bank
        'u.s. bank', 'us bank',  # U.S. Bank
        'fifth third',  # Fifth Third Bank
        'bank of america',  # Bank of America
        'wells fargo',  # Wells Fargo
        'citizens bank',  # Citizens Bank
        'keybank', 'key bank',  # KeyBank
        'huntington',  # Huntington Bank
        'm&t bank', 'm and t',  # M&T Bank
    ]
    
    lender_lower = lender_name.lower()
    for cba_lender in cba_lenders:
        if cba_lender in lender_lower:
            return True
    
    return False


def search_lender_background_web(lender_name: str, search_results: dict = None) -> dict:
    """
    Search for comprehensive background information on a lender
    
    This function performs web searches for:
    - Headquarters location
    - Company history and mergers
    - Website URL
    - Community Benefits Agreement (CBA) status
    - Fair lending violations
    - Redlining complaints
    
    Args:
        lender_name: Name of the lender to search for
        search_results: Optional pre-searched results dictionary with keys:
            'headquarters', 'history', 'mergers', 'website', 'cba', 'violations', 'redlining'
            Each value should be a string containing search result text
    
    Returns:
        Dictionary with extracted background information
    """
    background_info = {
        'headquarters': None,
        'history': None,
        'mergers': None,
        'website': None,
        'has_cba': False,
        'fair_lending_violations': None,
        'redlining_complaints': None
    }
    
    # Check for CBA
    background_info['has_cba'] = check_lender_cba(lender_name)
    
    # If pre-searched results are provided, extract information from them
    if search_results:
        if 'headquarters' in search_results and search_results['headquarters']:
            background_info['headquarters'] = extract_location_from_search(
                search_results['headquarters'], lender_name
            )
        if 'history' in search_results and search_results['history']:
            background_info['history'] = extract_history_from_search(
                search_results['history'], lender_name
            )
        if 'mergers' in search_results and search_results['mergers']:
            background_info['mergers'] = extract_mergers_from_search(
                search_results['mergers'], lender_name
            )
        if 'website' in search_results and search_results['website']:
            # Extract website URL from search results
            website_text = search_results['website']
            import re
            # Look for URLs in the text
            url_pattern = r'https?://(?:www\.)?([\w\.-]+\.(?:com|org|net|edu|gov|io))'
            match = re.search(url_pattern, website_text)
            if match:
                # Reconstruct full URL
                domain = match.group(1)
                background_info['website'] = f"https://www.{domain}"
            else:
                # Try to find just domain name
                domain_pattern = r'(?:www\.)?([\w\.-]+\.(?:com|org|net|edu|gov|io))'
                match = re.search(domain_pattern, website_text, re.IGNORECASE)
                if match:
                    domain = match.group(1)
                    background_info['website'] = f"https://www.{domain}"
        if 'violations' in search_results and search_results['violations']:
            background_info['fair_lending_violations'] = extract_violations_from_search(
                search_results['violations'], lender_name
            )
        if 'redlining' in search_results and search_results['redlining']:
            background_info['redlining_complaints'] = extract_redlining_from_search(
                search_results['redlining'], lender_name
            )
        if 'cba' in search_results and search_results['cba']:
            # Check search results for CBA mentions
            cba_text = search_results['cba'].lower()
            if 'community benefits' in cba_text or 'cba' in cba_text:
                background_info['has_cba'] = True
    
    # Check for CBA if not already found
    if not background_info['has_cba']:
        background_info['has_cba'] = check_lender_cba(lender_name)
    
    # Define search queries for reference (used by AI assistant)
    queries = {
        'headquarters': f"{lender_name} headquarters location city",
        'history': f"{lender_name} history founding year",
        'mergers': f"{lender_name} mergers acquisitions recent",
        'website': f"{lender_name} official website",
        'cba': f"{lender_name} NCRC Community Benefits Agreement CBA",
        'violations': f"{lender_name} fair lending violations CFPB DOJ settlement",
        'redlining': f"{lender_name} redlining complaint CFPB DOJ enforcement"
    }
    
    # Store queries for potential future use
    background_info['_queries'] = queries
    
    return background_info


# Import background search utilities
try:
    sys.path.insert(0, str(member_reports_dir / 'utils'))
    from lender_background_search import (
        extract_location_from_search,
        extract_history_from_search,
        extract_mergers_from_search,
        extract_violations_from_search,
        extract_redlining_from_search,
        parse_search_results
    )
except ImportError:
    # Fallback functions if import fails
    def extract_location_from_search(search_results: str, lender_name: str) -> str:
        return None
    def extract_history_from_search(search_results: str, lender_name: str) -> str:
        return None
    def extract_mergers_from_search(search_results: str, lender_name: str) -> str:
        return None
    def extract_violations_from_search(search_results: str, lender_name: str) -> str:
        return None
    def extract_redlining_from_search(search_results: str, lender_name: str) -> str:
        return None
    def parse_search_results(search_results: dict) -> dict:
        return {}


def generate_lender_lead_in(lender_info_row: pd.Series, lender_name: str, background_info: dict = None) -> str:
    """Generate 2-sentence lead-in for each lender with background information"""
    if lender_info_row.empty or pd.isna(lender_info_row.get('type_name')):
        lender_type = "financial institution"
    else:
        type_name = lender_info_row.get('type_name', '')
        type_lower = str(type_name).lower()
        if 'credit union' in type_lower or 'cu' in type_lower:
            lender_type = "credit union"
        elif 'mortgage' in type_lower:
            lender_type = "mortgage company"
        elif 'bank' in type_lower:
            lender_type = "bank"
        else:
            lender_type = "financial institution"
    
    # Start with basic description, including headquarters if available
    if background_info and background_info.get('headquarters'):
        location = background_info['headquarters']
        lead_in = f"{lender_name} is a {lender_type} headquartered in {location}."
    elif lender_info_row.empty or pd.isna(lender_info_row.get('type_name')):
        lead_in = f"{lender_name} is one of the top lenders in Montgomery County."
    else:
        lead_in = f"{lender_name} is a {lender_type}."
    
    # Add asset information if available (only for banks/credit unions)
    assets_thousands = lender_info_row.get('assets_thousands') if not lender_info_row.empty else None
    if assets_thousands and not pd.isna(assets_thousands) and assets_thousands > 0:
        type_lower = str(lender_info_row.get('type_name', '')).lower() if not lender_info_row.empty else ''
        # Only mention assets for banks and credit unions, not mortgage companies
        if 'mortgage' not in type_lower:
            # Assets are in thousands, convert appropriately
            assets_billions = assets_thousands / 1000000
            if assets_billions >= 1000:
                lead_in += f" The institution reported assets of approximately ${assets_billions/1000:.2f} trillion."
            elif assets_billions >= 1:
                lead_in += f" The institution reported assets of approximately ${assets_billions:.2f} billion."
            else:
                assets_millions = assets_thousands / 1000
                lead_in += f" The institution reported assets of approximately ${assets_millions:.0f} million."
    
    # Add relevant history/merger info or CBA info as second sentence
    if background_info:
        second_sentence = None
        
        # Prioritize CBA mention if available
        if background_info.get('has_cba'):
            second_sentence = f"{lender_name} has a Community Benefits Agreement (CBA) with NCRC, demonstrating a commitment to serving low- and moderate-income communities. For more information, visit https://ncrc.org/cba/."
        elif background_info.get('history'):
            second_sentence = background_info['history']
        elif background_info.get('mergers'):
            second_sentence = background_info['mergers']
        
        if second_sentence:
            lead_in += f" {second_sentence}"
    
    return lead_in


def generate_lender_analysis(lender_metrics: pd.DataFrame, market_metrics: pd.DataFrame, lender_name: str, background_info: dict = None) -> str:
    """Generate comprehensive narrative analysis for individual lender comparing to market"""
    lender_sorted = lender_metrics.sort_values('activity_year')
    market_sorted = market_metrics.sort_values('activity_year')
    
    latest_year = int(lender_sorted['activity_year'].iloc[-1])
    earliest_year = int(lender_sorted['activity_year'].iloc[0])
    
    # Calculate trends over the full period
    earliest_volume = int(lender_sorted['total_originations'].iloc[0])
    latest_volume = int(lender_sorted['total_originations'].iloc[-1])
    peak_volume = int(lender_sorted['total_originations'].max())
    peak_year = int(lender_sorted.loc[lender_sorted['total_originations'].idxmax(), 'activity_year'])
    
    volume_change_pct = ((latest_volume - earliest_volume) / earliest_volume * 100) if earliest_volume > 0 else 0
    
    # Get latest metrics for comparison
    latest_lender = lender_sorted.iloc[-1]
    latest_market = market_sorted.iloc[-1]
    
    # Compare to market for key metrics
    lender_hispanic = latest_lender.get('hispanic_homebuyer_share', 0)
    market_hispanic = latest_market.get('hispanic_homebuyer_share', 0)
    hispanic_gap = lender_hispanic - market_hispanic
    
    lender_black = latest_lender.get('black_homebuyer_share', 0)
    market_black = latest_market.get('black_homebuyer_share', 0)
    black_gap = lender_black - market_black
    
    lender_asian = latest_lender.get('asian_homebuyer_share', 0)
    market_asian = latest_market.get('asian_homebuyer_share', 0)
    asian_gap = lender_asian - market_asian
    
    lender_white = latest_lender.get('white_homebuyer_share', 0)
    market_white = latest_market.get('white_homebuyer_share', 0)
    white_gap = lender_white - market_white
    
    lender_lmib = latest_lender.get('lmib_share', 0)
    market_lmib = latest_market.get('lmib_share', 0)
    lmib_gap = lender_lmib - market_lmib
    
    lender_lmict = latest_lender.get('lmict_share', 0)
    market_lmict = latest_market.get('lmict_share', 0)
    lmict_gap = lender_lmict - market_lmict
    
    lender_mmct = latest_lender.get('mmct_share', 0)
    market_mmct = latest_market.get('mmct_share', 0)
    mmct_gap = lender_mmct - market_mmct
    
    # Build comprehensive narrative paragraphs
    paragraphs = []
    
    # First paragraph: Volume trends over time
    volume_sentences = []
    volume_sentences.append(f"{lender_name} originated {latest_volume} home purchase loans in {latest_year}.")
    if peak_year != latest_year:
        volume_sentences.append(f"This was down from a peak of {peak_volume} loans in {peak_year}.")
    if earliest_year != latest_year:
        if volume_change_pct > 10:
            volume_sentences.append(
                f"Over the {earliest_year}-{latest_year} period, the lender's origination volume increased by approximately {abs(volume_change_pct):.0f} percent."
            )
        elif volume_change_pct < -10:
            volume_sentences.append(
                f"Over the {earliest_year}-{latest_year} period, the lender's origination volume declined by approximately {abs(volume_change_pct):.0f} percent."
            )
        else:
            volume_sentences.append(
                f"Over the {earliest_year}-{latest_year} period, the lender's origination volume remained relatively stable."
            )
    paragraphs.append(" ".join(volume_sentences))
    
    # Second paragraph: Demographic lending patterns compared to market
    demographic_observations = []
    
    if abs(hispanic_gap) > 10:
        direction = "substantially higher" if hispanic_gap > 0 else "substantially lower"
        demographic_observations.append(f"{lender_name}'s share of loans to Hispanic borrowers was {direction} than the market average")
    elif abs(hispanic_gap) > 5:
        direction = "higher" if hispanic_gap > 0 else "lower"
        demographic_observations.append(f"{lender_name}'s share of loans to Hispanic borrowers was {direction} than the market average")
    
    if abs(black_gap) > 10:
        direction = "substantially higher" if black_gap > 0 else "substantially lower"
        demographic_observations.append(f"{lender_name}'s share of loans to Black borrowers was {direction} than the market average")
    elif abs(black_gap) > 5:
        direction = "higher" if black_gap > 0 else "lower"
        demographic_observations.append(f"{lender_name}'s share of loans to Black borrowers was {direction} than the market average")
    
    if abs(asian_gap) > 10:
        direction = "substantially higher" if asian_gap > 0 else "substantially lower"
        demographic_observations.append(f"{lender_name}'s share of loans to Asian borrowers was {direction} than the market average")
    elif abs(asian_gap) > 5:
        direction = "higher" if asian_gap > 0 else "lower"
        demographic_observations.append(f"{lender_name}'s share of loans to Asian borrowers was {direction} than the market average")
    
    if abs(white_gap) > 10:
        direction = "substantially higher" if white_gap > 0 else "substantially lower"
        demographic_observations.append(f"{lender_name}'s share of loans to White borrowers was {direction} than the market average")
    
    if demographic_observations:
        demo_sentences = []
        demo_sentences.append(f"When compared to the overall market in {latest_year}, {demographic_observations[0]}.")
        if len(demographic_observations) > 1:
            demo_sentences.append(f"Additionally, {demographic_observations[1]}.")
        paragraphs.append(" ".join(demo_sentences))
    else:
        paragraphs.append(
            f"{lender_name}'s lending patterns across racial and ethnic groups were generally consistent with overall market trends in {latest_year}."
        )
    
    # Third paragraph: Geographic lending patterns
    geographic_observations = []
    
    if abs(lmib_gap) > 10:
        direction = "substantially higher" if lmib_gap > 0 else "substantially lower"
        geographic_observations.append(f"the lender's share of loans to low-to-moderate income borrowers was {direction} than the market average")
    elif abs(lmib_gap) > 5:
        direction = "higher" if lmib_gap > 0 else "lower"
        geographic_observations.append(f"the lender's share of loans to low-to-moderate income borrowers was {direction} than the market average")
    
    if abs(lmict_gap) > 10:
        direction = "substantially higher" if lmict_gap > 0 else "substantially lower"
        geographic_observations.append(f"the lender's share of loans in low-to-moderate income census tracts was {direction} than the market average")
    elif abs(lmict_gap) > 5:
        direction = "higher" if lmict_gap > 0 else "lower"
        geographic_observations.append(f"the lender's share of loans in low-to-moderate income census tracts was {direction} than the market average")
    
    if abs(mmct_gap) > 10:
        direction = "substantially higher" if mmct_gap > 0 else "substantially lower"
        geographic_observations.append(f"the lender's share of loans in majority-minority census tracts was {direction} than the market average")
    elif abs(mmct_gap) > 5:
        direction = "higher" if mmct_gap > 0 else "lower"
        geographic_observations.append(f"the lender's share of loans in majority-minority census tracts was {direction} than the market average")
    
    if geographic_observations:
        geo_sentences = []
        geo_sentences.append(f"In terms of geographic lending patterns, {geographic_observations[0]}.")
        if len(geographic_observations) > 1:
            geo_sentences.append(f"Also, {geographic_observations[1]}.")
        paragraphs.append(" ".join(geo_sentences))
    else:
        paragraphs.append(
            f"{lender_name}'s geographic lending patterns were generally aligned with market averages in {latest_year}."
        )
    
    # Join paragraphs with double newlines for proper paragraph breaks
    return "\n\n".join([para.strip() for para in paragraphs if para.strip()])


def main():
    print("\n" + "="*80)
    print("MONTGOMERY MARKET REPORT GENERATION")
    print("="*80)
    
    # Query and process data from BigQuery
    print("\nQuerying and processing HMDA data...")
    market_metrics, top_10_metrics, top_lenders = query_and_process_montgomery_data()
    
    if market_metrics is None or top_10_metrics is None or top_lenders is None:
        print("ERROR: Could not retrieve or process data. Exiting.")
        return
    
    print(f"  Market data: {len(market_metrics)} year rows")
    print(f"  Top 10 lenders: {len(top_10_metrics)} lender-year rows")
    
    # Get lender info from BigQuery
    print("\nFetching lender information...")
    top_10_leis = top_lenders['lei'].tolist()
    lender_info = get_lender_info(top_10_leis)
    if len(lender_info) > 0:
        print(f"  Found info for {len(lender_info)} lenders")
    else:
        print("  Warning: Could not fetch lender info")
    
    # Look up official lender names and additional info from GLEIF BEFORE creating tables
    print("\nLooking up official lender information from GLEIF...")
    lei_to_official_name = {}
    lei_to_gleif_info = {}  # Store full GLEIF info (headquarters, etc.)
    top_10_leis = top_lenders['lei'].tolist()
    for lei in top_10_leis:
        print(f"    Looking up LEI: {lei[:8]}...")
        gleif_info = lookup_lender_info_by_lei(lei)
        if gleif_info and gleif_info.get('name'):
            official_name = format_lender_name(gleif_info['name'])
            lei_to_official_name[lei] = official_name
            lei_to_gleif_info[lei] = gleif_info
            print(f"      Found: {official_name}")
            if gleif_info.get('headquarters'):
                print(f"        Headquarters: {gleif_info['headquarters']}")
            if gleif_info.get('lei_url'):
                print(f"        GLEIF Record: {gleif_info['lei_url']}")
        else:
            # Fallback to BigQuery name
            if lender_info is not None and len(lender_info) > 0:
                lei_match = lender_info[lender_info['lei'] == lei]
                if len(lei_match) > 0:
                    bigquery_name = lei_match.iloc[0].get('respondent_name', lei)
                    if pd.notna(bigquery_name) and bigquery_name != '':
                        lei_to_official_name[lei] = format_lender_name(bigquery_name)
                        print(f"      Using BigQuery name: {lei_to_official_name[lei]}")
                    else:
                        lei_to_official_name[lei] = lei
                        print(f"      No name found, using LEI: {lei}")
                else:
                    lei_to_official_name[lei] = lei
            else:
                lei_to_official_name[lei] = lei
    
    # Update top_lenders with official names
    top_lenders['respondent_name'] = top_lenders['lei'].map(lei_to_official_name)
    
    # Update lender_info with official names if available
    if lender_info is not None and len(lender_info) > 0:
        lender_info['respondent_name'] = lender_info['lei'].map(lei_to_official_name).fillna(lender_info['respondent_name'])
    
    # Create tables (now with official names)
    print("\nCreating report tables...")
    market_tables = create_market_overview_tables(market_metrics)
    lender_tables_pdf, lender_tables_excel, lender_metadata = create_top_lenders_tables(top_10_metrics, top_lenders, lender_info)
    lender_tables = lender_tables_pdf  # Use PDF version for PDF generation
    
    # Generate lead-ins and analyses for each lender
    print("\nGathering background information on lenders...")
    lender_narratives = {}
    for lender_name, metadata in lender_metadata.items():
        lei = metadata['lei']
        lender_data = metadata['lender_data']
        
        # Find lender info
        lender_info_row = pd.Series()
        if lender_info is not None and len(lender_info) > 0:
            lender_info_match = lender_info[lender_info['lei'] == lei]
            if len(lender_info_match) > 0:
                lender_info_row = lender_info_match.iloc[0]
        
        # Search for background information using web search
        print(f"  Searching for background on {lender_name}...")
        
        # Try to load pre-searched background info from JSON file
        background_data_file = member_reports_dir / "data" / "lender_background_info.json"
        background_info = {}
        if background_data_file.exists():
            try:
                with open(background_data_file, 'r') as f:
                    all_background_data = json.load(f)
                    # Case-insensitive lookup (lender_name is uppercase, JSON keys may be mixed case)
                    lender_key = None
                    for key in all_background_data.keys():
                        if key.upper() == lender_name.upper():
                            lender_key = key
                            break
                    
                    if lender_key:
                        # Use stored data directly (already extracted), but GLEIF data takes precedence
                        stored_data = all_background_data[lender_key]
                        # Merge: GLEIF headquarters takes precedence, but use stored website/history if available
                        if not background_info.get('headquarters'):
                            background_info['headquarters'] = stored_data.get('headquarters')
                        background_info['history'] = stored_data.get('history')
                        background_info['mergers'] = stored_data.get('mergers')
                        if not background_info.get('website'):
                            background_info['website'] = stored_data.get('website')
                        background_info['has_cba'] = stored_data.get('has_cba', False) or check_lender_cba(lender_name)
                        background_info['fair_lending_violations'] = stored_data.get('fair_lending_violations')
                        background_info['redlining_complaints'] = stored_data.get('redlining_complaints')
                        
                        if background_info.get('headquarters'):
                            print(f"    Found headquarters: {background_info['headquarters']}")
                        if background_info.get('website'):
                            print(f"    Found website: {background_info['website']}")
                        if background_info.get('gleif_url'):
                            print(f"    GLEIF Record: {background_info['gleif_url']}")
                        if background_info.get('has_cba'):
                            print(f"    Has NCRC Community Benefits Agreement")
            except Exception as e:
                print(f"    Warning: Could not load background data: {e}")
                background_info = search_lender_background_web(lender_name, None)
        else:
            background_info = search_lender_background_web(lender_name, None)
        
        # Generate lead-in with background info
        lead_in = generate_lender_lead_in(lender_info_row, lender_name, background_info)
        
        # Generate analysis with background info
        analysis = generate_lender_analysis(lender_data, market_metrics, lender_name, background_info)
        
        lender_narratives[lender_name] = {
            'lead_in': lead_in,
            'analysis': analysis,
            'background_info': background_info
        }
    
    print(f"  Generated narratives for {len(lender_narratives)} lenders")
    
    print(f"  Market tables: race/ethnicity ({len(market_tables['race_ethnicity'])} rows) and geographic ({len(market_tables['geographic'])} rows)")
    print(f"  Top lenders: {len(lender_tables)} separate tables")
    
    # Load community profile data
    print("\nLoading community profile data...")
    community_data = load_community_profile_data()
    if community_data:
        print(f"  Loaded community profile data for {community_data.get('community_name', 'community')}")
    
    # Generate narratives
    print("\nGenerating narratives...")
    introduction = generate_introduction(community_data)
    key_findings = generate_key_findings(market_metrics)
    market_narrative = generate_market_patterns_narrative(market_metrics, community_data)
    top_lenders_narrative = generate_top_lenders_narrative(top_lenders, market_metrics)
    
    # Convert DataFrames to list of lists for PDF tables
    def df_to_table_data(df):
        """Convert DataFrame to list of lists for PDF Table"""
        # Get column names
        headers = [df.columns.tolist()]
        # Get data rows
        data = df.values.tolist()
        return headers + data
    
    # Prepare report data structure
    report_data = {
        'introduction': introduction,
        'key_points': key_findings,
        'overview': {
            'lead_in': market_narrative['lead_in'],
            'analysis': market_narrative['analysis'],
            'race_table': df_to_table_data(market_tables['race_ethnicity']) if len(market_tables['race_ethnicity']) > 0 else None,
            'geographic_table': df_to_table_data(market_tables['geographic']) if len(market_tables['geographic']) > 0 else None
        },
        'top_lenders': {
            'narrative': top_lenders_narrative,
            'tables': {name: df_to_table_data(df) for name, df in lender_tables.items()} if lender_tables else None,
            'lender_narratives': lender_narratives,
            'lender_info': lender_info.to_dict('records') if len(lender_info) > 0 else None
        },
        'tables': {
            'Market Overview - Race/Ethnicity': market_tables['race_ethnicity'],
            'Market Overview - Geographic': market_tables['geographic'],
            **{f'{name}': df for name, df in lender_tables_excel.items()}  # Use Excel version with extra metrics
        },
        'methods': {
            'text': generate_methodology_text()
        }
    }
    
    # Create organized output folder: CommunityName_MemberName
    community_name = "Montgomery_MD"
    member_name = "Sample_Member"
    report_folder = member_reports_dir / "outputs" / f"{community_name}_{member_name}"
    report_folder.mkdir(parents=True, exist_ok=True)
    
    print(f"\nOutput folder: {report_folder}")
    
    report_title = "Mortgage Lending in Montgomery County, Maryland"
    report_subtitle = "Market Dynamics and Community Patterns (2018-2024)"
    
    # Copy supporting documents to report folder
    supporting_dir = member_reports_dir / "supporting_files"
    print("\nCopying supporting documents...")
    
    import shutil
    
    # Copy community profile
    community_profile = supporting_dir / "Community Profile of Montgomery, MD (County, 2022).pdf"
    if community_profile.exists():
        shutil.copy2(community_profile, report_folder / community_profile.name)
        print(f"  Copied: {community_profile.name}")
    
    # Copy configuration
    config_file = member_reports_dir / "configs" / "montgomery_market_report.json"
    if config_file.exists():
        shutil.copy2(config_file, report_folder / config_file.name)
        print(f"  Copied: {config_file.name}")
    
    # Generate PDF
    if PDFReportGenerator:
        print("\nGenerating PDF report...")
        pdf_path = report_folder / f"{community_name}_{member_name}_Report.pdf"
        pdf_gen = PDFReportGenerator()
        
        try:
            pdf_gen.generate_report(
                str(pdf_path),
                report_title,
                report_data,
                member_org="Sample Member",
                report_date=datetime.now().strftime('%Y-%m-%d')
            )
            print(f"  PDF saved: {pdf_path}")
        except Exception as e:
            print(f"  PDF generation error: {e}")
            import traceback
            traceback.print_exc()
    
    # Generate Excel
    if ExcelReportGenerator:
        print("\nGenerating Excel report...")
        excel_path = report_folder / f"{community_name}_{member_name}_Data.xlsx"
        excel_gen = ExcelReportGenerator()
        
        try:
            excel_gen.generate_report(
                str(excel_path),
                report_title,
                report_data,
                member_org="Sample Member",
                report_date=datetime.now().strftime('%Y-%m-%d')
            )
            print(f"  Excel saved: {excel_path}")
        except Exception as e:
            print(f"  Excel generation error: {e}")
            import traceback
            traceback.print_exc()
    
    # Copy processed data files
    data_dir = member_reports_dir / "data" / "processed"
    if (data_dir / "montgomery_market_metrics.csv").exists():
        shutil.copy2(data_dir / "montgomery_market_metrics.csv", report_folder / "montgomery_market_metrics.csv")
        print(f"  Copied: montgomery_market_metrics.csv")
    if (data_dir / "montgomery_top_10_lenders_metrics.csv").exists():
        shutil.copy2(data_dir / "montgomery_top_10_lenders_metrics.csv", report_folder / "montgomery_top_10_lenders_metrics.csv")
        print(f"  Copied: montgomery_top_10_lenders_metrics.csv")
    
    # Copy raw data
    raw_data_dir = member_reports_dir / "data" / "raw"
    raw_folder = report_folder / "raw_data"
    raw_folder.mkdir(exist_ok=True)
    
    for file in ["montgomery_market_data.csv", "montgomery_top_lenders_2024.csv"]:
        src = raw_data_dir / file
        if src.exists():
            shutil.copy2(src, raw_folder / file)
            print(f"  Copied raw data: {file}")
    
    print("\n" + "="*80)
    print("REPORT GENERATION COMPLETE!")
    print("="*80)


def generate_methodology_text() -> str:
    """Generate methodology section text"""
    return """
METHODOLOGY

Data Source and Years:
This report uses Home Mortgage Disclosure Act (HMDA) data from the Federal Financial 
Institutions Examination Council (FFIEC) for years 2018 through 2024.

Geographic Scope:
The analysis focuses on Montgomery County, Maryland, encompassing all census tracts within the 
county boundaries. Geographic scope was identified from the Community Profile of Montgomery, MD (County, 2022).

Loan Filters:
This analysis applies standard HMDA filters to home purchase loan originations:

- Loan Purpose: Home purchase loans only (loan_purpose = '1')
- Action Taken: Originations only (action_taken = '1')
- Occupancy Type: Owner-occupied properties (occupancy_type = '1')
- Reverse Mortgages: Excluded (reverse_mortgage != '1')
- Construction Method: Site-built only (construction_method = '1')
- Property Units: 1-4 family units (total_units IN ('1', '2', '3', '4'))

All loan types (conventional, FHA, VA, USDA) are included within these filters.

Core Metrics:
The following metrics are calculated:

1. Black share: Black borrowers as percentage of originations with demographic data

2. Hispanic share: Hispanic borrowers as percentage of originations with demographic data

3. Asian share: Asian borrowers as percentage of originations with demographic data

4. White share: White borrowers as percentage of originations with demographic data

5. Native American share: Native American borrowers as percentage of originations with demographic data

6. Hawaiian/Pacific Islander share: Hawaiian/Pacific Islander borrowers as percentage of originations with demographic data

7. LMIB lending share: Originations to Low-to-Moderate Income Borrowers as percentage of total originations

8. LMICT lending share: Originations in Low-to-Moderate Income Census Tracts as percentage of total originations

9. MMCT lending share: Originations in Majority-Minority Census Tracts as percentage of total originations

Race/Ethnicity Classification:
NCRC methodology uses hierarchical classification with Hispanic ethnicity checked first. 
If any ethnicity field contains codes 1, 11, 12, 13, or 14, the borrower is classified as Hispanic. 
If not Hispanic, borrowers are categorized by race using all 5 race fields.

Missing Data:
HMDA allows demographic data omissions. For borrower demographic metrics, the denominator 
is loans WITH demographic data (excluding missing data from the percentage calculation). 
Geographic metrics (LMICT, MMCT) use all originations as the denominator.

Top Lender Analysis:
Top 10 lenders are identified by 2024 home purchase origination volume. Each lender's 
performance is analyzed across all six metrics for the entire 2018-2024 period, broken 
out year-over-year, similar to the market overview analysis.

Related Resources:
NCRC's 2025 Mortgage Market Series provides national context for local lending patterns:

- Part 1: Introduction to Mortgage Market Trends
  (https://ncrc.org/mortgage-market-report-series-part-1-introduction-to-mortgage-market-trends/)

- Part 2: Lending Trends by Borrower and Neighborhood Characteristics
  (https://ncrc.org/mortgage-market-report-series-part-2-lending-trends-by-borrower-and-neighborhood-characteristics/)

- Part 3: Native American and Hawaiian Lending
  (https://ncrc.org/mortgage-market-report-series-part-3-native-american-and-hawaiian-lending/)

- Part 4: Mortgage Lending Across American Cities
  (https://ncrc.org/mortgage-market-report-series-part-4-mortgage-lending-across-american-cities/)

Report Production and Disclaimer:
This report was produced using Cursor, an AI-powered code editor, and other AI language models 
to assist with data analysis, narrative generation, and report formatting. While NCRC staff have 
reviewed this report for accuracy and quality, there may be errors or omissions. If readers have 
questions about the data, methodology, or findings presented in this report, or if they identify 
any potential errors, please contact the NCRC Research Department for review and clarification.

Contact:
NCRC Research Department
National Community Reinvestment Coalition
research@ncrc.org
www.ncrc.org
    """.strip()


if __name__ == '__main__':
    main()

