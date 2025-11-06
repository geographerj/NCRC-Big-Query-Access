# Wells Fargo HMDA Records by Year

## Overview
This analysis queries the HMDA (Home Mortgage Disclosure Act) dataset to count the number of records from Wells Fargo for each year.

## Wells Fargo Information
- **Institution**: Wells Fargo Bank, N.A.
- **LEI (Legal Entity Identifier)**: KB1H1DSPRFMYMCUFXT09

## Files Included
All files should be located in the root directory: `c:/dream`

1. **`c:/dream/wells_fargo_hmda_query.sql`** - SQL query to run directly in BigQuery
2. **`c:/dream/wells_fargo_hmda_by_year.py`** - Python script to run the query programmatically

## Option 1: Run Query in BigQuery Console (Easiest)

1. Go to [BigQuery Console](https://console.cloud.google.com/bigquery)
2. Select project: `hdma1-242116`
3. Click "Compose New Query"
4. Copy the contents of `c:/dream/wells_fargo_hmda_query.sql` into the editor
5. Click "Run"
6. Export results:
   - Click "Save Results" → "CSV (local file)"
   - Save as `c:/dream/wells_fargo_hmda_by_year.csv`

## Option 2: Run Python Script

### Prerequisites
1. Service account key file: `c:/dream/hdma1-242116-74024e2eb88f.json` (must be in the root directory)
2. Python packages installed:
   ```bash
   cd c:/dream
   pip install -r requirements.txt
   ```

### Run the Script
```bash
cd c:/dream
python wells_fargo_hmda_by_year.py
```

This will:
- Connect to BigQuery
- Execute the query
- Display results in console
- Save results to `c:/dream/wells_fargo_hmda_by_year.csv`

## Query Details

The query returns the following information for each year:

| Column | Description |
|--------|-------------|
| `activity_year` | Year of the HMDA record |
| `total_records` | Total number of HMDA records from Wells Fargo |
| `originations` | Number of loans originated (action_taken = '1') |
| `denials` | Number of loan applications denied (action_taken = '3') |
| `states_with_activity` | Number of distinct states with Wells Fargo HMDA activity |
| `tracts_with_activity` | Number of distinct census tracts with Wells Fargo HMDA activity |
| `total_originated_amount` | Total dollar amount of originated loans |

## Expected Results

The query will return one row per year that Wells Fargo has HMDA records in the dataset. Typical years include:
- 2018-2024 (modern HMDA data)
- Potentially older years if historical data is included

## Troubleshooting

### Authentication Issues
If you get authentication errors:
1. Make sure `c:/dream/hdma1-242116-74024e2eb88f.json` is in the root directory
2. Or run the query directly in BigQuery Console instead
3. Or set up Application Default Credentials:
   ```bash
   gcloud auth application-default login
   ```

### LEI Not Found
If the query returns no results:
- Wells Fargo may use multiple LEIs for different entities
- Check the HMDA dataset for other Wells Fargo LEIs using the lenders18 table:
  ```sql
  SELECT *
  FROM `hdma1-242116.hmda.lenders18`
  WHERE LOWER(respondent_name) LIKE '%wells%fargo%'
     OR LOWER(respondent_name) LIKE '%wellsfargo%'
  ```

## Additional Analysis Ideas

### 1. Get All Wells Fargo Entities
```sql
SELECT *
FROM `hdma1-242116.hmda.lenders18`
WHERE LOWER(respondent_name) LIKE '%wells%fargo%'
   OR LOWER(respondent_name) LIKE '%wellsfargo%'
```

### 2. Analyze by State
```sql
SELECT 
    activity_year,
    state_code,
    COUNT(*) as total_records
FROM `hdma1-242116.hmda.hmda`
WHERE lei = 'KB1H1DSPRFMYMCUFXT09'
GROUP BY activity_year, state_code
ORDER BY activity_year, state_code;
```

### 3. Analyze by Loan Purpose
```sql
SELECT 
    activity_year,
    CASE 
        WHEN loan_purpose = '1' THEN 'Home Purchase'
        WHEN loan_purpose IN ('31', '32') THEN 'Refinancing'
        WHEN loan_purpose = '2' THEN 'Home Improvement'
        ELSE 'Other'
    END as loan_purpose_category,
    COUNT(*) as total_records
FROM `hdma1-242116.hmda.hmda`
WHERE lei = 'KB1H1DSPRFMYMCUFXT09'
GROUP BY activity_year, loan_purpose_category
ORDER BY activity_year, total_records DESC;
```

## Need Help?

Contact your BigQuery administrator or refer to:
- [HMDA Documentation](https://ffiec.cfpb.gov/documentation/)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
