-- Find Fifth Third and Comerica Small Business Lending Data
-- Using RSSD matching (most reliable method)

-- Fifth Third Bank: RSSD 723112
-- Comerica Bank: RSSD 60143

-- Get summary by CBSA for both banks
SELECT 
    l.sb_rssd as rssd,
    l.sb_lender as lender_name,
    d.msamd as cbsa_code,
    d.cbsa as cbsa_name,
    d.year,
    -- Total SB Loans
    SUM(num_under_100k + num_100k_250k + num_250k_1m) as total_sb_loans,
    SUM(amt_under_100k + amt_100k_250k + amt_250k_1m) as total_sb_amount,
    -- LMICT loans (income_group_total IN 101, 102, 1-8)
    SUM(CASE WHEN income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
        THEN (num_under_100k + num_100k_250k + num_250k_1m) ELSE 0 END) as lmict_loan_count,
    SUM(CASE WHEN income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
        THEN (amt_under_100k + amt_100k_250k + amt_250k_1m) ELSE 0 END) as lmict_loan_amount,
    -- Avg SB LMICT Loan Amount
    CASE 
        WHEN SUM(CASE WHEN income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
            THEN (num_under_100k + num_100k_250k + num_250k_1m) ELSE 0 END) > 0
        THEN SUM(CASE WHEN income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
            THEN (amt_under_100k + amt_100k_250k + amt_250k_1m) ELSE 0 END) / 
             SUM(CASE WHEN income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
            THEN (num_under_100k + num_100k_250k + num_250k_1m) ELSE 0 END)
        ELSE NULL
    END as avg_sb_lmict_loan_amount,
    -- Loans Rev Under $1m
    SUM(numsbrev_under_1m) as loans_rev_under_1m,
    SUM(amtsbrev_under_1m) as amount_rev_under_1m,
    -- Avg Loan Amt for RUM SB
    CASE 
        WHEN SUM(numsbrev_under_1m) > 0
        THEN SUM(amtsbrev_under_1m) / SUM(numsbrev_under_1m)
        ELSE NULL
    END as avg_loan_amt_rum_sb
FROM `hdma1-242116.sb.disclosure` d
INNER JOIN `hdma1-242116.sb.lenders` l
    ON d.respondent_id = l.sb_resid
WHERE l.sb_rssd IN ('723112', '60143')  -- Fifth Third and Comerica
  AND d.year >= 2018  -- Focus on recent years
  AND d.msamd IS NOT NULL
  AND d.msamd != ''
GROUP BY l.sb_rssd, l.sb_lender, d.msamd, d.cbsa, d.year
ORDER BY l.sb_rssd, d.year DESC, total_sb_loans DESC;

