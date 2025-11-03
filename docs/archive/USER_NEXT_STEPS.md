# Next Steps for Fifth Third Bank CBA Analysis

## Summary

I've prepared everything needed to add **8 tract-level demographic metrics** to your Fifth Third Bank CBA analysis. The metrics analyze loans by the demographic composition of the **census tracts** where properties are located, using 50% and 80% thresholds.

### Metrics to Add:
1. Majority Minority 50% and 80%
2. Majority Black 50% and 80%
3. Majority Hispanic 50% and 80%
4. Majority Black and Hispanic Combined 50% and 80%

## Current Status

✅ **Excel Generator**: Ready and working (`ncrc_worst_lenders_analysis_v4.py`)
✅ **Standard Filters**: Defined (owner-occupied, site-built 1-4 unit, exclude reverse mortgages)
✅ **Utilities**: Created (hmda_codes.py, hmda_crosswalks.py, hmda_demographics.py)
✅ **Fifth Third LEI**: Found (`QFROUN1UWUYU0DVIWD51`)

❌ **Missing**: Need to verify the BigQuery geo dataset has tract demographics
❌ **Missing**: Need to write the BigQuery SQL query

## What You Need to Do

### 1. Verify Geo Dataset Tables

Run this Python script to check what tables exist in your BigQuery `geo` dataset:

```python
from google.cloud import bigquery

key_path = "hdma1-242116-74024e2eb88f.json"
project_id = "hdma1-242116"
client = bigquery.Client.from_service_account_json(key_path, project=project_id)

# List all datasets
datasets = list(client.list_datasets())
print("Available datasets:")
for dataset in datasets:
    print(f"  - {dataset.dataset_id}")

# Look specifically for geo dataset
for dataset in datasets:
    if 'geo' in dataset.dataset_id.lower():
        print(f"\nFound geo dataset: {dataset.dataset_id}")
        tables = list(client.list_tables(dataset.reference))
        print("Tables:")
        for table in tables:
            print(f"  - {table.table_id}")
            # Get schema
            bq_table = client.get_table(table.reference)
            if 'majority' in table.table_id.lower() or 'demographic' in table.table_id.lower():
                print(f"    Columns: {[field.name for field in bq_table.schema]}")
```

**Tell me**:
- What dataset contains tract demographics?
- What is the table name?
- What are the column names (especially for Black %, Hispanic %, Minority %, etc.)?

### 2. Verify HMDA Field Names

I need to confirm the exact field names in your HMDA table. Can you check for:
- **Occupancy field**: Owner-occupied indicator (might be `occupancy_type`, `owner_occupancy`, etc.)
- **Reverse mortgage field**: Exclusion flag (might be `reverse_mortgage`, `reverse`, etc.)
- **Property type field**: Site-built 1-4 unit indicator

You can check by running a small query:

```python
query = """
SELECT * 
FROM `hdma1-242116.hmda.hmda`
LIMIT 1
"""

result = client.query(query).to_dataframe()
print(result.columns.tolist())
# Look for fields matching the criteria above
```

## What I'll Do Next

Once you provide the geo dataset information, I will:

1. ✅ **Create BigQuery SQL query** that:
   - Joins HMDA data with tract demographics
   - Applies standard filters
   - Counts loans in each tract demographic category
   - Aggregates by subject bank (Fifth Third) vs peers

2. ✅ **Update Excel generator** to add the 8 new metrics to the METRICS dictionary

3. ✅ **Create analysis script** to:
   - Run the BigQuery query
   - Export results to CSV
   - Generate Excel report using the Excel generator

4. ✅ **Test with sample data** before running full analysis

## Documentation Files Created

I've created these files to help:

1. **`TRACT_DEMOGRAPHIC_METRICS_REQUIREMENTS.md`**: Detailed documentation of all 8 metrics, column names, and SQL query patterns
2. **`IMPLEMENTATION_SUMMARY.md`**: Technical implementation details and current status
3. **`USER_NEXT_STEPS.md`**: This file - what you need to do next

## Quick Questions

1. Do you have a `geo` dataset in BigQuery with tract demographics?
2. What's the table name?
3. What columns does it have for Black %, Hispanic %, and Minority %?

Once I have this information, I can complete the implementation in minutes!

