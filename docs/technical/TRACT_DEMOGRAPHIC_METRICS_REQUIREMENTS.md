# Tract-Level Demographic Metrics for CBA Analysis

## Overview
These metrics analyze loans by the **demographic composition of the census tracts** where the properties are located, NOT by borrower demographics. The data comes from joining HMDA loan records with tract-level demographic data from the BigQuery `geo` dataset.

## Required Metrics

Based on the user's request, we need to add **8 tract demographic metrics**:

### 1. Majority Minority (Total) at 50%
- **Definition**: Share of loans in tracts where >50% of population is non-White
- **SQL Join**: HMDA `census_tract` → GEO tract demographics
- **Threshold**: Minority percentage > 50%
- **Column Names**: 
  - Subject: `subject_mmct_50_originations`
  - Peer: `peer_mmct_50_originations`
  - Display: `MMCT 50%`

### 2. Majority Minority (Total) at 80%
- **Definition**: Share of loans in tracts where >80% of population is non-White
- **Threshold**: Minority percentage > 80%
- **Column Names**:
  - Subject: `subject_mmct_80_originations`
  - Peer: `peer_mmct_80_originations`
  - Display: `MMCT 80%`

### 3. Majority Black at 50%
- **Definition**: Share of loans in tracts where >50% of population is Black/African American
- **Threshold**: Black percentage > 50%
- **Column Names**:
  - Subject: `subject_black_tract_50_originations`
  - Peer: `peer_black_tract_50_originations`
  - Display: `Black Tract 50%`

### 4. Majority Black at 80%
- **Definition**: Share of loans in tracts where >80% of population is Black/African American
- **Threshold**: Black percentage > 80%
- **Column Names**:
  - Subject: `subject_black_tract_80_originations`
  - Peer: `peer_black_tract_80_originations`
  - Display: `Black Tract 80%`

### 5. Majority Hispanic at 50%
- **Definition**: Share of loans in tracts where >50% of population is Hispanic/Latino
- **Threshold**: Hispanic percentage > 50%
- **Column Names**:
  - Subject: `subject_hispanic_tract_50_originations`
  - Peer: `peer_hispanic_tract_50_originations`
  - Display: `Hispanic Tract 50%`

### 6. Majority Hispanic at 80%
- **Definition**: Share of loans in tracts where >80% of population is Hispanic/Latino
- **Threshold**: Hispanic percentage > 80%
- **Column Names**:
  - Subject: `subject_hispanic_tract_80_originations`
  - Peer: `peer_hispanic_tract_80_originations`
  - Display: `Hispanic Tract 80%`

### 7. Majority Black and Hispanic Combined at 50%
- **Definition**: Share of loans in tracts where >50% of population is either Black OR Hispanic
- **Threshold**: (Black percentage + Hispanic percentage) > 50%
- **Column Names**:
  - Subject: `subject_black_hispanic_tract_50_originations`
  - Peer: `peer_black_hispanic_tract_50_originations`
  - Display: `Black+Hispanic Tract 50%`

### 8. Majority Black and Hispanic Combined at 80%
- **Definition**: Share of loans in tracts where >80% of population is either Black OR Hispanic
- **Threshold**: (Black percentage + Hispanic percentage) > 80%
- **Column Names**:
  - Subject: `subject_black_hispanic_tract_80_originations`
  - Peer: `peer_black_hispanic_tract_80_originations`
  - Display: `Black+Hispanic Tract 80%`

## BigQuery Table Reference

**Expected Geo Data Table**: `hdma1-242116.geo.black_hispanic_majority` or similar

### Expected Table Schema:
```
- census_tract (string): 11-digit census tract code
- minority_pct (float): Percentage of tract population that is minority/non-White
- black_pct (float): Percentage of tract population that is Black/African American
- hispanic_pct (float): Percentage of tract population that is Hispanic/Latino
- black_hispanic_pct (float): Percentage of tract population that is either Black OR Hispanic
```

## SQL Query Pattern

The BigQuery SQL will need to:
1. Join HMDA data with tract demographic data
2. Apply thresholds for each metric (50% or 80%)
3. Filter by standard HMDA filters:
   - Owner-occupied (occupancy_type = '1')
   - Site-built 1-4 unit (property_type codes)
   - Exclude reverse mortgages (reverse_mortgage != '1')

### Example Join:
```sql
SELECT 
    h.activity_year,
    h.cbsa_code,
    h.lei,
    -- Count loans by tract demographics
    COUNTIF(g.minority_pct > 50) as mmct_50_originations,
    COUNTIF(g.minority_pct > 80) as mmct_80_originations,
    COUNTIF(g.black_pct > 50) as black_tract_50_originations,
    COUNTIF(g.black_pct > 80) as black_tract_80_originations,
    -- etc.
FROM `hdma1-242116.hmda.hmda` h
LEFT JOIN `hdma1-242116.geo.black_hispanic_majority` g
    ON h.census_tract = g.census_tract
WHERE h.activity_year IN (2018, 2019, 2020, 2021, 2022, 2023, 2024)
  AND h.action_taken = '1'  -- Originations only
  AND h.loan_purpose = '1'  -- Home Purchase
  -- Standard filters
  AND h.occupancy_type = '1'  -- Owner-occupied
  AND h.reverse_mortgage != '1'  -- Not reverse mortgage
GROUP BY h.activity_year, h.cbsa_code, h.lei
```

## Excel Generator Updates Needed

Update `ncrc_worst_lenders_analysis_v4.py` to:
1. Add new metrics to METRICS dictionary
2. Add metric calculations in `calculate_metrics()` function
3. Add conditional formatting rules (already exists)
4. Update methodology sheet documentation

## Next Steps

1. **Verify Geo Table Exists**: Run BigQuery query to check if `geo.black_hispanic_majority` table exists
2. **Check Table Schema**: Confirm column names match expected schema
3. **Update METRICS Dictionary**: Add all 8 new metrics to the Excel generator
4. **Test with Sample Data**: Generate small CSV to verify new columns
5. **Generate Full Report**: Run full Fifth Third Bank analysis with new metrics

