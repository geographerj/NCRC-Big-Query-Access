# Implementation Summary: Tract Demographic Metrics for Fifth Third Bank CBA Analysis

## User Request Summary

The user wants to add **8 tract-level demographic metrics** to the CBA analysis for Fifth Third Bank. These metrics analyze loans by the **demographic composition of the census tracts** where properties are located, using 50% and 80% thresholds.

### Metrics to Add

1. Majority Minority 50% (MMCT 50%)
2. Majority Minority 80% (MMCT 80%)  
3. Majority Black 50%
4. Majority Black 80%
5. Majority Hispanic 50%
6. Majority Hispanic 80%
7. Majority Black and Hispanic Combined 50%
8. Majority Black and Hispanic Combined 80%

## Current State

✅ **Excel Generator**: `ncrc_worst_lenders_analysis_v4.py` is complete and working
- Processes CSV input with subject/peer originations for each metric
- Generates ratio sheets with conditional formatting
- Handles two-proportion z-tests for statistical significance

✅ **Standard Filters**: Defined in `hmda_codes.py`
- Owner-occupied, site-built 1-4 unit
- Exclude reverse mortgages

❌ **Missing**: BigQuery SQL query to generate input CSV with new tract demographics
❌ **Missing**: Verification that `geo` dataset tables exist in BigQuery

## Next Steps

### Step 1: Verify Geo Dataset (User Required)

The user must verify if BigQuery has the `geo` dataset with tract demographics:

```python
# Run this to check available datasets/tables
from utils import create_client

client = create_client()
datasets = list(client.list_datasets())

for dataset in datasets:
    if 'geo' in dataset.dataset_id.lower():
        print(f"Found dataset: {dataset.dataset_id}")
        tables = list(client.list_tables(dataset.reference))
        for table in tables:
            if 'majority' in table.table_id.lower() or 'demographic' in table.table_id.lower():
                print(f"  Table: {table.table_id}")
```

**Expected Tables**:
- `hdma1-242116.geo.black_hispanic_majority` OR
- `hdma1-242116.geo.tract_demographics` OR
- Similar table with tract-level demographic percentages

### Step 2: Update Excel Generator (Completed Conceptually)

Once we have the column names from the SQL query, we need to:

1. **Add metrics to METRICS dictionary** (line 40-52):
```python
METRICS = {
    'lmict': 'LMICT%',
    'lmib': 'LMIB%', 
    'lmib_amount': 'LMIB$',
    'mmct': 'MMCT%',
    # NEW METRICS:
    'mmct_50': 'MMCT 50%',
    'mmct_80': 'MMCT 80%',
    'black_tract_50': 'Black Tract 50%',
    'black_tract_80': 'Black Tract 80%',
    'hispanic_tract_50': 'Hispanic Tract 50%',
    'hispanic_tract_80': 'Hispanic Tract 80%',
    'black_hispanic_tract_50': 'Black+Hispanic Tract 50%',
    'black_hispanic_tract_80': 'Black+Hispanic Tract 80%',
    # Borrower demographics:
    'hispanic': 'Hispanic%',
    'black': 'Black%',
    'asian': 'Asian%',
    'native_american': 'Native American%',
    'hopi': 'HoPI%',
    'minb': 'MINB%'
}
```

2. **Calculate metrics function already handles it** - no changes needed
   - The `calculate_metrics()` function dynamically looks for `subject_{metric}_originations` and `peer_{metric}_originations` columns
   - If columns exist, it calculates shares and gaps automatically

3. **Conditional formatting already handles it** - no changes needed
   - Excel color coding already works for all metrics

### Step 3: Create BigQuery SQL Query (Pending)

This is the main missing piece. We need SQL that:

1. **Joins HMDA with tract demographics**:
```sql
FROM `hdma1-242116.hmda.hmda` h
LEFT JOIN `hdma1-242116.geo.[TBD]` g
    ON h.census_tract = g.census_tract
```

2. **Applies standard filters**:
```sql
WHERE h.action_taken = '1'  -- Originations only
  AND h.loan_purpose IN ('1', '2', '31', '32')  -- All residential
  AND h.occupancy_type = '1'  -- Owner-occupied  
  AND h.reverse_mortgage != '1'  -- Not reverse mortgage
  -- Site-built 1-4 unit property type (check exact field name)
```

