-- Fifth Third Bank Small Business Lending Analysis
-- Top 10 CBSAs by SB loan volume (2018-2023)
-- Metrics: SB Loans, LMICT, Avg SB LMICT Loan Amount, Loans Rev Under $1m, Avg Loan Amt for RUM SB
-- Uses peer comparison (50%-200% volume range)

WITH cbsa_crosswalk AS (
    -- Load CBSA crosswalk if needed (SB data already has msamd/CBSA)
    SELECT DISTINCT
        msamd as cbsa_code,
        cbsa as cbsa_name
    FROM `hdma1-242116.sb.disclosure`
    WHERE msamd IS NOT NULL
      AND msamd != ''
),

subject_volume AS (
    -- Get subject bank's SB loan volume by CBSA and year for peer matching
    SELECT
        d.year,
        d.msamd as cbsa_code,
        SUM(d.num_under_100k + d.num_100k_250k + d.num_250k_1m) as subject_sb_vol
    FROM `hdma1-242116.sb.disclosure` d
    INNER JOIN `hdma1-242116.sb.lenders` l
        ON d.respondent_id = l.sb_resid
    WHERE l.sb_rssd = '723112'  -- Fifth Third Bank
      AND CAST(d.year AS INT64) BETWEEN 2018 AND 2023
      AND d.msamd IS NOT NULL
      AND d.msamd != ''
    GROUP BY d.year, d.msamd
),

top_10_cbsas AS (
    -- Find top 10 CBSAs by Fifth Third SB loan volume across all years
    SELECT 
        d.msamd as cbsa_code
    FROM `hdma1-242116.sb.disclosure` d
    INNER JOIN `hdma1-242116.sb.lenders` l
        ON d.respondent_id = l.sb_resid
    WHERE l.sb_rssd = '723112'  -- Fifth Third Bank
      AND CAST(d.year AS INT64) BETWEEN 2018 AND 2023
      AND d.msamd IS NOT NULL
      AND d.msamd != ''
    GROUP BY d.msamd
    ORDER BY SUM(d.num_under_100k + d.num_100k_250k + d.num_250k_1m) DESC
    LIMIT 10
),

all_lenders AS (
    -- Get all lenders' SB volume for peer comparison
    SELECT
        d.year,
        d.msamd as cbsa_code,
        l.sb_rssd,
        SUM(d.num_under_100k + d.num_100k_250k + d.num_250k_1m) as lender_sb_vol
    FROM `hdma1-242116.sb.disclosure` d
    INNER JOIN `hdma1-242116.sb.lenders` l
        ON d.respondent_id = l.sb_resid
    INNER JOIN top_10_cbsas t
        ON d.msamd = t.cbsa_code
    WHERE CAST(d.year AS INT64) BETWEEN 2018 AND 2023
      AND d.msamd IS NOT NULL
      AND d.msamd != ''
    GROUP BY d.year, d.msamd, l.sb_rssd
),

