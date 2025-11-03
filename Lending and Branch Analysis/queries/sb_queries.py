"""
Small Business (SB) Data Query Templates

Common SQL queries for working with Small Business Lending (CRA) data.
"""

# SB dataset
SB_DATASET = "hdma1-242116.sb"
DISCLOSURE_TABLE = f"{SB_DATASET}.disclosure"
LENDERS_TABLE = f"{SB_DATASET}.lenders"

# Key metric formulas:
# SB Loans = num_under_100k + num_100k_250k + num_250k_1m
# LMICT = income_group_total IN (101, 102, 1, 2, 3, 4, 5, 6, 7, 8)
# Avg SB LMICT Loan Amount = total_LMICT_amount / total_LMICT_count
# Loans Rev Under $1m = numsbrev_under_1m
# Avg Loan Amt for RUM SB = amtsbrev_under_1m / numsbrev_under_1m

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def is_lmict_filter():
    """Return SQL filter for LMICT (Low-to-Moderate Income Census Tract)"""
    return "income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')"

def sb_loans_count():
    """Return SQL expression for total SB loans count"""
    return "(num_under_100k + num_100k_250k + num_250k_1m)"

def sb_loans_amount():
    """Return SQL expression for total SB loans amount"""
    return "(amt_under_100k + amt_100k_250k + amt_250k_1m)"

# =============================================================================
# LENDER-SPECIFIC QUERIES
# =============================================================================

def get_sb_data_by_respondent_id(
    respondent_id: str,
    year: int = None,
    cbsa_code: str = None
) -> str:
    """
    Get small business lending data by respondent_id
    
    Args:
        respondent_id: Respondent ID (e.g., '0000025190' for Fifth Third)
        year: Optional year filter
        cbsa_code: Optional CBSA code filter
    
    Returns:
        SQL query string with key SB metrics
    """
    where_clause = f"WHERE respondent_id = '{respondent_id}'"
    
    if year:
        where_clause += f" AND year = {year}"
    
    if cbsa_code:
        where_clause += f" AND msamd = '{cbsa_code}'"
    
    query = f"""
    SELECT 
        d.respondent_id,
        d.msamd as cbsa_code,
        d.cbsa as cbsa_name,
        d.year,
        d.geoid5,
        d.county,
        d.state,
        -- SB Loans (total count)
        {sb_loans_count()} as total_sb_loans,
        -- SB Loans (total amount)
        {sb_loans_amount()} as total_sb_amount,
        -- LMICT loans
        SUM(CASE WHEN {is_lmict_filter()}
            THEN {sb_loans_count()} ELSE 0 END) OVER (PARTITION BY d.msamd, d.year, d.respondent_id) as lmict_loan_count,
        SUM(CASE WHEN {is_lmict_filter()}
            THEN {sb_loans_amount()} ELSE 0 END) OVER (PARTITION BY d.msamd, d.year, d.respondent_id) as lmict_loan_amount,
        -- Loans Rev Under $1m
        d.numsbrev_under_1m as loans_rev_under_1m,
        d.amtsbrev_under_1m as amount_rev_under_1m,
        -- Income group for filtering
        d.income_group_total,
        -- Loan size breakdowns
        d.num_under_100k,
        d.amt_under_100k,
        d.num_100k_250k,
        d.amt_100k_250k,
        d.num_250k_1m,
        d.amt_250k_1m
    FROM `{DISCLOSURE_TABLE}` d
    {where_clause}
    ORDER BY d.year DESC, d.msamd, d.income_group_total
    """
    return query

