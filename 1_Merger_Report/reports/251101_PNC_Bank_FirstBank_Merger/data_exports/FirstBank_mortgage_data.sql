-- Subject Bank

-- Goal-Setting Analysis: HMDA Data Query
-- Subject Bank: 5493009V3WNJX9V2GZ85
-- Assessment Area Counties: 26 counties
-- Years: 2020, 2021, 2022, 2023, 2024

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

assessment_area_counties AS (
    -- Filter to only assessment area counties using GEOID5
    SELECT DISTINCT
        '04013', '04021', '06065', '06071', '08037', '08045', '08049', '08057', '08065', '08097', '08107', '08117', '08041', '08119', '08001', '08005', '08013', '08014', '08019', '08031', '08035', '08047', '08059', '08093', '08123', '08069' as geoid5
    FROM UNNEST(['04013', '04021', '06065', '06071', '08037', '08045', '08049', '08057', '08065', '08097', '08107', '08117', '08041', '08119', '08001', '08005', '08013', '08014', '08019', '08031', '08035', '08047', '08059', '08093', '08123', '08069']) as geoid5
),

filtered_hmda AS (
    -- Filter HMDA data early: years, LEI, assessment area counties, standard filters
    SELECT 
        CAST(h.activity_year AS STRING) as activity_year,
        c.cbsa_code,
        CAST(h.county_code AS STRING) as county_code,
        h.census_tract,
        h.loan_amount,
        -- Pre-calculate flags in SQL (more efficient)
        CASE 
            WHEN h.tract_to_msa_income_percentage IS NOT NULL
                AND CAST(h.tract_to_msa_income_percentage AS FLOAT64) <= 80 
            THEN 1 ELSE 0 
        END as is_lmict,
        -- LMIB: Calculate borrower income as % of MSA median
        -- Use calculated approach: (income * 1000) / ffiec_msa_md_median_family_income * 100
        CASE 
            WHEN h.income IS NOT NULL
              AND h.ffiec_msa_md_median_family_income IS NOT NULL
              AND h.ffiec_msa_md_median_family_income > 0
              AND (CAST(h.income AS FLOAT64) * 1000.0) / 
                  CAST(h.ffiec_msa_md_median_family_income AS FLOAT64) * 100.0 <= 80.0
            THEN 1 
            ELSE 0 
        END as is_lmib,
        CASE 
            WHEN h.tract_minority_population_percent IS NOT NULL
                AND CAST(h.tract_minority_population_percent AS FLOAT64) > 50 
            THEN 1 ELSE 0 
        END as is_mmct,
        -- Borrower demographics (NCRC methodology: Hispanic checked first)
        CASE 
            WHEN h.applicant_ethnicity_1 IN ('1','11','12','13','14')
                OR h.applicant_ethnicity_2 IN ('1','11','12','13','14')
                OR h.applicant_ethnicity_3 IN ('1','11','12','13','14')
                OR h.applicant_ethnicity_4 IN ('1','11','12','13','14')
                OR h.applicant_ethnicity_5 IN ('1','11','12','13','14')
            THEN 1 ELSE 0 
        END as is_hispanic,
        CASE 
            WHEN h.applicant_ethnicity_1 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_2 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_3 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_4 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_5 NOT IN ('1','11','12','13','14')
                AND (h.applicant_race_1 = '3' OR h.applicant_race_2 = '3' 
                     OR h.applicant_race_3 = '3' OR h.applicant_race_4 = '3' 
                     OR h.applicant_race_5 = '3')
            THEN 1 ELSE 0 
        END as is_black,
        CASE 
            WHEN h.applicant_ethnicity_1 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_2 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_3 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_4 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_5 NOT IN ('1','11','12','13','14')
                AND (h.applicant_race_1 IN ('2','21','22','23','24','25','26','27')
                     OR h.applicant_race_2 IN ('2','21','22','23','24','25','26','27')
                     OR h.applicant_race_3 IN ('2','21','22','23','24','25','26','27')
                     OR h.applicant_race_4 IN ('2','21','22','23','24','25','26','27')
                     OR h.applicant_race_5 IN ('2','21','22','23','24','25','26','27'))
            THEN 1 ELSE 0 
        END as is_asian,
        CASE 
            WHEN h.applicant_ethnicity_1 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_2 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_3 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_4 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_5 NOT IN ('1','11','12','13','14')
                AND (h.applicant_race_1 = '1' OR h.applicant_race_2 = '1' 
                     OR h.applicant_race_3 = '1' OR h.applicant_race_4 = '1' 
                     OR h.applicant_race_5 = '1')
            THEN 1 ELSE 0 
        END as is_native_american,
        CASE 
            WHEN h.applicant_ethnicity_1 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_2 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_3 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_4 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_5 NOT IN ('1','11','12','13','14')
                AND (h.applicant_race_1 IN ('4','41','42','43','44')
                     OR h.applicant_race_2 IN ('4','41','42','43','44')
                     OR h.applicant_race_3 IN ('4','41','42','43','44')
                     OR h.applicant_race_4 IN ('4','41','42','43','44')
                     OR h.applicant_race_5 IN ('4','41','42','43','44'))
            THEN 1 ELSE 0 
        END as is_hopi
    FROM `hdma1-242116.hmda.hmda` h
    LEFT JOIN cbsa_crosswalk c
        ON CAST(h.county_code AS STRING) = c.county_code
    WHERE CAST(h.activity_year AS STRING) IN ('2020', '2021', '2022', '2023', '2024')
        AND h.lei = '5493009V3WNJX9V2GZ85'
        AND CAST(h.county_code AS STRING) IN ('04013', '04021', '06065', '06071', '08037', '08045', '08049', '08057', '08065', '08097', '08107', '08117', '08041', '08119', '08001', '08005', '08013', '08014', '08019', '08031', '08035', '08047', '08059', '08093', '08123', '08069')
        AND h.action_taken = '1'  -- Originations only
        -- Standard HMDA filters
        AND h.occupancy_type = '1'  -- Owner-occupied
        AND h.reverse_mortgage != '1'  -- Not reverse mortgage
        AND h.construction_method = '1'  -- Site-built
        AND h.total_units IN ('1', '2', '3', '4')  -- 1-4 units
            AND h.loan_purpose = '1'
),

