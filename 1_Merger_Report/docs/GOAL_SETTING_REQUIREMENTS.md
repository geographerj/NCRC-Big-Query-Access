# Local Market Analysis Requirements

## Summary

The **Local Market Analysis** is a standard, repeatable analysis that compares two banks planning to merge and sets statewide performance goals for post-merger performance. This analysis can be recreated at any time by running the main workflow script with the appropriate merger research ticket.

**Note**: Bank names are dynamic and come from the merger research ticket. This documentation uses generic placeholders (Bank A = Acquirer, Bank B = Target) that should be replaced with actual bank names from the ticket for each analysis. The analysis scripts automatically extract and use actual bank names from the ticket.

## Sheet Structure

### 1. Mortgage Goals Sheet
- **Purpose**: Combined goals for both banks post-merger
- **Scope**: Combines both banks (Bank A + Bank B) and combines states where either bank had assessment areas
- **Action**: Insert data only - preserve all formulas exactly as they are
- **No calculations** - just populate with data from other sheets

### 2. Notes Sheet
- **Purpose**: Methodology documentation
- **Format**: Same as "Methods" sheet from worst lenders analysis
- **Content**: Document methodology, data sources, peer selection criteria, etc.

### 3. Assessment Areas Sheet
- **Purpose**: List assessment areas for each bank
- **Columns**:
  - Bank Name (from ticket: Acquirer Bank and Target Bank)
  - CBSA Name
  - CBSA Code
  - State Code
  - County Name
  - County Code (GEOID)
- **Note**: Only specific counties within each CBSA (not all counties in the CBSA)

