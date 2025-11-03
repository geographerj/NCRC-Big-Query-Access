
-- Goal-Setting Analysis: Branch Data Query
-- Subject Bank RSSD: 12311
-- Assessment Area Counties: 194 counties
-- Year: 2025
-- Comparison: Subject bank vs ALL other lenders in assessment areas

WITH assessment_area_counties AS (
    -- Filter to only assessment area counties using GEOID5
    SELECT DISTINCT geoid5
    FROM UNNEST(['17031', '17043', '17073', '17197', '17037', '17089', '17093', '17097', '55059', '21015', '21117', '39017', '39025', '39061', '39165', '39081', '54029', '39099', '39155', '42085', '08013', '08041', '08001', '08005', '08014', '08031', '08035', '08059', '12021', '18011', '18057', '18063', '18081', '18095', '18097', '18157', '26161', '26025', '26017', '26163', '26087', '26093', '26099', '26125', '26147', '26049', '26067', '26081', '26117', '26139', '26075', '26077', '26037', '26045', '26065', '26155', '26111', '26115', '26121', '26021', '26145', '26027', '26005', '26007', '26009', '26011', '26015', '26023', '26029', '26033', '26035', '26039', '26041', '26043', '26047', '26051', '26055', '26057', '26059', '26061', '26063', '26069', '26073', '26079', '26089', '26091', '26101', '26103', '26105', '26107', '26113', '26119', '26123', '26127', '26129', '26133', '26135', '26137', '26141', '26143', '26151', '26149', '26157', '26159', '26165', '27137', '27013', '27003', '27019', '27037', '27053', '27123', '27139', '27141', '27163', '27171', '27009', '27145', '27131', '39133', '39153', '39019', '39151', '39035', '39055', '39085', '39093', '39103', '39041', '39045', '39049', '39089', '39097', '39129', '39159', '39057', '39109', '39113', '39003', '39139', '39023', '39051', '39095', '39123', '39173', '39013', '39005', '39007', '39029', '39033', '39039', '39043', '39047', '39059', '39063', '39065', '39067', '39069', '39077', '39083', '39091', '39101', '39119', '39137', '39141', '39143', '39147', '39157', '39167', '39169', '39171', '39175', '42049', '42003', '42007', '42019', '42125', '42129', '42073', '46099', '54039', '54011', '54079', '51820', '54061', '54107', '51660', '54041', '54049', '54083', '54085', '55079', '55133', '55101']) as geoid5
),

-- CBSA crosswalk to get CBSA codes from GEOID5
cbsa_crosswalk AS (
    SELECT
        geoid5 as county_code,
        cbsa_code,
        cbsa as cbsa_name,
        County as county_name,
        State as state_name
    FROM `hdma1-242116.geo.cbsa_to_county`
),

-- Filter branches to assessment area counties and year 2025
filtered_branches AS (
    SELECT 
        CAST(b.rssd AS STRING) as rssd,
        b.bank_name as institution_name,  -- sod25 uses bank_name (not institution_name)
        COALESCE(c.cbsa_code, 'N/A') as cbsa_code,  -- Join with crosswalk to get CBSA
        CAST(b.geoid5 AS STRING) as county_code,  -- geoid5 is the 5-digit county code (GEOID5)
        b.geoid,  -- 11-digit census tract identifier
        b.br_lmi,  -- Flag: 1 = branch in LMICT, 0 = not
        b.br_minority as cr_minority,  -- sod25 uses br_minority (not cr_minority)
        b.uninumbr  -- Unique branch identifier
    FROM `hdma1-242116.branches.sod25` b
    LEFT JOIN cbsa_crosswalk c
        ON CAST(b.geoid5 AS STRING) = c.county_code
    WHERE CAST(b.year AS STRING) = '2025'
        AND CAST(b.geoid5 AS STRING) IN ('17031', '17043', '17073', '17197', '17037', '17089', '17093', '17097', '55059', '21015', '21117', '39017', '39025', '39061', '39165', '39081', '54029', '39099', '39155', '42085', '08013', '08041', '08001', '08005', '08014', '08031', '08035', '08059', '12021', '18011', '18057', '18063', '18081', '18095', '18097', '18157', '26161', '26025', '26017', '26163', '26087', '26093', '26099', '26125', '26147', '26049', '26067', '26081', '26117', '26139', '26075', '26077', '26037', '26045', '26065', '26155', '26111', '26115', '26121', '26021', '26145', '26027', '26005', '26007', '26009', '26011', '26015', '26023', '26029', '26033', '26035', '26039', '26041', '26043', '26047', '26051', '26055', '26057', '26059', '26061', '26063', '26069', '26073', '26079', '26089', '26091', '26101', '26103', '26105', '26107', '26113', '26119', '26123', '26127', '26129', '26133', '26135', '26137', '26141', '26143', '26151', '26149', '26157', '26159', '26165', '27137', '27013', '27003', '27019', '27037', '27053', '27123', '27139', '27141', '27163', '27171', '27009', '27145', '27131', '39133', '39153', '39019', '39151', '39035', '39055', '39085', '39093', '39103', '39041', '39045', '39049', '39089', '39097', '39129', '39159', '39057', '39109', '39113', '39003', '39139', '39023', '39051', '39095', '39123', '39173', '39013', '39005', '39007', '39029', '39033', '39039', '39043', '39047', '39059', '39063', '39065', '39067', '39069', '39077', '39083', '39091', '39101', '39119', '39137', '39141', '39143', '39147', '39157', '39167', '39169', '39171', '39175', '42049', '42003', '42007', '42019', '42125', '42129', '42073', '46099', '54039', '54011', '54079', '51820', '54061', '54107', '51660', '54041', '54049', '54083', '54085', '55079', '55133', '55101')
        -- Filter by geoid5 directly (5-digit county code: state_code + county_code)
        -- This matches the assessment area GEOID5 codes
),