aggregated_metrics AS (
    -- Aggregate once, calculate all 11 metrics
    SELECT 
        activity_year,
        cbsa_code,
        COUNT(*) as total_loans,
        SUM(loan_amount) as total_amount,
        -- LMICT%
        COUNTIF(is_lmict = 1) as lmict_loans,
        SAFE_DIVIDE(COUNTIF(is_lmict = 1), COUNT(*)) * 100 as lmict_percentage,
        -- LMIB%
        COUNTIF(is_lmib = 1) as lmib_loans,
        SAFE_DIVIDE(COUNTIF(is_lmib = 1), COUNT(*)) * 100 as lmib_percentage,
        -- LMIB$
        SUM(CASE WHEN is_lmib = 1 THEN loan_amount END) as lmib_amount,
        -- MMCT%
        COUNTIF(is_mmct = 1) as mmct_loans,
        SAFE_DIVIDE(COUNTIF(is_mmct = 1), COUNT(*)) * 100 as mmct_percentage,
        -- MINB% (combined minority)
        COUNTIF(is_hispanic = 1 OR is_black = 1 OR is_asian = 1 
                OR is_native_american = 1 OR is_hopi = 1) as minb_loans,
        SAFE_DIVIDE(COUNTIF(is_hispanic = 1 OR is_black = 1 OR is_asian = 1 
                           OR is_native_american = 1 OR is_hopi = 1), COUNT(*)) * 100 as minb_percentage,
        -- Asian%
        COUNTIF(is_asian = 1) as asian_loans,
        SAFE_DIVIDE(COUNTIF(is_asian = 1), COUNT(*)) * 100 as asian_percentage,
        -- Black%
        COUNTIF(is_black = 1) as black_loans,
        SAFE_DIVIDE(COUNTIF(is_black = 1), COUNT(*)) * 100 as black_percentage,
        -- Native American%
        COUNTIF(is_native_american = 1) as native_american_loans,
        SAFE_DIVIDE(COUNTIF(is_native_american = 1), COUNT(*)) * 100 as native_american_percentage,
        -- HoPI%
        COUNTIF(is_hopi = 1) as hopi_loans,
        SAFE_DIVIDE(COUNTIF(is_hopi = 1), COUNT(*)) * 100 as hopi_percentage,
        -- Hispanic%
        COUNTIF(is_hispanic = 1) as hispanic_loans,
        SAFE_DIVIDE(COUNTIF(is_hispanic = 1), COUNT(*)) * 100 as hispanic_percentage
    FROM filtered_hmda
    GROUP BY activity_year, cbsa_code
)

-- Final output: only aggregated summary rows
SELECT * FROM aggregated_metrics
ORDER BY activity_year, cbsa_code


-- Peer Banks

-- Goal-Setting Analysis: Peer HMDA Data Query
-- Subject Bank: 5493009V3WNJX9V2GZ85
-- Assessment Area Counties: 26 counties
-- Years: 2020, 2021, 2022, 2023, 2024
-- Peer Rule: 50%-200% of subject bank's volume by year and CBSA

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

assessment_area_counties AS (
    -- Filter to only assessment area counties using GEOID5
    SELECT DISTINCT geoid5
    FROM UNNEST(['04013', '04021', '06065', '06071', '08037', '08045', '08049', '08057', '08065', '08097', '08107', '08117', '08041', '08119', '08001', '08005', '08013', '08014', '08019', '08031', '08035', '08047', '08059', '08093', '08123', '08069']) as geoid5
),

