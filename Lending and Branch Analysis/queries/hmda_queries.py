"""
HMDA Query Templates

Common SQL queries for working with HMDA (Home Mortgage Disclosure Act) data.
These queries can be customized for your specific analysis needs.
"""

# Base HMDA table reference
HMDA_TABLE = "hdma1-242116.hmda.hmda"

# =============================================================================
# BASIC QUERIES
# =============================================================================

def get_lender_activity_by_year(year: int, lender_lei: str = None) -> str:
    """
    Get lender activity summary by year
    
    Args:
        year: Year to query (2018-2024)
        lender_lei: Optional LEI to filter for specific lender
    
    Returns:
        SQL query string
    """
    where_clause = f"WHERE activity_year = {year}"
    if lender_lei:
        where_clause += f" AND lei = '{lender_lei}'"
    
    query = f"""
    SELECT 
        lei,
        activity_year,
        COUNT(*) as total_applications,
        COUNTIF(action_taken = '1') as originations,
        SUM(CASE WHEN action_taken = '1' THEN loan_amount END) as total_loan_amount,
        COUNT(DISTINCT census_tract) as tracts_with_activity,
        COUNT(DISTINCT state_code || county_code) as counties_with_activity
    FROM `{HMDA_TABLE}`
    {where_clause}
    GROUP BY lei, activity_year
    ORDER BY total_applications DESC
    LIMIT 100
    """
    return query


def get_cbsa_lending_patterns(cbsa_code: str, year: int) -> str:
    """
    Get lending patterns for a specific CBSA and year
    
    Args:
        cbsa_code: CBSA code (as string, e.g., '33860')
        year: Year to query
    
    Returns:
        SQL query string
    """
    query = f"""
    SELECT 
        lei,
        COUNT(*) as total_applications,
        COUNTIF(action_taken = '1') as originations,
        COUNTIF(loan_purpose = '1') as home_purchase_count,
        COUNTIF(loan_purpose IN ('31', '32')) as refinance_count,
        AVG(CASE WHEN action_taken = '1' THEN loan_amount END) as avg_loan_amount,
        SUM(CASE WHEN action_taken = '1' THEN loan_amount END) as total_loan_amount
    FROM `{HMDA_TABLE}`
    WHERE activity_year = {year}
      AND cbsa_code = '{cbsa_code}'
    GROUP BY lei
    ORDER BY total_applications DESC
    """
    return query


# =============================================================================
# DEMOGRAPHIC ANALYSIS QUERIES
# =============================================================================

def get_race_ethnicity_originations(year: int, cbsa_code: str = None, lender_lei: str = None) -> str:
    """
    Get originations by race/ethnicity
    
    This is a simplified version - you may need to adjust based on your specific
    race/ethnicity classification logic (checking multiple fields, hierarchical classification, etc.)
    
    Args:
        year: Year to query
        cbsa_code: Optional CBSA code filter
        lender_lei: Optional lender LEI filter
    
    Returns:
        SQL query string
    """
    where_conditions = [f"activity_year = {year}", "action_taken = '1'"]
    
    if cbsa_code:
        where_conditions.append(f"cbsa_code = '{cbsa_code}'")
    if lender_lei:
        where_conditions.append(f"lei = '{lender_lei}'")
    
    where_clause = "WHERE " + " AND ".join(where_conditions)
    
    query = f"""
    SELECT 
        lei,
        -- Hispanic classification (check all ethnicity fields)
        CASE 
            WHEN applicant_ethnicity_1 IN ('1', '11', '12', '13', '14') 
              OR applicant_ethnicity_2 IN ('1', '11', '12', '13', '14')
              OR applicant_ethnicity_3 IN ('1', '11', '12', '13', '14')
              OR applicant_ethnicity_4 IN ('1', '11', '12', '13', '14')
              OR applicant_ethnicity_5 IN ('1', '11', '12', '13', '14')
            THEN 'Hispanic'
            -- Non-Hispanic race classification
            WHEN applicant_race_1 = '3' OR applicant_race_2 = '3' OR applicant_race_3 = '3' 
              OR applicant_race_4 = '3' OR applicant_race_5 = '3'
            THEN 'Black'
            WHEN applicant_race_1 IN ('2', '21', '22', '23', '24', '25', '26', '27')
              OR applicant_race_2 IN ('2', '21', '22', '23', '24', '25', '26', '27')
              OR applicant_race_3 IN ('2', '21', '22', '23', '24', '25', '26', '27')
              OR applicant_race_4 IN ('2', '21', '22', '23', '24', '25', '26', '27')
              OR applicant_race_5 IN ('2', '21', '22', '23', '24', '25', '26', '27')
            THEN 'Asian'
            WHEN applicant_race_1 = '1' OR applicant_race_2 = '1' OR applicant_race_3 = '1'
              OR applicant_race_4 = '1' OR applicant_race_5 = '1'
            THEN 'Native American'
            WHEN applicant_race_1 = '5' OR applicant_race_2 = '5' OR applicant_race_3 = '5'
              OR applicant_race_4 = '5' OR applicant_race_5 = '5'
            THEN 'White'
            ELSE 'Unknown'
        END as borrower_category,
        COUNT(*) as originations,
        SUM(loan_amount) as total_loan_amount
    FROM `{HMDA_TABLE}`
    {where_clause}
    GROUP BY lei, borrower_category
    ORDER BY lei, originations DESC
    """
    return query


