-- Bank A (PNC Bank)

-- Goal-Setting Analysis: HMDA Data Query
-- Subject Bank: AD6GFRVSDT01YPT1CS68
-- Assessment Area Counties: 434 counties
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
        '01047', '01087', '01121', '01123', '01081', '01073', '01117', '01115', '01003', '01103', '01083', '01089', '01097', '01001', '01051', '01101', '01125', '04013', '08031', '10001', '10003', '10005', '12071', '12035', '12127', '12093', '12001', '12031', '12109', '12011', '12086', '12099', '12021', '12081', '12115', '12083', '12069', '12095', '12097', '12117', '12009', '12085', '12111', '12015', '12061', '12057', '12101', '12103', '13057', '13061', '13067', '13077', '13089', '13097', '13113', '13117', '13121', '13135', '13151', '13223', '13093', '13193', '13285', '17113', '17019', '17031', '17037', '17043', '17089', '17097', '17073', '17197', '17115', '17095', '17091', '17143', '17179', '17007', '17201', '17167', '17163', '18105', '18073', '18089', '18005', '18039', '18003', '18179', '18183', '18017', '18069', '18071', '18079', '18085', '18099', '18103', '18107', '18137', '18011', '18013', '18057', '18059', '18063', '18081', '18095', '18097', '18133', '18145', '18067', '18157', '18019', '18043', '18175', '18141', '05071', '21227', '21015', '21013', '21117', '21093', '21019', '21087', '21021', '21051', '21073', '21121', '21125', '21151', '21179', '21049', '21067', '21113', '21209', '21239', '21029', '21111', '21185', '21059', '24003', '24005', '24013', '24025', '24027', '24035', '24037', '24001', '24043', '24011', '24029', '24041', '24015', '24039', '24045', '24047', '24009', '24017', '24021', '24031', '24033', '25009', '25017', '25021', '25025', '26161', '26025', '26017', '26087', '26093', '26099', '26125', '26163', '26049', '26015', '26081', '26139', '26075', '26077', '26159', '26037', '26045', '26065', '26155', '26005', '26007', '26009', '26023', '26031', '26035', '26047', '26051', '26055', '26057', '26069', '26073', '26101', '26105', '26107', '26119', '26129', '26157', '26111', '26115', '26121', '26145', '29095', '29071', '29099', '29183', '29189', '29219', '34041', '34001', '34003', '34013', '34017', '34019', '34023', '34025', '34027', '34029', '34031', '34035', '34037', '34039', '34009', '34005', '34007', '34015', '34021', '34011', '36061', '37021', '37089', '37001', '37007', '37071', '37097', '37119', '37179', '37037', '37063', '37077', '37135', '37051', '37085', '37093', '37191', '37081', '37151', '37147', '37027', '37035', '37133', '37019', '37049', '37031', '37039', '37041', '37045', '37047', '37055', '37083', '37091', '37105', '37107', '37113', '37117', '37125', '37131', '37139', '37143', '37153', '37155', '37161', '37163', '37165', '37171', '37175', '37181', '37187', '37189', '37195', '37199', '37101', '37183', '37065', '37127', '37053', '37129', '37141', '37067', '39133', '39153', '39019', '39151', '39017', '39025', '39061', '39165', '39035', '39055', '39085', '39093', '39103', '39041', '39045', '39049', '39073', '39089', '39097', '39127', '39129', '39159', '39057', '39109', '39113', '39087', '39139', '39005', '39027', '39029', '39031', '39043', '39047', '39059', '39067', '39069', '39075', '39077', '39079', '39083', '39091', '39101', '39119', '39141', '39143', '39145', '39147', '39149', '39157', '39169', '39171', '39023', '39051', '39095', '39173', '39081', '39013', '39099', '39155', '42025', '42077', '42095', '42013', '42037', '42089', '42049', '42001', '42041', '42043', '42099', '42071', '42075', '42103', '42031', '42033', '42039', '42047', '42059', '42061', '42063', '42065', '42073', '42083', '42111', '42121', '42123', '42127', '42017', '42029', '42045', '42091', '42101', '42003', '42007', '42019', '42051', '42125', '42129', '42011', '42069', '42079', '42027', '42081', '42133', '42085', '45019', '45091', '45079', '45041', '45045', '45077', '45013', '45051', '45043', '47037', '47165', '47187', '48085', '48113', '48121', '48439', '48157', '48201', '48339', '51095', '51001', '51131', '51013', '51059', '51061', '51107', '51153', '51177', '51179', '54057', '54011', '54061', '55059', '55079', '55089', '55131', '55133', '55127' as geoid5
    FROM UNNEST(['01047', '01087', '01121', '01123', '01081', '01073', '01117', '01115', '01003', '01103', '01083', '01089', '01097', '01001', '01051', '01101', '01125', '04013', '08031', '10001', '10003', '10005', '12071', '12035', '12127', '12093', '12001', '12031', '12109', '12011', '12086', '12099', '12021', '12081', '12115', '12083', '12069', '12095', '12097', '12117', '12009', '12085', '12111', '12015', '12061', '12057', '12101', '12103', '13057', '13061', '13067', '13077', '13089', '13097', '13113', '13117', '13121', '13135', '13151', '13223', '13093', '13193', '13285', '17113', '17019', '17031', '17037', '17043', '17089', '17097', '17073', '17197', '17115', '17095', '17091', '17143', '17179', '17007', '17201', '17167', '17163', '18105', '18073', '18089', '18005', '18039', '18003', '18179', '18183', '18017', '18069', '18071', '18079', '18085', '18099', '18103', '18107', '18137', '18011', '18013', '18057', '18059', '18063', '18081', '18095', '18097', '18133', '18145', '18067', '18157', '18019', '18043', '18175', '18141', '05071', '21227', '21015', '21013', '21117', '21093', '21019', '21087', '21021', '21051', '21073', '21121', '21125', '21151', '21179', '21049', '21067', '21113', '21209', '21239', '21029', '21111', '21185', '21059', '24003', '24005', '24013', '24025', '24027', '24035', '24037', '24001', '24043', '24011', '24029', '24041', '24015', '24039', '24045', '24047', '24009', '24017', '24021', '24031', '24033', '25009', '25017', '25021', '25025', '26161', '26025', '26017', '26087', '26093', '26099', '26125', '26163', '26049', '26015', '26081', '26139', '26075', '26077', '26159', '26037', '26045', '26065', '26155', '26005', '26007', '26009', '26023', '26031', '26035', '26047', '26051', '26055', '26057', '26069', '26073', '26101', '26105', '26107', '26119', '26129', '26157', '26111', '26115', '26121', '26145', '29095', '29071', '29099', '29183', '29189', '29219', '34041', '34001', '34003', '34013', '34017', '34019', '34023', '34025', '34027', '34029', '34031', '34035', '34037', '34039', '34009', '34005', '34007', '34015', '34021', '34011', '36061', '37021', '37089', '37001', '37007', '37071', '37097', '37119', '37179', '37037', '37063', '37077', '37135', '37051', '37085', '37093', '37191', '37081', '37151', '37147', '37027', '37035', '37133', '37019', '37049', '37031', '37039', '37041', '37045', '37047', '37055', '37083', '37091', '37105', '37107', '37113', '37117', '37125', '37131', '37139', '37143', '37153', '37155', '37161', '37163', '37165', '37171', '37175', '37181', '37187', '37189', '37195', '37199', '37101', '37183', '37065', '37127', '37053', '37129', '37141', '37067', '39133', '39153', '39019', '39151', '39017', '39025', '39061', '39165', '39035', '39055', '39085', '39093', '39103', '39041', '39045', '39049', '39073', '39089', '39097', '39127', '39129', '39159', '39057', '39109', '39113', '39087', '39139', '39005', '39027', '39029', '39031', '39043', '39047', '39059', '39067', '39069', '39075', '39077', '39079', '39083', '39091', '39101', '39119', '39141', '39143', '39145', '39147', '39149', '39157', '39169', '39171', '39023', '39051', '39095', '39173', '39081', '39013', '39099', '39155', '42025', '42077', '42095', '42013', '42037', '42089', '42049', '42001', '42041', '42043', '42099', '42071', '42075', '42103', '42031', '42033', '42039', '42047', '42059', '42061', '42063', '42065', '42073', '42083', '42111', '42121', '42123', '42127', '42017', '42029', '42045', '42091', '42101', '42003', '42007', '42019', '42051', '42125', '42129', '42011', '42069', '42079', '42027', '42081', '42133', '42085', '45019', '45091', '45079', '45041', '45045', '45077', '45013', '45051', '45043', '47037', '47165', '47187', '48085', '48113', '48121', '48439', '48157', '48201', '48339', '51095', '51001', '51131', '51013', '51059', '51061', '51107', '51153', '51177', '51179', '54057', '54011', '54061', '55059', '55079', '55089', '55131', '55133', '55127']) as geoid5
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
        AND h.lei = 'AD6GFRVSDT01YPT1CS68'
        AND CAST(h.county_code AS STRING) IN ('01047', '01087', '01121', '01123', '01081', '01073', '01117', '01115', '01003', '01103', '01083', '01089', '01097', '01001', '01051', '01101', '01125', '04013', '08031', '10001', '10003', '10005', '12071', '12035', '12127', '12093', '12001', '12031', '12109', '12011', '12086', '12099', '12021', '12081', '12115', '12083', '12069', '12095', '12097', '12117', '12009', '12085', '12111', '12015', '12061', '12057', '12101', '12103', '13057', '13061', '13067', '13077', '13089', '13097', '13113', '13117', '13121', '13135', '13151', '13223', '13093', '13193', '13285', '17113', '17019', '17031', '17037', '17043', '17089', '17097', '17073', '17197', '17115', '17095', '17091', '17143', '17179', '17007', '17201', '17167', '17163', '18105', '18073', '18089', '18005', '18039', '18003', '18179', '18183', '18017', '18069', '18071', '18079', '18085', '18099', '18103', '18107', '18137', '18011', '18013', '18057', '18059', '18063', '18081', '18095', '18097', '18133', '18145', '18067', '18157', '18019', '18043', '18175', '18141', '05071', '21227', '21015', '21013', '21117', '21093', '21019', '21087', '21021', '21051', '21073', '21121', '21125', '21151', '21179', '21049', '21067', '21113', '21209', '21239', '21029', '21111', '21185', '21059', '24003', '24005', '24013', '24025', '24027', '24035', '24037', '24001', '24043', '24011', '24029', '24041', '24015', '24039', '24045', '24047', '24009', '24017', '24021', '24031', '24033', '25009', '25017', '25021', '25025', '26161', '26025', '26017', '26087', '26093', '26099', '26125', '26163', '26049', '26015', '26081', '26139', '26075', '26077', '26159', '26037', '26045', '26065', '26155', '26005', '26007', '26009', '26023', '26031', '26035', '26047', '26051', '26055', '26057', '26069', '26073', '26101', '26105', '26107', '26119', '26129', '26157', '26111', '26115', '26121', '26145', '29095', '29071', '29099', '29183', '29189', '29219', '34041', '34001', '34003', '34013', '34017', '34019', '34023', '34025', '34027', '34029', '34031', '34035', '34037', '34039', '34009', '34005', '34007', '34015', '34021', '34011', '36061', '37021', '37089', '37001', '37007', '37071', '37097', '37119', '37179', '37037', '37063', '37077', '37135', '37051', '37085', '37093', '37191', '37081', '37151', '37147', '37027', '37035', '37133', '37019', '37049', '37031', '37039', '37041', '37045', '37047', '37055', '37083', '37091', '37105', '37107', '37113', '37117', '37125', '37131', '37139', '37143', '37153', '37155', '37161', '37163', '37165', '37171', '37175', '37181', '37187', '37189', '37195', '37199', '37101', '37183', '37065', '37127', '37053', '37129', '37141', '37067', '39133', '39153', '39019', '39151', '39017', '39025', '39061', '39165', '39035', '39055', '39085', '39093', '39103', '39041', '39045', '39049', '39073', '39089', '39097', '39127', '39129', '39159', '39057', '39109', '39113', '39087', '39139', '39005', '39027', '39029', '39031', '39043', '39047', '39059', '39067', '39069', '39075', '39077', '39079', '39083', '39091', '39101', '39119', '39141', '39143', '39145', '39147', '39149', '39157', '39169', '39171', '39023', '39051', '39095', '39173', '39081', '39013', '39099', '39155', '42025', '42077', '42095', '42013', '42037', '42089', '42049', '42001', '42041', '42043', '42099', '42071', '42075', '42103', '42031', '42033', '42039', '42047', '42059', '42061', '42063', '42065', '42073', '42083', '42111', '42121', '42123', '42127', '42017', '42029', '42045', '42091', '42101', '42003', '42007', '42019', '42051', '42125', '42129', '42011', '42069', '42079', '42027', '42081', '42133', '42085', '45019', '45091', '45079', '45041', '45045', '45077', '45013', '45051', '45043', '47037', '47165', '47187', '48085', '48113', '48121', '48439', '48157', '48201', '48339', '51095', '51001', '51131', '51013', '51059', '51061', '51107', '51153', '51177', '51179', '54057', '54011', '54061', '55059', '55079', '55089', '55131', '55133', '55127')
        AND h.action_taken = '1'  -- Originations only
        -- Standard HMDA filters
        AND h.occupancy_type = '1'  -- Owner-occupied
        AND h.reverse_mortgage != '1'  -- Not reverse mortgage
        AND h.construction_method = '1'  -- Site-built
        AND h.total_units IN ('1', '2', '3', '4')  -- 1-4 units
            AND h.loan_purpose = '1'  -- Home Purchase
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


-- Bank B (FirstBank)

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
            AND h.loan_purpose = '1'  -- Home Purchase
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