def get_sb_data_by_rssd(
    rssd: str,
    year: int = None,
    cbsa_code: str = None
) -> str:
    """
    Get small business lending data by RSSD (RECOMMENDED - more reliable!)
    
    Args:
        rssd: RSSD ID (e.g., '723112' for Fifth Third, '60143' for Comerica)
        year: Optional year filter
        cbsa_code: Optional CBSA code filter
    
    Returns:
        SQL query string with key SB metrics
    """
    where_clause = f"WHERE l.sb_rssd = '{rssd}'"
    
    if year:
        where_clause += f" AND d.year = {year}"
    
    if cbsa_code:
        where_clause += f" AND d.msamd = '{cbsa_code}'"
    
    query = f"""
    SELECT 
        d.respondent_id,
        l.sb_lender as lender_name,
        l.sb_rssd as rssd,
        d.msamd as cbsa_code,
        d.cbsa as cbsa_name,
        d.year,
        d.geoid5,
        d.county,
        d.state,
        -- SB Loans (total count)
        {sb_loans_count()} as total_sb_loans,
        -- SB Loans (total amount)
        {sb_loans_amount()} as total_sb_amount,
        -- LMICT indicator
        CASE WHEN {is_lmict_filter()} THEN 1 ELSE 0 END as is_lmict,
        -- LMICT loans (calculated in aggregation)
        CASE WHEN {is_lmict_filter()}
            THEN {sb_loans_count()} ELSE 0 END as lmict_loan_count,
        CASE WHEN {is_lmict_filter()}
            THEN {sb_loans_amount()} ELSE 0 END as lmict_loan_amount,
        -- Loans Rev Under $1m
        d.numsbrev_under_1m as loans_rev_under_1m,
        d.amtsbrev_under_1m as amount_rev_under_1m,
        -- Income group
        d.income_group_total,
        -- Loan size breakdowns
        d.num_under_100k,
        d.amt_under_100k,
        d.num_100k_250k,
        d.amt_100k_250k,
        d.num_250k_1m,
        d.amt_250k_1m
    FROM `{DISCLOSURE_TABLE}` d
    INNER JOIN `{LENDERS_TABLE}` l
        ON d.respondent_id = l.sb_resid
    {where_clause}
    ORDER BY d.year DESC, d.msamd, d.income_group_total
    """
    return query

def get_sb_summary_by_cbsa(
    rssd: str,
    year: int,
    cbsa_code: str = None
) -> str:
    """
    Get aggregated SB metrics by CBSA
    
    Returns:
        - Total SB loans
        - LMICT loan count and amount
        - Avg SB LMICT Loan Amount
        - Loans Rev Under $1m
        - Avg Loan Amt for RUM SB
    """
    where_clause = f"WHERE l.sb_rssd = '{rssd}' AND d.year = {year}"
    
    if cbsa_code:
        where_clause += f" AND d.msamd = '{cbsa_code}'"
    
    query = f"""
    SELECT 
        d.msamd as cbsa_code,
        d.cbsa as cbsa_name,
        d.year,
        l.sb_lender as lender_name,
        -- Total SB Loans
        SUM({sb_loans_count()}) as total_sb_loans,
        SUM({sb_loans_amount()}) as total_sb_amount,
        -- LMICT metrics
        SUM(CASE WHEN {is_lmict_filter()}
            THEN {sb_loans_count()} ELSE 0 END) as lmict_loan_count,
        SUM(CASE WHEN {is_lmict_filter()}
            THEN {sb_loans_amount()} ELSE 0 END) as lmict_loan_amount,
        -- Avg SB LMICT Loan Amount
        CASE 
            WHEN SUM(CASE WHEN {is_lmict_filter()} THEN {sb_loans_count()} ELSE 0 END) > 0
            THEN SUM(CASE WHEN {is_lmict_filter()} THEN {sb_loans_amount()} ELSE 0 END) / 
                 SUM(CASE WHEN {is_lmict_filter()} THEN {sb_loans_count()} ELSE 0 END)
            ELSE NULL
        END as avg_sb_lmict_loan_amount,
        -- Loans Rev Under $1m
        SUM(d.numsbrev_under_1m) as loans_rev_under_1m,
        SUM(d.amtsbrev_under_1m) as amount_rev_under_1m,
        -- Avg Loan Amt for RUM SB
        CASE 
            WHEN SUM(d.numsbrev_under_1m) > 0
            THEN SUM(d.amtsbrev_under_1m) / SUM(d.numsbrev_under_1m)
            ELSE NULL
        END as avg_loan_amt_rum_sb
    FROM `{DISCLOSURE_TABLE}` d
    INNER JOIN `{LENDERS_TABLE}` l
        ON d.respondent_id = l.sb_resid
    {where_clause}
    GROUP BY d.msamd, d.cbsa, d.year, l.sb_lender
    ORDER BY total_sb_loans DESC
    """
    return query

