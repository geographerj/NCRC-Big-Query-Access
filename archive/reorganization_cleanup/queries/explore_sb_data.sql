-- Explore Small Business (SB) Dataset Structure
-- Links disclosure table with lenders table using respondent_id

-- First, check what tables exist in the sb dataset
SELECT 
    table_name,
    table_type,
    row_count,
    size_bytes
FROM `hdma1-242116.sb.INFORMATION_SCHEMA.TABLES`
ORDER BY table_name;

-- Check the disclosure table structure
SELECT 
    column_name,
    data_type,
    is_nullable
FROM `hdma1-242116.sb.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'disclosure'
ORDER BY ordinal_position
LIMIT 100;

-- Check the lenders table structure
SELECT 
    column_name,
    data_type,
    is_nullable
FROM `hdma1-242116.sb.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'lenders'
ORDER BY ordinal_position
LIMIT 100;

-- Sample disclosure data to understand structure
SELECT *
FROM `hdma1-242116.sb.disclosure`
LIMIT 10;

-- Sample lenders data
SELECT *
FROM `hdma1-242116.sb.lenders`
LIMIT 10;

-- Check the join relationship
SELECT 
    d.respondent_id,
    l.respondent_name,
    l.respondent_rssd,
    COUNT(*) as disclosure_count
FROM `hdma1-242116.sb.disclosure` d
LEFT JOIN `hdma1-242116.sb.lenders` l
    ON d.respondent_id = l.respondent_id
GROUP BY d.respondent_id, l.respondent_name, l.respondent_rssd
ORDER BY disclosure_count DESC
LIMIT 20;

