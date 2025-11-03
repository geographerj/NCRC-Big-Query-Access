# Local Market Analysis - Complete Requirements

## Overview

The **Local Market Analysis** is a standard, repeatable analysis that compares two banks planning to merge and sets statewide performance goals for post-merger performance. This analysis can be recreated at any time using the automated workflow scripts.

**Note**: Bank names are specified in the merger research ticket (Acquirer Bank and Target Bank). This documentation uses generic placeholders (Bank A and Bank B) that should be replaced with actual bank names from the ticket. The analysis scripts dynamically extract and use actual bank names from the ticket.

## Sheet Structure Summary

### 1. Mortgage Goals Sheet
- **Action**: Insert data only, preserve all formulas exactly
- **Scope**: Combines both banks (Bank A + Bank B) and combines states where either bank had assessment areas
- **Loan Type Structure**: **Separate columns for each loan type group** (each requires its own SQL query):
  1. **Home Purchase Column**: `loan_purpose = '1'` (run separate query with `loan_purpose_group='home_purchase'`)
  2. **Refinance Column**: `loan_purpose IN ('31', '32')` (run separate query with `loan_purpose_group='refinance'`)
     - Combines both refinance types into one column
  3. **Home Equity Column**: `loan_purpose IN ('2', '4')` (run separate query with `loan_purpose_group='home_equity'`)
     - Combines home improvement ('2') and home equity ('4') into one column
- **Data Insertion**: Each loan type group gets its own column in Excel - do NOT combine data in SQL
- **No calculations** - formulas handle everything (including combining columns later if needed)

### 2. Notes Sheet
- **Format**: Same as "Methods" sheet from worst lenders analysis
- **Content**: Methodology documentation

### 3. Assessment Areas Sheet
- **Structure**: One row per bank + CBSA + County
- **Columns**: Bank Name, CBSA Name, CBSA Code, State Code, County Name, County Code (GEOID)
- **Key**: Only specific counties within each CBSA (NOT all counties in the CBSA)
- **Note**: Bank names come from merger ticket (Acquirer Bank and Target Bank)

### 4. [Bank A]Mortgage Data Sheet
- **Sheet Name**: `[Bank A Name]Mortgage Data` (e.g., "PNCMortgage Data", "JPMortgage Data")
- **Separate sheet** for Bank A (Acquirer) only
- **Rows**: State + CBSA + Metric (one row per metric)
- **Columns**: State, CBSA, Metrics, [Bank A] values, Peer values
- **Format**: 
  - Counts: Numbers
  - Percentages: ##.##%
  - Dollars: $#,###

### 5. [Bank B]Mortgage Data Sheet
- **Sheet Name**: `[Bank B Name]Mortgage Data` (e.g., "FirstBankMortgage Data", "BankXMortgage Data")
- **Separate sheet** for Bank B (Target) only
- **Same structure** as Bank A Mortgage Data

