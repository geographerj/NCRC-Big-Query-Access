
-- Goal-Setting Analysis: Branch Data Query
-- Subject Bank RSSD: 288853
-- Assessment Area Counties: 26 counties
-- Year: 2025
-- Comparison: Subject bank vs ALL other lenders in assessment areas

WITH assessment_area_counties AS (
    -- Filter to only assessment area counties using GEOID5
    SELECT DISTINCT geoid5
    FROM UNNEST(['04013', '04021', '06065', '06071', '08037', '08045', '08049', '08057', '08065', '08097', '08107', '08117', '08041', '08119', '08001', '08005', '08013', '08014', '08019', '08031', '08035', '08047', '08059', '08093', '08123', '08069']) as geoid5
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
        AND CAST(b.geoid5 AS STRING) IN ('04013', '04021', '06065', '06071', '08037', '08045', '08049', '08057', '08065', '08097', '08107', '08117', '08041', '08119', '08001', '08005', '08013', '08014', '08019', '08031', '08035', '08047', '08059', '08093', '08123', '08069')
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
    WHERE rssd = '288853'
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
    WHERE rssd != '288853'  -- Exclude subject bank
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
