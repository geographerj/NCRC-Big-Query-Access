-- SIMPLE QUERIES TO CHECK SOD TABLE YEAR RANGES
-- Run each query separately in BigQuery

-- ============================================================
-- Check sod25 table - year distribution
-- ============================================================
SELECT 
    year,
    COUNT(*) as total_records,
    COUNT(DISTINCT uninumbr) as unique_branches,
    COUNT(DISTINCT rssd) as unique_institutions
FROM `hdma1-242116.branches.sod25`
GROUP BY year
ORDER BY year;

-- Summary for sod25
SELECT 
    'sod25' as table_name,
    MIN(year) as min_year,
    MAX(year) as max_year,
    COUNT(DISTINCT year) as years_available,
    COUNT(*) as total_records,
    COUNT(DISTINCT uninumbr) as total_unique_branches,
    COUNT(DISTINCT rssd) as total_unique_institutions
FROM `hdma1-242116.branches.sod25`;

-- ============================================================
-- Check sod table - year distribution
-- ============================================================
SELECT 
    year,
    COUNT(*) as total_records,
    COUNT(DISTINCT uninumbr) as unique_branches,
    COUNT(DISTINCT rssd) as unique_institutions
FROM `hdma1-242116.branches.sod`
GROUP BY year
ORDER BY year;

-- Summary for sod
SELECT 
    'sod' as table_name,
    MIN(year) as min_year,
    MAX(year) as max_year,
    COUNT(DISTINCT year) as years_available,
    COUNT(*) as total_records,
    COUNT(DISTINCT uninumbr) as total_unique_branches,
    COUNT(DISTINCT rssd) as total_unique_institutions
FROM `hdma1-242116.branches.sod`;

-- ============================================================
-- Check sod_legacy table - year distribution
-- ============================================================
SELECT 
    year,
    COUNT(*) as total_records,
    COUNT(DISTINCT uninumbr) as unique_branches,
    COUNT(DISTINCT rssd) as unique_institutions
FROM `hdma1-242116.branches.sod_legacy`
GROUP BY year
ORDER BY year;

-- Summary for sod_legacy
SELECT 
    'sod_legacy' as table_name,
    MIN(year) as min_year,
    MAX(year) as max_year,
    COUNT(DISTINCT year) as years_available,
    COUNT(*) as total_records,
    COUNT(DISTINCT uninumbr) as total_unique_branches,
    COUNT(DISTINCT rssd) as total_unique_institutions
FROM `hdma1-242116.branches.sod_legacy`;

-- ============================================================
-- QUICK COMPARISON - All tables side by side
-- ============================================================
SELECT 
    'sod25' as table_name,
    MIN(year) as min_year,
    MAX(year) as max_year,
    COUNT(DISTINCT year) as years_available,
    COUNT(*) as total_records
FROM `hdma1-242116.branches.sod25`
UNION ALL
SELECT 
    'sod',
    MIN(year),
    MAX(year),
    COUNT(DISTINCT year),
    COUNT(*)
FROM `hdma1-242116.branches.sod`
UNION ALL
SELECT 
    'sod_legacy',
    MIN(year),
    MAX(year),
    COUNT(DISTINCT year),
    COUNT(*)
FROM `hdma1-242116.branches.sod_legacy`
ORDER BY table_name;

