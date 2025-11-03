-- Worst Lenders Redlining Analysis Query
-- Identifies banks with worst redlining patterns for CBA enforcement
-- 
-- Requirements:
-- - Top 200 CBSAs by total applications (2018-2024)
-- - Banks: $10B-$100B assets, ≥500 apps in CBSA (2018-2024 total), appropriate type_name
-- - Applications and originations (kind column: 'Application' or 'Origination')
-- - All loans and home purchase (loan_purpose: 'All Loans' or 'Home Purchase')
-- - County-level breakdown within CBSAs
-- - Peer matching: 50%-200% of subject's volume by year/CBSA/loan_purpose/kind
-- - 8 redlining metrics: MMCT 50%, MMCT 80%, Black Tract 50%/80%, Hispanic Tract 50%/80%, Black+Hispanic Tract 50%/80%

WITH cbsa_crosswalk AS (
    -- CBSA to county mapping with state and county names
    SELECT
        geoid5 as county_code,
        cbsa_code,
        cbsa as cbsa_name,
        County as county_name,
        State as state_name
    FROM `hdma1-242116.geo.cbsa_to_county`
),

top_200_cbsas AS (
    -- Find top 200 CBSAs by total applications (2018-2024)
    SELECT 
        c.cbsa_code,
        COUNT(*) as total_applications
    FROM `hdma1-242116.hmda.hmda` h
    LEFT JOIN cbsa_crosswalk c
        ON h.county_code = c.county_code
    WHERE CAST(h.activity_year AS INT64) BETWEEN 2018 AND 2024
      AND c.cbsa_code IS NOT NULL
      AND c.cbsa_code != '99999'
      -- Standard HMDA filters
      AND h.occupancy_type = '1'  -- Owner-occupied
      AND h.reverse_mortgage != '1'  -- Not reverse mortgage
      AND h.construction_method = '1'  -- Site-built
      AND h.total_units IN ('1', '2', '3', '4')  -- 1-4 units
    GROUP BY c.cbsa_code
    ORDER BY total_applications DESC
    LIMIT 200
),

bank_filters AS (
    -- Filter banks by asset size ($10B-$100B), type_name
    -- Assets are stored as strings in $000s (thousands of dollars)
    -- $10 billion = 10,000,000,000 / 1,000 = 10,000,000
    -- $100 billion = 100,000,000,000 / 1,000 = 100,000,000
    -- Only include banks and bank affiliates, exclude credit unions
    SELECT DISTINCT
        l.lei,
        l.respondent_name as lender_name,
        CAST(REPLACE(COALESCE(l.assets, '0'), ',', '') AS INT64) as assets_thousands,
        l.type_name
    FROM `hdma1-242116.hmda.lenders18` l
    WHERE CAST(REPLACE(COALESCE(l.assets, '0'), ',', '') AS INT64) BETWEEN 10000000 AND 100000000  -- $10B-$100B in $000s
      AND l.type_name IS NOT NULL
      AND l.lei IS NOT NULL
      -- Exclude credit unions - only include banks and bank affiliates
      AND UPPER(l.type_name) NOT LIKE '%CREDIT UNION%'
      AND UPPER(l.type_name) NOT LIKE '%CU%'
      -- Include banks and bank affiliates (common patterns)
      AND (
          UPPER(l.type_name) LIKE '%BANK%' 
          OR UPPER(l.type_name) LIKE '%AFFILIATE%'
          OR UPPER(l.type_name) LIKE '%BANCORP%'
          OR UPPER(l.type_name) LIKE '%BANCSHARES%'
          OR UPPER(l.type_name) LIKE '%SAVINGS%'
          OR UPPER(l.type_name) LIKE '%COMMERCIAL%'
      )
      -- Exclude CBA banks (will be filtered later in Python)
),

