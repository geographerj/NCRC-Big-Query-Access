-- Bank A (The Huntington National Bank)

-- Goal-Setting Analysis: HMDA Data Query
-- Subject Bank: 2WHM8VNJH63UN14OL754
-- Assessment Area Counties: 194 counties
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
        '17031', '17043', '17073', '17197', '17037', '17089', '17093', '17097', '55059', '21015', '21117', '39017', '39025', '39061', '39165', '39081', '54029', '39099', '39155', '42085', '08013', '08041', '08001', '08005', '08014', '08031', '08035', '08059', '12021', '18011', '18057', '18063', '18081', '18095', '18097', '18157', '26161', '26025', '26017', '26163', '26087', '26093', '26099', '26125', '26147', '26049', '26067', '26081', '26117', '26139', '26075', '26077', '26037', '26045', '26065', '26155', '26111', '26115', '26121', '26021', '26145', '26027', '26005', '26007', '26009', '26011', '26015', '26023', '26029', '26033', '26035', '26039', '26041', '26043', '26047', '26051', '26055', '26057', '26059', '26061', '26063', '26069', '26073', '26079', '26089', '26091', '26101', '26103', '26105', '26107', '26113', '26119', '26123', '26127', '26129', '26133', '26135', '26137', '26141', '26143', '26151', '26149', '26157', '26159', '26165', '27137', '27013', '27003', '27019', '27037', '27053', '27123', '27139', '27141', '27163', '27171', '27009', '27145', '27131', '39133', '39153', '39019', '39151', '39035', '39055', '39085', '39093', '39103', '39041', '39045', '39049', '39089', '39097', '39129', '39159', '39057', '39109', '39113', '39003', '39139', '39023', '39051', '39095', '39123', '39173', '39013', '39005', '39007', '39029', '39033', '39039', '39043', '39047', '39059', '39063', '39065', '39067', '39069', '39077', '39083', '39091', '39101', '39119', '39137', '39141', '39143', '39147', '39157', '39167', '39169', '39171', '39175', '42049', '42003', '42007', '42019', '42125', '42129', '42073', '46099', '54039', '54011', '54079', '51820', '54061', '54107', '51660', '54041', '54049', '54083', '54085', '55079', '55133', '55101' as geoid5
    FROM UNNEST(['17031', '17043', '17073', '17197', '17037', '17089', '17093', '17097', '55059', '21015', '21117', '39017', '39025', '39061', '39165', '39081', '54029', '39099', '39155', '42085', '08013', '08041', '08001', '08005', '08014', '08031', '08035', '08059', '12021', '18011', '18057', '18063', '18081', '18095', '18097', '18157', '26161', '26025', '26017', '26163', '26087', '26093', '26099', '26125', '26147', '26049', '26067', '26081', '26117', '26139', '26075', '26077', '26037', '26045', '26065', '26155', '26111', '26115', '26121', '26021', '26145', '26027', '26005', '26007', '26009', '26011', '26015', '26023', '26029', '26033', '26035', '26039', '26041', '26043', '26047', '26051', '26055', '26057', '26059', '26061', '26063', '26069', '26073', '26079', '26089', '26091', '26101', '26103', '26105', '26107', '26113', '26119', '26123', '26127', '26129', '26133', '26135', '26137', '26141', '26143', '26151', '26149', '26157', '26159', '26165', '27137', '27013', '27003', '27019', '27037', '27053', '27123', '27139', '27141', '27163', '27171', '27009', '27145', '27131', '39133', '39153', '39019', '39151', '39035', '39055', '39085', '39093', '39103', '39041', '39045', '39049', '39089', '39097', '39129', '39159', '39057', '39109', '39113', '39003', '39139', '39023', '39051', '39095', '39123', '39173', '39013', '39005', '39007', '39029', '39033', '39039', '39043', '39047', '39059', '39063', '39065', '39067', '39069', '39077', '39083', '39091', '39101', '39119', '39137', '39141', '39143', '39147', '39157', '39167', '39169', '39171', '39175', '42049', '42003', '42007', '42019', '42125', '42129', '42073', '46099', '54039', '54011', '54079', '51820', '54061', '54107', '51660', '54041', '54049', '54083', '54085', '55079', '55133', '55101']) as geoid5
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
        AND h.lei = '2WHM8VNJH63UN14OL754'
        AND CAST(h.county_code AS STRING) IN ('17031', '17043', '17073', '17197', '17037', '17089', '17093', '17097', '55059', '21015', '21117', '39017', '39025', '39061', '39165', '39081', '54029', '39099', '39155', '42085', '08013', '08041', '08001', '08005', '08014', '08031', '08035', '08059', '12021', '18011', '18057', '18063', '18081', '18095', '18097', '18157', '26161', '26025', '26017', '26163', '26087', '26093', '26099', '26125', '26147', '26049', '26067', '26081', '26117', '26139', '26075', '26077', '26037', '26045', '26065', '26155', '26111', '26115', '26121', '26021', '26145', '26027', '26005', '26007', '26009', '26011', '26015', '26023', '26029', '26033', '26035', '26039', '26041', '26043', '26047', '26051', '26055', '26057', '26059', '26061', '26063', '26069', '26073', '26079', '26089', '26091', '26101', '26103', '26105', '26107', '26113', '26119', '26123', '26127', '26129', '26133', '26135', '26137', '26141', '26143', '26151', '26149', '26157', '26159', '26165', '27137', '27013', '27003', '27019', '27037', '27053', '27123', '27139', '27141', '27163', '27171', '27009', '27145', '27131', '39133', '39153', '39019', '39151', '39035', '39055', '39085', '39093', '39103', '39041', '39045', '39049', '39089', '39097', '39129', '39159', '39057', '39109', '39113', '39003', '39139', '39023', '39051', '39095', '39123', '39173', '39013', '39005', '39007', '39029', '39033', '39039', '39043', '39047', '39059', '39063', '39065', '39067', '39069', '39077', '39083', '39091', '39101', '39119', '39137', '39141', '39143', '39147', '39157', '39167', '39169', '39171', '39175', '42049', '42003', '42007', '42019', '42125', '42129', '42073', '46099', '54039', '54011', '54079', '51820', '54061', '54107', '51660', '54041', '54049', '54083', '54085', '55079', '55133', '55101')
        AND h.action_taken = '1'  -- Originations only
        -- Standard HMDA filters
        AND h.occupancy_type = '1'  -- Owner-occupied
        AND h.reverse_mortgage != '1'  -- Not reverse mortgage
        AND h.construction_method = '1'  -- Site-built
        AND h.total_units IN ('1', '2', '3', '4')  -- 1-4 units
            AND h.loan_purpose IN ('2', '4', '5')  -- Home Improvement (2), Home Equity (4), and Other (5)
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


