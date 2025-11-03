"""
Query builder for Tampa Market Report

Market overview query with:
- All lenders (market overview)
- Top 10 lenders by 2024 volume
- Year-over-year analysis 2018-2024
- Standard 6 metrics
"""

def build_tampa_market_query(tract_list: list, years: list) -> str:
    """
    Build market overview query for Tampa
    
    Args:
        tract_list: List of census tract GEOIDs
        years: List of years to analyze
    
    Returns:
        SQL query string
    """
    years_list = ', '.join([f"'{str(y)}'" for y in years])
    tracts_list = ', '.join([f"'{tract}'" for tract in tract_list])
    
    query = f"""
-- Tampa Market Overview Query
-- Home Purchase Originations, All Lenders
-- Years: {years_list}
-- Census Tracts: {len(tract_list)} tracts

WITH filtered_hmda AS (
    SELECT 
        CAST(h.activity_year AS STRING) as activity_year,
        h.census_tract,
        h.lei,
        h.loan_amount,
        -- Borrower demographics (NCRC methodology: Check ethnicity first, then first race choice)
        -- First: Check if ANY ethnicity field indicates Hispanic (1, 11, 12, 13, 14)
        CASE 
            WHEN h.applicant_ethnicity_1 IN ('1','11','12','13','14')
                OR h.applicant_ethnicity_2 IN ('1','11','12','13','14')
                OR h.applicant_ethnicity_3 IN ('1','11','12','13','14')
                OR h.applicant_ethnicity_4 IN ('1','11','12','13','14')
                OR h.applicant_ethnicity_5 IN ('1','11','12','13','14')
            THEN 1 ELSE 0 
        END as is_hispanic,
        -- Race classifications: Only if NOT Hispanic, check FIRST race choice (race_1 first, then race_2, etc.)
        -- Black: first valid race code is '3'
        CASE 
            WHEN (h.applicant_ethnicity_1 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_1 IS NULL)
                AND (h.applicant_ethnicity_2 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_2 IS NULL)
                AND (h.applicant_ethnicity_3 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_3 IS NULL)
                AND (h.applicant_ethnicity_4 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_4 IS NULL)
                AND (h.applicant_ethnicity_5 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_5 IS NULL)
                AND COALESCE(
                    CASE WHEN h.applicant_race_1 IS NOT NULL AND h.applicant_race_1 != '' AND h.applicant_race_1 NOT IN ('6','7','8') 
                         THEN h.applicant_race_1 ELSE NULL END,
                    CASE WHEN h.applicant_race_2 IS NOT NULL AND h.applicant_race_2 != '' AND h.applicant_race_2 NOT IN ('6','7','8') 
                         THEN h.applicant_race_2 ELSE NULL END,
                    CASE WHEN h.applicant_race_3 IS NOT NULL AND h.applicant_race_3 != '' AND h.applicant_race_3 NOT IN ('6','7','8') 
                         THEN h.applicant_race_3 ELSE NULL END,
                    CASE WHEN h.applicant_race_4 IS NOT NULL AND h.applicant_race_4 != '' AND h.applicant_race_4 NOT IN ('6','7','8') 
                         THEN h.applicant_race_4 ELSE NULL END,
                    CASE WHEN h.applicant_race_5 IS NOT NULL AND h.applicant_race_5 != '' AND h.applicant_race_5 NOT IN ('6','7','8') 
                         THEN h.applicant_race_5 ELSE NULL END
                ) = '3'
            THEN 1 ELSE 0 
        END as is_black,
        -- Asian: first valid race code is '2' or '21'-'27'
        CASE 
            WHEN (h.applicant_ethnicity_1 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_1 IS NULL)
                AND (h.applicant_ethnicity_2 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_2 IS NULL)
                AND (h.applicant_ethnicity_3 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_3 IS NULL)
                AND (h.applicant_ethnicity_4 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_4 IS NULL)
                AND (h.applicant_ethnicity_5 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_5 IS NULL)
                AND COALESCE(
                    CASE WHEN h.applicant_race_1 IS NOT NULL AND h.applicant_race_1 != '' AND h.applicant_race_1 NOT IN ('6','7','8') 
                         THEN h.applicant_race_1 ELSE NULL END,
                    CASE WHEN h.applicant_race_2 IS NOT NULL AND h.applicant_race_2 != '' AND h.applicant_race_2 NOT IN ('6','7','8') 
                         THEN h.applicant_race_2 ELSE NULL END,
                    CASE WHEN h.applicant_race_3 IS NOT NULL AND h.applicant_race_3 != '' AND h.applicant_race_3 NOT IN ('6','7','8') 
                         THEN h.applicant_race_3 ELSE NULL END,
                    CASE WHEN h.applicant_race_4 IS NOT NULL AND h.applicant_race_4 != '' AND h.applicant_race_4 NOT IN ('6','7','8') 
                         THEN h.applicant_race_4 ELSE NULL END,
                    CASE WHEN h.applicant_race_5 IS NOT NULL AND h.applicant_race_5 != '' AND h.applicant_race_5 NOT IN ('6','7','8') 
                         THEN h.applicant_race_5 ELSE NULL END
                ) IN ('2','21','22','23','24','25','26','27')
            THEN 1 ELSE 0 
        END as is_asian,
        -- White: first valid race code is '5'
        CASE 
            WHEN (h.applicant_ethnicity_1 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_1 IS NULL)
                AND (h.applicant_ethnicity_2 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_2 IS NULL)
                AND (h.applicant_ethnicity_3 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_3 IS NULL)
                AND (h.applicant_ethnicity_4 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_4 IS NULL)
                AND (h.applicant_ethnicity_5 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_5 IS NULL)
                AND COALESCE(
                    CASE WHEN h.applicant_race_1 IS NOT NULL AND h.applicant_race_1 != '' AND h.applicant_race_1 NOT IN ('6','7','8') 
                         THEN h.applicant_race_1 ELSE NULL END,
                    CASE WHEN h.applicant_race_2 IS NOT NULL AND h.applicant_race_2 != '' AND h.applicant_race_2 NOT IN ('6','7','8') 
                         THEN h.applicant_race_2 ELSE NULL END,
                    CASE WHEN h.applicant_race_3 IS NOT NULL AND h.applicant_race_3 != '' AND h.applicant_race_3 NOT IN ('6','7','8') 
                         THEN h.applicant_race_3 ELSE NULL END,
                    CASE WHEN h.applicant_race_4 IS NOT NULL AND h.applicant_race_4 != '' AND h.applicant_race_4 NOT IN ('6','7','8') 
                         THEN h.applicant_race_4 ELSE NULL END,
                    CASE WHEN h.applicant_race_5 IS NOT NULL AND h.applicant_race_5 != '' AND h.applicant_race_5 NOT IN ('6','7','8') 
                         THEN h.applicant_race_5 ELSE NULL END
                ) = '5'
            THEN 1 ELSE 0 
        END as is_white,
        -- Native American: first valid race code is '1'
        CASE 
            WHEN (h.applicant_ethnicity_1 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_1 IS NULL)
                AND (h.applicant_ethnicity_2 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_2 IS NULL)
                AND (h.applicant_ethnicity_3 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_3 IS NULL)
                AND (h.applicant_ethnicity_4 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_4 IS NULL)
                AND (h.applicant_ethnicity_5 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_5 IS NULL)
                AND COALESCE(
                    CASE WHEN h.applicant_race_1 IS NOT NULL AND h.applicant_race_1 != '' AND h.applicant_race_1 NOT IN ('6','7','8') 
                         THEN h.applicant_race_1 ELSE NULL END,
                    CASE WHEN h.applicant_race_2 IS NOT NULL AND h.applicant_race_2 != '' AND h.applicant_race_2 NOT IN ('6','7','8') 
                         THEN h.applicant_race_2 ELSE NULL END,
                    CASE WHEN h.applicant_race_3 IS NOT NULL AND h.applicant_race_3 != '' AND h.applicant_race_3 NOT IN ('6','7','8') 
                         THEN h.applicant_race_3 ELSE NULL END,
                    CASE WHEN h.applicant_race_4 IS NOT NULL AND h.applicant_race_4 != '' AND h.applicant_race_4 NOT IN ('6','7','8') 
                         THEN h.applicant_race_4 ELSE NULL END,
                    CASE WHEN h.applicant_race_5 IS NOT NULL AND h.applicant_race_5 != '' AND h.applicant_race_5 NOT IN ('6','7','8') 
                         THEN h.applicant_race_5 ELSE NULL END
                ) = '1'
            THEN 1 ELSE 0 
        END as is_native_american,
        -- HoPI: first valid race code is '4', '41'-'44'
        CASE 
            WHEN (h.applicant_ethnicity_1 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_1 IS NULL)
                AND (h.applicant_ethnicity_2 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_2 IS NULL)
                AND (h.applicant_ethnicity_3 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_3 IS NULL)
                AND (h.applicant_ethnicity_4 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_4 IS NULL)
                AND (h.applicant_ethnicity_5 NOT IN ('1','11','12','13','14') OR h.applicant_ethnicity_5 IS NULL)
                AND COALESCE(
                    CASE WHEN h.applicant_race_1 IS NOT NULL AND h.applicant_race_1 != '' AND h.applicant_race_1 NOT IN ('6','7','8') 
                         THEN h.applicant_race_1 ELSE NULL END,
                    CASE WHEN h.applicant_race_2 IS NOT NULL AND h.applicant_race_2 != '' AND h.applicant_race_2 NOT IN ('6','7','8') 
                         THEN h.applicant_race_2 ELSE NULL END,
                    CASE WHEN h.applicant_race_3 IS NOT NULL AND h.applicant_race_3 != '' AND h.applicant_race_3 NOT IN ('6','7','8') 
                         THEN h.applicant_race_3 ELSE NULL END,
                    CASE WHEN h.applicant_race_4 IS NOT NULL AND h.applicant_race_4 != '' AND h.applicant_race_4 NOT IN ('6','7','8') 
                         THEN h.applicant_race_4 ELSE NULL END,
                    CASE WHEN h.applicant_race_5 IS NOT NULL AND h.applicant_race_5 != '' AND h.applicant_race_5 NOT IN ('6','7','8') 
                         THEN h.applicant_race_5 ELSE NULL END
                ) IN ('4','41','42','43','44')
            THEN 1 ELSE 0 
        END as is_hopi,
        -- Income metrics
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
            WHEN h.tract_to_msa_income_percentage IS NOT NULL
                AND CAST(h.tract_to_msa_income_percentage AS FLOAT64) <= 80 
            THEN 1 ELSE 0 
        END as is_lmict,
        -- Redlining metrics
        CASE 
            WHEN h.tract_minority_population_percent IS NOT NULL
                AND CAST(h.tract_minority_population_percent AS FLOAT64) > 50 
            THEN 1 ELSE 0 
        END as is_mmct,
        -- Check if has demographic data for race/ethnicity calculations
        -- Must have either: Hispanic ethnicity OR explicit race selection
        -- Hispanic ethnicity: codes 1, 11-14
        -- Explicit race: codes 1-5, 21-27, 41-44 (NOT codes 6,7,8 which mean "not provided", "not applicable", "no co-applicant")
        CASE 
            WHEN (h.applicant_ethnicity_1 IN ('1','11','12','13','14')
                  OR h.applicant_ethnicity_2 IN ('1','11','12','13','14')
                  OR h.applicant_ethnicity_3 IN ('1','11','12','13','14')
                  OR h.applicant_ethnicity_4 IN ('1','11','12','13','14')
                  OR h.applicant_ethnicity_5 IN ('1','11','12','13','14'))
                OR (h.applicant_race_1 IN ('1','2','3','4','5','21','22','23','24','25','26','27','41','42','43','44')
                    OR h.applicant_race_2 IN ('1','2','3','4','5','21','22','23','24','25','26','27','41','42','43','44')
                    OR h.applicant_race_3 IN ('1','2','3','4','5','21','22','23','24','25','26','27','41','42','43','44')
                    OR h.applicant_race_4 IN ('1','2','3','4','5','21','22','23','24','25','26','27','41','42','43','44')
                    OR h.applicant_race_5 IN ('1','2','3','4','5','21','22','23','24','25','26','27','41','42','43','44'))
            THEN 1 ELSE 0 
        END as has_demographic_data
    FROM `hdma1-242116.hmda.hmda` h
    WHERE CAST(h.activity_year AS STRING) IN ({years_list})
        AND h.census_tract IN ({tracts_list})
        AND h.action_taken = '1'  -- Originations only
        AND h.loan_purpose = '1'  -- Home purchase
        AND h.occupancy_type = '1'  -- Owner-occupied
        AND h.reverse_mortgage != '1'  -- Not reverse mortgage
        AND h.construction_method = '1'  -- Site-built
        AND h.total_units IN ('1', '2', '3', '4')  -- 1-4 units
),

market_aggregated AS (
    SELECT 
        activity_year,
        COUNT(*) as total_originations,
        SUM(loan_amount) as total_amount,
        -- Counts with demographic data
        COUNTIF(has_demographic_data = 1) as loans_with_demographics,
        -- Black borrowers (with data)
        COUNTIF(has_demographic_data = 1 AND is_black = 1) as black_loans,
        -- Hispanic borrowers (with data)
        COUNTIF(has_demographic_data = 1 AND is_hispanic = 1) as hispanic_loans,
        -- Asian borrowers (with data)
        COUNTIF(has_demographic_data = 1 AND is_asian = 1) as asian_loans,
        -- White borrowers (with data)
        COUNTIF(has_demographic_data = 1 AND is_white = 1) as white_loans,
        -- Native American borrowers (with data)
        COUNTIF(has_demographic_data = 1 AND is_native_american = 1) as native_american_loans,
        -- Hawaiian/Pacific Islander borrowers (with data)
        COUNTIF(has_demographic_data = 1 AND is_hopi = 1) as hopi_loans,
        -- LMIB
        COUNTIF(is_lmib = 1) as lmib_loans,
        -- LMICT
        COUNTIF(is_lmict = 1) as lmict_loans,
        -- MMCT
        COUNTIF(is_mmct = 1) as mmct_loans
    FROM filtered_hmda
    GROUP BY activity_year
),

lender_aggregated AS (
    SELECT 
        activity_year,
        lei,
        COUNT(*) as total_originations,
        SUM(loan_amount) as total_amount,
        COUNTIF(has_demographic_data = 1) as loans_with_demographics,
        COUNTIF(has_demographic_data = 1 AND is_black = 1) as black_loans,
        COUNTIF(has_demographic_data = 1 AND is_hispanic = 1) as hispanic_loans,
        COUNTIF(has_demographic_data = 1 AND is_asian = 1) as asian_loans,
        COUNTIF(has_demographic_data = 1 AND is_white = 1) as white_loans,
        COUNTIF(has_demographic_data = 1 AND is_native_american = 1) as native_american_loans,
        COUNTIF(has_demographic_data = 1 AND is_hopi = 1) as hopi_loans,
        COUNTIF(is_lmib = 1) as lmib_loans,
        COUNTIF(is_lmict = 1) as lmict_loans,
        COUNTIF(is_mmct = 1) as mmct_loans
    FROM filtered_hmda
    GROUP BY activity_year, lei
)

SELECT 
    'Market' as analysis_type,
    activity_year,
    NULL as lei,
    total_originations,
    total_amount,
    loans_with_demographics,
    black_loans,
    hispanic_loans,
    asian_loans,
    white_loans,
    native_american_loans,
    hopi_loans,
    lmib_loans,
    lmict_loans,
    mmct_loans
FROM market_aggregated

UNION ALL

SELECT 
    'Lender' as analysis_type,
    activity_year,
    lei,
    total_originations,
    total_amount,
    loans_with_demographics,
    black_loans,
    hispanic_loans,
    asian_loans,
    white_loans,
    native_american_loans,
    hopi_loans,
    lmib_loans,
    lmict_loans,
    mmct_loans
FROM lender_aggregated

ORDER BY analysis_type, activity_year, lei
"""
    
    return query


def build_top_lenders_2024_query(tract_list: list) -> str:
    """
    Get top 10 lenders by 2024 volume (names will be merged from crosswalk)
    
    Args:
        tract_list: List of census tract GEOIDs
    
    Returns:
        SQL query to get top lenders
    """
    tracts_list = ', '.join([f"'{tract}'" for tract in tract_list])
    
    query = f"""
-- Get top 10 lenders by 2024 volume
SELECT 
    lei,
    COUNT(*) as total_originations_2024,
    SUM(loan_amount) as total_amount_2024
FROM `hdma1-242116.hmda.hmda`
WHERE CAST(activity_year AS STRING) = '2024'
    AND census_tract IN ({tracts_list})
    AND action_taken = '1'
    AND loan_purpose = '1'
    AND occupancy_type = '1'
    AND reverse_mortgage != '1'
    AND construction_method = '1'
    AND total_units IN ('1', '2', '3', '4')
GROUP BY lei
ORDER BY total_originations_2024 DESC
LIMIT 10
"""
    
    return query

