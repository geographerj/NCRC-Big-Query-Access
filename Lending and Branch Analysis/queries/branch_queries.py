"""
Branch Data Query Templates

Common SQL queries for working with branch/banking data (Summary of Deposits, etc.)
"""

# Branch data tables
BRANCHES_DATASET = "hdma1-242116.branches"
# NOTE: Multiple SOD tables exist (sod, sod25, sod_legacy) - they overlap
# Use the table with 2017-2025 data (likely sod25, but verify!)
# Default to sod - USER MUST VERIFY which table has the year range they need
SOD_TABLE = f"{BRANCHES_DATASET}.sod"  # Summary of Deposits - VERIFY YEAR RANGE
SOD25_TABLE = f"{BRANCHES_DATASET}.sod25"  # 2025 data - may overlap with sod
SOD_LEGACY_TABLE = f"{BRANCHES_DATASET}.sod_legacy"  # Legacy data - may overlap
OPENINGS_TABLE = f"{BRANCHES_DATASET}.openings"
CLOSINGS_TABLE = f"{BRANCHES_DATASET}.closings"

# IMPORTANT: uninumbr is unique per branch per year - use for deduplication
# Always deduplicate when combining data from multiple SOD tables!

# =============================================================================
# BRANCH LOCATION QUERIES
# =============================================================================

def get_branches_by_cbsa(
    cbsa_code: str, 
    year: int = None,
    sod_table: str = None
) -> str:
    """
    Get all branches in a specific CBSA
    
    Args:
        cbsa_code: CBSA code
        year: Optional year filter (defaults to most recent)
        sod_table: Which SOD table to use (sod, sod25, sod_legacy)
                   Defaults to SOD_TABLE constant. USER MUST SPECIFY if using
                   multiple tables to avoid double counting!
    
    Returns:
        SQL query string
        
    NOTE: Always deduplicate results using uninumbr + year if combining
    data from multiple SOD tables!
    """
    table = sod_table or SOD_TABLE
    
    where_clause = f"WHERE cbsa_code = '{cbsa_code}'"
    if year:
        where_clause += f" AND year = {year}"
    
    query = f"""
    SELECT 
        institution_name,
        branch_name,
        address,
        city,
        state,
        zip_code,
        cbsa_code,
        county_code,
        year,
        deposits,
        uninumbr,  -- Unique branch identifier (use for deduplication!)
        geoid,  -- Unique tract identifier - can match to HMDA census_tract!
        br_lmi,  -- Flag: branch is in LMI (Low-to-Moderate Income) tract
        cr_minority  -- Flag: branch is in majority minority tract
    FROM `{table}`
    {where_clause}
    ORDER BY deposits DESC
    """
    return query


def get_branch_openings_closings(cbsa_code: str, start_year: int, end_year: int) -> str:
    """
    Get branch openings and closings for a CBSA over a time period
    
    Args:
        cbsa_code: CBSA code
        start_year: Start year
        end_year: End year
    
    Returns:
        SQL query string
    """
    query = f"""
    WITH openings AS (
        SELECT 
            cbsa_code,
            EXTRACT(YEAR FROM opening_date) as year,
            COUNT(*) as branches_opened
        FROM `{OPENINGS_TABLE}`
        WHERE cbsa_code = '{cbsa_code}'
          AND EXTRACT(YEAR FROM opening_date) BETWEEN {start_year} AND {end_year}
        GROUP BY cbsa_code, year
    ),
    closings AS (
        SELECT 
            cbsa_code,
            EXTRACT(YEAR FROM closing_date) as year,
            COUNT(*) as branches_closed
        FROM `{CLOSINGS_TABLE}`
        WHERE cbsa_code = '{cbsa_code}'
          AND EXTRACT(YEAR FROM closing_date) BETWEEN {start_year} AND {end_year}
        GROUP BY cbsa_code, year
    )
    SELECT 
        COALESCE(o.year, c.year) as year,
        COALESCE(o.branches_opened, 0) as branches_opened,
        COALESCE(c.branches_closed, 0) as branches_closed,
        COALESCE(o.branches_opened, 0) - COALESCE(c.branches_closed, 0) as net_change
    FROM openings o
    FULL OUTER JOIN closings c ON o.cbsa_code = c.cbsa_code AND o.year = c.year
    ORDER BY year
    """
    return query