qualifying_banks_by_cbsa AS (
    -- Banks with ≥500 applications in CBSA across 2018-2024 period
    SELECT
        b.lei,
        b.lender_name,
        c.cbsa_code,
        COUNT(*) as total_cbsa_applications
    FROM `hdma1-242116.hmda.hmda` h
    INNER JOIN bank_filters b
        ON h.lei = b.lei
    LEFT JOIN cbsa_crosswalk c
        ON h.county_code = c.county_code
    INNER JOIN top_200_cbsas t
        ON c.cbsa_code = t.cbsa_code
    WHERE CAST(h.activity_year AS INT64) BETWEEN 2018 AND 2024
      AND c.cbsa_code IS NOT NULL
      AND c.cbsa_code != '99999'
      -- Standard HMDA filters
      AND h.occupancy_type = '1'
      AND h.reverse_mortgage != '1'
      AND h.construction_method = '1'
      AND h.total_units IN ('1', '2', '3', '4')
    GROUP BY b.lei, b.lender_name, c.cbsa_code
    HAVING COUNT(*) >= 500  -- Minimum 500 applications in CBSA (2018-2024 total)
),

hmda_with_geography AS (
    -- Join HMDA data with tract demographics and filter to qualifying banks/CBSAs
    SELECT
        h.activity_year,
        h.lei,
        h.county_code,
        h.state_code,
        c.cbsa_code,
        c.cbsa_name,
        c.county_name,
        c.state_name,
        h.loan_purpose,
        h.action_taken,
        -- Tract demographics
        h.tract_minority_population_percent as tract_minority_pct,
        g.black_pct,
        g.hispanic_pct,
        g.black_and_hispanic_pct
    FROM `hdma1-242116.hmda.hmda` h
    LEFT JOIN cbsa_crosswalk c
        ON h.county_code = c.county_code
    INNER JOIN top_200_cbsas t
        ON c.cbsa_code = t.cbsa_code
    INNER JOIN qualifying_banks_by_cbsa qb
        ON h.lei = qb.lei
        AND c.cbsa_code = qb.cbsa_code
    LEFT JOIN `hdma1-242116.geo.black_hispanic_majority` g
        ON CAST(h.census_tract AS STRING) = CAST(g.geoid AS STRING)
    WHERE CAST(h.activity_year AS INT64) BETWEEN 2018 AND 2024
      AND c.cbsa_code IS NOT NULL
      AND c.cbsa_code != '99999'
      -- Standard HMDA filters
      AND h.occupancy_type = '1'
      AND h.reverse_mortgage != '1'
      AND h.construction_method = '1'
      AND h.total_units IN ('1', '2', '3', '4')
      -- Loan purpose: all (1, 2, 31, 32) OR home purchase (1)
      AND h.loan_purpose IN ('1', '2', '31', '32')
),

expanded_data AS (
    -- Expand data to create 'kind' and unified loan_purpose columns
    -- First: All Applications (all loan purposes combined)
    SELECT
        activity_year,
        lei,
        county_code,
        state_code,
        cbsa_code,
        cbsa_name,
        county_name,
        state_name,
        'Application' as kind,
        'All Loans' as loan_purpose_category,
        tract_minority_pct,
        black_pct,
        hispanic_pct,
        black_and_hispanic_pct
    FROM hmda_with_geography
    
    UNION ALL
    
    -- Second: All Originations (all loan purposes combined)
    SELECT
        activity_year,
        lei,
        county_code,
        state_code,
        cbsa_code,
        cbsa_name,
        county_name,
        state_name,
        'Origination' as kind,
        'All Loans' as loan_purpose_category,
        tract_minority_pct,
        black_pct,
        hispanic_pct,
        black_and_hispanic_pct
    FROM hmda_with_geography
    WHERE action_taken = '1'  -- Originations only
      AND loan_purpose IN ('1', '2', '31', '32')  -- All loan purposes
    
    UNION ALL
    
    -- Third: Home Purchase Applications only
    SELECT
        activity_year,
        lei,
        county_code,
        state_code,
        cbsa_code,
        cbsa_name,
        county_name,
        state_name,
        'Application' as kind,
        'Home Purchase' as loan_purpose_category,
        tract_minority_pct,
        black_pct,
        hispanic_pct,
        black_and_hispanic_pct
    FROM hmda_with_geography
    WHERE loan_purpose = '1'  -- Home Purchase only
    
    UNION ALL
    
    -- Fourth: Home Purchase Originations only
    SELECT
        activity_year,
        lei,
        county_code,
        state_code,
        cbsa_code,
        cbsa_name,
        county_name,
        state_name,
        'Origination' as kind,
        'Home Purchase' as loan_purpose_category,
        tract_minority_pct,
        black_pct,
        hispanic_pct,
        black_and_hispanic_pct
    FROM hmda_with_geography
    WHERE loan_purpose = '1'  -- Home Purchase only
      AND action_taken = '1'  -- Originations only
),

