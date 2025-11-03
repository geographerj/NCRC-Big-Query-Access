# SQL Query Optimization Guidelines for Local Market Analysis

## Principle

**Only query and return the data needed for the analysis to minimize processing time and BigQuery costs.**

## Optimization Strategies

### 1. Column Selection

**❌ BAD:**
```sql
SELECT * FROM `hdma1-242116.hmda.hmda`
```

**✅ GOOD:**
```sql
SELECT 
  activity_year,
  cbsa_code,
  county_code,
  census_tract,
  action_taken,
  loan_amount,
  tract_to_msa_income_percentage,
  applicant_income_percentage_of_msamd
FROM `hdma1-242116.hmda.hmda`
```

### 2. Filter Early and Often

**❌ BAD:** Filter after selecting all data
```sql
SELECT ... FROM hmda
-- Process millions of rows
WHERE activity_year = 2024  -- Filter comes too late
```

**✅ GOOD:** Filter in WHERE clause early
```sql
WITH filtered_data AS (
  SELECT ...
  FROM `hdma1-242116.hmda.hmda`
  WHERE activity_year IN (2020, 2021, 2022, 2023, 2024)
    AND lei = 'BANK_LEI'
    AND action_taken = '1'
    AND county_code IN ('01001', '01002', ...)  -- Assessment area counties only
)
```

### 3. Assessment Area County Filtering

**Critical**: Filter to assessment area counties in the WHERE clause, not after:

```sql
WITH assessment_area_counties AS (
  SELECT DISTINCT 
    state_code || county_code as county_code,
    cbsa_code,
    state_code
  FROM assessment_areas_parsed
  WHERE bank_name = 'PNC Bank'
)
SELECT ...
FROM hmda h
INNER JOIN assessment_area_counties aac
  ON h.county_code = aac.county_code
```

### 4. Aggregate in SQL, Not Python

**❌ BAD:** Return all rows, aggregate in Python
```sql
SELECT activity_year, cbsa_code, lei, loan_amount
FROM hmda
-- Returns millions of rows
```

**✅ GOOD:** Aggregate in SQL
```sql
SELECT 
  activity_year,
  cbsa_code,
  COUNT(*) as loan_count,
  SUM(loan_amount) as total_amount,
  COUNTIF(tract_to_msa_income_percentage <= 80) as lmict_count,
  COUNTIF(applicant_income_percentage_of_msamd <= 80) as lmib_count
FROM filtered_hmda
GROUP BY activity_year, cbsa_code
-- Returns only aggregated summary rows
```

### 5. Calculate Metrics in SQL

Calculate percentages and ratios in SQL:

```sql
SELECT 
  activity_year,
  cbsa_code,
  COUNT(*) as total_loans,
  COUNTIF(is_lmict) as lmict_loans,
  SAFE_DIVIDE(COUNTIF(is_lmict), COUNT(*)) * 100 as lmict_percentage,
  SUM(loan_amount) as total_amount,
  SUM(CASE WHEN is_lmib THEN loan_amount END) as lmib_amount
FROM filtered_hmda
GROUP BY activity_year, cbsa_code
```

### 6. Use CTEs for Complex Logic

Break complex queries into CTEs:

```sql
WITH assessment_counties AS (
  -- Filter assessment areas
  SELECT county_code, cbsa_code, state_code
  FROM assessment_areas
),
filtered_hmda AS (
  -- Apply filters early
  SELECT ...
  FROM hmda
  INNER JOIN assessment_counties USING (county_code)
  WHERE ...
),
subject_metrics AS (
  -- Calculate subject bank metrics
  SELECT ...
  FROM filtered_hmda
  WHERE lei = 'SUBJECT_LEI'
  GROUP BY ...
),
peer_metrics AS (
  -- Calculate peer metrics separately
  SELECT ...
  FROM filtered_hmda
  WHERE lei IN (SELECT lei FROM peers)
  GROUP BY ...
)
-- Final select combines everything
SELECT ... FROM subject_metrics
JOIN peer_metrics USING (...)
```

### 7. Limit Joins

- Use INNER JOIN when possible (faster than LEFT JOIN)
- Join on filtered/aggregated datasets when possible
- Join assessment area list early, not late

### 8. Specific Column Requirements

#### HMDA Queries
**Required columns only:**
- `activity_year`
- `cbsa_code`
- `county_code`
- `census_tract` (for tract demographics)
- `action_taken`
- `loan_amount`
- `loan_purpose` (if filtering by purpose)
- `tract_to_msa_income_percentage` (for LMICT)
- `applicant_income_percentage_of_msamd` (for LMIB)
- Race/ethnicity fields (for borrower demographics)
- `tract_minority_population_percent` (for MMCT)