def get_branch_density_by_cbsa(year: int) -> str:
    """
    Calculate branch density (branches per population) by CBSA
    
    Note: This requires joining with population data, which may be in
    the geo.census or misc datasets.
    
    Args:
        year: Year to analyze
    
    Returns:
        SQL query string
    """
    query = f"""
    SELECT 
        b.cbsa_code,
        COUNT(DISTINCT b.branch_id) as total_branches,
        -- You'll need to join with population data
        -- AVG(p.population) as population
    FROM `{SOD_TABLE}` b
    WHERE b.year = {year}
    GROUP BY b.cbsa_code
    ORDER BY total_branches DESC
    """
    return query


# =============================================================================
# LENDER-SPECIFIC BRANCH QUERIES
# =============================================================================

def get_branches_by_rssd(
    rssd: str,
    year: int = None,
    sod_table: str = None
) -> str:
    """
    Get all branches for a lender by RSSD (MOST RELIABLE METHOD!).
    
    RSSD is the same in SOD - use this instead of name matching when possible.
    
    Args:
        rssd: RSSD/RSS-ID number (as string, e.g., '723112')
        year: Optional year filter
        sod_table: Which SOD table to use (sod, sod25, sod_legacy)
    
    Returns:
        SQL query string
    """
    table = sod_table or SOD_TABLE
    
    # RSSD is stored as string
    where_clause = f"WHERE rssd = '{rssd}'"
    if year:
        # Year might be string or int - cast for safety
        where_clause += f" AND CAST(year AS STRING) = CAST({year} AS STRING)"
    
    # Check if this is sod25 (which has different column names)
    is_sod25 = 'sod25' in table.lower()
    
    if is_sod25:
        # sod25 uses: bank_name, deposits_000s, br_minority (not cr_minority), geoid5
        # Note: deposits_000s is in thousands, need to multiply by 1000
        query = f"""
        SELECT 
            rssd,
            year,
            CAST(deposits_000s AS FLOAT64) * 1000 as deposits,
            uninumbr,
            geoid,
            geoid5,
            br_lmi,
            br_minority as cr_minority,
            bank_name,
            branch_name,
            address,
            city,
            state,
            zip as zip_code
        FROM `{table}`
        {where_clause}
        ORDER BY deposits DESC
        """
    else:
        # Original sod table structure
        query = f"""
        SELECT 
            institution_name,
            branch_name,
            address,
            city,
            state,
            zip_code,
            cbsa_code,
            county_code,
            year,
            deposits,
            uninumbr,
            rssd,
            geoid,
            br_lmi,
            cr_minority
        FROM `{table}`
        {where_clause}
        ORDER BY cbsa_code, deposits DESC
        """
    return query


def get_lender_branches(
    lender_name: str = None,
    rssd: str = None,
    year: int = None,
    sod_table: str = None,
    exact_match: bool = False
) -> str:
    """
    Get all branches for a specific lender.
    
    PREFER RSSD MATCHING! Use rssd parameter if you have RSSD number (most reliable).
    Name matching may have issues - names differ between HMDA and SOD.
    
    Args:
        lender_name: Name of the lender (partial match by default) - use if no RSSD
        rssd: RSSD/RSS-ID number (RECOMMENDED - most reliable method)
        year: Optional year filter
        sod_table: Which SOD table to use (sod, sod25, sod_legacy)
        exact_match: If True, use exact match instead of LIKE (only for name matching)
    
    Returns:
        SQL query string
        
    NOTE: Results must be deduplicated using uninumbr + year if combining
    multiple SOD tables!
    """
    table = sod_table or SOD_TABLE
    
    # Prefer RSSD matching if available
    if rssd:
        # RSSD is stored as integer, so cast to int for comparison
        rssd_int = int(rssd) if isinstance(rssd, str) else rssd
        where_clause = f"WHERE CAST(rssd AS INT64) = {rssd_int}"
        if year:
            where_clause += f" AND year = {year}"
    elif lender_name:
        if exact_match:
            where_clause = f"WHERE UPPER(TRIM(institution_name)) = UPPER(TRIM('{lender_name}'))"
        else:
            where_clause = f"WHERE UPPER(institution_name) LIKE UPPER('%{lender_name}%')"
        if year:
            where_clause += f" AND year = {year}"
    else:
        raise ValueError("Must provide either lender_name or rssd")
    
    query = f"""
    SELECT 
        institution_name,
        branch_name,
        address,
        city,
        state,
        zip_code,
        cbsa_code,
        county_code,
        year,
        deposits,
        uninumbr,  -- Unique branch identifier
        rssd,  -- RSSD ID (not in HMDA, but useful for reference)
        geoid,  -- Unique tract identifier - can match to HMDA census_tract!
        br_lmi,  -- Flag: branch is in LMI (Low-to-Moderate Income) tract
        cr_minority  -- Flag: branch is in majority minority tract
    FROM `{table}`
    {where_clause}
    ORDER BY cbsa_code, deposits DESC
    """
    return query


