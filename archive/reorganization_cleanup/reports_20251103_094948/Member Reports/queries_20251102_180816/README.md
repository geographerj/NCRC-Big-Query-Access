# Queries Directory

BigQuery SQL query builders for HMDA data.

## Files

### `tampa_market_query.py` ⭐ **PRIMARY TEMPLATE**
Complete query builder for Tampa market report.

**Features:**
- Market overview query (all lenders combined)
- Top 10 lenders query (individual lender analysis)
- NCRC race/ethnicity classification methodology
- Geographic metrics (LMICT, MMCT classification)
- Correct handling of "no data" loans

**Key Functions:**
- Query builder functions that return SQL strings
- Handles 2018-2024 data
- Supports census tract filtering

**Race Classification Logic:**
1. Hispanic ethnicity checked first (codes 1, 11, 12, 13, 14)
2. If not Hispanic, uses first explicit race code from `applicant_race_1` through `applicant_race_5`
3. "No data" loans excluded from race share denominators

**Usage:**
```python
from queries.tampa_market_query import build_market_query, build_top_lenders_query

market_sql = build_market_query(census_tracts, years)
lenders_sql = build_top_lenders_query(census_tracts, years, top_n=10)
```

---

### `member_report_queries.py`
General-purpose query builder for member reports.

**Features:**
- More flexible than Tampa-specific queries
- Supports various geographic scopes
- Configurable filters

**Usage:**
```python
from queries.member_report_queries import build_base_query

sql = build_base_query(config)
```

---

## Query Structure

### Market Overview Query
Returns aggregated data by year:
- Total originations
- Race/ethnicity counts (Black, Hispanic, Asian, White, Native American, HoPI)
- Geographic metrics (LMIB, LMICT, MMCT)
- Loans with demographic data

### Top Lenders Query
Returns lender-level data:
- Same metrics as market overview
- Grouped by lender (LEI)
- Filtered to top N lenders by volume

---

## NCRC Methodology Implementation

Queries implement NCRC's HMDA methodology:

### Race/Ethnicity Classification
```sql
-- Hispanic checked first
CASE 
    WHEN applicant_ethnicity_1 IN ('1','11','12','13','14') OR
         applicant_ethnicity_2 IN ('1','11','12','13','14') OR
         applicant_ethnicity_3 IN ('1','11','12','13','14') OR
         applicant_ethnicity_4 IN ('1','11','12','13','14') OR
         applicant_ethnicity_5 IN ('1','11','12','13','14')
    THEN TRUE
    ELSE FALSE
END AS is_hispanic,

-- Then first explicit race code
COALESCE(
    NULLIF(applicant_race_1, ''),
    NULLIF(applicant_race_2, ''),
    ...
) AS first_race_code
```

### Missing Data Handling
```sql
-- Exclude "not provided" codes
WHERE applicant_ethnicity_1 NOT IN ('3','4','5','6','7','8')
  AND applicant_race_1 NOT IN ('6','7','8')
```

### Geographic Classification
```sql
-- LMICT: Median family income <= 80% of MSA median
-- MMCT: Minority population > 50%
```

---

## Creating Queries for New Locations

**Recommended approach:**

1. Copy `tampa_market_query.py` to `[location]_query.py`
2. Update:
   - Function names
   - Census tract list parameter
   - Any location-specific filters
3. Import in your report script:
   ```python
   from queries.[location]_query import build_market_query
   ```

---

## Query Validation

Before running queries, verify:
- Census tracts are strings (not numbers)
- Years are valid (2018-2024 for current HMDA data)
- Loan filters match HMDA codes
- Geographic filters are correct

---

## BigQuery Table Structure

**Main Table:** `hdma1-242116.hmda.hmda`

**Key Fields:**
- `activity_year` - Year (INT64)
- `census_tract` - Census tract code (STRING)
- `lei` - Legal Entity Identifier
- `applicant_race_1` through `applicant_race_5` - Race codes
- `applicant_ethnicity_1` through `applicant_ethnicity_5` - Ethnicity codes
- `tract_to_msamd_income` - Income ratio for LMICT
- `minority_population` - For MMCT classification

**Lender Info Table:** `hdma1-242116.hmda.lenders18`

**Key Fields:**
- `lei` - Legal Entity Identifier
- `respondent_name` - Lender name
- `assets_thousands` - Asset size
- `type_name` - Institution type (bank, credit union, mortgage company)

---

## Notes

- Queries return SQL strings, not executed results
- Actual query execution happens in report scripts using BigQuery client
- Queries are optimized for the specific report structure
- Consider query cost when running for large geographic areas

---

## Testing Queries

Test queries in BigQuery console before using in production:

1. Copy SQL from query builder function
2. Replace parameters with actual values
3. Run in BigQuery console
4. Verify results match expected structure

---

## Dependencies

- `google-cloud-bigquery` - For query execution (not in this directory)
- Standard SQL syntax for BigQuery
- Understanding of HMDA data structure


