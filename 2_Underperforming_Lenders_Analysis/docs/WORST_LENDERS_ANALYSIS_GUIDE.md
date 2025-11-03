# Worst Lenders Redlining Analysis Guide

## Overview

This analysis identifies the 15 worst-performing banks for redlining patterns in mortgage lending. It focuses exclusively on tract-level demographic metrics (redlining indicators) and uses rigorous selection criteria to identify banks with consistent, non-improving patterns of underperformance.

## Files Created

### 1. SQL Query: `queries/worst_lenders_redlining_query.sql`

This BigQuery SQL query:
- Identifies top 200 CBSAs by total applications (2018-2024)
- Filters banks: $10B-$100B assets, ≥500 applications in CBSA, appropriate type_name
- Breaks down data by county within each CBSA
- Creates separate datasets for:
  - Applications (all loan purposes)
  - Originations (all loan purposes)
  - Home Purchase Applications
  - Home Purchase Originations
- Calculates 8 redlining metrics (tract demographics)
- Identifies peer banks (50%-200% of subject's volume)

### 2. Python Script: `scripts/worst_lenders_analysis.py`

This script:
- Processes the SQL output CSV
- Calculates shares, gaps, and ratios for all metrics
- Uses chi-squared test for statistical significance
- Implements scoring logic (ratios ≥ 2.0, weighted by CBSA size)
- Applies selection filters (consistency, non-improvement)
- Excludes CBA banks
- Force includes 3 specific banks
- Selects worst 15 banks
- Creates Excel output with ratio and shares/gaps sheets

## Key Requirements

### Metrics (8 Redlining Metrics Only)

1. **MMCT 50%** - Loans in majority-minority tracts (>50% non-white)
2. **MMCT 80%** - Loans in supermajority-minority tracts (>80% non-white)
3. **Black Tract 50%** - Loans in majority-Black tracts (>50% Black)
4. **Black Tract 80%** - Loans in supermajority-Black tracts (>80% Black)
5. **Hispanic Tract 50%** - Loans in majority-Hispanic tracts (>50% Hispanic)
6. **Hispanic Tract 80%** - Loans in supermajority-Hispanic tracts (>80% Hispanic)
7. **Black+Hispanic Tract 50%** - Loans in majority Black+Hispanic tracts (>50% combined)
8. **Black+Hispanic Tract 80%** - Loans in supermajority Black+Hispanic tracts (>80% combined)

### Bank Selection Criteria

**Inclusion Requirements:**
- Asset size: $10 billion to $100 billion (from lenders18 table)
- Volume: ≥500 applications in CBSA across 2018-2024 period
- Type: Appropriate type_name (from lenders18 table)
- Geographic scope: Must operate in one of top 200 CBSAs

**Selection Filters:**
1. **Consistency**: Bad in ≥50% of CBSAs where bank operates
2. **Non-Improvement**: Must have ratios ≥ 2.0 in 2023-2024 (recent years)
3. **Scoring**: Weighted by:
   - CBSA size (total applications)
   - Number of metrics affected

**Force Included Banks:**
- 1st National Bank of Pennsylvania
- Webster Bank
- Frost Bank

**Excluded Banks (CBA Signatories):**
- UMB Bank, Atlantic Union Bank, SouthState Bank, BMO Harris Bank
- Umpqua, US Bank, Old National Bancorp, Flagstar Bank
- M&T Bank, PNC Bank, First Citizens Bank, CIT Group
- Morgan Stanley, First Merchants Bank, Truist, Cadence Bank
- Wells Fargo, First Horizon Bank, IBERIABANK, Santander Bank
- First Financial Bank, Fifth Third Bank, Huntington Bancshares, KeyBank

## Usage

### Step 1: Run SQL Query in BigQuery

1. Open BigQuery console
2. Load `queries/worst_lenders_redlining_query.sql`
3. Execute query
4. Export results to CSV (this may take several hours for full dataset)

### Step 2: Run Python Analysis

```bash
python scripts/worst_lenders_analysis.py --input data/raw/worst_lenders_data.csv --output Worst_Lenders_Analysis.xlsx
```

### Step 3: Review Excel Output

The Excel file contains:
- **Ratio Sheets** (one per bank): Shows peer/subject ratios by year
  - Values < 1.0: Green (bank outperforms peers)
  - Values 1.0-1.5: Yellow
  - Values 1.5-2.0: Orange
  - Values 2.0-3.0: Light Red (significant underperformance)
  - Values ≥ 3.0: Red (severe underperformance)

- **Shares/Gaps Sheets** (one per bank): Shows counts, shares, and gaps
  - Subject Count: Number of loans from subject bank
  - Subject Share: Percentage for subject bank
  - Peer Share: Percentage for peer banks
  - Gap: Percentage points difference (negative = underperformance)
  - Asterisk (*): Indicates statistically significant negative gap (chi-squared, p < 0.05)

Each sheet includes:
- County-level breakdown (within CBSAs)
- `Kind` column: 'Application' or 'Origination' (filterable)
- `Loan_Purpose` column: 'All Loans' or 'Home Purchase' (filterable)
- Years 2018-2024 as columns

## Output Structure

### Sheet Names
- `{BankName}_Ratios` - Ratio analysis
- `{BankName}_SharesGaps` - Detailed shares and gaps

### Columns
- **Identifier Columns**: CBSA_Code, CBSA_Name, County_Code, Loan_Purpose, Kind, Metric
- **Year Columns**: 2018, 2019, 2020, 2021, 2022, 2023, 2024
  - For Ratio sheets: Just the ratio value
  - For Shares/Gaps sheets: Subject_Count, Subject_Share, Peer_Share, Gap

## Interpretation

### Ratio Sheets
- Focus on ratios ≥ 2.0 (red/orange cells)
- Ratios ≥ 2.0 indicate subject bank has at least 50% deficit compared to peers
- Consistent patterns across years and CBSAs are most concerning

### Shares/Gaps Sheets
- Focus on negative gaps marked with asterisk (*)
- Significant negative gaps indicate statistical evidence of underperformance
- Use county-level data to identify specific geographic problems
- Filter by `Kind` to see applications vs. originations separately
- Filter by `Loan_Purpose` to see all loans vs. home purchase separately

## Technical Details

### Statistical Testing
- Uses chi-squared test (not z-test)
- Tests for significant difference between subject and peer proportions
- Only flags negative gaps as significant (subject underperforming peers)
- Significance threshold: p < 0.05

### Peer Matching
- Peers defined as lenders with 50%-200% of subject's volume
- Calculated separately for each:
  - Year (2018-2024)
  - CBSA
  - County
  - Loan purpose category (All Loans vs. Home Purchase)
  - Kind (Application vs. Origination)

### Scoring Methodology
1. Count all ratios ≥ 2.0 across all combinations
2. Weight each bad ratio by:
   - CBSA size (normalized by millions of applications)
   - Number of metrics affected (equal weight per metric)
3. Filter for consistency: Bad in ≥50% of CBSAs
4. Filter for non-improvement: Bad ratios in 2023-2024
5. Rank by weighted score
6. Select top 15 (ensuring force-included banks are included)

## Limitations

- Does not account for business model differences
- Geographic selection biased toward high-volume markets
- Peer matching based solely on application volume
- County-level data may have small sample sizes in some cases
- Correlation does not imply causation
- Does not assess individual loan applications for discrimination

## Contact

For questions about methodology or results:
NCRC Research Department
National Community Reinvestment Coalition
research@ncrc.org



