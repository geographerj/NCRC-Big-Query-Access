"""Test New York County mapping"""

import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'reports' / 'Local Markets Analyses' / '_shared' / 'utils'))

from map_counties_to_geoid import map_assessment_areas_to_geoid

aa_file = project_root / 'reports' / 'Local Markets Analyses' / '251101_PNC_Bank_FirstBank_Merger' / 'supporting_files' / 'assessment_areas_from_ticket.json'

with open(aa_file, 'r') as f:
    data = json.load(f)

mapped = map_assessment_areas_to_geoid(data)

pnc_mapped = sum(1 for c in mapped['pnc'] if c.get('geoid5'))
pnc_total = len(mapped['pnc'])
fb_mapped = sum(1 for c in mapped['firstbank'] if c.get('geoid5'))
fb_total = len(mapped['firstbank'])

print(f'PNC: {pnc_mapped}/{pnc_total} counties mapped ({100*pnc_mapped/pnc_total:.1f}%)')
print(f'FirstBank: {fb_mapped}/{fb_total} counties mapped ({100*fb_mapped/fb_total:.1f}%)')

# Check New York County
ny_counties = [c for c in mapped['pnc'] if 'New York' in str(c.get('county_name')) and c.get('state_name') == 'New York']
print(f'\nNew York County entries: {len(ny_counties)}')
for c in ny_counties:
    print(f"  County: {c.get('county_name')}, State: {c.get('state_name')} -> GEOID5: {c.get('geoid5', 'UNMAPPED')}")
    print(f"    Full string: {c.get('full_county_string', 'N/A')}")

