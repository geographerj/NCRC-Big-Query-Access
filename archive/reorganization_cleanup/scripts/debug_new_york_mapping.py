"""Debug New York County mapping step by step"""

import sys
import pandas as pd
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'reports' / 'Local Markets Analyses' / '_shared' / 'utils'))

from map_counties_to_geoid import (
    load_county_cbsa_crosswalk, 
    normalize_county_name, 
    normalize_state_name
)

# Load crosswalk
crosswalk = load_county_cbsa_crosswalk()

# Input
county_name = "New York"
state_name = "New York"

print("="*80)
print("DEBUGGING NEW YORK COUNTY MAPPING")
print("="*80)

# Special case handling
county_lower = str(county_name).lower().strip() if county_name else ""
state_lower = str(state_name).lower().strip() if state_name else ""

print(f"\n1. Input:")
print(f"   county_name: {county_name}")
print(f"   state_name: {state_name}")

if (county_lower == 'new york' and state_lower == 'new york'):
    county_name = "New York County"
    print(f"\n2. Special case applied:")
    print(f"   Converted to: {county_name}")

county_norm = normalize_county_name(county_name)
state_norm = normalize_state_name(state_name)

print(f"\n3. Normalized:")
print(f"   county_norm: {county_norm}")
print(f"   state_norm: {state_norm}")

# Find state rows
state_rows = []
for idx, row in crosswalk.iterrows():
    county_state_str = row.get('County State', '')
    if pd.isna(county_state_str):
        continue
    
    county_state_lower = str(county_state_str).lower()
    if state_norm in county_state_lower:
        state_code_str = str(row.get('State Code', '')).strip()
        if state_code_str and len(state_code_str) <= 2:
            state_code = state_code_str.zfill(2)
            state_rows.append((idx, row, state_code, county_state_str))

print(f"\n4. Found {len(state_rows)} rows for New York state")
print(f"   First 5 state codes: {list(set([s[2] for s in state_rows[:5]]))}")

# Check New York County specifically
ny_county_rows = [r for r in state_rows if 'new york county' in str(r[3]).lower()]
print(f"\n5. Found {len(ny_county_rows)} rows matching 'New York County'")

if ny_county_rows:
    idx, row, state_code, county_state_str = ny_county_rows[0]
    print(f"   Sample row: {county_state_str}")
    print(f"   State Code: {state_code}")
    print(f"   County Code: {row.get('County Code')}")
    print(f"   GEOID5: {row.get('Geoid5')}")
    
    # Test matching logic
    county_state_lower = str(county_state_str).lower()
    county_part = county_state_lower.replace(state_norm.lower(), '').strip()
    if county_part.endswith(' county'):
        county_part = county_part[:-7].strip()
    
    cw_county_norm = normalize_county_name(county_part)
    
    print(f"\n6. Matching logic:")
    print(f"   county_part (after removing state): {county_part}")
    print(f"   cw_county_norm: {cw_county_norm}")
    print(f"   county_norm (from input): {county_norm}")
    print(f"   Match? {cw_county_norm == county_norm}")