### 4. [Bank A]Mortgage Data Sheet
- **Sheet Name**: `[Bank A Name]Mortgage Data` (e.g., "PNCMortgage Data", "JPMortgage Data")
- **Purpose**: Mortgage lending data for Bank A (Acquirer)
- **Structure**: Separate sheet (not combined with Bank B)
- **Rows**: One row per State + CBSA + Metric combination
- **Columns**:
  - State
  - CBSA
  - Metrics (one row per metric)
  - [Bank A] Number of loans
  - [Bank A] % for each metric (##.##% format)
  - LMIB$ ([Bank A] lending in dollars to LMIB)
  - Peer Number of loans
  - Peer % for each metric
  - Peer LMIB$

### 5. [Bank B]Mortgage Data Sheet
- **Sheet Name**: `[Bank B Name]Mortgage Data` (e.g., "FirstBankMortgage Data", "BankXMortgage Data")
- **Purpose**: Mortgage lending data for Bank B (Target)
- **Structure**: Same as Bank A Mortgage Data but for Bank B
- **Separate sheet** from Bank A

### 6. Small Business (SB) Sheets
- **Structure**: Separate sheets for Bank A and Bank B
- **Sheet Names**: `[Bank A Name]Small Business Data` and `[Bank B Name]Small Business Data`
- **Rows**: One row per State + CBSA + Metric combination
- **Columns**:
  - State
  - CBSA
  - Metrics (one row per metric)
  - Subject bank values
  - Peer bank values
- **Metrics**:
  1. **SB Loans** - Number of small business loans (count)
  2. **#LMICT** - Number of loans in Low/Moderate Income Census Tracts (count)
  3. **Avg SB LMICT Loan Amount** - Average loan amount for LMICT loans ($#,### format)
  4. **Loans Rev Under $1m** - Number of loans to businesses with revenue under $1 million (count)
  5. **Avg Loan Amt for RUM SB** - Average loan amount for Revenue Under $1M small business loans ($#,### format)
- **Format**: 
  - Dollars: $#,###
  - Percentages: ##.##%
- **Geographic Scope**: Same assessment area counties as mortgage data
- **Peer Selection**: Same 50%-200% volume rule as mortgage data
- **Data Source**: Small Business lending tables
- **Respondent ID**: From merger ticket (may have prefix separated by "-", ignore prefix to match in SB lenders table)
- **Years**: Same year range as mortgage data

### 7. Bank Branch Sheets
- **Structure**: Separate sheets for Bank A and Bank B
- **Sheet Names**: `[Bank A Name]Branch Data` and `[Bank B Name]Branch Data`
- **Purpose**: Branch distribution analysis (no goals - just format from sample)
- **Data**:
  - Branch counts by assessment area
  - Separated by:
    - Total number of branches
    - % of branches in LMICT (Low/Moderate Income Census Tract)
    - % of branches in MMCT (Majority-Minority Census Tract)
  - Comparison: Subject bank vs **all other lenders** in assessment areas (NOT using peer rule)
  - Show difference between subject bank and market (gap analysis)
- **Geographic Scope**: Assessment area counties only
- **Time Period**: 2025 only
- **Data Source**: sod25 (Summary of Deposits)
- **Peer Comparison**: Compare to ALL lenders in assessment areas (not 50%-200% rule)

## Metrics to Calculate

### All Percentage Metrics Use: `##.##%` format

1. **Loans** - Number of loans (count, not dollar volume)

2. **LMICT%** - Low/Moderate Income Census Tract percentage
   - Definition: Tract income ≤80% of MSA median income
   - Format: ##.##%

3. **LMIB%** - Low/Moderate Income Borrower percentage
   - Definition: Borrower income ≤80% of MSA median income
   - Format: ##.##%

4. **LMIB$** - LMIB lending in Dollars
   - Definition: Total dollar volume of loans to Low/Moderate Income Borrowers
   - Format: $#,###

5. **MMCT%** - Majority-Minority Census Tract percentage
   - Definition: Tract minority population >50%
   - Format: ##.##%

6. **MINB%** - Combined Minority Borrower percentage
   - Definition: Borrowers who are Hispanic, Black, Asian, Native American, or HoPI
   - Format: ##.##%

7. **Asian%** - Asian borrower percentage
   - Format: ##.##%

8. **Black%** - Black borrower percentage (non-Hispanic)
   - Format: ##.##%

9. **Native American%** - Native American borrower percentage (non-Hispanic)
   - Format: ##.##%

10. **HoPI%** - Hawaiian or Pacific Islander borrower percentage (non-Hispanic)
    - Format: ##.##%

11. **Hispanic%** - Hispanic borrower percentage
    - Format: ##.##%

## Geographic Filtering

- **Only include counties** listed in the Assessment Areas sheet
- Filter HMDA data by county codes (GEOIDs) from Assessment Areas sheet
- Do NOT include all counties in a CBSA - only specific assessment area counties

## Peer Selection

- **50% to 200% volume rule** (same as worst lenders analysis)
- Peers must have 50%-200% of subject bank's origination volume in the same:
  - CBSA
  - Year
  - Assessment area counties (filtered)

## Data Sources

### HMDA Data
- Table: `hdma1-242116.hmda.hmda`
- Years: To be specified by user when requesting analysis
- Filters: As specified in merger research ticket

### Small Business Data
- **TBD**: Need to understand source and requirements

### Bank Branch Data
- **TBD**: Need to understand source and requirements (likely from SOD tables)

## Race/Ethnicity Classification (NCRC Methodology)

- **Hierarchical classification**: Hispanic ethnicity checked FIRST (regardless of race)
- If any of the 5 ethnicity fields contains codes 1, 11, 12, 13, or 14 → Hispanic
- If NOT Hispanic, categorize by race:
  - Black: Race = 3
  - Asian: Race = 2 or 21-27
  - Native American: Race = 1
  - HoPI: Race = 4 or 41-44
  - White: Race = 5
  - Unknown: No data provided

## LMIB Calculation

- Borrower income (in thousands) * 1000 / MSA median family income * 100 ≤ 80%
- Use `income` field (in thousands) and `ffiec_msa_md_median_family_income` field

## LMICT Calculation

- Use `tract_to_msa_income_percentage` field ≤ 80%

