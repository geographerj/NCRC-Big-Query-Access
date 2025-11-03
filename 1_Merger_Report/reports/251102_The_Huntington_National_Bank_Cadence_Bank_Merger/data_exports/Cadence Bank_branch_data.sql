
-- Goal-Setting Analysis: Branch Data Query
-- Subject Bank RSSD: 606046
-- Assessment Area Counties: 142 counties
-- Year: 2025
-- Comparison: Subject bank vs ALL other lenders in assessment areas

WITH assessment_area_counties AS (
    -- Filter to only assessment area counties using GEOID5
    SELECT DISTINCT geoid5
    FROM UNNEST(['01081', '01009', '01073', '01115', '01117', '01003', '01103', '01055', '01083', '01089', '01097', '01085', '01101', '01125', '01013', '01025', '01039', '01049', '01071', '01095', '01121', '01129', '05007', '05143', '05033', '05131', '05051', '05031', '05045', '05085', '05119', '05091', '05001', '05027', '05055', '05057', '05065', '05073', '05093', '05095', '05103', '05117', '05121', '05133', '05139', '12091', '12131', '12017', '12081', '12115', '12083', '12005', '12033', '12113', '12103', '12053', '12057', '12101', '13059', '13089', '13121', '13135', '13073', '13189', '13245', '13047', '13295', '13139', '13021', '13169', '13067', '13051', '13153', '13093', '13267', '22079', '22005', '22033', '22063', '22055', '22019', '22067', '22073', '22083', '22015', '22017', '22061', '28047', '28059', '28035', '28073', '28049', '28089', '28121', '28123', '28127', '28033', '28137', '28003', '28013', '28017', '28025', '28043', '28057', '28061', '28067', '28071', '28081', '28087', '28095', '28099', '28105', '28107', '28115', '28117', '28141', '28145', '28149', '28153', '28159', '28161', '29189', '29189', '29077', '47065', '47033', '47053', '47113', '47047', '47157', '47167', '47037', '47187', '47055', '47095', '47103', '47109', '47183', '48021', '48209', '48453', '48491']) as geoid5
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
        AND CAST(b.geoid5 AS STRING) IN ('01081', '01009', '01073', '01115', '01117', '01003', '01103', '01055', '01083', '01089', '01097', '01085', '01101', '01125', '01013', '01025', '01039', '01049', '01071', '01095', '01121', '01129', '05007', '05143', '05033', '05131', '05051', '05031', '05045', '05085', '05119', '05091', '05001', '05027', '05055', '05057', '05065', '05073', '05093', '05095', '05103', '05117', '05121', '05133', '05139', '12091', '12131', '12017', '12081', '12115', '12083', '12005', '12033', '12113', '12103', '12053', '12057', '12101', '13059', '13089', '13121', '13135', '13073', '13189', '13245', '13047', '13295', '13139', '13021', '13169', '13067', '13051', '13153', '13093', '13267', '22079', '22005', '22033', '22063', '22055', '22019', '22067', '22073', '22083', '22015', '22017', '22061', '28047', '28059', '28035', '28073', '28049', '28089', '28121', '28123', '28127', '28033', '28137', '28003', '28013', '28017', '28025', '28043', '28057', '28061', '28067', '28071', '28081', '28087', '28095', '28099', '28105', '28107', '28115', '28117', '28141', '28145', '28149', '28153', '28159', '28161', '29189', '29189', '29077', '47065', '47033', '47053', '47113', '47047', '47157', '47167', '47037', '47187', '47055', '47095', '47103', '47109', '47183', '48021', '48209', '48453', '48491')
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
    WHERE rssd = '606046'
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
    WHERE rssd != '606046'  -- Exclude subject bank
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
