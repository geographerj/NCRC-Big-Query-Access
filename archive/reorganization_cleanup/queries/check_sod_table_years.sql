-- Check record counts by year in each SOD table
-- This helps determine which table has the years you need

-- Check sod25 table
SELECT 
    'sod25' as table_name,
    year,
    COUNT(*) as total_records,
    COUNT(DISTINCT uninumbr) as unique_branches,
    COUNT(DISTINCT rssd) as unique_institutions,
    COUNT(DISTINCT cbsa_code) as unique_cbsas,
    MIN(year) OVER () as min_year_all,
    MAX(year) OVER () as max_year_all
FROM `hdma1-242116.branches.sod25`
GROUP BY year
ORDER BY year;

-- Check sod table
SELECT 
    'sod' as table_name,
    year,
    COUNT(*) as total_records,
    COUNT(DISTINCT uninumbr) as unique_branches,
    COUNT(DISTINCT rssd) as unique_institutions,
    COUNT(DISTINCT cbsa_code) as unique_cbsas,
    MIN(year) OVER () as min_year_all,
    MAX(year) OVER () as max_year_all
FROM `hdma1-242116.branches.sod`
GROUP BY year
ORDER BY year;

-- Check sod_legacy table
SELECT 
    'sod_legacy' as table_name,
    year,
    COUNT(*) as total_records,
    COUNT(DISTINCT uninumbr) as unique_branches,
    COUNT(DISTINCT rssd) as unique_institutions,
    COUNT(DISTINCT cbsa_code) as unique_cbsas,
    MIN(year) OVER () as min_year_all,
    MAX(year) OVER () as max_year_all
FROM `hdma1-242116.branches.sod_legacy`
GROUP BY year
ORDER BY year;

-- Summary comparison (all tables)
SELECT 
    'sod25' as table_name,
    MIN(year) as min_year,
    MAX(year) as max_year,
    COUNT(DISTINCT year) as years_available,
    COUNT(*) as total_records_all_years,
    COUNT(DISTINCT uninumbr) as total_unique_branches,
    COUNT(DISTINCT rssd) as total_unique_institutions
FROM `hdma1-242116.branches.sod25`
UNION ALL
SELECT 
    'sod',
    MIN(year),
    MAX(year),
    COUNT(DISTINCT year),
    COUNT(*),
    COUNT(DISTINCT uninumbr),
    COUNT(DISTINCT rssd)
FROM `hdma1-242116.branches.sod`
UNION ALL
SELECT 
    'sod_legacy',
    MIN(year),
    MAX(year),
    COUNT(DISTINCT year),
    COUNT(*),
    COUNT(DISTINCT uninumbr),
    COUNT(DISTINCT rssd)
FROM `hdma1-242116.branches.sod_legacy`;

