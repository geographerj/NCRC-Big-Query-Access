"""
Generate optimized Small Business peer SQL query for goal-setting analysis.
Uses 50%-200% volume rule for peer selection.
"""

def build_peer_sb_query(
    subject_sb_respondent_id: str,
    assessment_area_geoids: list,
    years: list
) -> str:
    """
    Build optimized Small Business query for peer banks (50%-200% volume rule).
    
    Args:
        subject_sb_respondent_id: Subject bank's SB Respondent ID (string, may have prefix)
        assessment_area_geoids: List of GEOID5 codes (5-digit strings)
        years: List of years as strings
    
    Returns:
        SQL query string ready for BigQuery
    
    Peer Matching:
        - Peers identified by year and CBSA (not county-level)
        - Volume range: 50% to 200% of subject bank's volume
        - Subject bank excluded from peer calculations
    """
    
    # Format GEOID5 list for SQL IN clause
    geoid5_list = "', '".join([str(g).zfill(5) for g in assessment_area_geoids])
    
    # Format years list
    years_list = "', '".join([str(y) for y in years])
    
    # Extract respondent ID without prefix
    if '-' in subject_sb_respondent_id:
        subject_respondent_id_no_prefix = subject_sb_respondent_id.split('-', 1)[-1]
    else:
        subject_respondent_id_no_prefix = subject_sb_respondent_id
    
    query = f"""
-- Goal-Setting Analysis: Peer Small Business Data Query
-- Subject Bank SB Respondent ID: {subject_sb_respondent_id} (using {subject_respondent_id_no_prefix} for matching)
-- Assessment Area Counties: {len(assessment_area_geoids)} counties
-- Years: {', '.join(years)}
-- Peer Rule: 50%-200% of subject bank's volume by year and CBSA

WITH assessment_area_counties AS (
    -- Filter to only assessment area counties using GEOID5
    SELECT DISTINCT geoid5
    FROM UNNEST([{', '.join([f"'{g}'" for g in assessment_area_geoids])}]) as geoid5
),

filtered_sb_data AS (
    -- Filter SB data early: years, assessment area counties
    SELECT 
        CAST(d.year AS STRING) as year,
        d.msamd as cbsa_code,
        l.sb_resid as respondent_id,
        -- SB Loans count and amount for volume matching
        (d.num_under_100k + d.num_100k_250k + d.num_250k_1m) as sb_loans_count,
        (d.amt_under_100k + d.amt_100k_250k + d.amt_250k_1m) as sb_loans_amount,
        -- LMICT flag and counts/amounts
        CASE 
            WHEN d.income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
            THEN 1 ELSE 0
        END as is_lmict,
        CASE 
            WHEN d.income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
            THEN (d.num_under_100k + d.num_100k_250k + d.num_250k_1m)
            ELSE 0
        END as lmict_loans_count,
        CASE 
            WHEN d.income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
            THEN (d.amt_under_100k + d.amt_100k_250k + d.amt_250k_1m)
            ELSE 0
        END as lmict_loans_amount,
        -- Revenue under $1m
        d.numsbrev_under_1m as loans_rev_under_1m,
        d.amtsbrev_under_1m as amount_rev_under_1m
    FROM `hdma1-242116.sb.disclosure` d
    INNER JOIN `hdma1-242116.sb.lenders` l
        ON d.respondent_id = l.sb_resid
    INNER JOIN assessment_area_counties aac
        ON CAST(d.geoid5 AS STRING) = aac.geoid5
    WHERE CAST(d.year AS STRING) IN ('{years_list}')
        AND d.msamd IS NOT NULL
        AND d.msamd != ''
),

subject_volume AS (
    -- Calculate subject bank's volume by year and CBSA for peer matching
    SELECT 
        year,
        cbsa_code,
        SUM(sb_loans_count) as subject_sb_vol
    FROM filtered_sb_data
    WHERE respondent_id = '{subject_respondent_id_no_prefix}' 
       OR respondent_id = '{subject_sb_respondent_id}'
    GROUP BY year, cbsa_code
),

all_lenders_volume AS (
    -- Calculate all lenders' volumes by year, CBSA, and respondent_id
    SELECT 
        year,
        cbsa_code,
        respondent_id,
        SUM(sb_loans_count) as lender_sb_vol
    FROM filtered_sb_data
    GROUP BY year, cbsa_code, respondent_id
),

peers AS (
    -- Identify peer lenders (50%-200% of subject's volume) by year and CBSA
    SELECT DISTINCT
        al.year,
        al.cbsa_code,
        al.respondent_id
    FROM all_lenders_volume al
    INNER JOIN subject_volume sv
        ON al.year = sv.year
        AND al.cbsa_code = sv.cbsa_code
    WHERE al.respondent_id != '{subject_respondent_id_no_prefix}'  -- Exclude subject bank
      AND al.respondent_id != '{subject_sb_respondent_id}'
      AND al.lender_sb_vol >= sv.subject_sb_vol * 0.5  -- At least 50% of subject volume
      AND al.lender_sb_vol <= sv.subject_sb_vol * 2.0  -- At most 200% of subject volume
),

peer_sb_data AS (
    -- Filter to only peer lenders' loans
    SELECT f.*
    FROM filtered_sb_data f
    INNER JOIN peers p
        ON f.year = p.year
        AND f.cbsa_code = p.cbsa_code
        AND f.respondent_id = p.respondent_id
),

aggregated_peer_sb_metrics AS (
    -- Aggregate peer SB metrics by year and CBSA (same structure as subject query)
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
    FROM peer_sb_data
    GROUP BY year, cbsa_code
)

-- Final output: aggregated peer SB metrics by year and CBSA
SELECT * FROM aggregated_peer_sb_metrics
ORDER BY year, cbsa_code
"""
    
    return query

