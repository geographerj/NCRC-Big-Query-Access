# Find SOD Name Matches - Simple Instructions

## Quick Method: Run SQL in BigQuery

Open BigQuery and run the queries in `queries/find_sod_matches_simple.sql`

This will show you:
- All SOD names containing "FIFTH THIRD"
- All SOD names containing "COMERICA"  
- From both `sod` and `sod25` tables
- Branch counts and deposit totals

## What to Look For

### Fifth Third Bank
HMDA Name: `Fifth Third Bank`

**Likely SOD names** (most common patterns):
- `Fifth Third Bank, National Association`
- `Fifth Third Bank National Association`  
- `Fifth Third Bank N.A.`
- `Fifth Third Bank`

Look for the entry with the **most branches** - that's usually the main bank entity.

### Comerica Bank
HMDA Name: `Comerica Bank`

**Likely SOD names**:
- `Comerica Bank` (often matches exactly)
- `Comerica Bank, National Association`
- `Comerica National Bank`

Look for the entry with the **most branches**.

## After You Find the Names

Once you run the queries and see the results, tell me:

1. **Fifth Third SOD name**: `?`
2. **Comerica SOD name**: `?`
3. **Which SOD table** has your data: `sod` or `sod25`?

Then I'll update the merger analysis script and you can run the full analysis!

