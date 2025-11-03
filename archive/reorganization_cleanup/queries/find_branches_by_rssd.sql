-- Find branches using RSSD (much more reliable than name matching!)
-- Use RSSD from your crosswalk file

-- Example: Find Fifth Third branches by RSSD
-- Replace 'FIFTH_THIRD_RSSD' with actual RSSD from your crosswalk
SELECT 
    institution_name,
    rssd,
    COUNT(DISTINCT uninumbr) as branch_count,
    SUM(deposits) as total_deposits,
    MIN(year) as first_year,
    MAX(year) as last_year
FROM `hdma1-242116.branches.sod25`
WHERE rssd = 'FIFTH_THIRD_RSSD'  -- Replace with actual RSSD
  AND year = 2024
GROUP BY institution_name, rssd;

-- Example: Find Comerica branches by RSSD
-- Replace 'COMERICA_RSSD' with actual RSSD from your crosswalk
SELECT 
    institution_name,
    rssd,
    COUNT(DISTINCT uninumbr) as branch_count,
    SUM(deposits) as total_deposits,
    MIN(year) as first_year,
    MAX(year) as last_year
FROM `hdma1-242116.branches.sod25`
WHERE rssd = 'COMERICA_RSSD'  -- Replace with actual RSSD
  AND year = 2024
GROUP BY institution_name, rssd;

