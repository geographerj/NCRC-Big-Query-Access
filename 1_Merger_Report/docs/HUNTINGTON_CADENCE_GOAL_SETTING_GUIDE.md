# Huntington National Bank + Cadence Bank Goal Setting Analysis Guide

## Overview

This guide will help you produce a **Goal Setting Analysis** report (like the PNC Bank + FirstBank example) for the merger of Huntington National Bank and Cadence Bank.

## What You're Producing

A comprehensive Excel report (`Huntington_Cadence_Goal_Setting_Analysis.xlsx`) that:
- Compares both banks' lending performance
- Sets statewide performance goals for post-merger
- Analyzes HMDA mortgage data, Small Business data, and Branch data
- Provides peer comparisons
- Includes assessment area analysis

## Example File

**Reference**: `reports/Local Markets Analyses/251101_PNC_Bank_FirstBank_Merger/PNC Bank_FirstBank_Goal_Setting_Analysis.xlsx`

This is the exact format you'll be producing.

## Prerequisites

### 1. Bank Information (✅ You have this)

- **Huntington National Bank**:
  - **LEI**: `2WHM8VNJH63UN14OL754` ✅
  - **RSSD**: `12311` ✅
  - **SB Respondent ID**: `7745` ✅

- **Cadence Bank**:
  - **LEI**: `Q7C315HKI8VX0SSKBS64` ✅
  - **RSSD**: `606046` ✅
  - **SB Respondent ID**: `11813` ✅

### 2. Merger Research Ticket Excel File ⚠️ **REQUIRED**

You need to create an Excel file with the following structure. This file contains all the information the script needs.

**File Format**: `"Huntington+Cadence merger research ticket.xlsx"`

**Required Sheets**:

#### Sheet 1: "Bank Details"
Contains information for both banks:

| Column 2 (Label) | Column 3 (Acquirer Value) | Column 5 (Label) | Column 6 (Target Value) |
|------------------|-------------------------|------------------|------------------------|
| BANK             | The Huntington National Bank | BANK             | Cadence Bank |
| LEI CODE         | 2WHM8VNJH63UN14OL754    | LEI CODE         | Q7C315HKI8VX0SSKBS64 |
| RSS-ID           | [RSSD number]           | RSS-ID           | [RSSD number] |
| SB RESPONDENT ID | [SB Respondent ID]      | SB RESPONDENT ID | [SB Respondent ID] |

**Structure**: 
- Row 3: Headers (`BANK INFORMATION`, `ACQUIRER`, `BANK INFORMATION`, `TARGET`)
- Row 4+: Data rows with labels in column 2/5 and values in column 3/6

#### Sheet 2: "Assessment Areas" (or parsed from PDFs)
Contains the specific counties in each CBSA assessment area for each bank.

**Alternative**: Assessment areas can be parsed from PDF files if provided separately.

#### Sheet 3: "LMA Ticket Filters" (Optional)
Contains filter settings:
- Years for HMDA and Small Business data
- HMDA filters (occupancy, action taken, units, construction method, loan purpose)
- Other analysis parameters

**Note**: If this sheet doesn't exist, the script will use default filters.

### 3. Goal Setting Template Excel (✅ Should exist)

The script uses a standardized template. Check if it exists at:
- `reports/Local Markets Analyses/_shared/goal_setting_template.xlsx` (if exists)

Or the script will create one from scratch.

## Step-by-Step Process

### Step 1: Find Missing Bank Information

#### Find RSSD Numbers

**Option A: Query BigQuery**
```sql
-- Find Huntington RSSD
SELECT DISTINCT rssd, institution_name
FROM `hdma1-242116.branches.sod25`
WHERE LOWER(institution_name) LIKE '%huntington%'
  AND year = 2025
LIMIT 10;

-- Find Cadence RSSD
SELECT DISTINCT rssd, institution_name
FROM `hdma1-242116.branches.sod25`
WHERE LOWER(institution_name) LIKE '%cadence%'
  AND year = 2025
LIMIT 10;
```

**Option B: Use existing script**
```bash
# Check if there's a script to find RSSD by bank name
python scripts/05_find_bank_lei.py --bank "The Huntington National Bank"
```

#### Find SB Respondent IDs