-- Bank B (Cadence Bank)

-- Goal-Setting Analysis: HMDA Data Query
-- Subject Bank: Q7C315HKI8VX0SSKBS64
-- Assessment Area Counties: 142 counties
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
        '01081', '01009', '01073', '01115', '01117', '01003', '01103', '01055', '01083', '01089', '01097', '01085', '01101', '01125', '01013', '01025', '01039', '01049', '01071', '01095', '01121', '01129', '05007', '05143', '05033', '05131', '05051', '05031', '05045', '05085', '05119', '05091', '05001', '05027', '05055', '05057', '05065', '05073', '05093', '05095', '05103', '05117', '05121', '05133', '05139', '12091', '12131', '12017', '12081', '12115', '12083', '12005', '12033', '12113', '12103', '12053', '12057', '12101', '13059', '13089', '13121', '13135', '13073', '13189', '13245', '13047', '13295', '13139', '13021', '13169', '13067', '13051', '13153', '13093', '13267', '22079', '22005', '22033', '22063', '22055', '22019', '22067', '22073', '22083', '22015', '22017', '22061', '28047', '28059', '28035', '28073', '28049', '28089', '28121', '28123', '28127', '28033', '28137', '28003', '28013', '28017', '28025', '28043', '28057', '28061', '28067', '28071', '28081', '28087', '28095', '28099', '28105', '28107', '28115', '28117', '28141', '28145', '28149', '28153', '28159', '28161', '29189', '29189', '29077', '47065', '47033', '47053', '47113', '47047', '47157', '47167', '47037', '47187', '47055', '47095', '47103', '47109', '47183', '48021', '48209', '48453', '48491' as geoid5
    FROM UNNEST(['01081', '01009', '01073', '01115', '01117', '01003', '01103', '01055', '01083', '01089', '01097', '01085', '01101', '01125', '01013', '01025', '01039', '01049', '01071', '01095', '01121', '01129', '05007', '05143', '05033', '05131', '05051', '05031', '05045', '05085', '05119', '05091', '05001', '05027', '05055', '05057', '05065', '05073', '05093', '05095', '05103', '05117', '05121', '05133', '05139', '12091', '12131', '12017', '12081', '12115', '12083', '12005', '12033', '12113', '12103', '12053', '12057', '12101', '13059', '13089', '13121', '13135', '13073', '13189', '13245', '13047', '13295', '13139', '13021', '13169', '13067', '13051', '13153', '13093', '13267', '22079', '22005', '22033', '22063', '22055', '22019', '22067', '22073', '22083', '22015', '22017', '22061', '28047', '28059', '28035', '28073', '28049', '28089', '28121', '28123', '28127', '28033', '28137', '28003', '28013', '28017', '28025', '28043', '28057', '28061', '28067', '28071', '28081', '28087', '28095', '28099', '28105', '28107', '28115', '28117', '28141', '28145', '28149', '28153', '28159', '28161', '29189', '29189', '29077', '47065', '47033', '47053', '47113', '47047', '47157', '47167', '47037', '47187', '47055', '47095', '47103', '47109', '47183', '48021', '48209', '48453', '48491']) as geoid5
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
        AND h.lei = 'Q7C315HKI8VX0SSKBS64'
        AND CAST(h.county_code AS STRING) IN ('01081', '01009', '01073', '01115', '01117', '01003', '01103', '01055', '01083', '01089', '01097', '01085', '01101', '01125', '01013', '01025', '01039', '01049', '01071', '01095', '01121', '01129', '05007', '05143', '05033', '05131', '05051', '05031', '05045', '05085', '05119', '05091', '05001', '05027', '05055', '05057', '05065', '05073', '05093', '05095', '05103', '05117', '05121', '05133', '05139', '12091', '12131', '12017', '12081', '12115', '12083', '12005', '12033', '12113', '12103', '12053', '12057', '12101', '13059', '13089', '13121', '13135', '13073', '13189', '13245', '13047', '13295', '13139', '13021', '13169', '13067', '13051', '13153', '13093', '13267', '22079', '22005', '22033', '22063', '22055', '22019', '22067', '22073', '22083', '22015', '22017', '22061', '28047', '28059', '28035', '28073', '28049', '28089', '28121', '28123', '28127', '28033', '28137', '28003', '28013', '28017', '28025', '28043', '28057', '28061', '28067', '28071', '28081', '28087', '28095', '28099', '28105', '28107', '28115', '28117', '28141', '28145', '28149', '28153', '28159', '28161', '29189', '29189', '29077', '47065', '47033', '47053', '47113', '47047', '47157', '47167', '47037', '47187', '47055', '47095', '47103', '47109', '47183', '48021', '48209', '48453', '48491')
        AND h.action_taken = '1'  -- Originations only
        -- Standard HMDA filters
        AND h.occupancy_type = '1'  -- Owner-occupied
        AND h.reverse_mortgage != '1'  -- Not reverse mortgage
        AND h.construction_method = '1'  -- Site-built
        AND h.total_units IN ('1', '2', '3', '4')  -- 1-4 units
            AND h.loan_purpose IN ('2', '4', '5')  -- Home Improvement (2), Home Equity (4), and Other (5)
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
