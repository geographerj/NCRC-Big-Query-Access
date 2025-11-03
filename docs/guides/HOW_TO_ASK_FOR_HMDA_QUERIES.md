# How to Ask for HMDA Queries

Yes! You can absolutely come back here and ask me to run HMDA queries. I'll remember all the context about your project and data structure.

## What I Already Know

✅ **Your BigQuery Structure**:
- HMDA Table: `hdma1-242116.hmda.hmda`
- Geo Table: `hdma1-242116.geo.black_hispanic_majority`
- Crosswalks: CBSA to County, Lender Names

✅ **Your Standard Filters**:
- Owner-occupied (`occupancy_type = '1'`)
- Site-built 1-4 unit properties (`construction_method = '1'`, `total_units IN (1,2,3,4)`)
- Exclude reverse mortgages (`reverse_mortgage != '1'`)
- Originations only (`action_taken = '1'`)

✅ **Your Analysis Focus**:
- Fifth Third Bank (LEI: `QFROUN1UWUYU0DVIWD51`)
- Tract-level demographics from geo table
- Years 2018-2024
- Peer bank comparisons

✅ **HMDA Field Names** (from [FFIEC documentation](https://ffiec.cfpb.gov/documentation/publications/loan-level-datasets/lar-data-fields)):
- `activity_year`, `lei`, `cbsa_code`, `census_tract`
- `action_taken`, `loan_purpose`, `occupancy_type`
- `reverse_mortgage`, `construction_method`, `total_units`
- `tract_minority_population_percent`
- And all race/ethnicity fields

## How to Request a Query

### Simple Request
Just tell me what you want to analyze:

**Examples**:
- "Run a query for Fifth Third Bank loans in Chicago (CBSA 16980) in 2024"
- "Show me lending by tract demographics for the top 10 CBSAs"
- "Compare originations to Black borrowers in 2023 vs 2024"
- "Find all loans in majority Black tracts (>80%) by CBSA"

### I'll Ask If I Need
I'll ask clarifying questions if needed:
- **Geographic scope**: Which CBSAs? All or specific ones?
- **Time period**: Which years? Single year or multi-year?
- **Lenders**: Fifth Third only? Include peers? All lenders?
- **Loan types**: Home purchase? All purposes? Refinancing?
- **Filters**: Apply standard filters? Any additional filters?
- **Output format**: SQL query? CSV export? Direct analysis?

## Example Workflow

**You**: "I need to see Fifth Third's lending in majority minority tracts for 2024"

**Me**: I'll ask:
1. Which CBSAs? (Top 10? All? Specific ones?)
2. Standard filters? (Owner-occupied, site-built, etc.)
3. Threshold? (50% minority? 80%?)
4. Output format? (Query file? Run it? CSV export?)

**Then**: I'll generate the SQL and either:
- Save it as a file for you to run
- Run it directly and export CSV
- Analyze results immediately

## Ready to Use

Come back anytime and ask:

- "Create a query for [analysis description]"
- "Show me [metrics] for [geography] in [year]"
- "Compare [subject] to [peer] for [metric]"
- "Run [existing query] and export to CSV"
- "Generate Excel report for [bank] in [year]"

I have everything I need to help you quickly!


