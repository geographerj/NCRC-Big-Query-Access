"""
Local Market Analysis - Main Workflow Script

Orchestrates the complete Local Market Analysis for bank mergers.
This is a standard, repeatable analysis that can be recreated at any time.

The Local Market Analysis compares two banks planning to merge and sets 
statewide performance goals for their post-merger performance.

Handles all file paths using pathlib to avoid apostrophe issues.

Author: NCRC Research Department
Date: November 2025
"""

from pathlib import Path
from datetime import datetime
import sys
import json
import importlib.util
import shutil
import re
import pandas as pd

# Use pathlib for all paths to handle apostrophes
def sanitize_folder_name(name):
    """Sanitize bank name for use in folder name"""
    name = re.sub(r'[^\w\s-]', '', str(name))
    name = name.replace(' ', '_')
    name = re.sub(r'_+', '_', name)
    return name.strip('_').strip()

def load_module_from_path(module_name, file_path):
    """Load a Python module from file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# setup_merger_folder function moved to shared utils

def copy_files_to_merger_folder(files, merger_folder, subfolder='supporting_files'):
    """Copy files to merger folder"""
    target_dir = merger_folder / subfolder
    target_dir.mkdir(exist_ok=True)
    
    copied_files = []
    for file_path in files:
        source = Path(file_path)
        if source.exists():
            target = target_dir / source.name
            # Avoid overwriting
            counter = 1
            while target.exists():
                stem = source.stem
                suffix = source.suffix
                target = target_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            shutil.copy2(source, target)
            copied_files.append(target)
            print(f"  Copied: {source.name} -> {target}")
    
    return copied_files

def main():
    """Main workflow"""
    print("="*80)
    print("LOCAL MARKET ANALYSIS WORKFLOW")
    print("="*80)
    
    if len(sys.argv) < 2:
        print("\nUsage: python goal_setting_analysis_main.py <ticket_excel_file>")
        print("\nExample:")
        print('  python goal_setting_analysis_main.py "BankA+BankB merger research ticket.xlsx"')
        sys.exit(1)
    
    # Use pathlib to handle apostrophes in paths
    ticket_file = Path(sys.argv[1])
    
    if not ticket_file.exists():
        print(f"\nERROR: Ticket file not found: {ticket_file}")
        sys.exit(1)
    
    print(f"\nTicket file: {ticket_file}")
    
    # Step 1: Parse ticket to get bank info
    print("\n" + "="*80)
    print("STEP 1: Parsing Merger Ticket")
    print("="*80)
    
    # Load ticket parsing module from shared folder
    project_root = Path(__file__).parent.parent
    shared_utils = project_root / 'reports' / 'Local Markets Analyses' / '_shared' / 'utils'
    
    extract_ticket = load_module_from_path(
        'extract_ticket_info',
        shared_utils / 'extract_ticket_info.py'
    )
    
    ticket_info = extract_ticket.extract_ticket_info(str(ticket_file))
    
    bank_a_name = ticket_info['acquirer'].get('name', 'Bank A')
    bank_b_name = ticket_info['target'].get('name', 'Bank B')
    bank_a_lei = ticket_info['acquirer'].get('lei', '')
    bank_b_lei = ticket_info['target'].get('lei', '')
    bank_a_rssd = ticket_info['acquirer'].get('rssd', '')
    bank_b_rssd = ticket_info['target'].get('rssd', '')
    bank_a_sb_id = ticket_info['acquirer'].get('sb_respondent_id', '')
    bank_b_sb_id = ticket_info['target'].get('sb_respondent_id', '')
    
    # Extract separate year ranges for HMDA and Small Business
    # Check filters for specific year ranges
    hmda_years = ticket_info.get('filters', {}).get('hmda_years', {}).get('range', ticket_info.get('years', [2020, 2021, 2022, 2023, 2024]))
    sb_years = ticket_info.get('filters', {}).get('sb_years', {}).get('range', ticket_info.get('years', [2019, 2020, 2021, 2022, 2023]))
    
    # Ensure years are lists of strings
    if isinstance(hmda_years, list):
        hmda_years = [str(y) for y in hmda_years]
    else:
        hmda_years = [str(y) for y in range(2020, 2025)]
    
    if isinstance(sb_years, list):
        sb_years = [str(y) for y in sb_years]
    else:
        sb_years = [str(y) for y in range(2019, 2024)]
    
    print(f"\nAcquirer Bank: {bank_a_name}")
    print(f"  LEI: {bank_a_lei}")
    print(f"  RSSD: {bank_a_rssd}")
    print(f"  SB Respondent ID: {bank_a_sb_id}")
    print(f"\nTarget Bank: {bank_b_name}")
    print(f"  LEI: {bank_b_lei}")
    print(f"  RSSD: {bank_b_rssd}")
    print(f"  SB Respondent ID: {bank_b_sb_id}")
    print(f"\nHMDA Years: {hmda_years}")
    print(f"Small Business Years: {sb_years}")
    
    # Step 2: Setup merger folder
    print("\n" + "="*80)
    print("STEP 2: Setting Up Merger Folder")
    print("="*80)
    
    setup_merger_module = load_module_from_path(
        'setup_merger_folder',
        shared_utils / 'setup_merger_folder.py'
    )
    merger_folder = setup_merger_module.create_merger_folder(bank_a_name, bank_b_name)
    print(f"\nCreated merger folder: {merger_folder}")
    
    # Step 3: Parse assessment areas
    print("\n" + "="*80)
    print("STEP 3: Parsing Assessment Areas")
    print("="*80)
    
    # Load assessment area parser from shared folder
    parse_aa = load_module_from_path(
        'parse_assessment_areas_from_ticket',
        shared_utils / 'parse_assessment_areas_from_ticket.py'
    )
    
    assessment_areas_raw = parse_aa.parse_assessment_areas_sheet(
        str(ticket_file), 
        acquirer_name=bank_a_name,
        target_name=bank_b_name
    )
    
    # Convert from 'bank_a'/'bank_b' format to 'acquirer'/'target' format
    # The assessment_areas_raw now uses generic 'bank_a' and 'bank_b' keys
    assessment_areas = {
        'acquirer': {'counties': assessment_areas_raw.get('bank_a', assessment_areas_raw.get('acquirer', []))},
        'target': {'counties': assessment_areas_raw.get('bank_b', assessment_areas_raw.get('target', []))}
    }
    
    # Save parsed data to merger folder
    aa_output = merger_folder / 'supporting_files' / 'assessment_areas_from_ticket.json'
    with open(aa_output, 'w') as f:
        json.dump(assessment_areas, f, indent=2)
    print(f"  Saved: {aa_output}")
    
    # Step 4: Save ticket info
    ticket_info_output = merger_folder / 'supporting_files' / 'ticket_info_extracted.json'
    with open(ticket_info_output, 'w') as f:
        json.dump(ticket_info, f, indent=2)
    print(f"  Saved: {ticket_info_output}")
    
    # Step 5: Map counties to GEOIDs
    print("\n" + "="*80)
    print("STEP 5: Mapping Counties to GEOIDs")
    print("="*80)
    
    map_counties = load_module_from_path(
        'map_counties_to_geoid',
        shared_utils / 'map_counties_to_geoid.py'
    )
    
    # Map counties for both banks
    bank_a_counties = assessment_areas.get('acquirer', {}).get('counties', [])
    bank_b_counties = assessment_areas.get('target', {}).get('counties', [])
    
    # Map counties using individual county mapping
    bank_a_mapped = {'mapped_counties': [], 'unmapped_counties': []}
    bank_b_mapped = {'mapped_counties': [], 'unmapped_counties': []}
    
    crosswalk_df = map_counties.load_county_cbsa_crosswalk()
    
    for county_entry in bank_a_counties:
        county_name = county_entry.get('county_name')
        state_name = county_entry.get('state_name') or county_entry.get('state')
        cbsa_name = county_entry.get('cbsa_name') or county_entry.get('cbsa')
        
        if county_name and state_name:
            mapped = map_counties.map_county_to_geoid(county_name, state_name, crosswalk_df)
            if mapped:
                mapped['cbsa_name'] = cbsa_name  # Preserve CBSA name from input
                bank_a_mapped['mapped_counties'].append(mapped)
            else:
                bank_a_mapped['unmapped_counties'].append(county_entry)
    
    for county_entry in bank_b_counties:
        county_name = county_entry.get('county_name')
        state_name = county_entry.get('state_name') or county_entry.get('state')
        cbsa_name = county_entry.get('cbsa_name') or county_entry.get('cbsa')
        
        if county_name and state_name:
            mapped = map_counties.map_county_to_geoid(county_name, state_name, crosswalk_df)
            if mapped:
                mapped['cbsa_name'] = cbsa_name  # Preserve CBSA name from input
                bank_b_mapped['mapped_counties'].append(mapped)
            else:
                bank_b_mapped['unmapped_counties'].append(county_entry)
    
    print(f"\n  Bank A mapped: {len(bank_a_mapped['mapped_counties'])}/{len(bank_a_counties)} counties")
    print(f"  Bank B mapped: {len(bank_b_mapped['mapped_counties'])}/{len(bank_b_counties)} counties")
    
    # Combine mapped data
    mapped_assessment_areas = {
        'acquirer': bank_a_mapped,
        'target': bank_b_mapped
    }
    
    # Save mapped data
    mapped_output = merger_folder / 'supporting_files' / 'assessment_areas_from_ticket_with_geoid.json'
    with open(mapped_output, 'w') as f:
        json.dump(mapped_assessment_areas, f, indent=2, default=str)
    print(f"  Saved: {mapped_output}")
    
    # Get GEOID lists for queries
    bank_a_geoids = [county['geoid5'] for county in bank_a_mapped.get('mapped_counties', []) if county.get('geoid5')]
    bank_b_geoids = [county['geoid5'] for county in bank_b_mapped.get('mapped_counties', []) if county.get('geoid5')]
    all_geoids = list(set(bank_a_geoids + bank_b_geoids))
    
    print(f"\n  Bank A GEOIDs: {len(bank_a_geoids)} counties")
    print(f"  Bank B GEOIDs: {len(bank_b_geoids)} counties")
    print(f"  Total unique GEOIDs: {len(all_geoids)} counties")
    
    # Step 6: Build SQL Queries
    print("\n" + "="*80)
    print("STEP 6: Building SQL Queries")
    print("="*80)
    
    shared_queries = project_root / 'reports' / 'Local Markets Analyses' / '_shared' / 'queries'
    
    # Load query builders
    hmda_builder = load_module_from_path('goal_setting_hmda_query_builder', shared_queries / 'goal_setting_hmda_query_builder.py')
    peer_hmda_builder = load_module_from_path('goal_setting_peer_hmda_query_builder', shared_queries / 'goal_setting_peer_hmda_query_builder.py')
    sb_builder = load_module_from_path('goal_setting_sb_query_builder', shared_queries / 'goal_setting_sb_query_builder.py')
    peer_sb_builder = load_module_from_path('goal_setting_peer_sb_query_builder', shared_queries / 'goal_setting_peer_sb_query_builder.py')
    branch_builder = load_module_from_path('goal_setting_branch_query_builder', shared_queries / 'goal_setting_branch_query_builder.py')
    
    queries_dir = merger_folder / 'data_exports'
    queries_dir.mkdir(exist_ok=True)
    
    # Build HMDA queries for Mortgage Goals (separate loan types)
    if bank_a_lei and bank_b_lei:
        print("\n  Building HMDA queries for Mortgage Goals...")
        
        # Home Purchase
        goals_hp_a = hmda_builder.build_hmda_query(bank_a_lei, bank_a_geoids, hmda_years, loan_purpose_group='home_purchase')
        goals_hp_b = hmda_builder.build_hmda_query(bank_b_lei, bank_b_geoids, hmda_years, loan_purpose_group='home_purchase')
        
        # Refinance
        goals_ref_a = hmda_builder.build_hmda_query(bank_a_lei, bank_a_geoids, hmda_years, loan_purpose_group='refinance')
        goals_ref_b = hmda_builder.build_hmda_query(bank_b_lei, bank_b_geoids, hmda_years, loan_purpose_group='refinance')
        
        # Home Equity
        goals_he_a = hmda_builder.build_hmda_query(bank_a_lei, bank_a_geoids, hmda_years, loan_purpose_group='home_equity')
        goals_he_b = hmda_builder.build_hmda_query(bank_b_lei, bank_b_geoids, hmda_years, loan_purpose_group='home_equity')
        
        # Save queries
        with open(queries_dir / 'mortgage_goals_home_purchase.sql', 'w') as f:
            f.write(f"-- Bank A ({bank_a_name})\n{goals_hp_a}\n\n-- Bank B ({bank_b_name})\n{goals_hp_b}")
        
        with open(queries_dir / 'mortgage_goals_refinance.sql', 'w') as f:
            f.write(f"-- Bank A ({bank_a_name})\n{goals_ref_a}\n\n-- Bank B ({bank_b_name})\n{goals_ref_b}")
        
        with open(queries_dir / 'mortgage_goals_home_equity.sql', 'w') as f:
            f.write(f"-- Bank A ({bank_a_name})\n{goals_he_a}\n\n-- Bank B ({bank_b_name})\n{goals_he_b}")
        
        print(f"    Saved: mortgage_goals_*.sql queries")
        
        # Build HMDA queries for Mortgage Data sheets (home purchase only, default)
        loan_purpose = ticket_info.get('filters', {}).get('loan_purpose', {}).get('code', '1')
        
        print(f"\n  Building HMDA queries for Mortgage Data (loan_purpose={loan_purpose})...")
        mortgage_a = hmda_builder.build_hmda_query(bank_a_lei, bank_a_geoids, hmda_years, loan_purpose=loan_purpose)
        mortgage_b = hmda_builder.build_hmda_query(bank_b_lei, bank_b_geoids, hmda_years, loan_purpose=loan_purpose)
        mortgage_peer_a = peer_hmda_builder.build_peer_hmda_query(bank_a_lei, bank_a_geoids, hmda_years, loan_purpose=loan_purpose)
        mortgage_peer_b = peer_hmda_builder.build_peer_hmda_query(bank_b_lei, bank_b_geoids, hmda_years, loan_purpose=loan_purpose)
        
        with open(queries_dir / f'{bank_a_name}_mortgage_data.sql', 'w') as f:
            f.write(f"-- Subject Bank\n{mortgage_a}\n\n-- Peer Banks\n{mortgage_peer_a}")
        
        with open(queries_dir / f'{bank_b_name}_mortgage_data.sql', 'w') as f:
            f.write(f"-- Subject Bank\n{mortgage_b}\n\n-- Peer Banks\n{mortgage_peer_b}")
        
        print(f"    Saved: {bank_a_name}_mortgage_data.sql")
        print(f"    Saved: {bank_b_name}_mortgage_data.sql")
    
    # Build Small Business queries
    if bank_a_sb_id and bank_b_sb_id:
        print(f"\n  Building Small Business queries...")
        sb_a = sb_builder.build_sb_query(bank_a_sb_id, bank_a_geoids, sb_years)
        sb_b = sb_builder.build_sb_query(bank_b_sb_id, bank_b_geoids, sb_years)
        sb_peer_a = peer_sb_builder.build_peer_sb_query(bank_a_sb_id, bank_a_geoids, sb_years)
        sb_peer_b = peer_sb_builder.build_peer_sb_query(bank_b_sb_id, bank_b_geoids, sb_years)
        
        with open(queries_dir / f'{bank_a_name}_sb_data.sql', 'w') as f:
            f.write(f"-- Subject Bank\n{sb_a}\n\n-- Peer Banks\n{sb_peer_a}")
        
        with open(queries_dir / f'{bank_b_name}_sb_data.sql', 'w') as f:
            f.write(f"-- Subject Bank\n{sb_b}\n\n-- Peer Banks\n{sb_peer_b}")
        
        print(f"    Saved: {bank_a_name}_sb_data.sql")
        print(f"    Saved: {bank_b_name}_sb_data.sql")
    
    # Build Branch queries (2025 only)
    if bank_a_rssd and bank_b_rssd:
        print(f"\n  Building Branch queries (2025 only)...")
        branch_a = branch_builder.build_branch_query(bank_a_rssd, bank_a_geoids, year=2025)
        branch_b = branch_builder.build_branch_query(bank_b_rssd, bank_b_geoids, year=2025)
        
        with open(queries_dir / f'{bank_a_name}_branch_data.sql', 'w') as f:
            f.write(branch_a)
        
        with open(queries_dir / f'{bank_b_name}_branch_data.sql', 'w') as f:
            f.write(branch_b)
        
        print(f"    Saved: {bank_a_name}_branch_data.sql")
        print(f"    Saved: {bank_b_name}_branch_data.sql")
    
    # Step 7: Execute SQL Queries and Load Data
    print("\n" + "="*80)
    print("STEP 7: Executing SQL Queries in BigQuery")
    print("="*80)
    
    # Load BigQuery client
    bq_client_path = project_root / 'Lending and Branch Analysis' / 'utils' / 'bigquery_client.py'
    if not bq_client_path.exists():
        print("\nWARNING: BigQuery client not found. Skipping query execution.")
        print(f"  Expected location: {bq_client_path}")
        print("\n  Please execute queries manually and save CSV files to:")
        print(f"    {queries_dir}")
        bq_client = None
    else:
        bq_client_module = load_module_from_path('bigquery_client', bq_client_path)
        
        # Find credentials file (try multiple locations)
        creds_paths = [
            project_root / 'config' / 'credentials' / 'hdma1-242116-74024e2eb88f.json',
            project_root / 'workspace' / 'hdma1-242116-74024e2eb88f.json',
            Path('hdma1-242116-74024e2eb88f.json')
        ]
        
        creds_path = None
        for path in creds_paths:
            if path.exists():
                creds_path = path
                break
        
        if not creds_path:
            print("\nWARNING: BigQuery credentials not found. Skipping query execution.")
            print("  Please execute queries manually and save CSV files to:")
            print(f"    {queries_dir}")
            bq_client = None
        else:
            try:
                bq_client = bq_client_module.create_client(key_path=str(creds_path))
                print(f"  Connected to BigQuery using: {creds_path.name}")
            except Exception as e:
                print(f"\nERROR: Could not connect to BigQuery: {e}")
                print("  Please execute queries manually and save CSV files to:")
                print(f"    {queries_dir}")
                bq_client = None
    
    # Helper function to add state and CBSA name to dataframe using county GEOID mapping
    def add_state_to_df(df, mapped_counties):
        """Add state and cbsa_name columns to dataframe using direct county-to-state mapping.
        
        Maps each county to its state using the GEOID5 (first 2 digits = state code).
        This ensures accurate county-to-state mapping regardless of CBSA boundaries.
        """
        if df.empty:
            return df
        
        # State code to state name mapping (using GEOID5 first 2 digits)
        state_code_to_name = {
            '01': 'Alabama', '02': 'Alaska', '04': 'Arizona', '05': 'Arkansas', '06': 'California',
            '08': 'Colorado', '09': 'Connecticut', '10': 'Delaware', '11': 'District of Columbia',
            '12': 'Florida', '13': 'Georgia', '15': 'Hawaii', '16': 'Idaho', '17': 'Illinois',
            '18': 'Indiana', '19': 'Iowa', '20': 'Kansas', '21': 'Kentucky', '22': 'Louisiana',
            '23': 'Maine', '24': 'Maryland', '25': 'Massachusetts', '26': 'Michigan', '27': 'Minnesota',
            '28': 'Mississippi', '29': 'Missouri', '30': 'Montana', '31': 'Nebraska', '32': 'Nevada',
            '33': 'New Hampshire', '34': 'New Jersey', '35': 'New Mexico', '36': 'New York',
            '37': 'North Carolina', '38': 'North Dakota', '39': 'Ohio', '40': 'Oklahoma',
            '41': 'Oregon', '42': 'Pennsylvania', '44': 'Rhode Island', '45': 'South Carolina',
            '46': 'South Dakota', '47': 'Tennessee', '48': 'Texas', '49': 'Utah', '50': 'Vermont',
            '51': 'Virginia', '53': 'Washington', '54': 'West Virginia', '55': 'Wisconsin', '56': 'Wyoming'
        }
        
        # Create mapping from county_code (GEOID5) to state_name
        county_to_state = {}
        county_to_cbsa = {}
        cbsa_to_name = {}
        
        for county in mapped_counties:
            geoid5 = str(county.get('county_code', county.get('geoid5', ''))).zfill(5)
            state_name = county.get('state_name')
            cbsa_code = str(county.get('cbsa_code', '')) if county.get('cbsa_code') else None
            cbsa_name = county.get('cbsa_name')
            
            if geoid5 and len(geoid5) >= 5:
                # Extract state code from first 2 digits of GEOID5
                state_code = geoid5[:2]
                # Get state name from state code mapping or use provided state_name
                mapped_state = state_code_to_name.get(state_code, state_name)
                
                if mapped_state:
                    county_to_state[geoid5] = mapped_state
                
                # Map county to CBSA
                if cbsa_code and cbsa_code != 'nan' and cbsa_code != 'None':
                    county_to_cbsa[geoid5] = cbsa_code
                    # Map CBSA code to name
                    if cbsa_name and cbsa_code not in cbsa_to_name:
                        cbsa_to_name[cbsa_code] = cbsa_name
        
        # Add state column using county_code (GEOID5) from dataframe
        if 'county_code' in df.columns:
            df['county_code'] = df['county_code'].astype(str).str.zfill(5)
            if 'state' not in df.columns:
                df['state'] = df['county_code'].map(county_to_state)
        
        # Add CBSA mapping if needed
        if 'cbsa_code' in df.columns:
            df['cbsa_code'] = df['cbsa_code'].astype(str)
            
            # If we have county_code, use it to get CBSA
            if 'county_code' in df.columns and 'cbsa_code' not in df.columns or df['cbsa_code'].isna().any():
                df['cbsa_code'] = df['county_code'].map(county_to_cbsa)
            
            # Add cbsa_name column
            if 'cbsa_name' not in df.columns:
                df['cbsa_name'] = df['cbsa_code'].map(cbsa_to_name)
                
                # For rows without CBSA names, try to infer from state (Non-MSA areas)
                missing_name = df['cbsa_name'].isna()
                if missing_name.any() and 'state' in df.columns:
                    missing_mask = df['cbsa_name'].isna() & df['state'].notna()
                    df.loc[missing_mask, 'cbsa_name'] = df.loc[missing_mask, 'state'].apply(
                        lambda x: f"{x} Non-MSA" if pd.notna(x) and x else None
                    )
        
        return df
    
    # Execute queries and collect data
    mortgage_goals_data = {}
    bank_a_mortgage_data = None
    bank_b_mortgage_data = None
    bank_a_mortgage_peer_data = None
    bank_b_mortgage_peer_data = None
    bank_a_sb_data = None
    bank_b_sb_data = None
    bank_a_sb_peer_data = None
    bank_b_sb_peer_data = None
    bank_a_branch_data = None
    bank_b_branch_data = None
    
    if bq_client and bank_a_lei and bank_b_lei:
        # Execute Mortgage Goals queries (combine both banks, separate loan types)
        print("\n  Executing Mortgage Goals queries...")
        
        for loan_type in ['home_purchase', 'refinance', 'home_equity']:
            loan_purpose_group = loan_type
            
            print(f"    {loan_type}...")
            
            # Bank A
            query_a = hmda_builder.build_hmda_query(bank_a_lei, bank_a_geoids, hmda_years, loan_purpose_group=loan_purpose_group)
            df_a = bq_client.execute_query(query_a)
            
            # Add bank identifier
            if not df_a.empty:
                df_a['bank'] = bank_a_name
            
            # Bank B
            query_b = hmda_builder.build_hmda_query(bank_b_lei, bank_b_geoids, hmda_years, loan_purpose_group=loan_purpose_group)
            df_b = bq_client.execute_query(query_b)
            
            # Add bank identifier
            if not df_b.empty:
                df_b['bank'] = bank_b_name
            
            # Combine both banks
            if not df_a.empty or not df_b.empty:
                combined = pd.concat([df_a, df_b], ignore_index=True)
                
                # Map CBSA codes to states using the county mapping data
                # The county mapping already has state information
                if 'cbsa_code' in combined.columns and 'state' not in combined.columns:
                    # Create a mapping from CBSA to state from the mapped counties
                    cbsa_to_state = {}
                    for county in bank_a_mapped.get('mapped_counties', []) + bank_b_mapped.get('mapped_counties', []):
                        if county.get('cbsa_code') and county.get('state_name'):
                            cbsa_to_state[county['cbsa_code']] = county['state_name']
                    
                    # Add state column to combined data
                    combined['state'] = combined['cbsa_code'].map(cbsa_to_state)
                
                # Aggregate by state (combining both banks and all CBSAs within each state)
                if 'state' in combined.columns:
                    state_agg = combined.groupby('state').agg({
                        'total_loans': 'sum',
                        'lmict_loans': 'sum',
                        'lmib_loans': 'sum',
                        'lmib_amount': 'sum',
                        'mmct_loans': 'sum',
                        'minb_loans': 'sum',
                        'asian_loans': 'sum',
                        'black_loans': 'sum',
                        'native_american_loans': 'sum',
                        'hopi_loans': 'sum',
                        'hispanic_loans': 'sum'
                    }).reset_index()
                    
                    mortgage_goals_data[loan_type] = state_agg
                    print(f"      Aggregated to {len(state_agg)} states")
                else:
                    print(f"      WARNING: No state column found - cannot aggregate for Mortgage Goals sheet")
                
                # Save to CSV
                csv_path = queries_dir / f'mortgage_goals_{loan_type}_data.csv'
                combined.to_csv(csv_path, index=False)
                print(f"      Saved: {csv_path.name} ({len(combined)} rows)")
        
        # Execute Mortgage Data queries
        print(f"\n  Executing Mortgage Data queries (loan_purpose={loan_purpose})...")
        
        # Bank A
        query_a = hmda_builder.build_hmda_query(bank_a_lei, bank_a_geoids, hmda_years, loan_purpose=loan_purpose)
        bank_a_mortgage_data = bq_client.execute_query(query_a)
        bank_a_mortgage_data = add_state_to_df(bank_a_mortgage_data, bank_a_mapped.get('mapped_counties', []))
        csv_path = queries_dir / f'{bank_a_name}_mortgage_data.csv'
        bank_a_mortgage_data.to_csv(csv_path, index=False)
        print(f"    Saved: {csv_path.name} ({len(bank_a_mortgage_data)} rows)")
        
        query_a_peer = peer_hmda_builder.build_peer_hmda_query(bank_a_lei, bank_a_geoids, hmda_years, loan_purpose=loan_purpose)
        bank_a_mortgage_peer_data = bq_client.execute_query(query_a_peer)
        bank_a_mortgage_peer_data = add_state_to_df(bank_a_mortgage_peer_data, bank_a_mapped.get('mapped_counties', []))
        csv_path = queries_dir / f'{bank_a_name}_mortgage_peer_data.csv'
        bank_a_mortgage_peer_data.to_csv(csv_path, index=False)
        print(f"    Saved: {csv_path.name} ({len(bank_a_mortgage_peer_data)} rows)")
        
        # Bank B
        query_b = hmda_builder.build_hmda_query(bank_b_lei, bank_b_geoids, hmda_years, loan_purpose=loan_purpose)
        bank_b_mortgage_data = bq_client.execute_query(query_b)
        bank_b_mortgage_data = add_state_to_df(bank_b_mortgage_data, bank_b_mapped.get('mapped_counties', []))
        csv_path = queries_dir / f'{bank_b_name}_mortgage_data.csv'
        bank_b_mortgage_data.to_csv(csv_path, index=False)
        print(f"    Saved: {csv_path.name} ({len(bank_b_mortgage_data)} rows)")
        
        query_b_peer = peer_hmda_builder.build_peer_hmda_query(bank_b_lei, bank_b_geoids, hmda_years, loan_purpose=loan_purpose)
        bank_b_mortgage_peer_data = bq_client.execute_query(query_b_peer)
        bank_b_mortgage_peer_data = add_state_to_df(bank_b_mortgage_peer_data, bank_b_mapped.get('mapped_counties', []))
        csv_path = queries_dir / f'{bank_b_name}_mortgage_peer_data.csv'
        bank_b_mortgage_peer_data.to_csv(csv_path, index=False)
        print(f"    Saved: {csv_path.name} ({len(bank_b_mortgage_peer_data)} rows)")
    
    if bq_client and bank_a_sb_id and bank_b_sb_id:
        # Execute Small Business queries
        print(f"\n  Executing Small Business queries...")
        
        # Bank A
        query_a = sb_builder.build_sb_query(bank_a_sb_id, bank_a_geoids, sb_years)
        bank_a_sb_data = bq_client.execute_query(query_a)
        bank_a_sb_data = add_state_to_df(bank_a_sb_data, bank_a_mapped.get('mapped_counties', []))
        csv_path = queries_dir / f'{bank_a_name}_sb_data.csv'
        bank_a_sb_data.to_csv(csv_path, index=False)
        print(f"    Saved: {csv_path.name} ({len(bank_a_sb_data)} rows)")
        
        query_a_peer = peer_sb_builder.build_peer_sb_query(bank_a_sb_id, bank_a_geoids, sb_years)
        bank_a_sb_peer_data = bq_client.execute_query(query_a_peer)
        bank_a_sb_peer_data = add_state_to_df(bank_a_sb_peer_data, bank_a_mapped.get('mapped_counties', []))
        csv_path = queries_dir / f'{bank_a_name}_sb_peer_data.csv'
        bank_a_sb_peer_data.to_csv(csv_path, index=False)
        print(f"    Saved: {csv_path.name} ({len(bank_a_sb_peer_data)} rows)")
        
        # Bank B
        query_b = sb_builder.build_sb_query(bank_b_sb_id, bank_b_geoids, sb_years)
        bank_b_sb_data = bq_client.execute_query(query_b)
        bank_b_sb_data = add_state_to_df(bank_b_sb_data, bank_b_mapped.get('mapped_counties', []))
        csv_path = queries_dir / f'{bank_b_name}_sb_data.csv'
        bank_b_sb_data.to_csv(csv_path, index=False)
        print(f"    Saved: {csv_path.name} ({len(bank_b_sb_data)} rows)")
        
        query_b_peer = peer_sb_builder.build_peer_sb_query(bank_b_sb_id, bank_b_geoids, sb_years)
        bank_b_sb_peer_data = bq_client.execute_query(query_b_peer)
        bank_b_sb_peer_data = add_state_to_df(bank_b_sb_peer_data, bank_b_mapped.get('mapped_counties', []))
        csv_path = queries_dir / f'{bank_b_name}_sb_peer_data.csv'
        bank_b_sb_peer_data.to_csv(csv_path, index=False)
        print(f"    Saved: {csv_path.name} ({len(bank_b_sb_peer_data)} rows)")
    
    if bq_client and bank_a_rssd and bank_b_rssd:
        # Execute Branch queries
        print(f"\n  Executing Branch queries (2025 only)...")
        
        # Bank A
        query_a = branch_builder.build_branch_query(bank_a_rssd, bank_a_geoids, year=2025)
        bank_a_branch_data = bq_client.execute_query(query_a)
        bank_a_branch_data = add_state_to_df(bank_a_branch_data, bank_a_mapped.get('mapped_counties', []))
        csv_path = queries_dir / f'{bank_a_name}_branch_data.csv'
        bank_a_branch_data.to_csv(csv_path, index=False)
        print(f"    Saved: {csv_path.name} ({len(bank_a_branch_data)} rows)")
        
        # Bank B
        query_b = branch_builder.build_branch_query(bank_b_rssd, bank_b_geoids, year=2025)
        bank_b_branch_data = bq_client.execute_query(query_b)
        bank_b_branch_data = add_state_to_df(bank_b_branch_data, bank_b_mapped.get('mapped_counties', []))
        csv_path = queries_dir / f'{bank_b_name}_branch_data.csv'
        bank_b_branch_data.to_csv(csv_path, index=False)
        print(f"    Saved: {csv_path.name} ({len(bank_b_branch_data)} rows)")
    
    # Step 8: Generate Excel Workbook with Data
    print("\n" + "="*80)
    print("STEP 8: Generating Excel Workbook with Data")
    print("="*80)
    
    excel_generator = load_module_from_path(
        'excel_generator',
        shared_utils / 'excel_generator.py'
    )
    
    # Prepare assessment areas data for Excel
    aa_data = {
        'acquirer': {
            'bank_name': bank_a_name,
            'counties': bank_a_mapped.get('mapped_counties', [])
        },
        'target': {
            'bank_name': bank_b_name,
            'counties': bank_b_mapped.get('mapped_counties', [])
        }
    }
    
    # Output Excel file
    excel_output = merger_folder / f"{bank_a_name}_{bank_b_name}_Goal_Setting_Analysis.xlsx"
    
    # Use PNC/FirstBank example as template (has all required sheets with formulas)
    project_root = Path(__file__).parent.parent
    pnc_firstbank_example = project_root / 'reports' / 'Local Markets Analyses' / '251101_PNC_Bank_FirstBank_Merger' / 'PNC Bank_FirstBank_Goal_Setting_Analysis.xlsx'
    
    if pnc_firstbank_example.exists():
        template_file = pnc_firstbank_example
        print(f"\n  Using template: {template_file.name}")
    else:
        # Fallback: create from scratch if template not found
        template_file = None
        print(f"\n  WARNING: Template not found - creating sheets from scratch")
    
    # Generate Excel workbook with all data
    excel_generator.create_goal_setting_excel(
        output_path=excel_output,
        bank_a_name=bank_a_name,
        bank_b_name=bank_b_name,
        assessment_areas_data=aa_data,
        mortgage_goals_data=mortgage_goals_data if mortgage_goals_data else None,
        bank_a_mortgage_data=bank_a_mortgage_data,
        bank_b_mortgage_data=bank_b_mortgage_data,
        bank_a_mortgage_peer_data=bank_a_mortgage_peer_data,
        bank_b_mortgage_peer_data=bank_b_mortgage_peer_data,
        bank_a_sb_data=bank_a_sb_data,
        bank_b_sb_data=bank_b_sb_data,
        bank_a_sb_peer_data=bank_a_sb_peer_data,
        bank_b_sb_peer_data=bank_b_sb_peer_data,
        bank_a_branch_data=bank_a_branch_data,
        bank_b_branch_data=bank_b_branch_data,
        years_hmda=hmda_years,
        years_sb=sb_years,
        template_file=template_file
    )
    
    print(f"\n  Created: {excel_output.name} (with data)")
    
    # Step 9: Copy ticket file
    print("\n" + "="*80)
    print("STEP 9: Organizing Files")
    print("="*80)
    
    copied = copy_files_to_merger_folder([ticket_file], merger_folder)
    
    print(f"\n[OK] Files organized in: {merger_folder}")
    
    # Summary
    print("\n" + "="*80)
    print("WORKFLOW COMPLETE")
    print("="*80)
    print(f"\nMerger folder: {merger_folder}")
    print(f"\nGenerated files:")
    print(f"  - Excel workbook: {excel_output.name} (fully populated with data)")
    print(f"  - SQL queries: {queries_dir.name}/ (also executed and saved as CSV)")
    print(f"  - Assessment areas (mapped): {mapped_output.name}")
    print(f"\nCompleted steps:")
    print(f"  - All SQL queries executed in BigQuery")
    print(f"  - Query results saved to CSV files")
    print(f"  - Excel workbook populated with all data")
    print(f"\nNext steps:")
    print(f"  1. Review and validate final Excel file")
    print(f"  2. Check that all formulas are working correctly")
    print(f"  3. Verify data matches expected values")
    
    return merger_folder, ticket_info, assessment_areas, mapped_assessment_areas

if __name__ == "__main__":
    main()