peers AS (
    -- Identify peer lenders (50%-200% of subject's volume, excluding subject)
    SELECT DISTINCT
        al.year,
        al.cbsa_code,
        al.sb_rssd
    FROM all_lenders al
    INNER JOIN subject_volume sv
        ON al.year = sv.year
        AND al.cbsa_code = sv.cbsa_code
    WHERE al.sb_rssd != '723112'  -- Exclude Fifth Third
      AND al.lender_sb_vol >= sv.subject_sb_vol * 0.5
      AND al.lender_sb_vol <= sv.subject_sb_vol * 2.0
),

sb_data_with_metrics AS (
    -- Join disclosure with lenders and calculate all metrics
    SELECT
        d.year,
        d.msamd as cbsa_code,
        d.cbsa as cbsa_name,
        l.sb_rssd,
        l.sb_lender as lender_name,
        -- SB Loans (total count)
        d.num_under_100k + d.num_100k_250k + d.num_250k_1m as total_sb_loans,
        -- SB Loans (total amount)
        d.amt_under_100k + d.amt_100k_250k + d.amt_250k_1m as total_sb_amount,
        -- LMICT indicator
        CASE WHEN d.income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
            THEN 1 ELSE 0 END as is_lmict,
        -- LMICT loan count
        CASE WHEN d.income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
            THEN (d.num_under_100k + d.num_100k_250k + d.num_250k_1m) ELSE 0 END as lmict_loan_count,
        -- LMICT loan amount
        CASE WHEN d.income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
            THEN (d.amt_under_100k + d.amt_100k_250k + d.amt_250k_1m) ELSE 0 END as lmict_loan_amount,
        -- Loans Rev Under $1m
        d.numsbrev_under_1m as loans_rev_under_1m,
        d.amtsbrev_under_1m as amount_rev_under_1m
    FROM `hdma1-242116.sb.disclosure` d
    INNER JOIN `hdma1-242116.sb.lenders` l
        ON d.respondent_id = l.sb_resid
    INNER JOIN top_10_cbsas t
        ON d.msamd = t.cbsa_code
    WHERE CAST(d.year AS INT64) BETWEEN 2018 AND 2023
      AND d.msamd IS NOT NULL
      AND d.msamd != ''
),

subject_data AS (
    -- Calculate subject bank metrics by CBSA and year
    SELECT
        year,
        cbsa_code,
        cbsa_name,
        SUM(total_sb_loans) as subject_total_sb_loans,
        SUM(total_sb_amount) as subject_total_sb_amount,
        SUM(lmict_loan_count) as subject_lmict_loan_count,
        SUM(lmict_loan_amount) as subject_lmict_loan_amount,
        -- Avg SB LMICT Loan Amount
        CASE 
            WHEN SUM(lmict_loan_count) > 0
            THEN SUM(lmict_loan_amount) / SUM(lmict_loan_count)
            ELSE NULL
        END as subject_avg_sb_lmict_loan_amount,
        SUM(loans_rev_under_1m) as subject_loans_rev_under_1m,
        SUM(amount_rev_under_1m) as subject_amount_rev_under_1m,
        -- Avg Loan Amt for RUM SB
        CASE 
            WHEN SUM(loans_rev_under_1m) > 0
            THEN SUM(amount_rev_under_1m) / SUM(loans_rev_under_1m)
            ELSE NULL
        END as subject_avg_loan_amt_rum_sb
    FROM sb_data_with_metrics
    WHERE sb_rssd = '723112'  -- Fifth Third Bank
    GROUP BY year, cbsa_code, cbsa_name
),

peer_data AS (
    -- Calculate peer group metrics by CBSA and year
    SELECT
        h.year,
        h.cbsa_code,
        h.cbsa_name,
        SUM(h.total_sb_loans) as peer_total_sb_loans,
        SUM(h.total_sb_amount) as peer_total_sb_amount,
        SUM(h.lmict_loan_count) as peer_lmict_loan_count,
        SUM(h.lmict_loan_amount) as peer_lmict_loan_amount,
        -- Avg SB LMICT Loan Amount (peer)
        CASE 
            WHEN SUM(h.lmict_loan_count) > 0
            THEN SUM(h.lmict_loan_amount) / SUM(h.lmict_loan_count)
            ELSE NULL
        END as peer_avg_sb_lmict_loan_amount,
        SUM(h.loans_rev_under_1m) as peer_loans_rev_under_1m,
        SUM(h.amount_rev_under_1m) as peer_amount_rev_under_1m,
        -- Avg Loan Amt for RUM SB (peer)
        CASE 
            WHEN SUM(h.loans_rev_under_1m) > 0
            THEN SUM(h.amount_rev_under_1m) / SUM(h.loans_rev_under_1m)
            ELSE NULL
        END as peer_avg_loan_amt_rum_sb
    FROM sb_data_with_metrics h
    INNER JOIN peers p
        ON h.sb_rssd = p.sb_rssd
        AND h.year = p.year
        AND h.cbsa_code = p.cbsa_code
    GROUP BY h.year, h.cbsa_code, h.cbsa_name
)

-- Final output: Subject vs Peer comparison
SELECT
    s.year as activity_year,
    s.cbsa_code,
    s.cbsa_name,
    'Small Business Lending' as loan_purpose_category,
    'Fifth Third Bank' as lender_name,
    -- Subject metrics
    s.subject_total_sb_loans,
    s.subject_total_sb_amount,
    s.subject_lmict_loan_count,
    s.subject_lmict_loan_amount,
    s.subject_avg_sb_lmict_loan_amount,
    s.subject_loans_rev_under_1m,
    s.subject_amount_rev_under_1m,
    s.subject_avg_loan_amt_rum_sb,
    -- Peer metrics
    COALESCE(p.peer_total_sb_loans, 0) as peer_total_sb_loans,
    COALESCE(p.peer_lmict_loan_count, 0) as peer_lmict_loan_count,
    COALESCE(p.peer_avg_sb_lmict_loan_amount, 0) as peer_avg_sb_lmict_loan_amount,
    COALESCE(p.peer_loans_rev_under_1m, 0) as peer_loans_rev_under_1m,
    COALESCE(p.peer_avg_loan_amt_rum_sb, 0) as peer_avg_loan_amt_rum_sb
FROM subject_data s
LEFT JOIN peer_data p
    ON s.year = p.year
    AND s.cbsa_code = p.cbsa_code
ORDER BY s.year, s.cbsa_code;

