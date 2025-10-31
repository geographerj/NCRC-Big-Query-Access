/*
 * Query: Wells Fargo HMDA Records by Year
 * 
 * This query counts the number of HMDA records from Wells Fargo for each year
 * in the HMDA dataset.
 * 
 * Wells Fargo Bank, N.A. LEI: 549300RHCGHM14LPTW53
 * 
 * Run this query in BigQuery Console or using the Python script.
 */

SELECT 
    activity_year,
    COUNT(*) as total_records,
    COUNTIF(action_taken = '1') as originations,
    COUNTIF(action_taken = '3') as denials,
    COUNT(DISTINCT state_code) as states_with_activity,
    COUNT(DISTINCT census_tract) as tracts_with_activity,
    SUM(CASE WHEN action_taken = '1' THEN loan_amount ELSE 0 END) as total_originated_amount
FROM `hdma1-242116.hmda.hmda`
WHERE lei = '549300RHCGHM14LPTW53'
GROUP BY activity_year
ORDER BY activity_year;
