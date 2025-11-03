# SOD Name Matches - Please Verify

## Instructions

Run the SQL query in BigQuery (`queries/find_sod_name_matches.sql`) OR use the Python script to find potential matches, then tell me which names are correct.

## Expected Matches

Based on common patterns, here are my **educated guesses** for the SOD names:

### Fifth Third Bank
**HMDA Name**: `Fifth Third Bank`

**Possible SOD Names** (most likely):
1. `Fifth Third Bank, National Association` ← **Most likely**
2. `Fifth Third Bank National Association`
3. `Fifth Third Bank N.A.`
4. `Fifth Third Bank`

**Common pattern**: Banks often have ", National Association" or "National Association" suffix in SOD.

### Comerica Bank
**HMDA Name**: `Comerica Bank`

**Possible SOD Names** (most likely):
1. `Comerica Bank` ← **Most likely (same as HMDA)**
2. `Comerica Bank, National Association`
3. `Comerica National Bank`
4. `Comerica`

**Common pattern**: Sometimes SOD name matches HMDA exactly.

## How to Find the Exact Names

### Option 1: Run SQL in BigQuery (Easiest)

Open `queries/find_sod_name_matches.sql` and run all 4 queries. This will show you:
- All SOD names containing "Fifth Third"
- All SOD names containing "Comerica"
- From both `sod` and `sod25` tables

### Option 2: Use Python Script

```bash
python scripts/show_sod_matches.py
```

## What to Confirm

Once you see the results, please tell me:

1. **Fifth Third Bank SOD name**: `?`
2. **Comerica Bank SOD name**: `?`
3. **Which SOD table** has 2017-2025 data: `?` (sod, sod25, or sod_legacy)

## After Confirmation

Once you confirm the names, I'll update the merger analysis script with the correct SOD names and you can run the full analysis!