Check Small Business data:
```sql
-- Find Huntington SB Respondent ID
SELECT DISTINCT respondent_id, respondent_name
FROM `hdma1-242116.sb.sb`
WHERE LOWER(respondent_name) LIKE '%huntington%'
  AND lei = '2WHM8VNJH63UN14OL754'
LIMIT 10;

-- Find Cadence SB Respondent ID
SELECT DISTINCT respondent_id, respondent_name
FROM `hdma1-242116.sb.sb`
WHERE LOWER(respondent_name) LIKE '%cadence%'
  AND lei = 'Q7C315HKI8VX0SSKBS64'
LIMIT 10;
```

### Step 2: Create/Prepare Merger Research Ticket

#### Option A: Copy and Modify Existing Ticket

1. Look for an existing ticket in `reports/Local Markets Analyses/251101_PNC_Bank_FirstBank_Merger/supporting_files/`
2. Copy the structure
3. Update with Huntington and Cadence information

#### Option B: Create New Ticket from Template

Use the structure shown in "Prerequisites" section above.

**Key Requirements**:
- Sheet name: "Bank Details" (exact)
- Columns 2-3: Acquirer (Huntington) labels and values
- Columns 5-6: Target (Cadence) labels and values
- Must include: Bank name, LEI, RSSD, SB Respondent ID

### Step 3: Prepare Assessment Areas

**Option A: Parse from Ticket Sheet**
- Add "Assessment Areas" sheet to ticket Excel
- Format: List of counties with CBSA information for each bank

**Option B: Parse from PDF**
- Place PDF files in supporting_files folder
- Script will parse assessment area PDFs automatically

**Format Required**:
- County Name
- State Name
- CBSA Name
- Which bank (Acquirer/Target or Bank A/Bank B)

### Step 4: Run the Goal Setting Analysis Script

Once you have the merger ticket file:

```bash
python scripts/goal_setting_analysis_main.py "Huntington+Cadence merger research ticket.xlsx"
```

**What the script does**:
1. ✅ Parses the merger ticket to extract bank information
2. ✅ Extracts assessment areas (from sheet or PDFs)
3. ✅ Maps counties to GEOIDs
4. ✅ Queries BigQuery for:
   - HMDA mortgage data (both banks)
   - HMDA peer data
   - Small Business data (both banks)
   - Small Business peer data
   - Branch data (both banks, 2025 only)
   - Mortgage goals data (home purchase, refinance, home equity)
5. ✅ Generates SQL queries and saves them
6. ✅ Executes queries and saves results as CSV
7. ✅ Populates Excel template with all data
8. ✅ Saves everything to merger folder

### Step 5: Review Output

**Output Location**:
```
reports/Local Markets Analyses/YYMMDD_Huntington_Cadence_Merger/
├── Huntington_Cadence_Goal_Setting_Analysis.xlsx  # Main report
├── data_exports/                                    # SQL queries and CSV exports
│   ├── Huntington_branch_data.csv
│   ├── Huntington_mortgage_data.csv
│   ├── Cadence_branch_data.csv
│   ├── Cadence_mortgage_data.csv
│   ├── mortgage_goals_home_purchase_data.csv
│   ├── mortgage_goals_refinance_data.csv
│   ├── mortgage_goals_home_equity_data.csv
│   └── [and SQL query files]
└── supporting_files/                                # Ticket, parsed JSONs, PDFs
    ├── Huntington+Cadence merger research ticket.xlsx
    ├── assessment_areas_from_ticket.json
    └── ticket_info_extracted.json
```

**Review Checklist**:
- [ ] Excel file opens correctly
- [ ] All formulas are working (no errors)
- [ ] Data looks correct (numbers make sense)
- [ ] Bank names appear correctly in sheet names
- [ ] Assessment areas match expected counties
- [ ] Peer comparisons look reasonable
- [ ] Branch data shows 2025 data only

## Report Structure (What's in the Excel File)

### 1. Mortgage Goals Sheet
- Combined goals for both banks post-merger
- Separate columns for Home Purchase, Refinance, and Home Equity
- State-level aggregation
- **Formulas**: Preserved and must not be modified

### 2. Notes Sheet
- Methodology documentation
- Data sources
- Peer selection criteria

### 3. Assessment Areas Sheet
- List of all counties in assessment areas
- Organized by Bank, CBSA, State, County
- Includes GEOID codes

### 4. HuntingtonMortgage Data Sheet
- Mortgage lending metrics for Huntington only
- One row per State + CBSA + Metric
- Shows Huntington values and Peer values
- Metrics: Loans, LMICT%, LMIB%, LMIB$, MMCT%, MINB%, Asian%, Black%, etc.

### 5. CadenceMortgage Data Sheet
- Same structure as Huntington sheet
- Cadence-specific data

