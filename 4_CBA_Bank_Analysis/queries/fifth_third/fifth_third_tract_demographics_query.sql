-- BigQuery SQL Query for Fifth Third Bank CBA Analysis with Tract Demographics
-- Generates CSV input for ncrc_worst_lenders_analysis_v4.py Excel generator
--
-- This query calculates originations by tract demographics for:
-- - Subject Bank: Fifth Third Bank (LEI: QFROUN1UWUYU0DVIWD51)
-- - Peer Banks: All other lenders in same CBSA with 50%-200% of subject's volume
--
-- Metrics Calculated:
-- 1. MMCT 50% and 80% (Minority percentage >50%, >80%)
-- 2. Black Tract 50% and 80% (Black percentage >50%, >80%)  
-- 3. Hispanic Tract 50% and 80% (Hispanic percentage >50%, >80%)
-- 4. Black+Hispanic Tract 50% and 80% (Black+Hispanic percentage >50%, >80%)

-- Geo table: hdma1-242116.geo.black_hispanic_majority
-- Key field: geoid (matching HMDA census_tract)

WITH subject_volume AS (
    -- Get subject bank's volume by CBSA, year, and loan purpose
    SELECT
        activity_year,
        cbsa_code,
        loan_purpose,
        COUNT(*) as subject_vol
    FROM `hdma1-242116.hmda.hmda`
    WHERE lei = 'QFROUN1UWUYU0DVIWD51'  -- Fifth Third Bank
      AND action_taken = '1'
      AND activity_year BETWEEN 2018 AND 2024
    GROUP BY activity_year, cbsa_code, loan_purpose
),

all_lenders AS (
    -- Get all lenders' volume for peer comparison
    SELECT
        activity_year,
        cbsa_code,
        loan_purpose,
        lei,
        COUNT(*) as lender_vol
    FROM `hdma1-242116.hmda.hmda`
    WHERE action_taken = '1'
      AND activity_year BETWEEN 2018 AND 2024
    GROUP BY activity_year, cbsa_code, loan_purpose, lei
),

peers AS (
    -- Identify peer lenders (50%-200% of subject's volume)
    SELECT DISTINCT
        av.activity_year,
        av.cbsa_code,
        av.loan_purpose,
        av.lei
    FROM all_lenders av
    INNER JOIN subject_volume sv
        ON av.activity_year = sv.activity_year
        AND av.cbsa_code = sv.cbsa_code
        AND av.loan_purpose = sv.loan_purpose
    WHERE av.lender_vol >= sv.subject_vol * 0.5
      AND av.lender_vol <= sv.subject_vol * 2.0
      AND av.lei != 'QFROUN1UWUYU0DVIWD51'
),

hmda_with_geography AS (
    -- Join HMDA data with tract demographics
    SELECT
        h.activity_year,
        h.cbsa_code,
        h.loan_purpose,
        h.lei,
        -- Tract demographic percentages from geo table
        g.black_pct,
        g.hispanic_pct,
        g.black_and_hispanic_pct,
        -- Get minority percentage from HMDA table
        h.tract_minority_population_percent as tract_minority_pct
    FROM `hdma1-242116.hmda.hmda` h
    LEFT JOIN `hdma1-242116.geo.black_hispanic_majority` g
        ON CAST(h.census_tract AS STRING) = CAST(g.geoid AS STRING)
    WHERE h.action_taken = '1'
      AND h.activity_year BETWEEN 2018 AND 2024
      -- Standard HMDA filters (confirmed from FFIEC documentation)
      AND h.occupancy_type = '1'  -- Owner-occupied (1=Owner-occupied)
      AND h.reverse_mortgage != '1'  -- Not reverse mortgage (1=Reverse mortgage)
      -- Site-built 1-4 unit property filter (construction_method: 1=Site-built, 2=Manufactured home)
      AND h.construction_method = '1'  -- Site-built only
      AND h.total_units IN ('1', '2', '3', '4')  -- 1-4 unit properties
),

subject_data AS (
    -- Calculate subject bank metrics
    SELECT
        activity_year,
        cbsa_code,
        CASE 
            WHEN loan_purpose = '1' THEN 'Home Purchase'
            WHEN loan_purpose IN ('1', '2', '31', '32') THEN 'All Purposes'
        END as loan_purpose_category,
        COUNT(*) as subject_total_originations,
        -- MMCT metrics
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
    GROUP BY activity_year, cbsa_code, loan_purpose_category
),

peer_data AS (
    -- Calculate peer banks metrics
    SELECT
        activity_year,
        cbsa_code,
        CASE 
            WHEN loan_purpose = '1' THEN 'Home Purchase'
            WHEN loan_purpose IN ('1', '2', '31', '32') THEN 'All Purposes'
        END as loan_purpose_category,
        COUNT(*) as peer_total_originations,
        -- MMCT metrics
        COUNTIF(tract_minority_pct > 50) as peer_mmct_50_originations,
        COUNTIF(tract_minority_pct > 80) as peer_mmct_80_originations,
        -- Black tract metrics
        COUNTIF(black_pct > 50) as peer_black_tract_50_originations,
        COUNTIF(black_pct > 80) as peer_black_tract_80_originations,
        -- Hispanic tract metrics
        COUNTIF(hispanic_pct > 50) as peer_hispanic_tract_50_originations,
        COUNTIF(hispanic_pct > 80) as peer_hispanic_tract_80_originations,
        -- Black + Hispanic combined metrics
        COUNTIF(black_and_hispanic_pct > 50) as peer_black_hispanic_tract_50_originations,
        COUNTIF(black_and_hispanic_pct > 80) as peer_black_hispanic_tract_80_originations
    FROM hmda_with_geography
    WHERE lei IN (SELECT lei FROM peers)
    GROUP BY activity_year, cbsa_code, loan_purpose_category
)

-- Final output: Combine subject and peer data
SELECT
    s.activity_year as activity_year,
    s.cbsa_code as cbsa_code,
    s.loan_purpose_category as loan_purpose_category,
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
    AND s.loan_purpose_category = p.loan_purpose_category
ORDER BY s.activity_year, s.cbsa_code, s.loan_purpose_category;

