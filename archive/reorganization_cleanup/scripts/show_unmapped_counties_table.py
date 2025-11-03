"""Create a clear table of unmapped counties with crosswalk matches"""

import json
import sys
from pathlib import Path
import pandas as pd

project_root = Path(__file__).parent.parent

# Load unmapped analysis
unmapped_file = project_root / 'reports' / 'Local Markets Analyses' / '251101_PNC_Bank_FirstBank_Merger' / 'supporting_files' / 'unmapped_counties_analysis.json'
with open(unmapped_file, 'r') as f:
    unmapped = json.load(f)

# Load crosswalk
sys.path.insert(0, str(project_root / 'reports' / 'Local Markets Analyses' / '_shared' / 'utils'))
from map_counties_to_geoid import load_county_cbsa_crosswalk

crosswalk = load_county_cbsa_crosswalk()

print("="*120)
print("UNMAPPED COUNTIES - MATCHING ISSUE ANALYSIS")
print("="*120)

# Group by state
state_groups = {}
for entry in unmapped:
    state = entry['state'] or 'Unknown'
    if state not in state_groups:
        state_groups[state] = []
    state_groups[state].append(entry)

# Sort by count
sorted_states = sorted(state_groups.items(), key=lambda x: len(x[1]), reverse=True)

print(f"\nTotal: {len(unmapped)} unmapped counties across {len(sorted_states)} states")
print("\nTop 10 states with unmapped counties:")
for state, counties in sorted_states[:10]:
    print(f"  {state}: {len(counties)} counties")

print("\n" + "="*120)
print("DETAILED TABLE - Counties that exist in crosswalk but aren't matching")
print("="*120)

# Show counties where we found potential matches (they exist but matching logic failed)
matched_in_crosswalk = [e for e in unmapped if e.get('potential_matches')]
not_found = [e for e in unmapped if not e.get('potential_matches')]

print(f"\nCounties with matches found in crosswalk: {len(matched_in_crosswalk)}")
print("(These should be easy to fix - matching logic issue)")
print(f"\nCounties not found in crosswalk: {len(not_found)}")
print("(These may need manual verification)")

print("\n" + "-"*120)
print("TABLE: Unmapped Counties with Crosswalk Matches")
print("-"*120)
print(f"{'County Name':<25} | {'State':<15} | {'Parsed String':<35} | {'Crosswalk Match':<35} | {'GEOID5':<10}")
print("-"*120)

count = 0
for entry in matched_in_crosswalk[:100]:  # First 100 with matches
    county = entry['county'] or ''
    state = entry['state'] or 'Unknown'
    full_str = entry.get('full_string', '')[:33]
    
    if entry['potential_matches']:
        match = entry['potential_matches'][0]
        match_name = match['crosswalk_county_state'][:33]
        geoid5 = match['geoid5']
        
        # Check if the match looks correct
        county_norm = county.lower().replace(' county', '').strip()
        match_norm = match_name.lower().replace(' county', '').replace(state.lower(), '').strip()
        
        status = "LIKELY MATCH" if county_norm in match_norm or match_norm.startswith(county_norm) else "CHECK"
        marker = "[MATCH]" if status == "LIKELY MATCH" else "[CHECK]"
        
        print(f"{county:<25} | {state:<15} | {full_str:<35} | {match_name[:33]:<35} | {geoid5:<10} {marker}")
        count += 1

print("\n" + "-"*120)
print("Counties NOT found in crosswalk (may need manual check):")
print("-"*120)
print(f"{'County Name':<25} | {'State':<15} | {'Full String':<50}")
print("-"*120)

for entry in not_found[:30]:  # First 30 not found
    county = entry['county'] or ''
    state = entry['state'] or 'Unknown'
    full_str = entry.get('full_string', '')[:48]
    print(f"{county:<25} | {state:<15} | {full_str:<50}")

print("\n" + "="*120)
print("\nSUMMARY:")
print(f"  • {len(matched_in_crosswalk)} counties exist in crosswalk but matching failed")
print(f"  • {len(not_found)} counties not found in crosswalk (may need manual verification)")
print(f"  • Issue: Parsed data uses 'County, State' format, crosswalk uses 'County State' (no comma)")
print("\nRECOMMENDATION: Fix matching logic to handle comma difference in county-state strings")