filtered_hmda AS (
    -- Filter HMDA data early: years, assessment area counties, standard filters
    SELECT 
        CAST(h.activity_year AS STRING) as activity_year,
        c.cbsa_code,
        h.lei,
        CAST(h.county_code AS STRING) as county_code,
        h.loan_amount,
        -- Pre-calculate flags in SQL (same as subject query)
        CASE 
            WHEN h.tract_to_msa_income_percentage IS NOT NULL
                AND CAST(h.tract_to_msa_income_percentage AS FLOAT64) <= 80 
            THEN 1 ELSE 0 
        END as is_lmict,
        -- LMIB: Calculate borrower income as % of MSA median
        -- Use calculated approach: (income * 1000) / ffiec_msa_md_median_family_income * 100
        CASE 
            WHEN h.income IS NOT NULL
              AND h.ffiec_msa_md_median_family_income IS NOT NULL
              AND h.ffiec_msa_md_median_family_income > 0
              AND (CAST(h.income AS FLOAT64) * 1000.0) / 
                  CAST(h.ffiec_msa_md_median_family_income AS FLOAT64) * 100.0 <= 80.0
            THEN 1 
            ELSE 0 
        END as is_lmib,
        CASE 
            WHEN h.tract_minority_population_percent IS NOT NULL
                AND CAST(h.tract_minority_population_percent AS FLOAT64) > 50 
            THEN 1 ELSE 0 
        END as is_mmct,
        -- Borrower demographics (NCRC methodology)
        CASE 
            WHEN h.applicant_ethnicity_1 IN ('1','11','12','13','14')
                OR h.applicant_ethnicity_2 IN ('1','11','12','13','14')
                OR h.applicant_ethnicity_3 IN ('1','11','12','13','14')
                OR h.applicant_ethnicity_4 IN ('1','11','12','13','14')
                OR h.applicant_ethnicity_5 IN ('1','11','12','13','14')
            THEN 1 ELSE 0 
        END as is_hispanic,
        CASE 
            WHEN h.applicant_ethnicity_1 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_2 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_3 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_4 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_5 NOT IN ('1','11','12','13','14')
                AND (h.applicant_race_1 = '3' OR h.applicant_race_2 = '3' 
                     OR h.applicant_race_3 = '3' OR h.applicant_race_4 = '3' 
                     OR h.applicant_race_5 = '3')
            THEN 1 ELSE 0 
        END as is_black,
        CASE 
            WHEN h.applicant_ethnicity_1 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_2 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_3 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_4 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_5 NOT IN ('1','11','12','13','14')
                AND (h.applicant_race_1 IN ('2','21','22','23','24','25','26','27')
                     OR h.applicant_race_2 IN ('2','21','22','23','24','25','26','27')
                     OR h.applicant_race_3 IN ('2','21','22','23','24','25','26','27')
                     OR h.applicant_race_4 IN ('2','21','22','23','24','25','26','27')
                     OR h.applicant_race_5 IN ('2','21','22','23','24','25','26','27'))
            THEN 1 ELSE 0 
        END as is_asian,
        CASE 
            WHEN h.applicant_ethnicity_1 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_2 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_3 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_4 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_5 NOT IN ('1','11','12','13','14')
                AND (h.applicant_race_1 = '1' OR h.applicant_race_2 = '1' 
                     OR h.applicant_race_3 = '1' OR h.applicant_race_4 = '1' 
                     OR h.applicant_race_5 = '1')
            THEN 1 ELSE 0 
        END as is_native_american,
        CASE 
            WHEN h.applicant_ethnicity_1 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_2 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_3 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_4 NOT IN ('1','11','12','13','14')
                AND h.applicant_ethnicity_5 NOT IN ('1','11','12','13','14')
                AND (h.applicant_race_1 IN ('4','41','42','43','44')
                     OR h.applicant_race_2 IN ('4','41','42','43','44')
                     OR h.applicant_race_3 IN ('4','41','42','43','44')
                     OR h.applicant_race_4 IN ('4','41','42','43','44')
                     OR h.applicant_race_5 IN ('4','41','42','43','44'))
            THEN 1 ELSE 0 
        END as is_hopi
    FROM `hdma1-242116.hmda.hmda` h
    LEFT JOIN cbsa_crosswalk c
        ON CAST(h.county_code AS STRING) = c.county_code
    WHERE CAST(h.activity_year AS STRING) IN ('2020', '2021', '2022', '2023', '2024')
        AND CAST(h.county_code AS STRING) IN ('04013', '04021', '06065', '06071', '08037', '08045', '08049', '08057', '08065', '08097', '08107', '08117', '08041', '08119', '08001', '08005', '08013', '08014', '08019', '08031', '08035', '08047', '08059', '08093', '08123', '08069')
        AND h.action_taken = '1'  -- Originations only
        -- Standard HMDA filters
        AND h.occupancy_type = '1'  -- Owner-occupied
        AND h.reverse_mortgage != '1'  -- Not reverse mortgage
        AND h.construction_method = '1'  -- Site-built
        AND h.total_units IN ('1', '2', '3', '4')  -- 1-4 units
            AND h.loan_purpose = '1'
),