**Don't select:**
- Application date
- Loan-to-value ratio
- Debt-to-income ratio
- Other fields not used in metrics

#### Small Business Queries
**Required columns only:**
- `year`
- `msamd` (CBSA code)
- `geoid5` (county code)
- `income_group_total` (for LMICT filter)
- `num_under_100k`, `amt_under_100k`
- `num_100k_250k`, `amt_100k_250k`
- `num_250k_1m`, `amt_250k_1m`
- `numsbrev_under_1m`, `amtsbrev_under_1m`

#### Branch Queries
**Required columns only:**
- `year`
- `county_code`
- `cbsa_code`
- `rssd`
- `uninumbr` (for deduplication)
- `br_lmi` (LMICT flag)
- `cr_minority` (MMCT flag)

## Example: Optimized HMDA Query Structure

```sql
WITH assessment_area_counties AS (
  -- Small, filtered list of counties
  SELECT DISTINCT 
    state_code || county_code as county_code_5digit,
    cbsa_code,
    state_code
  FROM parsed_assessment_areas
  WHERE bank_name = 'PNC Bank'
),
filtered_hmda AS (
  -- Filter early: years, LEI, action, counties
  SELECT 
    h.activity_year,
    h.cbsa_code,
    h.county_code,
    h.census_tract,
    h.loan_amount,
    -- Pre-calculate flags in SQL
    CASE WHEN CAST(h.tract_to_msa_income_percentage AS FLOAT64) <= 80 
         THEN 1 ELSE 0 END as is_lmict,
    CASE WHEN CAST(h.applicant_income_percentage_of_msamd AS FLOAT64) <= 80 
         THEN 1 ELSE 0 END as is_lmib,
    -- Race/ethnicity calculations
    CASE WHEN h.applicant_ethnicity_1 IN ('1','11','12','13','14') 
         THEN 1 ELSE 0 END as is_hispanic,
    -- ... other demographic flags
  FROM `hdma1-242116.hmda.hmda` h
  INNER JOIN assessment_area_counties aac
    ON h.county_code = aac.county_code_5digit
  WHERE h.activity_year IN (2020, 2021, 2022, 2023, 2024)
    AND h.lei = 'PNC_LEI'
    AND h.action_taken = '1'
    AND h.occupancy_type = '1'
    AND h.construction_method = '1'
    AND h.total_units IN ('1','2','3','4')
    AND h.reverse_mortgage != '1'
),
aggregated_metrics AS (
  -- Aggregate once, calculate all metrics
  SELECT 
    activity_year,
    cbsa_code,
    COUNT(*) as total_loans,
    SUM(loan_amount) as total_amount,
    COUNTIF(is_lmict = 1) as lmict_loans,
    SAFE_DIVIDE(COUNTIF(is_lmict = 1), COUNT(*)) * 100 as lmict_percentage,
    COUNTIF(is_lmib = 1) as lmib_loans,
    SAFE_DIVIDE(COUNTIF(is_lmib = 1), COUNT(*)) * 100 as lmib_percentage,
    SUM(CASE WHEN is_lmib = 1 THEN loan_amount END) as lmib_amount,
    COUNTIF(is_hispanic = 1) as hispanic_loans,
    SAFE_DIVIDE(COUNTIF(is_hispanic = 1), COUNT(*)) * 100 as hispanic_percentage
    -- ... other metrics
  FROM filtered_hmda
  GROUP BY activity_year, cbsa_code
)
-- Final output: only aggregated summary rows
SELECT * FROM aggregated_metrics
ORDER BY activity_year, cbsa_code
```

## Performance Targets

- **Row Count**: Queries should return hundreds or thousands of aggregated rows, not millions of raw loan records
- **Processing Time**: Sub-minute execution for aggregated queries
- **Data Transfer**: Minimize bytes transferred from BigQuery to Python

## Checklist

Before finalizing each SQL query:

- [ ] Only SELECT columns actually used in analysis
- [ ] Filter by assessment area counties in WHERE clause
- [ ] Filter by years, LEIs, action_taken early
- [ ] Aggregate data in SQL (GROUP BY)
- [ ] Calculate percentages/metrics in SQL
- [ ] Use CTEs to organize and filter data
- [ ] Test query returns reasonable row count (< 10,000 rows typically)
- [ ] Verify query runs in < 60 seconds