def get_lender_branch_presence_by_cbsa(
    lender_name: str, 
    year: int,
    sod_table: str = None
) -> str:
    """
    Get branch presence summary by CBSA for a lender
    
    WARNING: Verify bank name matches manually!
    Names differ between HMDA and SOD datasets.
    
    Args:
        lender_name: Name of the lender (must match SOD institution_name)
        year: Year to analyze
        sod_table: Which SOD table to use (sod, sod25, sod_legacy)
    
    Returns:
        SQL query string
        
    NOTE: Use deduplicate_branches() function after querying if combining
    multiple SOD tables to avoid double counting!
    """
    table = sod_table or SOD_TABLE
    
    query = f"""
    SELECT 
        cbsa_code,
        COUNT(DISTINCT uninumbr) as branch_count,  -- Use uninumbr to avoid duplicates
        SUM(deposits) as total_deposits,
        AVG(deposits) as avg_branch_deposits
    FROM `{table}`
    WHERE UPPER(institution_name) LIKE UPPER('%{lender_name}%')
      AND year = {year}
    GROUP BY cbsa_code
    ORDER BY branch_count DESC
    """
    return query


def get_branches_2017_2025(
    cbsa_code: str = None,
    lender_name: str = None,
    use_table: str = 'sod25'  # Default assumption - VERIFY!
) -> str:
    """
    Get branches for years 2017-2025.
    
    NOTE: User must verify which SOD table has 2017-2025 data!
    This function defaults to sod25 but may need adjustment.
    
    Args:
        cbsa_code: Optional CBSA filter
        lender_name: Optional lender name filter
        use_table: Which table to use ('sod', 'sod25', 'sod_legacy')
                   Defaults to 'sod25' - VERIFY THIS IS CORRECT!
    
    Returns:
        SQL query string
    """
    table_map = {
        'sod': SOD_TABLE,
        'sod25': SOD25_TABLE,
        'sod_legacy': SOD_LEGACY_TABLE
    }
    
    table = table_map.get(use_table.lower(), SOD25_TABLE)
    
    where_clauses = []
    
    # Year filter (2017-2025)
    where_clauses.append("year BETWEEN 2017 AND 2025")
    
    if cbsa_code:
        where_clauses.append(f"cbsa_code = '{cbsa_code}'")
    
    if lender_name:
        where_clauses.append(f"UPPER(institution_name) LIKE UPPER('%{lender_name}%')")
    
    where_clause = "WHERE " + " AND ".join(where_clauses)
    
    query = f"""
    SELECT 
        institution_name,
        branch_name,
        address,
        city,
        state,
        zip_code,
        cbsa_code,
        county_code,
        year,
        deposits,
        uninumbr,
        rssd,
        geoid,  -- Unique tract identifier - can match to HMDA census_tract!
        br_lmi,  -- Flag: branch is in LMI (Low-to-Moderate Income) tract
        cr_minority  -- Flag: branch is in majority minority tract
    FROM `{table}`
    {where_clause}
    ORDER BY year, cbsa_code, deposits DESC
    """
    
    return query


# =============================================================================
# TRACT-LEVEL BRANCH ANALYSIS QUERIES
# =============================================================================

