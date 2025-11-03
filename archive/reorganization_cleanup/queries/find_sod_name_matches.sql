-- Find SOD institution names that might match Fifth Third and Comerica
-- Run this in BigQuery and review the results

-- FIFTH THIRD BANK matches
SELECT 
    'Fifth Third Bank' as hmda_name,
    'sod25' as sod_table,
    institution_name as sod_name,
    COUNT(DISTINCT uninumbr) as branch_count,
    SUM(deposits) as total_deposits
FROM `hdma1-242116.branches.sod25`
WHERE year = 2024
  AND UPPER(institution_name) LIKE UPPER('%FIFTH%THIRD%')
GROUP BY institution_name
ORDER BY branch_count DESC;

-- COMERICA BANK matches
SELECT 
    'Comerica Bank' as hmda_name,
    'sod25' as sod_table,
    institution_name as sod_name,
    COUNT(DISTINCT uninumbr) as branch_count,
    SUM(deposits) as total_deposits
FROM `hdma1-242116.branches.sod25`
WHERE year = 2024
  AND UPPER(institution_name) LIKE UPPER('%COMERICA%')
GROUP BY institution_name
ORDER BY branch_count DESC;

-- Also check 'sod' table:
SELECT 
    'Fifth Third Bank' as hmda_name,
    'sod' as sod_table,
    institution_name as sod_name,
    COUNT(DISTINCT uninumbr) as branch_count,
    SUM(deposits) as total_deposits
FROM `hdma1-242116.branches.sod`
WHERE year = 2024
  AND UPPER(institution_name) LIKE UPPER('%FIFTH%THIRD%')
GROUP BY institution_name
ORDER BY branch_count DESC;

SELECT 
    'Comerica Bank' as hmda_name,
    'sod' as sod_table,
    institution_name as sod_name,
    COUNT(DISTINCT uninumbr) as branch_count,
    SUM(deposits) as total_deposits
FROM `hdma1-242116.branches.sod`
WHERE year = 2024
  AND UPPER(institution_name) LIKE UPPER('%COMERICA%')
GROUP BY institution_name
ORDER BY branch_count DESC;

