-- SIMPLE QUERIES TO FIND SOD NAME MATCHES
-- Run each query separately in BigQuery to see results

-- ============================================================
-- FIFTH THIRD BANK - Search all SOD tables
-- ============================================================

-- Check sod25 table
SELECT 
    institution_name,
    COUNT(DISTINCT uninumbr) as branch_count,
    SUM(deposits) as total_deposits
FROM `hdma1-242116.branches.sod25`
WHERE year = 2024
  AND UPPER(institution_name) LIKE UPPER('%FIFTH%THIRD%')
GROUP BY institution_name
ORDER BY branch_count DESC;

-- Check sod table  
SELECT 
    institution_name,
    COUNT(DISTINCT uninumbr) as branch_count,
    SUM(deposits) as total_deposits
FROM `hdma1-242116.branches.sod`
WHERE year = 2024
  AND UPPER(institution_name) LIKE UPPER('%FIFTH%THIRD%')
GROUP BY institution_name
ORDER BY branch_count DESC;

-- ============================================================
-- COMERICA BANK - Search all SOD tables
-- ============================================================

-- Check sod25 table
SELECT 
    institution_name,
    COUNT(DISTINCT uninumbr) as branch_count,
    SUM(deposits) as total_deposits
FROM `hdma1-242116.branches.sod25`
WHERE year = 2024
  AND UPPER(institution_name) LIKE UPPER('%COMERICA%')
GROUP BY institution_name
ORDER BY branch_count DESC;

-- Check sod table
SELECT 
    institution_name,
    COUNT(DISTINCT uninumbr) as branch_count,
    SUM(deposits) as total_deposits
FROM `hdma1-242116.branches.sod`
WHERE year = 2024
  AND UPPER(institution_name) LIKE UPPER('%COMERICA%')
GROUP BY institution_name
ORDER BY branch_count DESC;

