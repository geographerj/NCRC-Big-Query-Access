"""Create a formatted table of unmapped counties with potential matches"""

import json
from pathlib import Path
import pandas as pd

project_root = Path(__file__).parent.parent

# Load unmapped counties analysis
unmapped_file = project_root / 'reports' / 'Local Markets Analyses' / '251101_PNC_Bank_FirstBank_Merger' / 'supporting_files' / 'unmapped_counties_analysis.json'

if not unmapped_file.exists():
    print("ERROR: Run analyze_unmapped_counties.py first")
    exit(1)

with open(unmapped_file, 'r') as f:
    unmapped = json.load(f)

# Load crosswalk to get all possible matches
sys.path.insert(0, str(project_root / 'reports' / 'Local Markets Analyses' / '_shared' / 'utils'))
from map_counties_to_geoid import load_county_cbsa_crosswalk

crosswalk = load_county_cbsa_crosswalk()

print("="*100)
print("UNMAPPED COUNTIES - POTENTIAL MATCHES ANALYSIS")
print("="*100)

# Group by state
states = {}
for entry in unmapped:
    state = entry['state'] or 'Unknown'
    if state not in states:
        states[state] = []
    states[state].append(entry)

# Sort by number of unmapped counties
sorted_states = sorted(states.items(), key=lambda x: len(x[1]), reverse=True)

print(f"\nTotal unmapped: {len(unmapped)} counties")
print(f"States affected: {len(sorted_states)}\n")

# Create detailed table for each state
for state, counties in sorted_states[:15]:  # Top 15 states
    print(f"\n{'='*100}")
    print(f"{state.upper()} - {len(counties)} unmapped counties")
    print("="*100)
    print(f"\n{'County Name':<30} | {'Full String':<40} | {'Potential Match in Crosswalk':<40} | {'GEOID5':<10} | {'CBSA':<20}")
    print("-" * 100)
    
    for entry in counties[:30]:  # First 30 per state
        county = entry['county'] or ''
        full_str = entry.get('full_string', '')[:38]
        
        # Find best match in crosswalk
        best_match = None
        if entry['potential_matches']:
            best_match = entry['potential_matches'][0]
            match_name = best_match['crosswalk_county_state'][:38]
            geoid5 = best_match['geoid5']
            cbsa = best_match['cbsa_code'] or best_match['cbsa_name'][:18] if best_match['cbsa_name'] else ''
            print(f"{county:<30} | {full_str:<40} | {match_name:<40} | {geoid5:<10} | {cbsa:<20}")
        else:
            # Try to find matches manually
            state_norm = state.lower()
            county_norm = (county or '').lower().replace(' county', '').replace(' st.', ' saint').replace("'", "")
            
            # Search crosswalk for this state
            state_matches = crosswalk[crosswalk['County State'].str.contains(state_norm, case=False, na=False)]
            
            for idx, row in state_matches.iterrows():
                cw_county = str(row.get('County State', ''))
                if county_norm in cw_county.lower() or cw_county.lower().startswith(county_norm):
                    geoid5 = str(row.get('Geoid5', ''))
                    cbsa = str(row.get('Cbsa Code', '')) if pd.notna(row.get('Cbsa Code')) else str(row.get('Cbsa', ''))[:18]
                    print(f"{county:<30} | {full_str:<40} | {cw_county[:38]:<40} | {geoid5:<10} | {cbsa:<20}")
                    break
            else:
                print(f"{county:<30} | {full_str:<40} | {'No match found':<40} | {'':<10} | {'':<20}")

print("\n" + "="*100)
print("\nNote: Many counties appear to exist in crosswalk but matching logic needs improvement.")
print("Most unmapped counties likely match entries that use 'County' suffix or different formatting.")

