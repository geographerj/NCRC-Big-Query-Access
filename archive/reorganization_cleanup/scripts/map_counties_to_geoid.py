"""
Map county names and states to GEOID5 codes.
Handles counties that exist in multiple states by requiring state name.
"""

import pandas as pd
from pathlib import Path
import sys
import json

def load_county_cbsa_crosswalk(crosswalk_path=None):
    """
    Load the CBSA to County mapping file.
    Returns DataFrame with county_code, state_code, county_name, cbsa_code, cbsa_name
    """
    if crosswalk_path is None:
        crosswalk_path = Path('data/reference/CBSA_to_County_Mapping.csv')
    else:
        crosswalk_path = Path(crosswalk_path)
    
    if not crosswalk_path.exists():
        raise FileNotFoundError(f"Crosswalk file not found: {crosswalk_path}")
    
    df = pd.read_csv(crosswalk_path)
    
    # Check what columns we have
    print(f"\nLoaded crosswalk: {len(df)} rows")
    print(f"  Columns: {list(df.columns)}")
    
    return df

def normalize_state_name(state_name):
    """
    Normalize state name for matching.
    Converts to lowercase and handles common variations.
    """
    if not state_name:
        return None
    
    state = str(state_name).strip().lower()
    
    # Handle common variations
    state_map = {
        'al': 'alabama',
        'az': 'arizona',
        'ar': 'arkansas',
        'ca': 'california',
        'co': 'colorado',
        'ct': 'connecticut',
        'de': 'delaware',
        'fl': 'florida',
        'ga': 'georgia',
        'il': 'illinois',
        'in': 'indiana',
        'ia': 'iowa',
        'ks': 'kansas',
        'ky': 'kentucky',
        'la': 'louisiana',
        'ma': 'massachusetts',
        'md': 'maryland',
        'me': 'maine',
        'mi': 'michigan',
        'mn': 'minnesota',
        'ms': 'mississippi',
        'mo': 'missouri',
        'mt': 'montana',
        'ne': 'nebraska',
        'nv': 'nevada',
        'nh': 'new hampshire',
        'nj': 'new jersey',
        'nm': 'new mexico',
        'ny': 'new york',
        'nc': 'north carolina',
        'nd': 'north dakota',
        'oh': 'ohio',
        'ok': 'oklahoma',
        'or': 'oregon',
        'pa': 'pennsylvania',
        'ri': 'rhode island',
        'sc': 'south carolina',
        'sd': 'south dakota',
        'tn': 'tennessee',
        'tx': 'texas',
        'ut': 'utah',
        'vt': 'vermont',
        'va': 'virginia',
        'wa': 'washington',
        'wv': 'west virginia',
        'wi': 'wisconsin',
        'wy': 'wyoming',
        'dc': 'district of columbia'
    }
    
    if state in state_map:
        return state_map[state]
    
    return state

def normalize_county_name(county_name):
    """Normalize county name for matching"""
    if not county_name:
        return None
    
    county = str(county_name).strip().lower()
    
    # Handle apostrophes - normalize variations
    county = county.replace("'s", "s")  # Queen Anne's -> Queen Annes
    county = county.replace("'", "")    # Remove any remaining apostrophes
    
    # Handle common variations
    county = county.replace("st.", "saint")  # St. -> Saint
    county = county.replace("st ", "saint ")
    
    # Remove common suffixes if present
    if county.endswith(' county'):
        county = county[:-7]
    
    return county.strip()

def parse_county_state_from_crosswalk(county_state_str):
    """
    Parse "County State" field from crosswalk (e.g., "Autauga County Alabama")
    Returns (county_name, state_name)
    """
    if pd.isna(county_state_str):
        return None, None
    
    text = str(county_state_str).strip()
    
    # Pattern: "County Name County State Name"
    # Remove "County" if it's a suffix, then split on last word (state)
    import re
    
    # Try to extract state name (last word)
    parts = text.rsplit(' ', 1)
    if len(parts) == 2:
        potential_state = parts[1]
        potential_county = parts[0]
        
        # Remove "County" suffix if present
        if potential_county.lower().endswith(' county'):
            potential_county = potential_county[:-7].strip()
        
        return potential_county.strip(), potential_state.strip()
    
    return None, None

