-- Goal-Setting Analysis: HMDA Data Query
-- Extracts lending data for subject banks with all 11 metrics
-- Filters to assessment area counties only
-- Optimized to return only aggregated summary data

-- Parameters:
--   @subject_lei: LEI of subject bank (string)
--   @assessment_area_geoids: List of GEOID5 codes (state+county) for assessment areas
--   @years: List of years as strings (e.g., ['2020', '2021', '2022', '2023', '2024'])

WITH assessment_area_counties AS (
    -- Filter to only assessment area counties using GEOID5
    SELECT DISTINCT
        geoid5,
        CAST(SUBSTR(geoid5, 1, 2) AS STRING) as state_code,
        CAST(SUBSTR(geoid5, 3, 3) AS STRING) as county_code
    FROM UNNEST(@assessment_area_geoids) as geoid5
),

filtered_hmda AS (
    -- Filter HMDA data early: years, LEI, assessment area counties, standard filters
    SELECT 
        CAST(h.activity_year AS STRING) as activity_year,
        h.cbsa_code,
        CAST(h.county_code AS STRING) as county_code,
        h.census_tract,
        h.loan_amount,
        -- Pre-calculate flags in SQL (more efficient)
        CASE 
            WHEN h.tract_to_msa_income_percentage IS NOT NULL
                AND CAST(h.tract_to_msa_income_percentage AS FLOAT64) <= 80 
            THEN 1 ELSE 0 
        END as is_lmict,
        CASE 
            WHEN h.applicant_income_percentage_of_msamd IS NOT NULL
                AND CAST(h.applicant_income_percentage_of_msamd AS FLOAT64) <= 80 
            THEN 1 ELSE 0 
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
    INNER JOIN assessment_area_counties aac
        ON CAST(h.county_code AS STRING) = aac.geoid5
    WHERE CAST(h.activity_year AS STRING) IN UNNEST(@years)
        AND h.lei = @subject_lei
        AND h.action_taken = '1'  -- Originations only
        -- Standard HMDA filters (from ticket if specified, otherwise defaults)
        AND h.occupancy_type = '1'  -- Owner-occupied
        AND h.reverse_mortgage != '1'  -- Not reverse mortgage
        AND h.construction_method = '1'  -- Site-built
        AND h.total_units IN ('1', '2', '3', '4')  -- 1-4 units
        -- Add loan_purpose filter if specified in ticket
        -- AND h.loan_purpose = '1'  -- Home purchase only (if specified)
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
        -- MINB% (combined minority: Hispanic, Black, Asian, Native American, HoPI)
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