def get_top_cbsas_by_sb_loans(
    rssd: str,
    year: int,
    limit: int = 10
) -> str:
    """
    Get top CBSAs by small business loan volume
    
    Args:
        rssd: RSSD ID
        year: Reporting year
        limit: Number of top CBSAs to return
    
    Returns:
        SQL query string
    """
    query = f"""
    SELECT 
        d.msamd as cbsa_code,
        d.cbsa as cbsa_name,
        SUM({sb_loans_count()}) as total_sb_loans,
        SUM({sb_loans_amount()}) as total_sb_amount
    FROM `{DISCLOSURE_TABLE}` d
    INNER JOIN `{LENDERS_TABLE}` l
        ON d.respondent_id = l.sb_resid
    WHERE l.sb_rssd = '{rssd}'
      AND d.year = {year}
      AND d.msamd IS NOT NULL
      AND d.msamd != ''
    GROUP BY d.msamd, d.cbsa
    ORDER BY total_sb_loans DESC
    LIMIT {limit}
    """
    return query

# =============================================================================
# PEER COMPARISON QUERIES
# =============================================================================

def get_sb_peer_comparison(
    subject_rssd: str,
    year: int,
    cbsa_code: str = None,
    volume_range: float = 0.5  # 50% to 200%
) -> str:
    """
    Get subject bank vs peer comparison for SB lending
    
    Peers defined as lenders with 50%-200% of subject's SB loan volume
    in the same CBSA-year.
    """
    where_clause = f"WHERE d.year = {year}"
    
    if cbsa_code:
        where_clause += f" AND d.msamd = '{cbsa_code}'"
    
    query = f"""
    WITH subject_volume AS (
        SELECT 
            d.msamd,
            SUM({sb_loans_count()}) as subject_sb_loans
        FROM `{DISCLOSURE_TABLE}` d
        INNER JOIN `{LENDERS_TABLE}` l
            ON d.respondent_id = l.sb_resid
        WHERE l.sb_rssd = '{subject_rssd}'
          AND d.year = {year}
        {f"AND d.msamd = '{cbsa_code}'" if cbsa_code else ""}
        GROUP BY d.msamd
    ),
    
    all_lenders AS (
        SELECT 
            d.msamd,
            l.sb_rssd,
            l.sb_lender,
            SUM({sb_loans_count()}) as lender_sb_loans
        FROM `{DISCLOSURE_TABLE}` d
        INNER JOIN `{LENDERS_TABLE}` l
            ON d.respondent_id = l.sb_resid
        {where_clause}
        GROUP BY d.msamd, l.sb_rssd, l.sb_lender
    ),
    
    peers AS (
        SELECT DISTINCT
            al.msamd,
            al.sb_rssd,
            al.sb_lender
        FROM all_lenders al
        INNER JOIN subject_volume sv
            ON al.msamd = sv.msamd
        WHERE al.sb_rssd != '{subject_rssd}'
          AND al.lender_sb_loans >= sv.subject_sb_loans * {volume_range}
          AND al.lender_sb_loans <= sv.subject_sb_loans * {2.0 / volume_range}
    )
    
    SELECT 
        d.msamd as cbsa_code,
        d.cbsa as cbsa_name,
        CASE WHEN l.sb_rssd = '{subject_rssd}' THEN 'Subject' ELSE 'Peer' END as lender_type,
        l.sb_rssd,
        l.sb_lender as lender_name,
        -- Total SB Loans
        SUM({sb_loans_count()}) as total_sb_loans,
        SUM({sb_loans_amount()}) as total_sb_amount,
        -- LMICT metrics
        SUM(CASE WHEN {is_lmict_filter()}
            THEN {sb_loans_count()} ELSE 0 END) as lmict_loan_count,
        SUM(CASE WHEN {is_lmict_filter()}
            THEN {sb_loans_amount()} ELSE 0 END) as lmict_loan_amount,
        -- Loans Rev Under $1m
        SUM(d.numsbrev_under_1m) as loans_rev_under_1m,
        SUM(d.amtsbrev_under_1m) as amount_rev_under_1m
    FROM `{DISCLOSURE_TABLE}` d
    INNER JOIN `{LENDERS_TABLE}` l
        ON d.respondent_id = l.sb_resid
    LEFT JOIN peers p
        ON d.msamd = p.msamd
        AND l.sb_rssd = p.sb_rssd
    {where_clause}
    AND (l.sb_rssd = '{subject_rssd}' OR p.sb_rssd IS NOT NULL)
    GROUP BY d.msamd, d.cbsa, lender_type, l.sb_rssd, l.sb_lender
    ORDER BY d.msamd, lender_type
    """
    return query

