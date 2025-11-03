"""
Generate optimized HMDA SQL query for goal-setting analysis.
Builds query with proper string formatting for BigQuery.
"""

def build_hmda_query(
    subject_lei: str,
    assessment_area_geoids: list,
    years: list,
    loan_purpose: str = None,  # '1' for home purchase, None for all loans
    loan_purpose_group: str = None  # 'home_purchase', 'refinance', 'home_equity' for Goals sheet
) -> str:
    """
    Build optimized HMDA query for subject bank.
    
    Args:
        subject_lei: Bank's LEI (string)
        assessment_area_geoids: List of GEOID5 codes (5-digit strings)
        years: List of years as strings (e.g., ['2020', '2021', '2022', '2023', '2024'])
        loan_purpose: Single loan purpose code (e.g., '1' for home purchase)
                     Takes precedence over loan_purpose_group if both provided
        loan_purpose_group: Loan type group for Goals sheet columns:
                           - 'home_purchase': loan_purpose = '1'
                           - 'refinance': loan_purpose IN ('31', '32')
                           - 'home_equity': loan_purpose IN ('2', '4', '5') (Home Improvement, Home Equity, and Other)
    
    Returns:
        SQL query string ready for BigQuery
    """
    
    # Check for empty assessment area list
    if not assessment_area_geoids:
        # Return empty result query if no counties
        return f"""
-- Goal-Setting Analysis: HMDA Data Query
-- Subject Bank: {subject_lei}
-- Assessment Area Counties: 0 counties (no data available)
-- Years: {', '.join(years)}

SELECT 
    CAST(NULL AS STRING) as activity_year,
    CAST(NULL AS STRING) as cbsa_code,
    CAST(NULL AS INT64) as total_loans,
    CAST(NULL AS FLOAT64) as total_amount,
    CAST(NULL AS INT64) as lmict_loans,
    CAST(NULL AS FLOAT64) as lmict_percentage,
    CAST(NULL AS INT64) as lmib_loans,
    CAST(NULL AS FLOAT64) as lmib_percentage,
    CAST(NULL AS FLOAT64) as lmib_amount,
    CAST(NULL AS INT64) as mmct_loans,
    CAST(NULL AS FLOAT64) as mmct_percentage,
    CAST(NULL AS INT64) as minb_loans,
    CAST(NULL AS FLOAT64) as minb_percentage,
    CAST(NULL AS INT64) as asian_loans,
    CAST(NULL AS FLOAT64) as asian_percentage,
    CAST(NULL AS INT64) as black_loans,
    CAST(NULL AS FLOAT64) as black_percentage,
    CAST(NULL AS INT64) as native_american_loans,
    CAST(NULL AS FLOAT64) as native_american_percentage,
    CAST(NULL AS INT64) as hopi_loans,
    CAST(NULL AS FLOAT64) as hopi_percentage,
    CAST(NULL AS INT64) as hispanic_loans,
    CAST(NULL AS FLOAT64) as hispanic_percentage
WHERE FALSE
"""
    
    # Format GEOID5 list for SQL IN clause
    geoid5_list = "', '".join([str(g).zfill(5) for g in assessment_area_geoids])
    
    # Format years list
    years_list = "', '".join([str(y) for y in years])
    
    # Build loan purpose filter
    loan_purpose_filter = ""
    
    if loan_purpose:
        # Single loan purpose code takes precedence
        loan_purpose_filter = f"    AND h.loan_purpose = '{loan_purpose}'"
    elif loan_purpose_group:
        # Use loan purpose group for Goals sheet columns
        if loan_purpose_group == 'home_purchase':
            loan_purpose_filter = "    AND h.loan_purpose = '1'  -- Home Purchase"
        elif loan_purpose_group == 'refinance':
            loan_purpose_filter = "    AND h.loan_purpose IN ('31', '32')  -- Refinance (Cash-out and No Cash-out)"
        elif loan_purpose_group == 'home_equity':
            loan_purpose_filter = "    AND h.loan_purpose IN ('2', '4', '5')  -- Home Improvement (2), Home Equity (4), and Other (5)"
    
    query = f"""
-- Goal-Setting Analysis: HMDA Data Query
-- Subject Bank: {subject_lei}
-- Assessment Area Counties: {len(assessment_area_geoids)} counties
-- Years: {', '.join(years)}

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
        '{geoid5_list}' as geoid5
    FROM UNNEST([{', '.join([f"'{g}'" for g in assessment_area_geoids])}]) as geoid5
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
    WHERE CAST(h.activity_year AS STRING) IN ('{years_list}')
        AND h.lei = '{subject_lei}'
        AND CAST(h.county_code AS STRING) IN ({', '.join([f"'{g}'" for g in assessment_area_geoids])})
        AND h.action_taken = '1'  -- Originations only
        -- Standard HMDA filters
        AND h.occupancy_type = '1'  -- Owner-occupied
        AND h.reverse_mortgage != '1'  -- Not reverse mortgage
        AND h.construction_method = '1'  -- Site-built
        AND h.total_units IN ('1', '2', '3', '4')  -- 1-4 units
        {loan_purpose_filter}
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
"""
    
    return query


