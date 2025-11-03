"""
Generate optimized branch SQL query for goal-setting analysis.
Compares subject bank to ALL other lenders in the CBSA (no peer selection rule).
Uses sod25 table for 2025 data.
"""

def build_branch_query(
    subject_rssd: str,
    assessment_area_geoids: list,
    year: int = 2025
) -> str:
    """
    Build optimized branch query comparing subject bank to all other lenders.
    
    Args:
        subject_rssd: Bank's RSSD ID (string)
        assessment_area_geoids: List of GEOID5 codes (5-digit strings) for assessment area counties
        year: Year for branch data (default: 2025)
    
    Returns:
        SQL query string ready for BigQuery
    
    Note:
        - Compares subject bank to ALL other lenders (no peer selection rule)
        - Filters to assessment area counties only
        - Calculates LMICT and MMCT percentages for subject and market
    """
    
    # Format GEOID5 list - convert to strings with proper padding
    geoid5_list = [str(g).zfill(5) for g in assessment_area_geoids]
    
    query = f"""
-- Goal-Setting Analysis: Branch Data Query
-- Subject Bank RSSD: {subject_rssd}
-- Assessment Area Counties: {len(assessment_area_geoids)} counties
-- Year: {year}
-- Comparison: Subject bank vs ALL other lenders in assessment areas

WITH assessment_area_counties AS (
    -- Filter to only assessment area counties using GEOID5
    SELECT DISTINCT geoid5
    FROM UNNEST([{', '.join([f"'{g}'" for g in geoid5_list])}]) as geoid5
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
    WHERE CAST(b.year AS STRING) = '{year}'
        AND CAST(b.geoid5 AS STRING) IN ({', '.join([f"'{g}'" for g in geoid5_list])})
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
    WHERE rssd = '{subject_rssd}'
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
    WHERE rssd != '{subject_rssd}'  -- Exclude subject bank
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
"""
    
    return query


def build_branch_query_by_state(
    subject_rssd: str,
    assessment_area_geoids: list,
    year: int = 2025
) -> str:
    """
    Build branch query aggregated by STATE (instead of CBSA).
    Useful for statewide goal-setting.
    
    Args:
        subject_rssd: Bank's RSSD ID (string)
        assessment_area_geoids: List of GEOID5 codes (5-digit strings)
        year: Year for branch data (default: 2025)
    
    Returns:
        SQL query string aggregated by state
    """
    
    geoid5_list = [str(g).zfill(5) for g in assessment_area_geoids]
    
    query = f"""
-- Goal-Setting Analysis: Branch Data Query (By State)
-- Subject Bank RSSD: {subject_rssd}
-- Assessment Area Counties: {len(assessment_area_geoids)} counties
-- Year: {year}

WITH assessment_area_counties AS (
    SELECT DISTINCT geoid5
    FROM UNNEST([{', '.join([f"'{g}'" for g in geoid5_list])}]) as geoid5
),

-- CBSA crosswalk to get CBSA codes from GEOID5 (for by-state aggregation)
cbsa_crosswalk AS (
    SELECT
        geoid5 as county_code,
        cbsa_code,
        cbsa as cbsa_name,
        County as county_name,
        State as state_name
    FROM `hdma1-242116.geo.cbsa_to_county`
),

filtered_branches AS (
    SELECT 
        CAST(b.rssd AS STRING) as rssd,
        b.bank_name as institution_name,  -- sod25 uses bank_name
        b.state,  -- State abbreviation
        CAST(b.geoid5 AS STRING) as county_code,  -- geoid5 is the 5-digit county code
        b.geoid,
        b.br_lmi,
        b.br_minority as cr_minority,  -- sod25 uses br_minority
        b.uninumbr,
        COALESCE(c.cbsa_code, 'N/A') as cbsa_code  -- Join with crosswalk to get CBSA (for aggregation)
    FROM `hdma1-242116.branches.sod25` b
    LEFT JOIN cbsa_crosswalk c
        ON CAST(b.geoid5 AS STRING) = c.county_code
    WHERE CAST(b.year AS STRING) = '{year}'
        AND CAST(b.geoid5 AS STRING) IN ({', '.join([f"'{g}'" for g in geoid5_list])})
),

deduplicated_branches AS (
    SELECT 
        rssd,
        institution_name,
        state,
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

subject_bank_aggregated AS (
    SELECT 
        state,
        COUNT(*) as total_branches,
        COUNTIF(br_lmi = 1) as branches_in_lmict,
        SAFE_DIVIDE(COUNTIF(br_lmi = 1), COUNT(*)) * 100 as pct_lmict,
        COUNTIF(cr_minority = 1) as branches_in_mmct,
        SAFE_DIVIDE(COUNTIF(cr_minority = 1), COUNT(*)) * 100 as pct_mmct
    FROM deduplicated_branches
    WHERE rssd = '{subject_rssd}'
    GROUP BY state
),

market_aggregated AS (
    SELECT 
        state,
        COUNT(*) as total_branches,
        COUNTIF(br_lmi = 1) as branches_in_lmict,
        SAFE_DIVIDE(COUNTIF(br_lmi = 1), COUNT(*)) * 100 as pct_lmict,
        COUNTIF(cr_minority = 1) as branches_in_mmct,
        SAFE_DIVIDE(COUNTIF(cr_minority = 1), COUNT(*)) * 100 as pct_mmct
    FROM deduplicated_branches
    WHERE rssd != '{subject_rssd}'
    GROUP BY state
)

SELECT 
    COALESCE(s.state, m.state) as state,
    COALESCE(s.total_branches, 0) as subject_total_branches,
    COALESCE(s.pct_lmict, 0) as subject_pct_lmict,
    COALESCE(s.pct_mmct, 0) as subject_pct_mmct,
    COALESCE(m.total_branches, 0) as market_total_branches,
    COALESCE(m.pct_lmict, 0) as market_pct_lmict,
    COALESCE(m.pct_mmct, 0) as market_pct_mmct,
    COALESCE(s.pct_lmict, 0) - COALESCE(m.pct_lmict, 0) as gap_lmict,
    COALESCE(s.pct_mmct, 0) - COALESCE(m.pct_mmct, 0) as gap_mmct
FROM subject_bank_aggregated s
FULL OUTER JOIN market_aggregated m
    ON s.state = m.state
ORDER BY state
"""
    
    return query

