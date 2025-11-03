"""Analyze unmapped counties and suggest potential matches"""

import sys
from pathlib import Path
import json
import pandas as pd

project_root = Path(__file__).parent.parent
shared_utils = project_root / 'reports' / 'Local Markets Analyses' / '_shared' / 'utils'
sys.path.insert(0, str(shared_utils))

from map_counties_to_geoid import load_county_cbsa_crosswalk, normalize_county_name, normalize_state_name

# Load assessment areas
aa_file = project_root / 'reports' / 'Local Markets Analyses' / '251101_PNC_Bank_FirstBank_Merger' / 'supporting_files' / 'assessment_areas_from_ticket.json'
with open(aa_file, 'r') as f:
    assessment_areas = json.load(f)

# Load crosswalk
crosswalk = load_county_cbsa_crosswalk()

print("="*80)
print("UNMAPPED COUNTIES ANALYSIS")
print("="*80)

# Find unmapped PNC counties
unmapped = []
for county in assessment_areas['pnc']:
    if not county.get('geoid5'):
        county_name = county.get('county_name')
        state_name = county.get('state_name') or county.get('state')
        
        # Try to find potential matches in crosswalk
        potential_matches = []
        
        if county_name and state_name:
            county_norm = normalize_county_name(county_name)
            state_norm = normalize_state_name(state_name)
            
            # Search crosswalk for similar county names
            for idx, row in crosswalk.iterrows():
                if pd.notna(row.get('County State')):
                    county_state = str(row.get('County State', ''))
                    if state_norm in county_state.lower():
                        cw_county_norm = normalize_county_name(county_state.split('County')[0].strip())
                        # Check if county names are similar
                        if county_norm in cw_county_norm or cw_county_norm in county_norm:
                            potential_matches.append({
                                'crosswalk_county_state': county_state,
                                'geoid5': str(row.get('Geoid5', '')),
                                'cbsa_code': str(row.get('Cbsa Code', '')) if pd.notna(row.get('Cbsa Code')) else '',
                                'cbsa_name': str(row.get('Cbsa', '')) if pd.notna(row.get('Cbsa')) else ''
                            })
        
        unmapped.append({
            'county': county_name,
            'state': state_name,
            'full_string': county.get('full_county_string', ''),
            'potential_matches': potential_matches[:3]  # Top 3 matches
        })

print(f"\nTotal unmapped counties: {len(unmapped)}")
print(f"\nUnmapped by state:")
state_counts = {}
for entry in unmapped:
    state = entry['state'] or 'Unknown'
    state_counts[state] = state_counts.get(state, 0) + 1
for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {state}: {count}")

print("\n" + "="*80)
print("UNMAPPED COUNTIES WITH POTENTIAL MATCHES")
print("="*80)
print("\n| County Name | State | Potential Match | GEOID5 | CBSA |")
print("|-------------|-------|-----------------|--------|------|")

for entry in unmapped[:50]:  # First 50
    county = entry['county']
    state = entry['state'] or 'Unknown'
    
    if entry['potential_matches']:
        match = entry['potential_matches'][0]
        match_name = match['crosswalk_county_state'][:40]
        geoid5 = match['geoid5']
        cbsa = match['cbsa_code'] or match['cbsa_name'][:20] if match['cbsa_name'] else ''
        print(f"| {county[:25]} | {state[:10]} | {match_name[:30]} | {geoid5} | {cbsa[:15]} |")
    else:
        print(f"| {county[:25]} | {state[:10]} | No close match found | - | - |")

# Save detailed report
output_file = project_root / 'reports' / 'Local Markets Analyses' / '251101_PNC_Bank_FirstBank_Merger' / 'supporting_files' / 'unmapped_counties_analysis.json'
with open(output_file, 'w') as f:
    json.dump(unmapped, f, indent=2)
print(f"\n\nDetailed analysis saved to: {output_file}")