def get_branches_by_tract_demographics(
    lender_name: str = None,
    year: int = None,
    sod_table: str = None,
    lmi_only: bool = False,
    minority_only: bool = False
) -> str:
    """
    Get branches by tract demographics (LMI and minority flags).
    
    Use GEOID to join with HMDA census_tract data!
    
    Args:
        lender_name: Optional lender name filter
        year: Optional year filter
        sod_table: Which SOD table to use
        lmi_only: If True, only return branches in LMI tracts (br_lmi = 1)
        minority_only: If True, only return branches in majority minority tracts (cr_minority = 1)
    
    Returns:
        SQL query string
    """
    table = sod_table or SOD_TABLE
    
    where_clauses = []
    
    if lender_name:
        where_clauses.append(f"UPPER(institution_name) LIKE UPPER('%{lender_name}%')")
    
    if year:
        where_clauses.append(f"year = {year}")
    
    if lmi_only:
        where_clauses.append("br_lmi = 1")
    
    if minority_only:
        where_clauses.append("cr_minority = 1")
    
    where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    query = f"""
    SELECT 
        institution_name,
        branch_name,
        geoid,  -- Match this to HMDA census_tract!
        cbsa_code,
        county_code,
        year,
        deposits,
        uninumbr,
        br_lmi,  -- 1 = branch in LMI tract, 0 = not
        cr_minority,  -- 1 = branch in majority minority tract, 0 = not
        address,
        city,
        state
    FROM `{table}`
    {where_clause}
    ORDER BY year, cbsa_code, br_lmi DESC, cr_minority DESC
    """
    
    return query


def get_branch_presence_in_lmi_minority_tracts(
    lender_name: str,
    year: int,
    sod_table: str = None
) -> str:
    """
    Get summary of branch presence in LMI and minority tracts.
    
    Args:
        lender_name: Name of the lender (verify SOD name!)
        year: Year to analyze
        sod_table: Which SOD table to use
    
    Returns:
        SQL query string with counts by tract type
    """
    table = sod_table or SOD_TABLE
    
    query = f"""
    SELECT 
        COUNT(DISTINCT uninumbr) as total_branches,
        SUM(CASE WHEN br_lmi = 1 THEN 1 ELSE 0 END) as branches_in_lmi_tracts,
        SUM(CASE WHEN cr_minority = 1 THEN 1 ELSE 0 END) as branches_in_minority_tracts,
        SUM(CASE WHEN br_lmi = 1 AND cr_minority = 1 THEN 1 ELSE 0 END) as branches_in_lmi_minority_tracts,
        SUM(CASE WHEN br_lmi = 0 AND cr_minority = 0 THEN 1 ELSE 0 END) as branches_in_non_lmi_non_minority_tracts,
        -- Percentages
        ROUND(100.0 * SUM(CASE WHEN br_lmi = 1 THEN 1 ELSE 0 END) / COUNT(DISTINCT uninumbr), 2) as pct_in_lmi_tracts,
        ROUND(100.0 * SUM(CASE WHEN cr_minority = 1 THEN 1 ELSE 0 END) / COUNT(DISTINCT uninumbr), 2) as pct_in_minority_tracts,
        ROUND(100.0 * SUM(CASE WHEN br_lmi = 1 AND cr_minority = 1 THEN 1 ELSE 0 END) / COUNT(DISTINCT uninumbr), 2) as pct_in_lmi_minority_tracts
    FROM `{table}`
    WHERE UPPER(institution_name) LIKE UPPER('%{lender_name}%')
      AND year = {year}
    """
    
    return query


def get_branches_by_cbsa_with_demographics(
    lender_name: str,
    year: int,
    sod_table: str = None
) -> str:
    """
    Get branch presence by CBSA with LMI and minority tract breakdown.
    
    Args:
        lender_name: Name of the lender (verify SOD name!)
        year: Year to analyze
        sod_table: Which SOD table to use
    
    Returns:
        SQL query string with branch counts by CBSA and tract type
    """
    table = sod_table or SOD_TABLE
    
    query = f"""
    SELECT 
        cbsa_code,
        COUNT(DISTINCT uninumbr) as total_branches,
        SUM(CASE WHEN br_lmi = 1 THEN 1 ELSE 0 END) as branches_in_lmi_tracts,
        SUM(CASE WHEN cr_minority = 1 THEN 1 ELSE 0 END) as branches_in_minority_tracts,
        SUM(CASE WHEN br_lmi = 1 AND cr_minority = 1 THEN 1 ELSE 0 END) as branches_in_lmi_minority_tracts,
        SUM(deposits) as total_deposits,
        AVG(deposits) as avg_branch_deposits
    FROM `{table}`
    WHERE UPPER(institution_name) LIKE UPPER('%{lender_name}%')
      AND year = {year}
      AND cbsa_code IS NOT NULL
      AND cbsa_code != ''
    GROUP BY cbsa_code
    ORDER BY total_branches DESC
    """
    
    return query

