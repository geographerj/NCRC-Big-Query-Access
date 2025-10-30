"""
Branch Data Query Templates

Common SQL queries for working with branch/banking data (Summary of Deposits, etc.)
"""

# Branch data tables
BRANCHES_DATASET = "hdma1-242116.branches"
SOD_TABLE = f"{BRANCHES_DATASET}.sod"  # Summary of Deposits
OPENINGS_TABLE = f"{BRANCHES_DATASET}.openings"
CLOSINGS_TABLE = f"{BRANCHES_DATASET}.closings"

# =============================================================================
# BRANCH LOCATION QUERIES
# =============================================================================

def get_branches_by_cbsa(cbsa_code: str, year: int = None) -> str:
    """
    Get all branches in a specific CBSA
    
    Args:
        cbsa_code: CBSA code
        year: Optional year filter (defaults to most recent)
    
    Returns:
        SQL query string
    """
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
        deposits
    FROM `{SOD_TABLE}`
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

def get_lender_branches(lender_name: str, year: int = None) -> str:
    """
    Get all branches for a specific lender
    
    Args:
        lender_name: Name of the lender (partial match)
        year: Optional year filter
    
    Returns:
        SQL query string
    """
    where_clause = f"WHERE UPPER(institution_name) LIKE UPPER('%{lender_name}%')"
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
        deposits
    FROM `{SOD_TABLE}`
    {where_clause}
    ORDER BY cbsa_code, deposits DESC
    """
    return query


def get_lender_branch_presence_by_cbsa(lender_name: str, year: int) -> str:
    """
    Get branch presence summary by CBSA for a lender
    
    Args:
        lender_name: Name of the lender
        year: Year to analyze
    
    Returns:
        SQL query string
    """
    query = f"""
    SELECT 
        cbsa_code,
        COUNT(*) as branch_count,
        SUM(deposits) as total_deposits,
        AVG(deposits) as avg_branch_deposits
    FROM `{SOD_TABLE}`
    WHERE UPPER(institution_name) LIKE UPPER('%{lender_name}%')
      AND year = {year}
    GROUP BY cbsa_code
    ORDER BY branch_count DESC
    """
    return query

