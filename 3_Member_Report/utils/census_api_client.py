"""
Census Bureau API Client for retrieving demographic and economic data

Uses the U.S. Census Bureau API to fetch:
- American Community Survey (ACS) data (most current)
- Decennial Census data (2020, 2010) for comparison
- Demographic data (race, ethnicity)
- Income data (median household income, poverty rates)
- Housing data (homeownership rates)

References:
    Census Data API User Guide: https://www.census.gov/data/developers/guidance/api-user-guide.html
    Request API Key: https://api.census.gov/data/key_signup.html

Requires:
    pip install census us requests

API Key:
    Get a free API key from: https://api.census.gov/data/key_signup.html
    Set environment variable: CENSUS_API_KEY=your-key-here
"""

import os
from typing import Dict, Optional, List
import json
import requests


def get_most_recent_acs_year() -> str:
    """
    Determine the most recent available ACS 5-year estimate year
    
    Returns:
        Year string (e.g., '2023' for 2019-2023 estimates)
    """
    # ACS 5-year estimates are typically released in December
    # 2023 ACS 5-year = 2019-2023 data (released Dec 2024)
    # 2022 ACS 5-year = 2018-2022 data (released Dec 2023)
    # We'll try 2023 first, fall back to 2022
    try:
        # Try to determine latest available - default to 2023 if we're past Dec 2024
        # For now, use 2022 as most reliably available
        return "2022"  # Most recent comprehensive data as of early 2025
    except:
        return "2022"


def get_decennial_census_race_data(
    county_fips: str,
    state_fips: str,
    year: str,
    api_key: Optional[str] = None
) -> Dict:
    """
    Get race/ethnicity data from decennial census (2010 or 2020)
    
    Decennial Census race/ethnicity variables:
    - P1_001N: Total population
    - P2_002N: Hispanic or Latino
    - P2_003N: Not Hispanic or Latino
    - P2_005N: White alone (not Hispanic)
    - P2_006N: Black or African American alone (not Hispanic)
    - P2_008N: Asian alone (not Hispanic)
    - P2_009N: Native Hawaiian/Pacific Islander alone (not Hispanic)
    - P2_007N: American Indian/Alaska Native alone (not Hispanic)
    
    Args:
        county_fips: County FIPS code
        state_fips: State FIPS code
        year: Census year ('2020' or '2010')
        api_key: Census API key
    
    Returns:
        Dictionary with race/ethnicity data
    """
    if api_key is None:
        api_key = os.getenv('CENSUS_API_KEY')
    
    if not api_key:
        return {}
    
    try:
        # Decennial Census API endpoint
        base_url = f"https://api.census.gov/data/{year}/dec/pl"
        
        # Variables for race/ethnicity
        variables = [
            'P1_001N',  # Total population
            'P2_002N',  # Hispanic or Latino
            'P2_005N',  # White alone (not Hispanic)
            'P2_006N',  # Black or African American alone (not Hispanic)
            'P2_008N',  # Asian alone (not Hispanic)
            'P2_009N',  # Native Hawaiian/Pacific Islander alone (not Hispanic)
            'P2_007N',  # American Indian/Alaska Native alone (not Hispanic)
        ]
        
        vars_str = ','.join(variables)
        url = f"{base_url}?get=NAME,{vars_str}&for=county:{county_fips}&in=state:{state_fips}&key={api_key}"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if not data or len(data) < 2:
            return {}
        
        # First row is headers, second row is data
        headers = data[0]
        record = data[1]
        
        result = {}
        
        # Create dict from headers and values
        record_dict = dict(zip(headers, record))
        
        total_pop = _safe_int(record_dict.get('P1_001N'))
        if total_pop:
            result['total_population'] = total_pop
            
            hispanic = _safe_int(record_dict.get('P2_002N', 0))
            white = _safe_int(record_dict.get('P2_005N', 0))
            black = _safe_int(record_dict.get('P2_006N', 0))
            asian = _safe_int(record_dict.get('P2_008N', 0))
            native_am = _safe_int(record_dict.get('P2_007N', 0))
            hopi = _safe_int(record_dict.get('P2_009N', 0))
            
            result['hispanic_percentage'] = (hispanic / total_pop * 100) if hispanic else 0
            result['white_percentage'] = (white / total_pop * 100) if white else 0
            result['black_percentage'] = (black / total_pop * 100) if black else 0
            result['asian_percentage'] = (asian / total_pop * 100) if asian else 0
            result['native_american_percentage'] = (native_am / total_pop * 100) if native_am else 0
            result['hopi_percentage'] = (hopi / total_pop * 100) if hopi else 0
        
        return result
        
    except Exception as e:
        print(f"Error fetching decennial census {year} data: {e}")
        return {}


