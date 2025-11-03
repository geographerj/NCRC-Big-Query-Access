-- Find Comerica Bank's LEI and HMDA name variations
-- Run this in BigQuery to find Comerica's identifiers

SELECT DISTINCT
    lei,
    respondent_name,
    COUNT(*) as total_records,
    COUNTIF(action_taken = '1') as originations,
    SUM(CASE WHEN action_taken = '1' THEN loan_amount END) as total_loan_amount,
    COUNT(DISTINCT cbsa_code) as cbsas_served,
    MIN(activity_year) as first_year,
    MAX(activity_year) as last_year
FROM `hdma1-242116.hmda.hmda`
WHERE UPPER(respondent_name) LIKE UPPER('%COMERICA%')
  AND activity_year >= 2020  -- Recent years
GROUP BY lei, respondent_name
ORDER BY originations DESC
LIMIT 20;

-- Look for variations like:
-- - Comerica Bank
-- - Comerica Bank, National Association
-- - Comerica, etc.

