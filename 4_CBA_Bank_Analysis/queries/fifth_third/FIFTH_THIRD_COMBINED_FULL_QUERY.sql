-- Fifth Third Bank Combined Analysis - Complete Query
-- Home Purchase loans, Top 10 CBSAs by originations (2018-2024)
-- Combines: Redlining (tract demographics) + Borrower Demographics + Income Metrics
-- Uses CBSA crosswalk via county_code (GEOID5) join

WITH cbsa_crosswalk AS (
    -- Load the CBSA crosswalk data from BigQuery table
    SELECT
        geoid5 as county_code,
        cbsa_code,
        cbsa as cbsa_name,
        County as county_name,
        State as state_name
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

hmda_combined AS (
    -- Combine all classifications: borrower demographics, tract demographics, and income metrics
    SELECT
        h.activity_year,
        c.cbsa_code,
        c.cbsa_name,
        h.lei,
        -- Tract demographics (for redlining metrics)
        h.tract_minority_population_percent as tract_minority_pct,
        g.black_pct,
        g.hispanic_pct,
        g.black_and_hispanic_pct,
        -- Borrower demographics (NCRC methodology)
        CASE 
            WHEN h.applicant_ethnicity_1 IN ('1', '11', '12', '13', '14')
              OR h.applicant_ethnicity_2 IN ('1', '11', '12', '13', '14')
              OR h.applicant_ethnicity_3 IN ('1', '11', '12', '13', '14')
              OR h.applicant_ethnicity_4 IN ('1', '11', '12', '13', '14')
              OR h.applicant_ethnicity_5 IN ('1', '11', '12', '13', '14')
            THEN 'Hispanic'
            WHEN h.applicant_race_1 = '3' OR h.applicant_race_2 = '3' 
              OR h.applicant_race_3 = '3' OR h.applicant_race_4 = '3' 
              OR h.applicant_race_5 = '3'
            THEN 'Black'
            WHEN h.applicant_race_1 IN ('2', '21', '22', '23', '24', '25', '26', '27')
              OR h.applicant_race_2 IN ('2', '21', '22', '23', '24', '25', '26', '27')
              OR h.applicant_race_3 IN ('2', '21', '22', '23', '24', '25', '26', '27')
              OR h.applicant_race_4 IN ('2', '21', '22', '23', '24', '25', '26', '27')
              OR h.applicant_race_5 IN ('2', '21', '22', '23', '24', '25', '26', '27')
            THEN 'Asian'
            WHEN h.applicant_race_1 = '1' OR h.applicant_race_2 = '1' 
              OR h.applicant_race_3 = '1' OR h.applicant_race_4 = '1' 
              OR h.applicant_race_5 = '1'
            THEN 'Native American'
            WHEN h.applicant_race_1 IN ('4', '41', '42', '43', '44')
              OR h.applicant_race_2 IN ('4', '41', '42', '43', '44')
              OR h.applicant_race_3 IN ('4', '41', '42', '43', '44')
              OR h.applicant_race_4 IN ('4', '41', '42', '43', '44')
              OR h.applicant_race_5 IN ('4', '41', '42', '43', '44')
            THEN 'HoPI'
            WHEN h.applicant_race_1 = '5' OR h.applicant_race_2 = '5' 
              OR h.applicant_race_3 = '5' OR h.applicant_race_4 = '5' 
              OR h.applicant_race_5 = '5'
            THEN 'White'
            ELSE 'Unknown'
        END as borrower_category,
        -- Income metrics
        -- LMIB: Low-to-Moderate Income Borrowers (borrower income ≤80% of MSA median)
        -- Calculate: (income * 1000) / ffiec_msa_md_median_family_income * 100
        CASE 
            WHEN h.income IS NOT NULL
              AND h.ffiec_msa_md_median_family_income IS NOT NULL
              AND h.ffiec_msa_md_median_family_income > 0
              AND (CAST(h.income AS FLOAT64) * 1000.0) / 
                  CAST(h.ffiec_msa_md_median_family_income AS FLOAT64) * 100.0 <= 80.0
            THEN 1 
            ELSE 0 
        END as is_lmib,
        -- LMICT: Low-to-Moderate Income Census Tracts (tract income ≤80% of MSA median)
        CASE 
            WHEN h.tract_to_msa_income_percentage IS NOT NULL
              AND CAST(h.tract_to_msa_income_percentage AS FLOAT64) <= 80
            THEN 1 
            ELSE 0 
        END as is_lmict
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

county_info AS (
    -- Aggregate county names by CBSA
    SELECT
        cbsa_code,
        STRING_AGG(DISTINCT CONCAT(county_name, ', ', state_name), ', ' ORDER BY CONCAT(county_name, ', ', state_name)) as counties_list
    FROM cbsa_crosswalk
    GROUP BY cbsa_code
),

subject_data AS (
    -- Calculate subject bank metrics - ALL metrics from one consistent dataset
    SELECT
        activity_year,
        cbsa_code,
        cbsa_name,
        COUNT(*) as subject_total_originations,
        -- Borrower demographics
        COUNTIF(borrower_category = 'Hispanic') as subject_hispanic_originations,
        COUNTIF(borrower_category = 'Black') as subject_black_originations,
        COUNTIF(borrower_category = 'Asian') as subject_asian_originations,
        COUNTIF(borrower_category = 'Native American') as subject_native_american_originations,
        COUNTIF(borrower_category = 'HoPI') as subject_hopi_originations,
        -- Income metrics
        COUNTIF(is_lmib = 1) as subject_lmib_originations,
        COUNTIF(is_lmict = 1) as subject_lmict_originations,
        -- Redlining metrics (tract-level demographics)
        COUNTIF(tract_minority_pct > 50) as subject_mmct_50_originations,
        COUNTIF(tract_minority_pct > 80) as subject_mmct_80_originations,
        COUNTIF(black_pct > 50) as subject_black_tract_50_originations,
        COUNTIF(black_pct > 80) as subject_black_tract_80_originations,
        COUNTIF(hispanic_pct > 50) as subject_hispanic_tract_50_originations,
        COUNTIF(hispanic_pct > 80) as subject_hispanic_tract_80_originations,
        COUNTIF(black_and_hispanic_pct > 50) as subject_black_hispanic_tract_50_originations,
        COUNTIF(black_and_hispanic_pct > 80) as subject_black_hispanic_tract_80_originations
    FROM hmda_combined
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
        -- Borrower demographics
        COUNTIF(h.borrower_category = 'Hispanic') as peer_hispanic_originations,
        COUNTIF(h.borrower_category = 'Black') as peer_black_originations,
        COUNTIF(h.borrower_category = 'Asian') as peer_asian_originations,
        COUNTIF(h.borrower_category = 'Native American') as peer_native_american_originations,
        COUNTIF(h.borrower_category = 'HoPI') as peer_hopi_originations,
        -- Income metrics
        COUNTIF(h.is_lmib = 1) as peer_lmib_originations,
        COUNTIF(h.is_lmict = 1) as peer_lmict_originations,
        -- Redlining metrics
        COUNTIF(h.tract_minority_pct > 50) as peer_mmct_50_originations,
        COUNTIF(h.tract_minority_pct > 80) as peer_mmct_80_originations,
        COUNTIF(h.black_pct > 50) as peer_black_tract_50_originations,
        COUNTIF(h.black_pct > 80) as peer_black_tract_80_originations,
        COUNTIF(h.hispanic_pct > 50) as peer_hispanic_tract_50_originations,
        COUNTIF(h.hispanic_pct > 80) as peer_hispanic_tract_80_originations,
        COUNTIF(h.black_and_hispanic_pct > 50) as peer_black_hispanic_tract_50_originations,
        COUNTIF(h.black_and_hispanic_pct > 80) as peer_black_hispanic_tract_80_originations
    FROM hmda_combined h
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
    COALESCE(ci.counties_list, '') as counties_included,
    'Home Purchase' as loan_purpose_category,
    'Fifth Third Bank' as lender_name,
    s.subject_total_originations,
    -- Borrower demographics
    s.subject_hispanic_originations,
    s.subject_black_originations,
    s.subject_asian_originations,
    s.subject_native_american_originations,
    s.subject_hopi_originations,
    -- Income metrics
    s.subject_lmib_originations,
    s.subject_lmict_originations,
    -- Redlining metrics
    s.subject_mmct_50_originations,
    s.subject_mmct_80_originations,
    s.subject_black_tract_50_originations,
    s.subject_black_tract_80_originations,
    s.subject_hispanic_tract_50_originations,
    s.subject_hispanic_tract_80_originations,
    s.subject_black_hispanic_tract_50_originations,
    s.subject_black_hispanic_tract_80_originations,
    COALESCE(p.peer_total_originations, 0) as peer_total_originations,
    -- Borrower demographics (peer)
    COALESCE(p.peer_hispanic_originations, 0) as peer_hispanic_originations,
    COALESCE(p.peer_black_originations, 0) as peer_black_originations,
    COALESCE(p.peer_asian_originations, 0) as peer_asian_originations,
    COALESCE(p.peer_native_american_originations, 0) as peer_native_american_originations,
    COALESCE(p.peer_hopi_originations, 0) as peer_hopi_originations,
    -- Income metrics (peer)
    COALESCE(p.peer_lmib_originations, 0) as peer_lmib_originations,
    COALESCE(p.peer_lmict_originations, 0) as peer_lmict_originations,
    -- Redlining metrics (peer)
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
LEFT JOIN county_info ci
    ON s.cbsa_code = ci.cbsa_code
ORDER BY s.activity_year, s.cbsa_code;