### 6. [Bank A]Small Business Data Sheet
- **Sheet Name**: `[Bank A Name]Small Business Data` (e.g., "PNCSmall Business Data")
- **Separate sheet** for Bank A only
- **Rows**: State + CBSA + Metric (one row per metric)
- **Metrics** (5 total):
  1. SB Loans (count)
  2. #LMICT (count of LMICT loans)
  3. Avg SB LMICT Loan Amount ($#,###)
  4. Loans Rev Under $1m (count)
  5. Avg Loan Amt for RUM SB ($#,###)
- **Format**: 
  - Dollars: $#,###
  - Percentages: ##.##% (if applicable)

### 7. [Bank B]Small Business Data Sheet
- **Sheet Name**: `[Bank B Name]Small Business Data`
- **Separate sheet** for Bank B only
- **Same structure** as Bank A Small Business Data

### 8. [Bank A]Branch Data Sheet
- **Sheet Name**: `[Bank A Name]Branch Data` (e.g., "PNCBranch Data")
- **Separate sheet** for Bank A only
- **Purpose**: Branch distribution analysis (NO goals - just format)
- **Year**: 2025 only
- **Metrics**:
  - Total number of branches
  - % of branches in LMICT (Low/Moderate Income Census Tract)
  - % of branches in MMCT (Majority-Minority Census Tract)
- **Comparison**: Subject bank vs **ALL other lenders** in assessment areas (NOT using peer rule)
- **Show**: Gap/difference between subject bank and market

### 9. [Bank B]Branch Data Sheet
- **Sheet Name**: `[Bank B Name]Branch Data`
- **Separate sheet** for Bank B only
- **Same structure** as Bank A Branch Data

## HMDA Metrics (Mortgage Data Sheets)

All percentage metrics use `##.##%` format.

1. **Loans** - Number of loans (count, not dollar volume)
2. **LMICT%** - Low/Moderate Income Census Tract % (##.##%)
3. **LMIB%** - Low/Moderate Income Borrower % (##.##%)
4. **LMIB$** - LMIB lending in Dollars ($#,###)
5. **MMCT%** - Majority-Minority Census Tract % (##.##%)
6. **MINB%** - Combined Minority Borrower % (##.##%)
7. **Asian%** - Asian borrower % (##.##%)
8. **Black%** - Black borrower % (##.##%)
9. **Native American%** - Native American borrower % (##.##%)
10. **HoPI%** - Hawaiian or Pacific Islander borrower % (##.##%)
11. **Hispanic%** - Hispanic borrower % (##.##%)

## Small Business Metrics (SB Data Sheets)

1. **SB Loans** - Number of small business loans (count)
2. **#LMICT** - Number of loans in Low/Moderate Income Census Tracts (count)
3. **Avg SB LMICT Loan Amount** - Average loan amount for LMICT loans ($#,###)
4. **Loans Rev Under $1m** - Number of loans to businesses with revenue under $1 million (count)
5. **Avg Loan Amt for RUM SB** - Average loan amount for Revenue Under $1M small business loans ($#,###)

### SB Data Source Details
- **Table**: `hdma1-242116.sb.disclosure`
- **Lenders Table**: `hdma1-242116.sb.lenders`
- **Join Key**: `disclosure.respondent_id` = `lenders.sb_resid`
- **Respondent ID**: From merger ticket (may have prefix separated by "-", **ignore prefix** to match in lenders table)
- **LMICT Filter**: `income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')`
- **SB Loans Count**: `num_under_100k + num_100k_250k + num_250k_1m`
- **SB Loans Amount**: `amt_under_100k + amt_100k_250k + amt_250k_1m`
- **Loans Rev Under $1m**: `numsbrev_under_1m`
- **Amount Rev Under $1m**: `amtsbrev_under_1m`

## Branch Metrics (Branch Data Sheets)

- **Total Branches** - Count of branches in assessment area counties
- **% in LMICT** - Percentage of branches in Low/Moderate Income Census Tracts (##.##%)
- **% in MMCT** - Percentage of branches in Majority-Minority Census Tracts (##.##%)
- **Comparison**: Subject bank vs **ALL lenders** in assessment areas (not peer rule)
- **Show Gap**: Difference between subject bank and market average

### Branch Data Source Details
- **Table**: `sod25` (Summary of Deposits)
- **Year**: 2025 only
- **Fields**:
  - `br_lmi` - Flag: 1 = branch in LMICT, 0 = not
  - `cr_minority` - Flag: 1 = branch in MMCT, 0 = not
  - `county_code` - Filter by assessment area counties
  - `geoid` - Census tract identifier (11 digits)
- **Filter**: Only branches in assessment area counties

## Geographic Filtering

**All data must be filtered to assessment area counties only:**
- Use county codes (GEOIDs) from Assessment Areas sheet
- Do NOT include all counties in a CBSA
- Only include the specific counties listed in the Assessment Areas sheet

## Peer Selection Rules

### HMDA and SB Data
- **50% to 200% volume rule** (same as worst lenders analysis)
- Peers must have 50%-200% of subject bank's origination/loan volume in the same:
  - CBSA
  - Year
  - Assessment area counties (filtered)

### Branch Data
- **NO peer rule** - Compare subject bank to **ALL other lenders** in assessment areas
- Calculate market average across all lenders (excluding subject bank)
- Show gap: Subject % - Market Average %
- **Important**: Query gets subject bank branches AND all other lender branches in the same CBSA/assessment areas

## Data Sources

### HMDA
- **Table**: `hdma1-242116.hmda.hmda`
- **Years**: To be specified when requesting analysis
- **Filters**: As specified in merger research ticket

### SQL Query Optimization

**CRITICAL**: All SQL queries must be optimized to return only the data needed to reduce processing time:

1. **Select Only Required Columns**:
   - Only include columns needed for calculations and final output
   - Avoid SELECT * unless truly necessary

2. **Apply Filters Early**:
   - Filter by assessment area counties in WHERE clause, not after
   - Filter by years, LEIs, action_taken, etc. early in query
   - Use CTEs (WITH clauses) to pre-filter data before joins

3. **Aggregate Early**:
   - Use GROUP BY and aggregations in SQL rather than processing raw rows in Python
   - Calculate metrics (counts, percentages, sums) in SQL
   - Only return aggregated results, not individual loan records

4. **Limit Data Volume**:
   - Filter to assessment area counties only (not all counties in CBSA)
   - Only include years specified in ticket
   - Only include loan types specified in filters (e.g., home purchase only if specified)

5. **Optimize Joins**:
   - Join with assessment area county list early
   - Use INNER JOIN when possible instead of LEFT JOIN
   - Index on join keys (BigQuery handles this automatically, but structure queries efficiently)

**Example Query Structure**:
```sql
WITH assessment_area_counties AS (
  SELECT DISTINCT county_code, state_code, cbsa_code
  FROM assessment_areas_table
),
filtered_hmda AS (
  SELECT 
    activity_year,
    cbsa_code,
    census_tract,
    -- Only columns needed for metrics
    action_taken,
    loan_amount,
    -- Income/demographic fields only if needed
    tract_to_msa_income_percentage,
    applicant_income_percentage_of_msamd
  FROM `hdma1-242116.hmda.hmda` h
  INNER JOIN assessment_area_counties aac
    ON h.county_code = aac.county_code
  WHERE activity_year IN (2020, 2021, 2022, 2023, 2024)
    AND lei = 'BANK_LEI'
    AND action_taken = '1'  -- Originations only if specified
    -- Other filters from ticket
)
-- Aggregate early, calculate metrics in SQL
SELECT 
  activity_year,
  cbsa_code,
  COUNT(*) as loan_count,
  SUM(loan_amount) as total_amount,
  COUNTIF(tract_to_msa_income_percentage <= 80) as lmict_count,
  -- Calculate percentages in SQL
FROM filtered_hmda
GROUP BY activity_year, cbsa_code
```

### Small Business
- **Disclosure Table**: `hdma1-242116.sb.disclosure`
- **Lenders Table**: `hdma1-242116.sb.lenders`
- **Years**: Same as HMDA data
- **Respondent ID Matching**: Strip prefix if separated by "-" (e.g., "PREFIX-12345" → use "12345")
- **Query Optimization**: 
  - Filter by assessment area counties (geoid5) early
  - Only select columns needed for the 5 SB metrics
  - Aggregate by CBSA/State early in SQL

### Branches
- **Table**: `sod25` (or appropriate SOD table)
- **Year**: 2025 only
- **Filter by**: RSSD or institution name
- **Counties**: Assessment area counties only
- **Query Optimization**:
  - Filter by assessment area counties (county_code) early
  - Only select columns needed: county_code, cbsa_code, br_lmi, cr_minority, uninumbr
  - Aggregate counts in SQL, not Python
  - Calculate percentages in SQL when possible

## Calculation Details

### LMIB (Low/Moderate Income Borrower)
- Borrower income (in thousands) * 1000 / MSA median family income * 100 ≤ 80%
- Use `income` field (in thousands) and `ffiec_msa_md_median_family_income` field

### LMICT (Low/Moderate Income Census Tract)
- **HMDA**: Use `tract_to_msa_income_percentage` field ≤ 80%
- **SB**: Use `income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')`
- **Branches**: Use `br_lmi` flag (1 = in LMICT)

### MMCT (Majority-Minority Census Tract)
- **HMDA**: Use `tract_minority_population_percent` > 50%
- **Branches**: Use `cr_minority` flag (1 = in MMCT)

### Race/Ethnicity Classification (NCRC Methodology)
- **Hierarchical**: Hispanic ethnicity checked FIRST (regardless of race)
- If any ethnicity field contains codes 1, 11, 12, 13, or 14 → Hispanic
- If NOT Hispanic, categorize by race:
  - Black: Race = 3
  - Asian: Race = 2 or 21-27
  - Native American: Race = 1
  - HoPI: Race = 4 or 41-44
  - White: Race = 5
  - Unknown: No data provided

## Workflow Steps

1. **Parse Merger Ticket** - Extract bank info (names, LEI, RSSD, SB Respondent ID) and filters
   - Bank A (Acquirer): Name, LEI, RSSD, SB Respondent ID
   - Bank B (Target): Name, LEI, RSSD, SB Respondent ID
2. **Parse Assessment Areas** - Extract specific counties per CBSA for each bank
   - Use bank names from ticket to identify which assessment areas belong to which bank
3. **Query HMDA Data** - Both banks, filtered by assessment area counties, calculate all metrics
4. **Query SB Data** - Both banks, filtered by assessment area counties, calculate all metrics
5. **Query Branch Data** - Both banks, 2025 only, filtered by assessment area counties
6. **Select Peers** - For HMDA and SB, using 50%-200% volume rule
7. **Calculate Market Average** - For branches, across all lenders (no peer rule)
8. **Populate Excel** - Insert data into template, preserve all formulas
   - Use actual bank names from ticket for sheet names (e.g., "PNCMortgage Data", "FirstBankMortgage Data")
9. **Verify** - Check formulas work correctly with new data

## Bank Name Handling

**Important**: Bank names are dynamic and come from the merger research ticket. The script should:
- Read bank names from the "Bank Details" sheet in the merger ticket
- Use actual bank names (not placeholders) for:
  - Sheet names in output Excel file
  - Column headers (e.g., "PNC Number of loans" vs "FirstBank Number of loans")
  - Assessment Areas sheet (list actual bank names)
- Handle variations in bank names (e.g., "PNC Bank" vs "PNC Bank, National Association")
- Match names between HMDA/SOD/SB datasets as needed

## File Organization

**All files must be saved to the merger-specific folder:**

```
reports/Local Markets Analyses/YYMMDD_BankA_BankB_Merger/
├── YYMMDD_BankA_BankB_GoalSetting_Analysis.xlsx  # Main output
├── supporting_files/
│   ├── ticket_info_extracted.json
│   ├── assessment_areas_from_ticket.json
│   ├── PNC Assessment Areas.pdf
│   ├── Firstbank Assessment Areas 2023.pdf
│   ├── [ticket Excel file]
│   └── [all other supporting files]
├── data_exports/
│   └── [SQL query exports if needed]
└── file_manifest.json  # List of all files
```

**Workflow ensures:**
- Merger folder created at start of analysis
- All extracted/parsed files saved to `supporting_files/`
- Main Excel output saved to merger folder root
- File manifest created listing all files

## Next Steps

1. Wait for Excel template file to be closed
2. Inspect template structure to identify data insertion points
3. Build SQL queries for all data types (using placeholders for bank identifiers)
4. Create Python script to orchestrate entire workflow
   - Script should dynamically use bank names from ticket
   - Script should generate sheet names based on actual bank names
   - Script should save all files to merger folder
5. Test with actual data

