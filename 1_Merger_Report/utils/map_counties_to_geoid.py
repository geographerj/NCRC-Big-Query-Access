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
    
    Process:
    1. Identify state name from input
    2. Find state code (2 digits) from crosswalk by matching state
    3. Filter crosswalk to that state only
    4. Match county name within that state
    5. Extract county code (3 digits)
    6. Concatenate state_code + county_code = GEOID5
    
    Args:
        county_name: County name (e.g., "Dallas" - may or may not include "County")
        state_name: State name (e.g., "Alabama")
        crosswalk_df: DataFrame with county mapping data
    
    Returns:
        Dictionary with: geoid5, state_code, county_code, cbsa_code, cbsa_name
        Returns None if not found
    """
    if not county_name or not state_name:
        return None
    
    # Special case: "New York, New York" refers to New York County (Manhattan)
    # Handle both cases: county_name = "New York" or county already parsed as "New York County"
    county_lower = str(county_name).lower().strip() if county_name else ""
    state_lower = str(state_name).lower().strip() if state_name else ""
    
    if (county_lower == 'new york' and state_lower == 'new york'):
        # Convert to "New York County" for matching (this is Manhattan)
        county_name = "New York County"
    
    county_norm = normalize_county_name(county_name)
    state_norm = normalize_state_name(state_name)
    
    if not county_norm or not state_norm:
        return None
    
    # Step 1 & 2: Filter crosswalk to the state first
    # The crosswalk "County State" column has format "County Name State Name"
    # Find all rows for this state
    state_rows = []
    
    if 'County State' in crosswalk_df.columns:
        for idx, row in crosswalk_df.iterrows():
            county_state_str = row.get('County State', '')
            if pd.isna(county_state_str):
                continue
            
            # Check if state name appears in the County State field
            county_state_lower = str(county_state_str).lower()
            if state_norm in county_state_lower:
                # Extract state code from this row (once we find it, all rows in state have same code)
                state_code_str = str(row.get('State Code', '')).strip()
                if state_code_str and len(state_code_str) <= 2:
                    state_code = state_code_str.zfill(2)
                    state_rows.append((idx, row, state_code))
        
        # Step 3 & 4: Within state rows, find matching county
        for idx, row, state_code in state_rows:
            county_state_str = str(row.get('County State', '')).strip()
            
            # Parse county name from "County Name State Name" format
            # Remove state name from END only, then extract county
            county_state_lower = county_state_str.lower()
            if state_norm in county_state_lower:
                # Remove state name from the END only (not all occurrences)
                # This handles "New York County New York" correctly
                if county_state_lower.endswith(' ' + state_norm.lower()):
                    county_part = county_state_lower[:-len(' ' + state_norm.lower())].strip()
                elif county_state_lower.endswith(state_norm.lower()):
                    county_part = county_state_lower[:-len(state_norm.lower())].strip()
                else:
                    county_part = county_state_lower.replace(state_norm.lower(), '').strip()
                
                # Remove "County" suffix if present
                if county_part.endswith(' county'):
                    county_part = county_part[:-7].strip()
                
                cw_county_norm = normalize_county_name(county_part)
                
                # Step 5: Match county names (fuzzy matching)
                county_match = (
                    cw_county_norm == county_norm or 
                    county_norm in cw_county_norm or 
                    cw_county_norm in county_norm or
                    # Handle cases where one has "County" and other doesn't
                    cw_county_norm.replace('county', '').strip() == county_norm.replace('county', '').strip()
                )
                
                if county_match:
                    # Found match! Extract county code
                    county_code_str = str(row.get('County Code', '')).strip()
                    if county_code_str:
                        county_code = county_code_str.zfill(3)
                        
                        # Step 6: Concatenate state_code + county_code = GEOID5
                        if len(state_code) == 2 and len(county_code) == 3:
                            geoid5 = state_code + county_code
                            
                            # Parse full county and state names for result
                            cw_county, cw_state = parse_county_state_from_crosswalk(county_state_str)
                            
                            result = {
                                'geoid5': geoid5,
                                'state_code': state_code,
                                'county_code': county_code,
                                'county_name': cw_county or county_part,
                                'state_name': cw_state or state_name,
                                'cbsa_code': str(row.get('Cbsa Code', '')) if pd.notna(row.get('Cbsa Code')) else None,
                                'cbsa_name': str(row.get('Cbsa', '')) if pd.notna(row.get('Cbsa')) else None
                            }
                            
                            return result
    
    return None

def map_assessment_areas_to_geoid(assessment_areas_data, crosswalk_path=None):
    """
    Map all assessment area counties to GEOID5 codes.
    
    Args:
        assessment_areas_data: Dictionary with 'bank_a'/'bank_b' or 'acquirer'/'target' lists
        crosswalk_path: Path to CBSA crosswalk file
    
    Returns:
        Dictionary with mapped data including GEOID5 for each county
    """
    crosswalk_df = load_county_cbsa_crosswalk(crosswalk_path)
    
    # Support both old format (pnc/firstbank) and new format (bank_a/bank_b or acquirer/target)
    mapped_data = {}
    
    # Normalize keys to bank_a/bank_b format
    key_mapping = {
        'pnc': 'bank_a',
        'firstbank': 'bank_b',
        'acquirer': 'bank_a',
        'target': 'bank_b'
    }
    
    for bank_key in assessment_areas_data.keys():
        normalized_key = key_mapping.get(bank_key, bank_key)
        if normalized_key not in mapped_data:
            mapped_data[normalized_key] = []
    
    # If no normalized keys found, create bank_a and bank_b
    if not mapped_data:
        mapped_data = {
            'bank_a': [],
            'bank_b': []
        }
    
    for bank_key in ['bank_a', 'bank_b', 'pnc', 'firstbank', 'acquirer', 'target']:
        if bank_key in assessment_areas_data:
            normalized_key = key_mapping.get(bank_key, 'bank_a' if 'a' in bank_key.lower() or 'acquirer' in bank_key.lower() else 'bank_b')
            print(f"\nMapping {normalized_key.upper()} counties to GEOID5...")
            
            counties = assessment_areas_data.get(bank_key, [])
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
                        mapped_data[normalized_key].append(mapped_entry)
                        mapped_count += 1
                    else:
                        # Keep original entry but mark as unmapped
                        county_entry['geoid5'] = None
                        county_entry['mapping_status'] = 'not_found'
                        mapped_data[normalized_key].append(county_entry)
                        unmapped_count += 1
                        print(f"  WARNING: Could not map {county_name}, {state_name}")
                else:
                    # Keep entry but mark as incomplete
                    county_entry['geoid5'] = None
                    county_entry['mapping_status'] = 'missing_data'
                    mapped_data[normalized_key].append(county_entry)
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
    bank_a_key = 'bank_a' if 'bank_a' in mapped else ('acquirer' if 'acquirer' in mapped else 'pnc')
    bank_b_key = 'bank_b' if 'bank_b' in mapped else ('target' if 'target' in mapped else 'firstbank')
    
    bank_a_mapped = sum(1 for c in mapped.get(bank_a_key, []) if c.get('geoid5'))
    bank_a_total = len(mapped.get(bank_a_key, []))
    bank_b_mapped = sum(1 for c in mapped.get(bank_b_key, []) if c.get('geoid5'))
    bank_b_total = len(mapped.get(bank_b_key, []))
    
    print(f"\nMapping Summary:")
    print(f"  Bank A (Acquirer): {bank_a_mapped}/{bank_a_total} counties mapped")
    print(f"  Bank B (Target): {bank_b_mapped}/{bank_b_total} counties mapped")

if __name__ == "__main__":
    main()