### 6. HuntingtonSmall Business Data Sheet
- Small Business lending metrics for Huntington
- Metrics: SB Loans, #LMICT, Avg SB LMICT Loan Amount, Loans Rev Under $1m, etc.

### 7. CadenceSmall Business Data Sheet
- Same structure as Huntington SB sheet
- Cadence-specific data

### 8. HuntingtonBranch Data Sheet
- Branch distribution for Huntington (2025 only)
- Metrics: Total branches, % in LMICT, % in MMCT
- Comparison vs. market average (all other lenders)

### 9. CadenceBranch Data Sheet
- Same structure as Huntington Branch sheet
- Cadence-specific data

## Key Scripts and Files

### Main Script
- **`scripts/goal_setting_analysis_main.py`**: Main workflow orchestrator
  - Run this with your merger ticket file
  - Handles all steps automatically

### Supporting Scripts (in `reports/Local Markets Analyses/_shared/`)

**Utilities** (`utils/`):
- `extract_ticket_info.py`: Parses merger ticket Excel
- `parse_assessment_areas_from_ticket.py`: Extracts assessment areas
- `map_counties_to_geoid.py`: Maps county names to GEOID codes
- `excel_generator.py`: Populates Excel template with data

**Query Builders** (`queries/`):
- `goal_setting_hmda_query_builder.py`: Builds HMDA mortgage queries
- `goal_setting_peer_hmda_query_builder.py`: Builds peer comparison queries
- `goal_setting_sb_query_builder.py`: Builds Small Business queries
- `goal_setting_peer_sb_query_builder.py`: Builds SB peer comparison queries
- `goal_setting_branch_query_builder.py`: Builds branch data queries

### Documentation
- **`docs/guides/LOCAL_MARKET_ANALYSIS_QUICK_REFERENCE.md`**: Quick start guide
- **`docs/guides/GOAL_SETTING_COMPLETE_REQUIREMENTS.md`**: Complete requirements
- **`docs/guides/LOCAL_MARKET_GOAL_SETTING_ANALYSIS.md`**: Detailed guide

## Troubleshooting

### Issue: Script can't find bank information in ticket
**Solution**: Verify "Bank Details" sheet exists and has correct column structure (columns 2-3 for acquirer, 5-6 for target)

### Issue: RSSD or SB Respondent ID not found
**Solution**: 
1. Check if values are in the ticket
2. Verify they're correct by querying BigQuery directly
3. Ensure spelling matches exactly (case-sensitive)

### Issue: Assessment areas not parsing correctly
**Solution**:
1. Check "Assessment Areas" sheet format
2. Verify county names and state names are correct
3. Check for typos in CBSA names
4. Use JSON output files to debug (in `supporting_files/`)

### Issue: Excel formulas showing errors
**Solution**:
1. Check that data was inserted into correct columns
2. Verify no formulas were accidentally overwritten
3. Check for division by zero (should be wrapped in IFERROR)

### Issue: Peer data seems incorrect
**Solution**:
1. Check peer selection criteria (50%-200% volume rule)
2. Verify LEI codes are correct
3. Check year filters match expectations

## Next Steps After Generating Report

1. **Review Data Quality**: 
   - Check for unexpected values
   - Verify peer comparisons make sense
   - Confirm branch counts match expectations

2. **Validate Assessment Areas**:
   - Ensure all expected counties are included
   - Verify CBSA assignments are correct

3. **Review Goals**:
   - Check Mortgage Goals sheet calculations
   - Verify statewide aggregations
   - Review peer gap calculations

4. **Prepare for Use**:
   - Document any manual adjustments
   - Save final version with notes
   - Prepare summary for stakeholders

## Quick Reference

**To generate the report**:
```bash
python scripts/goal_setting_analysis_main.py "Huntington+Cadence merger research ticket.xlsx"
```

**Required ticket structure**:
- Sheet: "Bank Details" (with LEI, RSSD, SB Respondent ID)
- Sheet: "Assessment Areas" (counties per CBSA per bank)
- Optional: "LMA Ticket Filters" (years and filters)

**Output location**:
- `reports/Local Markets Analyses/YYMMDD_Huntington_Cadence_Merger/`

**Bank Information**:
- **Huntington**:
  - LEI: `2WHM8VNJH63UN14OL754` ✅
  - RSSD: `12311` ✅
  - SB Respondent ID: `7745` ✅
- **Cadence**:
  - LEI: `Q7C315HKI8VX0SSKBS64` ✅
  - RSSD: `606046` ✅
  - SB Respondent ID: `11813` ✅