# =============================================================================
# INCOME-BASED ANALYSIS QUERIES
# =============================================================================

def get_lmi_originations(year: int, cbsa_code: str = None) -> str:
    """
    Get Low-to-Moderate Income (LMI) borrower originations
    
    Note: LMI classification typically requires comparing borrower income
    to MSA median income. You may need to join with geographic data.
    
    Args:
        year: Year to query
        cbsa_code: Optional CBSA code filter
    
    Returns:
        SQL query string
    """
    where_conditions = [f"activity_year = {year}", "action_taken = '1'"]
    
    if cbsa_code:
        where_conditions.append(f"cbsa_code = '{cbsa_code}'")
    
    where_clause = "WHERE " + " AND ".join(where_conditions)
    
    query = f"""
    SELECT 
        lei,
        cbsa_code,
        COUNT(*) as total_originations,
        COUNTIF(applicant_income_000s < 80) as estimated_lmi_originations,
        -- This is simplified - actual LMI requires MSA median income comparison
        SUM(loan_amount) as total_loan_amount
    FROM `{HMDA_TABLE}`
    {where_clause}
    GROUP BY lei, cbsa_code
    ORDER BY total_originations DESC
    """
    return query


# =============================================================================
# PEER ANALYSIS QUERIES
# =============================================================================

def get_peer_lenders(
    subject_lei: str,
    year: int,
    cbsa_code: str,
    volume_range: float = 0.5  # 50% to 200% of subject volume
) -> str:
    """
    Get peer lenders for comparative analysis
    
    Peers are defined as lenders in the same CBSA/year with application volume
    between volume_range and (1/volume_range) times the subject lender's volume.
    
    Args:
        subject_lei: LEI of the subject lender
        year: Year to analyze
        cbsa_code: CBSA code
        volume_range: Volume range multiplier (default 0.5 = 50% to 200%)
    
    Returns:
        SQL query string
    """
    query = f"""
    WITH subject_volume AS (
        SELECT 
            COUNT(*) as app_count
        FROM `{HMDA_TABLE}`
        WHERE lei = '{subject_lei}'
          AND activity_year = {year}
          AND cbsa_code = '{cbsa_code}'
    ),
    peer_candidates AS (
        SELECT 
            lei,
            COUNT(*) as app_count
        FROM `{HMDA_TABLE}`
        WHERE lei != '{subject_lei}'
          AND activity_year = {year}
          AND cbsa_code = '{cbsa_code}'
        GROUP BY lei
    )
    SELECT 
        p.lei,
        p.app_count
    FROM peer_candidates p
    CROSS JOIN subject_volume s
    WHERE p.app_count >= s.app_count * {volume_range}
      AND p.app_count <= s.app_count * (1 / {volume_range})
    ORDER BY p.app_count DESC
    """
    return query

