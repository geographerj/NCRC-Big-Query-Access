"""Test parsing of CBA ticket file"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
shared_utils = project_root / 'reports' / 'Local Markets Analyses' / '_shared' / 'utils'
sys.path.insert(0, str(shared_utils))

from extract_ticket_info import extract_ticket_info
import json

ticket_file = r"C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis\PNC+FirstBank Research Ticket_CBA.xlsx"

print("="*80)
print("TESTING CBA TICKET PARSING")
print("="*80)

info = extract_ticket_info(ticket_file)

print("\n" + "="*80)
print("EXTRACTED INFORMATION")
print("="*80)
print(json.dumps(info, indent=2))

# Check if all expected data was extracted
print("\n" + "="*80)
print("VERIFICATION")
print("="*80)

checks = {
    'Acquirer Name': info['acquirer'].get('name'),
    'Acquirer LEI': info['acquirer'].get('lei'),
    'Acquirer RSSD': info['acquirer'].get('rssd'),
    'Acquirer SB Respondent ID': info['acquirer'].get('sb_respondent_id'),
    'Target Name': info['target'].get('name'),
    'Target LEI': info['target'].get('lei'),
    'Target RSSD': info['target'].get('rssd'),
    'Target SB Respondent ID': info['target'].get('sb_respondent_id'),
    'Years': info.get('years'),
    'HMDA Years Filter': info['filters'].get('hmda_years'),
    'Occupancy Filter': info['filters'].get('occupancy'),
    'Action Taken Filter': info['filters'].get('action_taken'),
    'Loan Purpose Filter': info['filters'].get('loan_purpose'),
    'Units Filter': info['filters'].get('units'),
}

for check_name, check_value in checks.items():
    if check_value:
        print(f"  [OK] {check_name}: {check_value}")
    else:
        print(f"  [MISSING] {check_name}")

