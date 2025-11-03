# Branch-HMDA Joining Guide: Using GEOID

## Key Discovery: GEOID Enables Tract-Level Joining!

**GEOID in SOD** = **census_tract in HMDA**

This means we can join branch data with lending data at the tract level!

## Important Fields in SOD

### GEOID
- **What it is**: Unique tract identifier (11-digit code)
- **Matches to**: HMDA `census_tract` field
- **Use**: Join branch locations with lending patterns at tract level
- **Format**: Typically integer-like string (e.g., "01001000100")

### br_lmi (Branch LMI Flag)
- **What it is**: Indicator that branch is in Low-to-Moderate Income census tract
- **Values**: 
  - `1` = Branch IS in LMI tract
  - `0` = Branch is NOT in LMI tract
- **Use**: Filter branches by income demographics

### cr_minority (Census Tract Minority Flag)
- **What it is**: Indicator that branch is in majority minority census tract
- **Values**:
  - `1` = Branch IS in majority minority tract
  - `0` = Branch is NOT in majority minority tract
- **Use**: Filter branches by racial/ethnic demographics

## How to Join Branch and HMDA Data

### Step 1: Query Branch Data with GEOID

```python
from Lending and Branch Analysis.queries import branch_queries

query = branch_queries.get_branches_by_cbsa(
    cbsa_code='16980',  # Chicago
    year=2024,
    sod_table='sod25'  # Use table with your year range
)

# This query now includes:
# - geoid (for joining!)
# - br_lmi (LMI tract flag)
# - cr_minority (minority tract flag)
```

### Step 2: Query HMDA Data with census_tract

```python
from Lending and Branch Analysis.queries import hmda_queries

hmda_query = f"""
SELECT 
    lei,
    census_tract,  -- This matches GEOID!
    cbsa_code,
    activity_year,
    COUNTIF(action_taken = '1') as originations,
    SUM(CASE WHEN action_taken = '1' THEN loan_amount END) as total_loan_amount
FROM `hdma1-242116.hmda.hmda`
WHERE activity_year = 2024
  AND cbsa_code = '16980'
  AND lei = 'YOUR_LEI'
GROUP BY lei, census_tract, cbsa_code, activity_year
"""
```

### Step 3: Join Using GEOID = census_tract

```python
from Lending and Branch Analysis.utils.branch_hmda_join import join_branches_with_hmda

# Load your data
branches_df = client.execute_query(branch_query)
hmda_df = client.execute_query(hmda_query)

# Join them!
joined = join_branches_with_hmda(branches_df, hmda_df, how='left')
```

## Key Analyses Enabled by GEOID Join

### 1. Branch-Lending Alignment by Tract

**Question**: "Does the bank have branches in tracts where it makes loans?"

```python
from Lending and Branch Analysis.utils.branch_hmda_join import analyze_branch_lending_alignment

alignment = analyze_branch_lending_alignment(
    branches_df,
    hmda_df,
    lender_name="Wells Fargo"  # Verify SOD name!
)

# Results show:
# - Tracts with branches AND lending ✅
# - Tracts with branches but NO lending 🚩 (red flag!)
# - Tracts with lending but NO branches
# - Tracts with neither
```

### 2. Branch Presence in LMI/Minority Tracts

**Question**: "Are branches located in LMI and minority communities?"

```python
from Lending and Branch Analysis.queries import branch_queries

query = branch_queries.get_branch_presence_in_lmi_minority_tracts(
    lender_name="Fifth Third Bank",  # Verify SOD name!
    year=2024,
    sod_table='sod25'
)

# Returns summary:
# - Total branches
# - Branches in LMI tracts (count and %)
# - Branches in minority tracts (count and %)
# - Branches in LMI AND minority tracts (count and %)
```

### 3. Branch Closures in Vulnerable Communities

**Question**: "Are branches closing in LMI or minority tracts?"

