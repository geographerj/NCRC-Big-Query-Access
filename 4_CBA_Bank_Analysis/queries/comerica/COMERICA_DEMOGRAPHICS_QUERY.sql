-- Comerica Bank Borrower Demographics Analysis - Complete Query
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
    -- Find the top 10 CBSAs by Comerica home purchase originations
    SELECT 
        c.cbsa_code,
        COUNT(*) as total_originations
    FROM `hdma1-242116.hmda.hmda` h
    LEFT JOIN cbsa_crosswalk c
        ON h.county_code = c.county_code
    WHERE h.lei = '70WY0ID1N53Q4254VH70'  -- Comerica Bank
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
    WHERE h.lei = '70WY0ID1N53Q4254VH70'  -- Comerica Bank
      AND CAST(h.activity_year AS INT64) BETWEEN 2018 AND 2024
      AND h.loan_purpose = '1'
      AND h.action_taken = '1'
      -- Standard HMDA filters
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
      -- Standard HMDA filters
      AND h.occupancy_type = '1'
      AND h.reverse_mortgage != '1'
      AND h.construction_method = '1'
      AND h.total_units IN ('1', '2', '3', '4')
    GROUP BY h.activity_year, c.cbsa_code, h.lei
),

peers AS (
    -- Identify peer lenders (50%-200% of subject's volume, excluding subject)
    SELECT DISTINCT
        al.activity_year,
        al.cbsa_code,
        al.lei
    FROM all_lenders al
    INNER JOIN subject_volume sv
        ON al.activity_year = sv.activity_year
        AND al.cbsa_code = sv.cbsa_code
    WHERE al.lei != '70WY0ID1N53Q4254VH70'  -- Exclude Comerica
      AND al.lender_vol >= sv.subject_vol * 0.5
      AND al.lender_vol <= sv.subject_vol * 2.0
),

hmda_with_demographics AS (
    -- Join HMDA data with borrower demographics classification
    SELECT
        h.activity_year,
        c.cbsa_code,
        c.cbsa_name,
        h.lei,
        h.loan_purpose,
        -- Borrower race/ethnicity classification (NCRC methodology)
        -- Hispanic checked FIRST (regardless of race)
        CASE 
            WHEN h.applicant_ethnicity_1 IN ('1', '11', '12', '13', '14')
                OR h.applicant_ethnicity_2 IN ('1', '11', '12', '13', '14')
                OR h.applicant_ethnicity_3 IN ('1', '11', '12', '13', '14')
                OR h.applicant_ethnicity_4 IN ('1', '11', '12', '13', '14')
                OR h.applicant_ethnicity_5 IN ('1', '11', '12', '13', '14')
            THEN 1 ELSE 0 
        END as is_hispanic,
        -- Non-Hispanic race categories
        CASE 
            WHEN (h.applicant_ethnicity_1 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_1 IS NULL)
                AND (h.applicant_ethnicity_2 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_2 IS NULL)
                AND (h.applicant_ethnicity_3 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_3 IS NULL)
                AND (h.applicant_ethnicity_4 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_4 IS NULL)
                AND (h.applicant_ethnicity_5 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_5 IS NULL)
                AND (
                    h.applicant_race_1 = '3' OR h.applicant_race_2 = '3' 
                    OR h.applicant_race_3 = '3' OR h.applicant_race_4 = '3' OR h.applicant_race_5 = '3'
                )
            THEN 1 ELSE 0 
        END as is_black,
        CASE 
            WHEN (h.applicant_ethnicity_1 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_1 IS NULL)
                AND (h.applicant_ethnicity_2 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_2 IS NULL)
                AND (h.applicant_ethnicity_3 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_3 IS NULL)
                AND (h.applicant_ethnicity_4 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_4 IS NULL)
                AND (h.applicant_ethnicity_5 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_5 IS NULL)
                AND (
                    h.applicant_race_1 IN ('2', '21', '22', '23', '24', '25', '26', '27')
                    OR h.applicant_race_2 IN ('2', '21', '22', '23', '24', '25', '26', '27')
                    OR h.applicant_race_3 IN ('2', '21', '22', '23', '24', '25', '26', '27')
                    OR h.applicant_race_4 IN ('2', '21', '22', '23', '24', '25', '26', '27')
                    OR h.applicant_race_5 IN ('2', '21', '22', '23', '24', '25', '26', '27')
                )
            THEN 1 ELSE 0 
        END as is_asian,
        CASE 
            WHEN (h.applicant_ethnicity_1 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_1 IS NULL)
                AND (h.applicant_ethnicity_2 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_2 IS NULL)
                AND (h.applicant_ethnicity_3 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_3 IS NULL)
                AND (h.applicant_ethnicity_4 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_4 IS NULL)
                AND (h.applicant_ethnicity_5 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_5 IS NULL)
                AND (
                    h.applicant_race_1 = '1' OR h.applicant_race_2 = '1' 
                    OR h.applicant_race_3 = '1' OR h.applicant_race_4 = '1' OR h.applicant_race_5 = '1'
                )
            THEN 1 ELSE 0 
        END as is_native_american,
        CASE 
            WHEN (h.applicant_ethnicity_1 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_1 IS NULL)
                AND (h.applicant_ethnicity_2 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_2 IS NULL)
                AND (h.applicant_ethnicity_3 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_3 IS NULL)
                AND (h.applicant_ethnicity_4 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_4 IS NULL)
                AND (h.applicant_ethnicity_5 NOT IN ('1', '11', '12', '13', '14') OR h.applicant_ethnicity_5 IS NULL)
                AND (
                    h.applicant_race_1 IN ('4', '41', '42', '43', '44')
                    OR h.applicant_race_2 IN ('4', '41', '42', '43', '44')
                    OR h.applicant_race_3 IN ('4', '41', '42', '43', '44')
                    OR h.applicant_race_4 IN ('4', '41', '42', '43', '44')
                    OR h.applicant_race_5 IN ('4', '41', '42', '43', '44')
                )
            THEN 1 ELSE 0 
        END as is_hopi,
        -- Income metrics
        CASE 
            WHEN h.ffiec_msa_md_median_family_income > 0
                AND (CAST(h.income AS INT64) * 1000.0 / h.ffiec_msa_md_median_family_income * 100) <= 80
            THEN 1 ELSE 0 
        END as is_lmib,
        CASE 
            WHEN h.tract_to_msa_income_percentage <= 80
            THEN 1 ELSE 0 
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
        loan_purpose,
        COUNT(*) as total_originations,
        SUM(is_hispanic) as hispanic_count,
        SUM(is_black) as black_count,
        SUM(is_asian) as asian_count,
        SUM(is_native_american) as native_american_count,
        SUM(is_hopi) as hopi_count,
        SUM(is_lmib) as lmib_count,
        SUM(is_lmict) as lmict_count
    FROM hmda_with_demographics
    WHERE lei = '70WY0ID1N53Q4254VH70'  -- Comerica Bank
    GROUP BY activity_year, cbsa_code, cbsa_name, loan_purpose
),

peer_data AS (
    -- Calculate peer group metrics
    SELECT
        h.activity_year,
        h.cbsa_code,
        h.cbsa_name,
        h.loan_purpose,
        COUNT(*) as total_originations,
        SUM(h.is_hispanic) as hispanic_count,
        SUM(h.is_black) as black_count,
        SUM(h.is_asian) as asian_count,
        SUM(h.is_native_american) as native_american_count,
        SUM(h.is_hopi) as hopi_count,
        SUM(h.is_lmib) as lmib_count,
        SUM(h.is_lmict) as lmict_count
    FROM hmda_with_demographics h
    INNER JOIN peers p
        ON h.lei = p.lei
        AND h.activity_year = p.activity_year
        AND h.cbsa_code = p.cbsa_code
    GROUP BY h.activity_year, h.cbsa_code, h.cbsa_name, h.loan_purpose
)

-- Final output: Subject vs Peer comparison (match Fifth Third format)
SELECT
    s.activity_year as activity_year,
    s.cbsa_code as cbsa_code,
    s.cbsa_name as cbsa_name,
    'Home Purchase' as loan_purpose_category,
    'Comerica Bank' as lender_name,
    s.total_originations as subject_total_originations,
    -- Borrower demographics
    s.hispanic_count as subject_hispanic_originations,
    s.black_count as subject_black_originations,
    s.asian_count as subject_asian_originations,
    s.native_american_count as subject_native_american_originations,
    s.hopi_count as subject_hopi_originations,
    -- LMIB
    s.lmib_count as subject_lmib_originations,
    -- LMICT
    s.lmict_count as subject_lmict_originations,
    COALESCE(p.total_originations, 0) as peer_total_originations,
    -- Borrower demographics (peer)
    COALESCE(p.hispanic_count, 0) as peer_hispanic_originations,
    COALESCE(p.black_count, 0) as peer_black_originations,
    COALESCE(p.asian_count, 0) as peer_asian_originations,
    COALESCE(p.native_american_count, 0) as peer_native_american_originations,
    COALESCE(p.hopi_count, 0) as peer_hopi_originations,
    -- LMIB (peer)
    COALESCE(p.lmib_count, 0) as peer_lmib_originations,
    -- LMICT (peer)
    COALESCE(p.lmict_count, 0) as peer_lmict_originations
FROM subject_data s
LEFT JOIN peer_data p
    ON s.activity_year = p.activity_year
    AND s.cbsa_code = p.cbsa_code
    AND s.loan_purpose = p.loan_purpose
WHERE s.loan_purpose = '1'  -- Home Purchase only
ORDER BY s.activity_year, s.cbsa_code;