3. **Counts loans by tract demographics**:
```sql
COUNTIF(g.minority_pct > 50) as mmct_50_originations,
COUNTIF(g.minority_pct > 80) as mmct_80_originations,
COUNTIF(g.black_pct > 50) as black_tract_50_originations,
COUNTIF(g.black_pct > 80) as black_tract_80_originations,
COUNTIF(g.hispanic_pct > 50) as hispanic_tract_50_originations,
COUNTIF(g.hispanic_pct > 80) as hispanic_tract_80_originations,
COUNTIF((g.black_pct + g.hispanic_pct) > 50) as black_hispanic_tract_50_originations,
COUNTIF((g.black_pct + g.hispanic_pct) > 80) as black_hispanic_tract_80_originations,
```

4. **Aggregates by Subject Bank vs Peers**:
   - Similar to existing CBA analysis SQL
   - Subject bank: Fifth Third Bank specific LEI(s)
   - Peer banks: All other lenders in same CBSA with 50%-200% volume

### Step 4: Verify HMDA Field Names (Pending)

Need to confirm exact field names in HMDA table:
- **Census Tract**: `census_tract` ✅ (confirmed in existing queries)
- **Occupancy Type**: `occupancy_type` ❓ (needs verification)
- **Reverse Mortgage**: `reverse_mortgage` ❓ (needs verification)
- **Property Type**: `property_type` or `construction_method` ❓ (needs verification)

## Files Created/Modified

### New Files
1. ✅ `TRACT_DEMOGRAPHIC_METRICS_REQUIREMENTS.md` - Detailed requirements document
2. ✅ `IMPLEMENTATION_SUMMARY.md` - This file

### Files to Modify
1. ⏳ `ncrc_worst_lenders_analysis_v4.py` - Add 8 new metrics to METRICS dict
2. ⏳ Create new BigQuery SQL file - `fifth_third_tract_demographics.sql` or similar
3. ⏳ Create Fifth Third analysis script - `fifth_third_cba_analysis.py`

### Files Already Created (Previous Session)
1. ✅ `Lending and Branch Analysis/utils/hmda_codes.py` - Standard filter definitions
2. ✅ `Lending and Branch Analysis/utils/hmda_crosswalks.py` - Crosswalk utilities
3. ✅ `Lending and Branch Analysis/utils/hmda_demographics.py` - Borrower demographics
4. ✅ `Lending and Branch Analysis/examples/test_fifth_third.py` - Test script

## Action Items

### User Must Do:
1. ✅ Verify `geo` dataset exists in BigQuery
2. ✅ Check table name and schema for tract demographics
3. ✅ Confirm HMDA field names for standard filters

### AI Must Do (After User Provides Info):
1. ⏳ Write BigQuery SQL query joining HMDA with tract demographics
2. ⏳ Update METRICS dictionary in Excel generator
3. ⏳ Create Fifth Third analysis script
4. ⏳ Test with sample data
5. ⏳ Generate full report

## Key Assumptions

1. **Geo Dataset**: `hdma1-242116.geo.*` exists with tract demographics
2. **Field Names**: Either we'll find the table schema, or user will provide it
3. **HMD A Fields**: Field names match standard HMDA schema (occupancy_type, reverse_mortgage, etc.)
4. **Tract Code Format**: 11-digit census tract codes match between HMDA and geo data

## Testing Approach

1. **Small Sample First**: Query just 2024 data for one CBSA
2. **Verify Joins**: Check that tract demographic percentages are populated
3. **Check Filters**: Confirm standard filters are working correctly
4. **Validate Excel**: Run Excel generator on small CSV to ensure new metrics render
5. **Full Query**: Once verified, run full query for all years 2018-2024

## Questions for User

1. **Geo Dataset Location**: Can you check what tables exist in the `geo` dataset? 
2. **Table Schema**: What are the column names in the tract demographics table?
3. **HMDA Fields**: Do you have access to HMDA field documentation for occupancy_type, property_type, reverse_mortgage fields?
4. **Fifth Third LEI**: What is Fifth Third Bank's LEI (Legal Entity Identifier)?

