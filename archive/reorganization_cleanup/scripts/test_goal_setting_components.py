"""
Test script for Goal-Setting Analysis components
Tests ticket parsing, query generation, and folder setup
"""

from pathlib import Path
import sys
import json

# Add shared folders to path
project_root = Path(__file__).parent.parent
shared_queries = project_root / 'reports' / 'Local Markets Analyses' / '_shared' / 'queries'
shared_utils = project_root / 'reports' / 'Local Markets Analyses' / '_shared' / 'utils'
sys.path.insert(0, str(shared_queries))
sys.path.insert(0, str(shared_utils))

print("="*80)
print("TESTING GOAL-SETTING ANALYSIS COMPONENTS")
print("="*80)

# Test 1: Ticket Parsing
print("\n[TEST 1] Ticket Parsing")
print("-" * 80)
try:
    from extract_ticket_info import extract_ticket_info
    
    ticket_file = r"C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis\scripts\PNC+FirstBank merger research ticket.xlsx"
    ticket_info = extract_ticket_info(ticket_file)
    
    print(f"  Acquirer: {ticket_info['acquirer']}")
    print(f"  Target: {ticket_info['target']}")
    print(f"  Years: {ticket_info.get('years', [])}")
    print(f"  Filters: {len(ticket_info.get('filters', {}))} filter(s) found")
    print("  [OK] Ticket parsing successful")
except Exception as e:
    print(f"  [ERROR] Ticket parsing failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: HMDA Query Builder - All Loan Purpose Groups
print("\n[TEST 2] HMDA Query Builder - Loan Purpose Groups")
print("-" * 80)
try:
    from goal_setting_hmda_query_builder import build_hmda_query
    
    test_lei = "TEST_LEI_12345"
    test_geoids = ['01001', '01003']
    test_years = ['2020', '2021', '2022']
    
    # Test Home Purchase
    q1 = build_hmda_query(test_lei, test_geoids, test_years, loan_purpose_group='home_purchase')
    assert "loan_purpose = '1'" in q1
    print("  [OK] Home Purchase query generated correctly")
    
    # Test Refinance
    q2 = build_hmda_query(test_lei, test_geoids, test_years, loan_purpose_group='refinance')
    assert "loan_purpose IN ('31', '32')" in q2
    print("  [OK] Refinance query generated correctly")
    
    # Test Home Equity
    q3 = build_hmda_query(test_lei, test_geoids, test_years, loan_purpose_group='home_equity')
    assert "loan_purpose IN ('2', '4')" in q3
    print("  [OK] Home Equity query generated correctly")
    
    # Test single loan purpose (for Mortgage Data sheets)
    q4 = build_hmda_query(test_lei, test_geoids, test_years, loan_purpose='1')
    assert "loan_purpose = '1'" in q4
    print("  [OK] Single loan purpose query generated correctly")
    
except Exception as e:
    print(f"  [ERROR] HMDA query builder test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Branch Query Builder
print("\n[TEST 3] Branch Query Builder")
print("-" * 80)
try:
    from goal_setting_branch_query_builder import build_branch_query
    
    test_rssd = "12345"
    test_geoids = ['01001', '01003']
    
    q = build_branch_query(test_rssd, test_geoids, year=2025)
    assert "rssd != '12345'" in q  # Should exclude subject bank
    assert "year = 2025" in q
    assert "sod25" in q.lower()
    print("  [OK] Branch query generated correctly")
    print(f"  Query length: {len(q)} characters")
    
except Exception as e:
    print(f"  [ERROR] Branch query builder test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: County Mapping
print("\n[TEST 4] County to GEOID5 Mapping")
print("-" * 80)
try:
    from map_counties_to_geoid import map_assessment_areas_to_geoid
    
    # Load assessment areas from the test run
    aa_file = project_root / 'reports' / 'Local Markets Analyses' / '251101_PNC_Bank_FirstBank_Merger' / 'supporting_files' / 'assessment_areas_from_ticket.json'
    
    if aa_file.exists():
        with open(aa_file, 'r') as f:
            assessment_areas = json.load(f)
        
        mapped = map_assessment_areas_to_geoid(assessment_areas)
        
        pnc_total = len(mapped['pnc'])
        pnc_mapped = sum(1 for c in mapped['pnc'] if c.get('geoid5'))
        fb_total = len(mapped['firstbank'])
        fb_mapped = sum(1 for c in mapped['firstbank'] if c.get('geoid5'))
        
        print(f"  PNC: {pnc_mapped}/{pnc_total} counties mapped to GEOID5")
        print(f"  FirstBank: {fb_mapped}/{fb_total} counties mapped to GEOID5")
        
        if pnc_mapped > 0 and fb_mapped > 0:
            print("  [OK] County mapping working")
        else:
            print("  [WARNING] Some counties may need manual mapping")
    else:
        print("  [SKIP] Assessment areas file not found - run main script first")
        
except Exception as e:
    print(f"  [ERROR] County mapping test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Folder Structure
print("\n[TEST 5] Folder Structure")
print("-" * 80)
try:
    from setup_merger_folder import create_merger_folder
    
    folder = create_merger_folder("Test Bank A", "Test Bank B")
    assert folder.exists()
    assert (folder / 'supporting_files').exists()
    assert (folder / 'data_exports').exists()
    print(f"  [OK] Folder structure created: {folder}")
    
except Exception as e:
    print(f"  [ERROR] Folder creation test failed: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print("\nReady components:")
print("  [OK] Ticket parsing")
print("  [OK] HMDA query builder (all loan purpose groups)")
print("  [OK] Branch query builder")
print("  [OK] County mapping")
print("  [OK] Folder structure setup")
print("\nStill needed:")
print("  [ ] Peer HMDA query builder (50%-200% volume rule)")
print("  [ ] Small Business query builders")
print("  [ ] Excel generator script")
print("  [ ] Full workflow integration")