subject_volume AS (
    -- Subject bank volume by year, CBSA, county, loan_purpose_category, kind
    SELECT
        activity_year,
        cbsa_code,
        county_code,
        lei,
        loan_purpose_category,
        kind,
        COUNT(*) as subject_vol
    FROM expanded_data
    GROUP BY activity_year, cbsa_code, county_code, lei, loan_purpose_category, kind
),

all_lenders_volume AS (
    -- All lenders' volume for peer matching
    SELECT
        activity_year,
        cbsa_code,
        county_code,
        lei,
        loan_purpose_category,
        kind,
        COUNT(*) as lender_vol
    FROM expanded_data
    GROUP BY activity_year, cbsa_code, county_code, lei, loan_purpose_category, kind
),

peers AS (
    -- Identify peer lenders (50%-200% of subject's volume)
    SELECT DISTINCT
        al.activity_year,
        al.cbsa_code,
        al.county_code,
        al.lei,
        al.loan_purpose_category,
        al.kind,
        sv.lei as subject_lei
    FROM all_lenders_volume al
    INNER JOIN subject_volume sv
        ON al.activity_year = sv.activity_year
        AND al.cbsa_code = sv.cbsa_code
        AND al.county_code = sv.county_code
        AND al.loan_purpose_category = sv.loan_purpose_category
        AND al.kind = sv.kind
    WHERE al.lei != sv.lei  -- Exclude subject bank
      AND al.lender_vol >= sv.subject_vol * 0.5
      AND al.lender_vol <= sv.subject_vol * 2.0
),

subject_data AS (
    -- Calculate subject bank metrics by year, CBSA, county, loan_purpose_category, kind
    SELECT
        activity_year,
        cbsa_code,
        cbsa_name,
        county_code,
        county_name,
        state_code,
        state_name,
        lei,
        loan_purpose_category,
        kind,
        COUNT(*) as subject_total,
        -- 8 Redlining Metrics
        COUNTIF(tract_minority_pct > 50) as subject_mmct_50,
        COUNTIF(tract_minority_pct > 80) as subject_mmct_80,
        COUNTIF(black_pct > 50) as subject_black_tract_50,
        COUNTIF(black_pct > 80) as subject_black_tract_80,
        COUNTIF(hispanic_pct > 50) as subject_hispanic_tract_50,
        COUNTIF(hispanic_pct > 80) as subject_hispanic_tract_80,
        COUNTIF(black_and_hispanic_pct > 50) as subject_black_hispanic_tract_50,
        COUNTIF(black_and_hispanic_pct > 80) as subject_black_hispanic_tract_80
    FROM expanded_data
    WHERE lei IN (SELECT DISTINCT lei FROM subject_volume)
    GROUP BY activity_year, cbsa_code, cbsa_name, county_code, county_name, state_code, state_name, lei, loan_purpose_category, kind
),

peer_data AS (
    -- Calculate peer group metrics (aggregated across all peer lenders)
    SELECT
        e.activity_year,
        e.cbsa_code,
        e.cbsa_name,
        e.county_code,
        e.county_name,
        e.state_code,
        e.state_name,
        p.subject_lei as lei,
        e.loan_purpose_category,
        e.kind,
        COUNT(*) as peer_total,
        -- 8 Redlining Metrics
        COUNTIF(e.tract_minority_pct > 50) as peer_mmct_50,
        COUNTIF(e.tract_minority_pct > 80) as peer_mmct_80,
        COUNTIF(e.black_pct > 50) as peer_black_tract_50,
        COUNTIF(e.black_pct > 80) as peer_black_tract_80,
        COUNTIF(e.hispanic_pct > 50) as peer_hispanic_tract_50,
        COUNTIF(e.hispanic_pct > 80) as peer_hispanic_tract_80,
        COUNTIF(e.black_and_hispanic_pct > 50) as peer_black_hispanic_tract_50,
        COUNTIF(e.black_and_hispanic_pct > 80) as peer_black_hispanic_tract_80
    FROM expanded_data e
    INNER JOIN peers p
        ON e.activity_year = p.activity_year
        AND e.cbsa_code = p.cbsa_code
        AND e.county_code = p.county_code
        AND e.lei = p.lei
        AND e.loan_purpose_category = p.loan_purpose_category
        AND e.kind = p.kind
    GROUP BY e.activity_year, e.cbsa_code, e.cbsa_name, e.county_code, e.county_name, e.state_code, e.state_name, p.subject_lei, e.loan_purpose_category, e.kind
),

final_output AS (
    -- Final output: Subject vs Peer comparison with all metrics
    SELECT
        s.activity_year,
        s.cbsa_code,
        s.cbsa_name,
        s.county_code,
        s.county_name,
        s.state_code,
        s.state_name,
        s.lei,
        qb.lender_name,
        s.loan_purpose_category,
        s.kind,
        -- Total counts
        s.subject_total as subject_total_count,
        COALESCE(p.peer_total, 0) as peer_total_count,
        -- MMCT metrics
        s.subject_mmct_50,
        s.subject_mmct_80,
        COALESCE(p.peer_mmct_50, 0) as peer_mmct_50,
        COALESCE(p.peer_mmct_80, 0) as peer_mmct_80,
        -- Black Tract metrics
        s.subject_black_tract_50,
        s.subject_black_tract_80,
        COALESCE(p.peer_black_tract_50, 0) as peer_black_tract_50,
        COALESCE(p.peer_black_tract_80, 0) as peer_black_tract_80,
        -- Hispanic Tract metrics
        s.subject_hispanic_tract_50,
        s.subject_hispanic_tract_80,
        COALESCE(p.peer_hispanic_tract_50, 0) as peer_hispanic_tract_50,
        COALESCE(p.peer_hispanic_tract_80, 0) as peer_hispanic_tract_80,
        -- Black+Hispanic Tract metrics
        s.subject_black_hispanic_tract_50,
        s.subject_black_hispanic_tract_80,
        COALESCE(p.peer_black_hispanic_tract_50, 0) as peer_black_hispanic_tract_50,
        COALESCE(p.peer_black_hispanic_tract_80, 0) as peer_black_hispanic_tract_80
    FROM subject_data s
    INNER JOIN qualifying_banks_by_cbsa qb
        ON s.lei = qb.lei
        AND s.cbsa_code = qb.cbsa_code
    LEFT JOIN peer_data p
        ON s.activity_year = p.activity_year
        AND s.cbsa_code = p.cbsa_code
        AND s.county_code = p.county_code
        AND s.lei = p.lei
        AND s.loan_purpose_category = p.loan_purpose_category
        AND s.kind = p.kind
)

SELECT *
FROM final_output
ORDER BY lender_name, cbsa_code, county_code, activity_year, loan_purpose_category, kind