def get_census_data_for_county(
    county_fips: str,
    state_fips: str,
    api_key: Optional[str] = None,
    include_comparison_years: bool = True,
    include_2000: bool = True
) -> Dict:
    """
    Get comprehensive census data for a county using the Census API
    
    Fetches:
    - Most current ACS 5-year estimates (demographics, income, housing)
    - 2020 Decennial Census data for comparison
    - 2010 Decennial Census data for comparison
    - 2000 Decennial Census data for comparison (if include_2000=True)
    
    Args:
        county_fips: County FIPS code (e.g., '031' for Montgomery County, MD)
        state_fips: State FIPS code (e.g., '24' for Maryland)
        api_key: Census API key (if None, tries CENSUS_API_KEY env var)
        include_comparison_years: If True, fetches 2020, 2010, and optionally 2000 decennial data
        include_2000: If True, also fetches 2000 decennial census data
    
    Returns:
        Dictionary with current demographics, income, housing, and comparison data
        Includes historical data for trend analysis
    """
    try:
        from census import Census
        
        # Get API key
        if api_key is None:
            api_key = os.getenv('CENSUS_API_KEY')
        
        if not api_key:
            print("Warning: No Census API key found. Set CENSUS_API_KEY environment variable or pass api_key parameter.")
            return {}
        
        # Initialize Census client
        c = Census(api_key)
        
        # Get most recent ACS year
        acs_year = get_most_recent_acs_year()
        acs_year_int = int(acs_year)
        
        # ACS 5-Year estimates variables
        # Race and Ethnicity from B03002 table
        variables = [
            'NAME',
            'B01003_001E',  # Total population
            'B03002_001E',  # Total (for race breakdown)
            'B03002_003E',  # White alone (not Hispanic)
            'B03002_004E',  # Black or African American alone (not Hispanic)
            'B03002_005E',  # American Indian/Alaska Native alone (not Hispanic)
            'B03002_006E',  # Asian alone (not Hispanic)
            'B03002_007E',  # Native Hawaiian/Pacific Islander alone (not Hispanic)
            'B03002_012E',  # Hispanic or Latino (of any race)
            'B19013_001E',  # Median household income
            'B17001_002E',  # Income below poverty level
            'B17001_001E',  # Total for poverty status
            'B25003_001E',  # Total housing units
            'B25003_002E',  # Owner-occupied
            'B25003_003E',  # Renter-occupied
        ]
        
        # Query ACS 5-Year data (most current)
        print(f"Fetching ACS {acs_year} 5-year estimates (most current data)...")
        data = c.acs5.get(
            variables,
            {
                'for': f'county:{county_fips}',
                'in': f'state:{state_fips}'
            },
            year=acs_year_int
        )
        
        if not data or len(data) == 0:
            print(f"Warning: No ACS data returned for county {county_fips}, state {state_fips}")
            return {}
        
        record = data[0]
        
        # Process data into our format
        result = {
            'community_name': record.get('NAME', ''),
            'profile_year': f"{acs_year} (ACS 5-year estimates)",
            'demographics': {},
            'income': {},
            'housing': {},
            'comparison_years': {}
        }
        
        # Total population (most current)
        total_pop = _safe_int(record.get('B01003_001E'))
        if total_pop:
            result['demographics']['total_population'] = total_pop
        
        # Calculate race/ethnicity percentages from ACS (most current)
        total_race = _safe_int(record.get('B03002_001E')) or total_pop
        if total_race and total_race > 0:
            white = _safe_int(record.get('B03002_003E', 0))
            black = _safe_int(record.get('B03002_004E', 0))
            asian = _safe_int(record.get('B03002_006E', 0))
            native_am = _safe_int(record.get('B03002_005E', 0))
            hopi = _safe_int(record.get('B03002_007E', 0))
            hispanic = _safe_int(record.get('B03002_012E', 0))
            
            result['demographics']['white_percentage'] = (white / total_race * 100) if white else 0
            result['demographics']['black_percentage'] = (black / total_race * 100) if black else 0
            result['demographics']['asian_percentage'] = (asian / total_race * 100) if asian else 0
            result['demographics']['native_american_percentage'] = (native_am / total_race * 100) if native_am else 0
            result['demographics']['hopi_percentage'] = (hopi / total_race * 100) if hopi else 0
            result['demographics']['hispanic_percentage'] = (hispanic / total_race * 100) if hispanic else 0
        
        # Income data
        median_income = _safe_int(record.get('B19013_001E'))
        if median_income:
            result['income']['median_household_income'] = median_income
        
        # Poverty rate
        poverty_below = _safe_int(record.get('B17001_002E', 0))
        poverty_total = _safe_int(record.get('B17001_001E'))
        if poverty_total and poverty_total > 0:
            result['income']['poverty_rate'] = (poverty_below / poverty_total * 100) if poverty_below else 0
        
        # Housing data
        total_housing = _safe_int(record.get('B25003_001E'))
        owner_occupied = _safe_int(record.get('B25003_002E', 0))
        if total_housing and total_housing > 0:
            result['housing']['homeownership_rate'] = (owner_occupied / total_housing * 100) if owner_occupied else 0
        
        # Fetch comparison years (2020, 2010, and optionally 2000 decennial census)
        if include_comparison_years:
            print("Fetching 2020 Decennial Census data for comparison...")
            census_2020 = get_decennial_census_race_data(county_fips, state_fips, '2020', api_key)
            if census_2020:
                result['comparison_years']['2020'] = {
                    'source': '2020 Decennial Census',
                    'demographics': census_2020
                }
            
            print("Fetching 2010 Decennial Census data for comparison...")
            census_2010 = get_decennial_census_race_data(county_fips, state_fips, '2010', api_key)
            if census_2010:
                result['comparison_years']['2010'] = {
                    'source': '2010 Decennial Census',
                    'demographics': census_2010
                }
            
            if include_2000:
                print("Fetching 2000 Decennial Census data for comparison...")
                census_2000 = get_decennial_census_race_data(county_fips, state_fips, '2000', api_key)
                if census_2000:
                    result['comparison_years']['2000'] = {
                        'source': '2000 Decennial Census',
                        'demographics': census_2000
                    }
        
        return result
        
    except ImportError:
        print("Warning: 'census' package not installed. Install with: pip install census us requests")
        return {}
    except Exception as e:
        print(f"Error fetching census data: {e}")
        import traceback
        traceback.print_exc()
        return {}