-- Deduplicate branches (use uninumbr as unique identifier)
deduplicated_branches AS (
    SELECT 
        rssd,
        institution_name,
        cbsa_code,
        county_code,
        geoid,
        br_lmi,
        cr_minority
    FROM (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY uninumbr ORDER BY rssd) as rn
        FROM filtered_branches
    )
    WHERE rn = 1
),

-- Aggregate by CBSA for subject bank
subject_bank_aggregated AS (
    SELECT 
        cbsa_code,
        COUNT(*) as total_branches,
        COUNTIF(br_lmi = 1) as branches_in_lmict,
        SAFE_DIVIDE(COUNTIF(br_lmi = 1), COUNT(*)) * 100 as pct_lmict,
        COUNTIF(cr_minority = 1) as branches_in_mmct,
        SAFE_DIVIDE(COUNTIF(cr_minority = 1), COUNT(*)) * 100 as pct_mmct
    FROM deduplicated_branches
    WHERE rssd = '12311'
    GROUP BY cbsa_code
),

-- Aggregate by CBSA for ALL OTHER lenders (market average)
market_aggregated AS (
    SELECT 
        cbsa_code,
        COUNT(*) as total_branches,
        COUNTIF(br_lmi = 1) as branches_in_lmict,
        SAFE_DIVIDE(COUNTIF(br_lmi = 1), COUNT(*)) * 100 as pct_lmict,
        COUNTIF(cr_minority = 1) as branches_in_mmct,
        SAFE_DIVIDE(COUNTIF(cr_minority = 1), COUNT(*)) * 100 as pct_mmct
    FROM deduplicated_branches
    WHERE rssd != '12311'  -- Exclude subject bank
    GROUP BY cbsa_code
)

-- Final output: subject bank vs market comparison
SELECT 
    COALESCE(s.cbsa_code, m.cbsa_code) as cbsa_code,
    -- Subject bank metrics
    COALESCE(s.total_branches, 0) as subject_total_branches,
    COALESCE(s.pct_lmict, 0) as subject_pct_lmict,
    COALESCE(s.pct_mmct, 0) as subject_pct_mmct,
    -- Market (all other lenders) metrics
    COALESCE(m.total_branches, 0) as market_total_branches,
    COALESCE(m.pct_lmict, 0) as market_pct_lmict,
    COALESCE(m.pct_mmct, 0) as market_pct_mmct,
    -- Gap calculations (subject - market)
    COALESCE(s.pct_lmict, 0) - COALESCE(m.pct_lmict, 0) as gap_lmict,
    COALESCE(s.pct_mmct, 0) - COALESCE(m.pct_mmct, 0) as gap_mmct
FROM subject_bank_aggregated s
FULL OUTER JOIN market_aggregated m
    ON s.cbsa_code = m.cbsa_code
ORDER BY cbsa_code
