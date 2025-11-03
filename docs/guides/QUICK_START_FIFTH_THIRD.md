# Quick Start: Fifth Third Redlining Report

## Current Issue
PowerShell terminal has an issue that prevents running Python scripts. But we have all the SQL files ready!

## What You Need to Do

### Step 1: Get Top 10 CBSAs
**Copy and run this in BigQuery Console** (`fifth_third_top_cbsas.sql`):

```sql
SELECT 
    cbsa_code,
    COUNTIF(action_taken = '1') as total_originations
FROM `hdma1-242116.hmda.hmda`
WHERE lei = 'QFROUN1UWUYU0DVIWD51'
  AND activity_year BETWEEN 2018 AND 2024
  AND loan_purpose = '1'
  AND action_taken = '1'
  AND cbsa_code IS NOT NULL
  AND cbsa_code != ''
  AND occupancy_type = '1'
  AND reverse_mortgage != '1'
  AND construction_method = '1'
  AND total_units IN ('1', '2', '3', '4')
GROUP BY cbsa_code
ORDER BY total_originations DESC
LIMIT 10;
```

**Copy the 10 CBSA codes** from the results.

### Step 2: Run Main Query
Once you have the CBSA codes, I need you to paste them here so I can update the main query file with the exact codes and give you the complete ready-to-run SQL!

**OR** tell me the CBSA codes and I'll create the complete query for you right now.

## What I Need From You

**Option 1**: Run the query above and give me the 10 CBSA codes
**Option 2**: Tell me if you already know the top CBSAs for Fifth Third

Then I'll generate the complete query ready to run!