def map_county_to_geoid(county_name, state_name, crosswalk_df):
    """
    Map county name + state name to GEOID5.
    
    Args:
        county_name: County name (e.g., "Dallas" - without "County")
        state_name: State name (e.g., "Alabama")
        crosswalk_df: DataFrame with county mapping data
    
    Returns:
        Dictionary with: geoid5, state_code, county_code, cbsa_code, cbsa_name
        Returns None if not found
    """
    county_norm = normalize_county_name(county_name)
    state_norm = normalize_state_name(state_name)
    
    if not county_norm or not state_norm:
        return None
    
    # The crosswalk has "County State" column like "Autauga County Alabama"
    # Parse this column and match
    
    if 'County State' in crosswalk_df.columns:
        # Parse each row's County State field
        for idx, row in crosswalk_df.iterrows():
            cw_county, cw_state = parse_county_state_from_crosswalk(row.get('County State', ''))
            
            if cw_county and cw_state:
                cw_county_norm = normalize_county_name(cw_county)
                cw_state_norm = normalize_state_name(cw_state)
                
                # Match if county and state both match (fuzzy matching for edge cases)
                county_match = (cw_county_norm == county_norm) or (county_norm in cw_county_norm) or (cw_county_norm in county_norm)
                state_match = (cw_state_norm == state_norm)
                
                if county_match and state_match:
                    # Found match!
                    state_code = str(row.get('State Code', '')).zfill(2)
                    county_code = str(row.get('County Code', '')).zfill(3)
                    
                    if state_code and county_code and len(state_code) == 2 and len(county_code) == 3:
                        geoid5 = state_code + county_code
                        
                        result = {
                            'geoid5': geoid5,
                            'state_code': state_code,
                            'county_code': county_code,
                            'county_name': cw_county,
                            'state_name': cw_state,
                            'cbsa_code': str(row.get('Cbsa Code', '')) if pd.notna(row.get('Cbsa Code')) else None,
                            'cbsa_name': str(row.get('Cbsa', '')) if pd.notna(row.get('Cbsa')) else None
                        }
                        
                        return result
    
    return None

def map_assessment_areas_to_geoid(assessment_areas_data, crosswalk_path=None):
    """
    Map all assessment area counties to GEOID5 codes.
    
    Args:
        assessment_areas_data: Dictionary with 'pnc' and 'firstbank' lists
        crosswalk_path: Path to CBSA crosswalk file
    
    Returns:
        Dictionary with mapped data including GEOID5 for each county
    """
    crosswalk_df = load_county_cbsa_crosswalk(crosswalk_path)
    
    mapped_data = {
        'pnc': [],
        'firstbank': []
    }
    
    for bank in ['pnc', 'firstbank']:
        print(f"\nMapping {bank.upper()} counties to GEOID5...")
        
        counties = assessment_areas_data.get(bank, [])
        mapped_count = 0
        unmapped_count = 0
        
        for county_entry in counties:
            county_name = county_entry.get('county_name')
            state_name = county_entry.get('state_name') or county_entry.get('state')
            
            if county_name and state_name:
                geoid_info = map_county_to_geoid(county_name, state_name, crosswalk_df)
                
                if geoid_info:
                    # Merge geoid info with original entry
                    mapped_entry = {**county_entry, **geoid_info}
                    mapped_data[bank].append(mapped_entry)
                    mapped_count += 1
                else:
                    # Keep original entry but mark as unmapped
                    county_entry['geoid5'] = None
                    county_entry['mapping_status'] = 'not_found'
                    mapped_data[bank].append(county_entry)
                    unmapped_count += 1
                    print(f"  WARNING: Could not map {county_name}, {state_name}")
            else:
                # Keep entry but mark as incomplete
                county_entry['geoid5'] = None
                county_entry['mapping_status'] = 'missing_data'
                mapped_data[bank].append(county_entry)
                unmapped_count += 1
        
        print(f"  Mapped: {mapped_count}, Unmapped: {unmapped_count}")
    
    return mapped_data

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python map_counties_to_geoid.py <assessment_areas_json_file>")
        print("\nExample:")
        print('  python map_counties_to_geoid.py "assessment_areas_from_ticket.json"')
        sys.exit(1)
    
    json_file = Path(sys.argv[1])
    
    if not json_file.exists():
        print(f"ERROR: File not found: {json_file}")
        sys.exit(1)
    
    # Load assessment areas
    with open(json_file, 'r') as f:
        assessment_areas = json.load(f)
    
    # Map to GEOID5
    mapped = map_assessment_areas_to_geoid(assessment_areas)
    
    # Save mapped data
    output_file = json_file.parent / f"{json_file.stem}_with_geoid.json"
    with open(output_file, 'w') as f:
        json.dump(mapped, f, indent=2)
    
    print(f"\n\nMapped data saved to: {output_file}")
    
    # Summary
    pnc_mapped = sum(1 for c in mapped['pnc'] if c.get('geoid5'))
    pnc_total = len(mapped['pnc'])
    fb_mapped = sum(1 for c in mapped['firstbank'] if c.get('geoid5'))
    fb_total = len(mapped['firstbank'])
    
    print(f"\nMapping Summary:")
    print(f"  PNC: {pnc_mapped}/{pnc_total} counties mapped")
    print(f"  FirstBank: {fb_mapped}/{fb_total} counties mapped")

if __name__ == "__main__":
    main()

