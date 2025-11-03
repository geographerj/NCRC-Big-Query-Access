-- Fifth Third Bank Redlining Analysis - Complete Query
-- Home Purchase loans, Top 10 CBSAs by originations (2018-2024)
-- Tract demographic metrics: MMCT, Black, Hispanic, Black+Hispanic (50% and 80% thresholds)
-- Uses CBSA crosswalk via county_code (GEOID5) join

WITH cbsa_crosswalk AS (
    -- Load the CBSA crosswalk data from BigQuery table
    SELECT
        geoid5 as county_code,
        cbsa_code,
        cbsa as cbsa_name
    FROM `hdma1-242116.geo.cbsa_to_county`
),

top_10_cbsas AS (
    -- Find the top 10 CBSAs by Fifth Third home purchase originations
    SELECT 
        c.cbsa_code,
        COUNT(*) as total_originations
    FROM `hdma1-242116.hmda.hmda` h
    LEFT JOIN cbsa_crosswalk c
        ON h.county_code = c.county_code
    WHERE h.lei = 'QFROUN1UWUYU0DVIWD51'  -- Fifth Third Bank
      AND CAST(h.activity_year AS INT64) BETWEEN 2018 AND 2024
      AND h.loan_purpose = '1'  -- Home Purchase only
      AND h.action_taken = '1'  -- Originations only
      AND c.cbsa_code IS NOT NULL
      AND c.cbsa_code != '99999'  -- Exclude invalid CBSA code
      -- Standard HMDA filters
      AND h.occupancy_type = '1'  -- Owner-occupied
      AND h.reverse_mortgage != '1'  -- Not reverse mortgage
      AND h.construction_method = '1'  -- Site-built only
      AND h.total_units IN ('1', '2', '3', '4')  -- 1-4 unit properties
    GROUP BY c.cbsa_code
    ORDER BY total_originations DESC
    LIMIT 10
),

subject_volume AS (
    -- Get subject bank's volume by CBSA and year for peer matching
    SELECT
        h.activity_year,
        c.cbsa_code,
        COUNT(*) as subject_vol
    FROM `hdma1-242116.hmda.hmda` h
    LEFT JOIN cbsa_crosswalk c
        ON h.county_code = c.county_code
    INNER JOIN top_10_cbsas t
        ON c.cbsa_code = t.cbsa_code
    WHERE h.lei = 'QFROUN1UWUYU0DVIWD51'
      AND h.action_taken = '1'  -- Originations only
      AND CAST(h.activity_year AS INT64) BETWEEN 2018 AND 2024
      AND h.loan_purpose = '1'  -- Home Purchase
      -- Standard filters
      AND h.occupancy_type = '1'
      AND h.reverse_mortgage != '1'
      AND h.construction_method = '1'
      AND h.total_units IN ('1', '2', '3', '4')
    GROUP BY h.activity_year, c.cbsa_code
),

all_lenders AS (
    -- Get all lenders' volume for peer comparison
    SELECT
        h.activity_year,
        c.cbsa_code,
        h.lei,
        COUNT(*) as lender_vol
    FROM `hdma1-242116.hmda.hmda` h
    LEFT JOIN cbsa_crosswalk c
        ON h.county_code = c.county_code
    INNER JOIN top_10_cbsas t
        ON c.cbsa_code = t.cbsa_code
    WHERE h.action_taken = '1'
      AND CAST(h.activity_year AS INT64) BETWEEN 2018 AND 2024
      AND h.loan_purpose = '1'
      -- Standard filters
      AND h.occupancy_type = '1'
      AND h.reverse_mortgage != '1'
      AND h.construction_method = '1'
      AND h.total_units IN ('1', '2', '3', '4')
    GROUP BY h.activity_year, c.cbsa_code, h.lei
),