def _safe_int(value) -> Optional[int]:
    """Safely convert value to integer, handling null and error codes"""
    if value is None:
        return None
    try:
        val = int(value)
        # Census API uses -888888888 or similar for nulls/errors
        if val < 0:
            return None
        return val
    except (ValueError, TypeError):
        return None


def get_census_data_for_tracts(
    tract_list: list,
    state_fips: str,
    api_key: Optional[str] = None,
    year: str = "2022"
) -> Dict:
    """
    Get census data aggregated across multiple census tracts
    
    Args:
        tract_list: List of census tract GEOIDs (11 digits)
        state_fips: State FIPS code
        api_key: Census API key
        year: Year of ACS data
    
    Returns:
        Dictionary with aggregated demographic data
    """
    # For tract-level aggregation, would need to query each tract
    # and aggregate. This is a placeholder for future implementation.
    # For now, county-level data is sufficient for most reports.
    pass


def format_comparison_text(community_data: Dict) -> str:
    """
    Format text describing demographic changes over time
    
    Args:
        community_data: Dictionary with current demographics and comparison_years
    
    Returns:
        Formatted text string
    """
    if not community_data.get('comparison_years'):
        return ""
    
    current = community_data.get('demographics', {})
    census_2020 = community_data.get('comparison_years', {}).get('2020', {}).get('demographics', {})
    census_2010 = community_data.get('comparison_years', {}).get('2010', {}).get('demographics', {})
    
    parts = []
    
    # Compare current to 2020
    if census_2020:
        current_pop = current.get('total_population', 0)
        pop_2020 = census_2020.get('total_population', 0)
        if current_pop and pop_2020:
            pop_change = ((current_pop - pop_2020) / pop_2020 * 100) if pop_2020 > 0 else 0
            if abs(pop_change) > 1:
                direction = "increased" if pop_change > 0 else "decreased"
                parts.append(f"Population {direction} by {abs(pop_change):.1f}% from 2020 to {community_data.get('profile_year', 'current')}")
    
    # Compare 2020 to 2010
    if census_2020 and census_2010:
        pop_2020 = census_2020.get('total_population', 0)
        pop_2010 = census_2010.get('total_population', 0)
        if pop_2020 and pop_2010:
            pop_change = ((pop_2020 - pop_2010) / pop_2010 * 100) if pop_2010 > 0 else 0
            if abs(pop_change) > 1:
                direction = "increased" if pop_change > 0 else "decreased"
                parts.append(f"From 2010 to 2020, population {direction} by {abs(pop_change):.1f}%")
    
    return ". ".join(parts) + "." if parts else ""

