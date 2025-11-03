# How to Run Fifth Third Redlining Report

## Quick Start

I've created SQL files for you to run in BigQuery. Here's what to do:

### Option 1: Use Python Script (If terminal works)

```bash
python generate_fifth_third_report.py
```

### Option 2: Run Queries Manually in BigQuery (Recommended)

#### Step 1: Find Top 10 CBSAs

1. Open BigQuery console: https://console.cloud.google.com/bigquery
2. Create new query
3. Paste contents of `fifth_third_top_cbsas.sql`
4. Run query
5. **Copy the 10 CBSA codes** from results

#### Step 2: Run Main Query

1. Create new query
2. Paste contents of `fifth_third_tract_demographics_query.sql`
3. **Update the CBSA list** in the query:
   - Find: `AND cbsa_code IN ('{cbsa_str}')`
   - Replace with your 10 CBSA codes, e.g.: `AND cbsa_code IN ('16980', '19100', '26420', ...)`
4. Run query (may take 10-30 minutes)
5. Export results to CSV: `fifth_third_redlining_report.csv`

#### Step 3: Generate Excel Report

```bash
python ncrc_worst_lenders_analysis_v4.py fifth_third_redlining_report.csv
```

### Option 3: I Can Generate the Full Query for You

Just tell me the 10 CBSAs and I'll create the complete query file ready to run!

## What You'll Get

**CSV Output with columns**:
- `activity_year` (2018-2024)
- `cbsa_code`
- `lender_name`: "Fifth Third Bank"
- `loan_purpose_category`: "Home Purchase"
- Subject bank originations for each metric
- Peer bank originations for each metric

**Metrics**:
- `subject_mmct_50_originations`, `peer_mmct_50_originations`
- `subject_mmct_80_originations`, `peer_mmct_80_originations`
- `subject_black_tract_50_originations`, `peer_black_tract_50_originations`
- `subject_black_tract_80_originations`, `peer_black_tract_80_originations`
- `subject_hispanic_tract_50_originations`, `peer_hispanic_tract_50_originations`
- `subject_hispanic_tract_80_originations`, `peer_hispanic_tract_80_originations`
- `subject_black_hispanic_tract_50_originations`, `peer_black_hispanic_tract_50_originations`
- `subject_black_hispanic_tract_80_originations`, `peer_black_hispanic_tract_80_originations`

**Excel Report**:
- Years as columns (2018-2024)
- Metrics as rows
- Conditional formatting (red/yellow/green)
- Statistical significance indicators
- Separate sheets for ratios and raw data

## Need Help?

Just tell me:
1. "Run the top CBSAs query" - I'll execute it
2. "Generate full query for CBSAs X, Y, Z..." - I'll create complete SQL
3. "Generate Excel report" - I'll run the generator

Let me know what you'd like to do!


