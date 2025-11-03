-- Fifth Third Bank Borrower Demographics Analysis - Complete Query
-- Home Purchase loans, Top 10 CBSAs by originations (2018-2024)
-- Borrower demographic metrics: Hispanic, Black, Asian, Native American, HoPI, MINB
-- Plus LMICT (Low-to-Moderate Income Census Tracts)
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

hmda_with_classifications AS (
    -- Classify borrowers using NCRC methodology and add LMICT flag
    SELECT
        h.activity_year,
        c.cbsa_code,
        c.cbsa_name,
        h.lei,
        -- NCRC Hierarchical Borrower Classification
        -- Step 1: Check ethnicity first (Hispanic takes precedence)
        CASE 
            WHEN h.applicant_ethnicity_1 IN ('1', '11', '12', '13', '14')
              OR h.applicant_ethnicity_2 IN ('1', '11', '12', '13', '14')
              OR h.applicant_ethnicity_3 IN ('1', '11', '12', '13', '14')
              OR h.applicant_ethnicity_4 IN ('1', '11', '12', '13', '14')
              OR h.applicant_ethnicity_5 IN ('1', '11', '12', '13', '14')
            THEN 'Hispanic'
            -- Step 2: If not Hispanic, classify by race
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
        -- LMIB: Low-to-Moderate Income Borrowers (borrower income ≤80% of MSA median)
        CASE 
            WHEN h.applicant_income_percentage_of_msamd IS NOT NULL
              AND CAST(h.applicant_income_percentage_of_msamd AS FLOAT64) <= 80
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
        -- Borrower demographics
        COUNTIF(borrower_category = 'Hispanic') as subject_hispanic_originations,
        COUNTIF(borrower_category = 'Black') as subject_black_originations,
        COUNTIF(borrower_category = 'Asian') as subject_asian_originations,
        COUNTIF(borrower_category = 'Native American') as subject_native_american_originations,
        COUNTIF(borrower_category = 'HoPI') as subject_hopi_originations,
        -- LMIB
        COUNTIF(is_lmib = 1) as subject_lmib_originations,
        -- LMICT
        COUNTIF(is_lmict = 1) as subject_lmict_originations
    FROM hmda_with_classifications
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
        -- LMIB
        COUNTIF(h.is_lmib = 1) as peer_lmib_originations,
        -- LMICT
        COUNTIF(h.is_lmict = 1) as peer_lmict_originations
    FROM hmda_with_classifications h
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
    -- Borrower demographics
    s.subject_hispanic_originations,
    s.subject_black_originations,
    s.subject_asian_originations,
    s.subject_native_american_originations,
    s.subject_hopi_originations,
    -- LMIB
    s.subject_lmib_originations,
    -- LMICT
    s.subject_lmict_originations,
    COALESCE(p.peer_total_originations, 0) as peer_total_originations,
    -- Borrower demographics (peer)
    COALESCE(p.peer_hispanic_originations, 0) as peer_hispanic_originations,
    COALESCE(p.peer_black_originations, 0) as peer_black_originations,
    COALESCE(p.peer_asian_originations, 0) as peer_asian_originations,
    COALESCE(p.peer_native_american_originations, 0) as peer_native_american_originations,
    COALESCE(p.peer_hopi_originations, 0) as peer_hopi_originations,
    -- LMIB (peer)
    COALESCE(p.peer_lmib_originations, 0) as peer_lmib_originations,
    -- LMICT (peer)
    COALESCE(p.peer_lmict_originations, 0) as peer_lmict_originations
FROM subject_data s
LEFT JOIN peer_data p
    ON s.activity_year = p.activity_year
    AND s.cbsa_code = p.cbsa_code
ORDER BY s.activity_year, s.cbsa_code;