subject_volume AS (
    -- Calculate subject bank's volume by year and CBSA for peer matching
    SELECT 
        activity_year,
        cbsa_code,
        COUNT(*) as subject_vol
    FROM filtered_hmda
    WHERE lei = '5493009V3WNJX9V2GZ85'
    GROUP BY activity_year, cbsa_code
),

all_lenders_volume AS (
    -- Calculate all lenders' volumes by year, CBSA, and LEI
    SELECT 
        activity_year,
        cbsa_code,
        lei,
        COUNT(*) as lender_vol
    FROM filtered_hmda
    GROUP BY activity_year, cbsa_code, lei
),

peers AS (
    -- Identify peer lenders (50%-200% of subject's volume) by year and CBSA
    SELECT DISTINCT
        al.activity_year,
        al.cbsa_code,
        al.lei
    FROM all_lenders_volume al
    INNER JOIN subject_volume sv
        ON al.activity_year = sv.activity_year
        AND al.cbsa_code = sv.cbsa_code
    WHERE al.lei != '5493009V3WNJX9V2GZ85'  -- Exclude subject bank
      AND al.lender_vol >= sv.subject_vol * 0.5  -- At least 50% of subject volume
      AND al.lender_vol <= sv.subject_vol * 2.0  -- At most 200% of subject volume
),

peer_hmda AS (
    -- Filter to only peer lenders' loans
    SELECT f.*
    FROM filtered_hmda f
    INNER JOIN peers p
        ON f.activity_year = p.activity_year
        AND f.cbsa_code = p.cbsa_code
        AND f.lei = p.lei
),

aggregated_peer_metrics AS (
    -- Aggregate peer metrics by year and CBSA (same structure as subject query)
    SELECT 
        activity_year,
        cbsa_code,
        COUNT(*) as total_loans,
        SUM(loan_amount) as total_amount,
        -- LMICT%
        COUNTIF(is_lmict = 1) as lmict_loans,
        SAFE_DIVIDE(COUNTIF(is_lmict = 1), COUNT(*)) * 100 as lmict_percentage,
        -- LMIB%
        COUNTIF(is_lmib = 1) as lmib_loans,
        SAFE_DIVIDE(COUNTIF(is_lmib = 1), COUNT(*)) * 100 as lmib_percentage,
        -- LMIB$
        SUM(CASE WHEN is_lmib = 1 THEN loan_amount END) as lmib_amount,
        -- MMCT%
        COUNTIF(is_mmct = 1) as mmct_loans,
        SAFE_DIVIDE(COUNTIF(is_mmct = 1), COUNT(*)) * 100 as mmct_percentage,
        -- MINB% (combined minority)
        COUNTIF(is_hispanic = 1 OR is_black = 1 OR is_asian = 1 
                OR is_native_american = 1 OR is_hopi = 1) as minb_loans,
        SAFE_DIVIDE(COUNTIF(is_hispanic = 1 OR is_black = 1 OR is_asian = 1 
                           OR is_native_american = 1 OR is_hopi = 1), COUNT(*)) * 100 as minb_percentage,
        -- Asian%
        COUNTIF(is_asian = 1) as asian_loans,
        SAFE_DIVIDE(COUNTIF(is_asian = 1), COUNT(*)) * 100 as asian_percentage,
        -- Black%
        COUNTIF(is_black = 1) as black_loans,
        SAFE_DIVIDE(COUNTIF(is_black = 1), COUNT(*)) * 100 as black_percentage,
        -- Native American%
        COUNTIF(is_native_american = 1) as native_american_loans,
        SAFE_DIVIDE(COUNTIF(is_native_american = 1), COUNT(*)) * 100 as native_american_percentage,
        -- HoPI%
        COUNTIF(is_hopi = 1) as hopi_loans,
        SAFE_DIVIDE(COUNTIF(is_hopi = 1), COUNT(*)) * 100 as hopi_percentage,
        -- Hispanic%
        COUNTIF(is_hispanic = 1) as hispanic_loans,
        SAFE_DIVIDE(COUNTIF(is_hispanic = 1), COUNT(*)) * 100 as hispanic_percentage
    FROM peer_hmda
    GROUP BY activity_year, cbsa_code
)

-- Final output: aggregated peer metrics by year and CBSA
SELECT * FROM aggregated_peer_metrics
ORDER BY activity_year, cbsa_code
