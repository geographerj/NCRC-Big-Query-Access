# Branch Matching Workflow

## Overview

Since HMDA and SOD (Summary of Deposits) don't have a reliable join column, we must match bank names manually with your verification.

## Key Constraints

1. **No reliable join**: RSSD exists in SOD but NOT in HMDA
2. **Name differences**: "Wells Fargo" in HMDA ≠ "Wells Fargo Bank" in SOD
3. **Manual verification required**: Always ask you to confirm matches
4. **Table overlap**: `sod`, `sod25`, `sod_legacy` overlap - avoid double counting
5. **Deduplication**: Use `uninumbr` + `year` (unique per branch per year)

## Step-by-Step Workflow

### Step 1: Identify Which SOD Table to Use

First, determine which table has the years you need:

```sql
-- Check year ranges in each table
SELECT 'sod' as table_name, MIN(year) as min_year, MAX(year) as max_year
FROM `hdma1-242116.branches.sod`
UNION ALL
SELECT 'sod25', MIN(year), MAX(year)
FROM `hdma1-242116.branches.sod25`
UNION ALL
SELECT 'sod_legacy', MIN(year), MAX(year)
FROM `hdma1-242116.branches.sod_legacy`
```

**You mentioned needing 2017-2025 data** - verify which table has this range!

### Step 2: Run Bank Name Matching Tool

```bash
python scripts/verify_bank_name_matches.py
```

This will:
1. Get unique bank names from HMDA (top N by volume)
2. Get unique bank names from SOD
3. Find potential matches using fuzzy matching
4. Create an Excel file for you to verify matches

### Step 3: Verify Matches Manually

1. Open the Excel file: `data/reference/bank_name_matches_to_verify_2024.xlsx`
2. Review each potential match
3. Mark `is_match` column:
   - **Y/Yes/True/1** if same bank
   - **N/No/False/0** if different banks
4. Add notes if needed
5. Save the file

**Example:**
- "Wells Fargo" (HMDA) vs "Wells Fargo Bank" (SOD) → **Y** (same bank)
- "Wells Fargo" (HMDA) vs "Wells Fargo Mortgage" (SOD) → **N** (different entity)

### Step 4: Save Verified Matches

Once you've verified matches, the script will save them to:
- `data/reference/bank_name_matches_verified.csv`

This crosswalk can be reused for future analyses.

### Step 5: Use Verified Matches in Queries

When querying branch data, use the verified SOD name:

```python
from Lending and Branch Analysis.utils.branch_matching import load_verified_matches

# Load verified matches
matches = load_verified_matches('data/reference/bank_name_matches_verified.csv')

# HMDA name: "Wells Fargo"
# Verified SOD name: "Wells Fargo Bank"
hmda_name = "Wells Fargo"
sod_name = matches.get(hmda_name, hmda_name)  # Falls back to HMDA name if not found

# Query branches using verified SOD name
query = branch_queries.get_lender_branches(
    lender_name=sod_name,
    year=2024,
    sod_table='sod25'  # Use table with your year range
)
```

### Step 6: Always Deduplicate if Using Multiple Tables

If you combine data from multiple SOD tables:

```python
from Lending and Branch Analysis.utils.branch_matching import deduplicate_branches

# Query from multiple tables
df1 = query_sod_table('sod', year=2024)
df2 = query_sod_table('sod25', year=2024)

# Combine
combined = pd.concat([df1, df2])

# Deduplicate using uninumbr + year
deduplicated = deduplicate_branches(combined, year_col='year', unique_col='uninumbr')
```

## Example: Matching Fifth Third Bank

**HMDA name**: "Fifth Third Bank"  
**SOD name**: ??? (need to verify)

**Steps:**
1. Run matching tool
2. Look for potential match like:
   - "Fifth Third Bank" (HMDA) vs "Fifth Third Bank, National Association" (SOD)
3. Verify: Yes, same bank
4. Use "Fifth Third Bank, National Association" when querying SOD

## Best Practices

1. **Always verify matches** - Don't assume fuzzy matching is correct
2. **Use uninumbr for deduplication** - Critical when combining tables
3. **Specify SOD table** - Don't rely on defaults, explicitly choose
4. **Save verified matches** - Build a reusable crosswalk
5. **Check for name variations** - Same bank may have different names in different years

## Questions to Ask Before Each Analysis

1. Which SOD table has the year range I need?
2. What is the exact SOD name for this bank? (verify with crosswalk)
3. Am I using multiple SOD tables? (if yes, deduplicate!)
4. Have I verified this match before? (check crosswalk)

## Troubleshooting

**Problem**: "No branches found for bank X"
- **Solution**: Check if SOD name matches exactly. Try variations.

**Problem**: "Too many branches returned"
- **Solution**: Verify you're not matching the wrong bank. Check name carefully.

**Problem**: "Duplicate branches"
- **Solution**: Use `deduplicate_branches()` function with `uninumbr` + `year`

**Problem**: "Wrong year range"
- **Solution**: Verify which SOD table has your years. Query min/max years first.

