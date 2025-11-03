"""
Generate optimized Small Business SQL query for goal-setting analysis.
Calculates all 5 SB metrics for subject bank.
"""

def build_sb_query(
    sb_respondent_id: str,
    assessment_area_geoids: list,
    years: list
) -> str:
    """
    Build optimized Small Business query for subject bank.
    
    Args:
        sb_respondent_id: Bank's SB Respondent ID (string, may have prefix like "1-0000001316")
                         Prefix should be stripped before matching
        assessment_area_geoids: List of GEOID5 codes (5-digit strings)
        years: List of years as strings (e.g., ['2018', '2019', '2020', '2021', '2022', '2023'])
    
    Returns:
        SQL query string ready for BigQuery
    
    Notes:
        - Respondent ID may have prefix separated by "-" (e.g., "1-0000001316")
        - Prefix should be ignored when matching to lenders.sb_resid
        - Join: disclosure.respondent_id = lenders.sb_resid
        - Geographic scope: Same assessment area counties as mortgage data
    """
    
    # Format GEOID5 list for SQL IN clause
    geoid5_list = "', '".join([str(g).zfill(5) for g in assessment_area_geoids])
    
    # Format years list
    years_list = "', '".join([str(y) for y in years])
    
    # Extract respondent ID without prefix
    # If format is "PREFIX-12345", extract "12345"
    if '-' in sb_respondent_id:
        respondent_id_no_prefix = sb_respondent_id.split('-', 1)[-1]
    else:
        respondent_id_no_prefix = sb_respondent_id
    
    query = f"""
-- Goal-Setting Analysis: Small Business Data Query
-- Subject Bank SB Respondent ID: {sb_respondent_id} (using {respondent_id_no_prefix} for matching)
-- Assessment Area Counties: {len(assessment_area_geoids)} counties
-- Years: {', '.join(years)}

WITH assessment_area_counties AS (
    -- Filter to only assessment area counties using GEOID5
    SELECT DISTINCT geoid5
    FROM UNNEST([{', '.join([f"'{g}'" for g in assessment_area_geoids])}]) as geoid5
),

filtered_sb_data AS (
    -- Filter SB data early: years, respondent ID, assessment area counties
    SELECT 
        CAST(d.year AS STRING) as year,
        d.msamd as cbsa_code,
        d.geoid5,
        -- SB Loans count (sum of all three size categories)
        (d.num_under_100k + d.num_100k_250k + d.num_250k_1m) as sb_loans_count,
        -- SB Loans amount (sum of all three size categories)
        (d.amt_under_100k + d.amt_100k_250k + d.amt_250k_1m) as sb_loans_amount,
        -- LMICT flag: income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
        CASE 
            WHEN d.income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
            THEN 1 ELSE 0
        END as is_lmict,
        -- LMICT loans count (if is_lmict = 1, use sb_loans_count)
        CASE 
            WHEN d.income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
            THEN (d.num_under_100k + d.num_100k_250k + d.num_250k_1m)
            ELSE 0
        END as lmict_loans_count,
        -- LMICT loans amount (if is_lmict = 1, use sb_loans_amount)
        CASE 
            WHEN d.income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
            THEN (d.amt_under_100k + d.amt_100k_250k + d.amt_250k_1m)
            ELSE 0
        END as lmict_loans_amount,
        -- Loans Rev Under $1m
        d.numsbrev_under_1m as loans_rev_under_1m,
        -- Amount Rev Under $1m
        d.amtsbrev_under_1m as amount_rev_under_1m
    FROM `hdma1-242116.sb.disclosure` d
    INNER JOIN `hdma1-242116.sb.lenders` l
        ON d.respondent_id = l.sb_resid
    INNER JOIN assessment_area_counties aac
        ON CAST(d.geoid5 AS STRING) = aac.geoid5
    WHERE CAST(d.year AS STRING) IN ('{years_list}')
        -- Match respondent ID (strip prefix if present)
        AND (l.sb_resid = '{respondent_id_no_prefix}' OR l.sb_resid = '{sb_respondent_id}')
        AND d.msamd IS NOT NULL
        AND d.msamd != ''
),

aggregated_sb_metrics AS (
    -- Aggregate SB metrics by year and CBSA
    SELECT 
        year,
        cbsa_code,
        -- Metric 1: SB Loans (count)
        SUM(sb_loans_count) as sb_loans_total,
        -- Metric 2: #LMICT (count of loans in LMICT tracts)
        SUM(lmict_loans_count) as lmict_count,
        -- Metric 3: Avg SB LMICT Loan Amount ($#,###)
        CASE 
            WHEN SUM(lmict_loans_count) > 0
            THEN SUM(lmict_loans_amount) / SUM(lmict_loans_count)
            ELSE NULL
        END as avg_sb_lmict_loan_amount,
        -- Metric 4: Loans Rev Under $1m (count)
        SUM(loans_rev_under_1m) as loans_rev_under_1m_count,
        -- Metric 5: Avg Loan Amt for RUM SB ($#,###)
        CASE 
            WHEN SUM(loans_rev_under_1m) > 0
            THEN SUM(amount_rev_under_1m) / SUM(loans_rev_under_1m)
            ELSE NULL
        END as avg_loan_amt_rum_sb
    FROM filtered_sb_data
    GROUP BY year, cbsa_code
)

-- Final output: aggregated SB metrics by year and CBSA
SELECT * FROM aggregated_sb_metrics
ORDER BY year, cbsa_code
"""
    
    return query