```python
from Lending and Branch Analysis.utils.branch_hmda_join import get_branch_closures_in_lmi_minority_tracts

# Get branches for two time periods
branches_2023 = query_branches(year=2023)
branches_2024 = query_branches(year=2024)

# Find closures
closures = get_branch_closures_in_lmi_minority_tracts(
    branches_prev=branches_2023,
    branches_current=branches_2024
)

# Results show:
# - Closed branches in LMI tracts
# - Closed branches in minority tracts
# - Closed branches in LMI AND minority tracts (worst case!)
```

### 4. Branch Distribution by CBSA and Demographics

**Question**: "How are branches distributed across CBSAs and demographic types?"

```python
from Lending and Branch Analysis.queries import branch_queries

query = branch_queries.get_branches_by_cbsa_with_demographics(
    lender_name="Fifth Third",  # Verify SOD name!
    year=2024,
    sod_table='sod25'
)

# Returns by CBSA:
# - Total branches
# - Branches in LMI tracts
# - Branches in minority tracts
# - Branches in LMI+minority tracts
# - Total deposits
```

## Example: Complete Workflow

### Analyzing Branch-Lending Relationship for Fifth Third

```python
# 1. Get verified SOD name for Fifth Third
# (Run verify_bank_name_matches.py first!)
verified_sod_name = "Fifth Third Bank, National Association"  # Example

# 2. Query branches with GEOID
branch_query = branch_queries.get_lender_branches(
    lender_name=verified_sod_name,
    year=2024,
    sod_table='sod25'
)
branches = client.execute_query(branch_query)

# 3. Query HMDA lending for Fifth Third
hmda_query = f"""
SELECT 
    census_tract,
    cbsa_code,
    COUNTIF(action_taken = '1') as originations,
    SUM(CASE WHEN action_taken = '1' THEN loan_amount END) as loan_volume
FROM `hdma1-242116.hmda.hmda`
WHERE activity_year = 2024
  AND lei = 'QFROUN1UWUYU0DVIWD51'  -- Fifth Third LEI
  AND action_taken = '1'
GROUP BY census_tract, cbsa_code
"""
lending = client.execute_query(hmda_query)

# 4. Join by GEOID
joined = join_branches_with_hmda(branches, lending, how='outer')

# 5. Analyze
# Tracts with branches but no lending
no_lending = joined[
    (joined['uninumbr'].notna()) & 
    (joined['originations'].isna() | (joined['originations'] == 0))
]

# Tracts with lending but no branches
no_branches = joined[
    (joined['originations'].notna() & (joined['originations'] > 0)) &
    (joined['uninumbr'].isna())
]

# Tracts with both
both = joined[
    (joined['uninumbr'].notna()) &
    (joined['originations'].notna() & (joined['originations'] > 0))
]
```

## Adding to Reports

### For Fifth Third Report

You could add a new sheet or section showing:

1. **Branch-Lending Alignment by CBSA**
   - Tracts with branches + lending
   - Tracts with branches but no lending (red flag)
   - Branch count in LMI tracts
   - Branch count in minority tracts

2. **Branch Closures**
   - Closures by year
   - Closures in LMI tracts
   - Closures in minority tracts

3. **Branch Distribution**
   - Total branches per CBSA
   - % of branches in LMI tracts
   - % of branches in minority tracts
   - Compare subject bank to peers

## Important Notes

1. **Verify bank names** before matching (use verification tool)
2. **Use uninumbr for deduplication** if combining multiple SOD tables
3. **GEOID format**: May need standardization (remove decimals, pad zeros)
4. **Tract matching**: Ensure GEOID format matches HMDA census_tract format
5. **Multiple years**: Join by GEOID + year for time-series analysis

## Next Steps

1. **Test GEOID matching**: Verify GEOID format matches HMDA census_tract
2. **Create branch-lending alignment analysis**: Add to Fifth Third report
3. **Build branch closure tracking**: Monitor closures in vulnerable communities
4. **Add branch metrics to reports**: Include branch presence in Excel outputs