peers AS (
    -- Identify peer lenders (50%-200% of subject's volume)
    SELECT DISTINCT
        av.activity_year,
        av.cbsa_code,
        av.lei
    FROM all_lenders av
    INNER JOIN subject_volume sv
        ON av.activity_year = sv.activity_year
        AND av.cbsa_code = sv.cbsa_code
    WHERE av.lender_vol >= sv.subject_vol * 0.5
      AND av.lender_vol <= sv.subject_vol * 2.0
      AND av.lei != 'QFROUN1UWUYU0DVIWD51'
),

hmda_with_geography AS (
    -- Join HMDA data with tract demographics
    SELECT
        h.activity_year,
        c.cbsa_code,
        c.cbsa_name,
        h.lei,
        h.tract_minority_population_percent as tract_minority_pct,
        g.black_pct,
        g.hispanic_pct,
        g.black_and_hispanic_pct
    FROM `hdma1-242116.hmda.hmda` h
    LEFT JOIN cbsa_crosswalk c
        ON h.county_code = c.county_code
    INNER JOIN top_10_cbsas t
        ON c.cbsa_code = t.cbsa_code
    LEFT JOIN `hdma1-242116.geo.black_hispanic_majority` g
        ON CAST(h.census_tract AS STRING) = CAST(g.geoid AS STRING)
    WHERE h.action_taken = '1'
      AND CAST(h.activity_year AS INT64) BETWEEN 2018 AND 2024
      AND h.loan_purpose = '1'
      -- Standard HMDA filters
      AND h.occupancy_type = '1'
      AND h.reverse_mortgage != '1'
      AND h.construction_method = '1'
      AND h.total_units IN ('1', '2', '3', '4')
),

subject_data AS (
    -- Calculate subject bank metrics
    SELECT
        activity_year,
        cbsa_code,
        cbsa_name,
        COUNT(*) as subject_total_originations,
        -- MMCT metrics (Majority Minority Census Tracts)
        COUNTIF(tract_minority_pct > 50) as subject_mmct_50_originations,
        COUNTIF(tract_minority_pct > 80) as subject_mmct_80_originations,
        -- Black tract metrics
        COUNTIF(black_pct > 50) as subject_black_tract_50_originations,
        COUNTIF(black_pct > 80) as subject_black_tract_80_originations,
        -- Hispanic tract metrics
        COUNTIF(hispanic_pct > 50) as subject_hispanic_tract_50_originations,
        COUNTIF(hispanic_pct > 80) as subject_hispanic_tract_80_originations,
        -- Black + Hispanic combined metrics
        COUNTIF(black_and_hispanic_pct > 50) as subject_black_hispanic_tract_50_originations,
        COUNTIF(black_and_hispanic_pct > 80) as subject_black_hispanic_tract_80_originations
    FROM hmda_with_geography
    WHERE lei = 'QFROUN1UWUYU0DVIWD51'
    GROUP BY activity_year, cbsa_code, cbsa_name
),

peer_data AS (
    -- Calculate peer banks metrics
    SELECT
        h.activity_year,
        h.cbsa_code,
        h.cbsa_name,
        COUNT(*) as peer_total_originations,
        -- MMCT metrics
        COUNTIF(h.tract_minority_pct > 50) as peer_mmct_50_originations,
        COUNTIF(h.tract_minority_pct > 80) as peer_mmct_80_originations,
        -- Black tract metrics
        COUNTIF(h.black_pct > 50) as peer_black_tract_50_originations,
        COUNTIF(h.black_pct > 80) as peer_black_tract_80_originations,
        -- Hispanic tract metrics
        COUNTIF(h.hispanic_pct > 50) as peer_hispanic_tract_50_originations,
        COUNTIF(h.hispanic_pct > 80) as peer_hispanic_tract_80_originations,
        -- Black + Hispanic combined metrics
        COUNTIF(h.black_and_hispanic_pct > 50) as peer_black_hispanic_tract_50_originations,
        COUNTIF(h.black_and_hispanic_pct > 80) as peer_black_hispanic_tract_80_originations
    FROM hmda_with_geography h
    INNER JOIN peers p
          ON h.lei = p.lei
          AND h.activity_year = p.activity_year
          AND h.cbsa_code = p.cbsa_code
    GROUP BY h.activity_year, h.cbsa_code, h.cbsa_name
)

-- Final output: Combine subject and peer data
SELECT
    s.activity_year as activity_year,
    s.cbsa_code as cbsa_code,
    s.cbsa_name as cbsa_name,
    'Home Purchase' as loan_purpose_category,
    'Fifth Third Bank' as lender_name,
    s.subject_total_originations,
    s.subject_mmct_50_originations,
    s.subject_mmct_80_originations,
    s.subject_black_tract_50_originations,
    s.subject_black_tract_80_originations,
    s.subject_hispanic_tract_50_originations,
    s.subject_hispanic_tract_80_originations,
    s.subject_black_hispanic_tract_50_originations,
    s.subject_black_hispanic_tract_80_originations,
    COALESCE(p.peer_total_originations, 0) as peer_total_originations,
    COALESCE(p.peer_mmct_50_originations, 0) as peer_mmct_50_originations,
    COALESCE(p.peer_mmct_80_originations, 0) as peer_mmct_80_originations,
    COALESCE(p.peer_black_tract_50_originations, 0) as peer_black_tract_50_originations,
    COALESCE(p.peer_black_tract_80_originations, 0) as peer_black_tract_80_originations,
    COALESCE(p.peer_hispanic_tract_50_originations, 0) as peer_hispanic_tract_50_originations,
    COALESCE(p.peer_hispanic_tract_80_originations, 0) as peer_hispanic_tract_80_originations,
    COALESCE(p.peer_black_hispanic_tract_50_originations, 0) as peer_black_hispanic_tract_50_originations,
    COALESCE(p.peer_black_hispanic_tract_80_originations, 0) as peer_black_hispanic_tract_80_originations
FROM subject_data s
LEFT JOIN peer_data p
    ON s.activity_year = p.activity_year
    AND s.cbsa_code = p.cbsa_code
ORDER BY s.activity_year, s.cbsa_code;
