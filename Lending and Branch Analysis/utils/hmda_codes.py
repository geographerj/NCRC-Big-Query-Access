"""
HMDA Code Definitions and Filters

Standard HMDA field values for filtering and classifying loan data.
Based on HMDA Filing Instructions Guide.
"""

# =============================================================================
# ACTION TAKEN CODES
# =============================================================================
ACTION_TAKEN = {
    '1': 'Loan originated',
    '2': 'Application approved but not accepted',
    '3': 'Application denied',
    '4': 'Application withdrawn by applicant',
    '5': 'File closed for incompleteness',
    '6': 'Loan purchased',
    '7': 'Preapproval request denied',
    '8': 'Preapproval request approved but not accepted'
}

# Only originated loans (action_taken = '1')
ORIGINATIONS = ['1']

# =============================================================================
# LOAN PURPOSE CODES
# =============================================================================
LOAN_PURPOSE = {
    '1': 'Home purchase',
    '2': 'Home improvement',
    '3': 'Refinancing',  # Not used after 2017
    '31': 'Cash-out refinancing',
    '32': 'No cash-out refinancing'
}

# Home purchase only
HOME_PURCHASE = ['1']

# All residential mortgage loan purposes
ALL_RESIDENTIAL = ['1', '2', '31', '32']

# =============================================================================
# HELPER FUNCTIONS FOR CREATING WHERE CLAUSES
# =============================================================================

def create_filter_where_clause(
    action_taken_codes=None,
    loan_purpose_codes=None,
    additional_filters=None
) -> str:
    """
    Create a WHERE clause for filtering HMDA data.
    
    Args:
        action_taken_codes: List of action_taken codes to include (e.g., ['1'] for originations)
        loan_purpose_codes: List of loan_purpose codes to include (e.g., ['1'] for home purchase)
        additional_filters: Dict of additional field:value filters
    
    Returns:
        SQL WHERE clause string (without the WHERE keyword)
    
    Example:
        clause = create_filter_where_clause(
            action_taken_codes=['1'],
            loan_purpose_codes=['1']
        )
        # Returns: "action_taken = '1' AND loan_purpose = '1'"
    """
    conditions = []
    
    if action_taken_codes:
        if len(action_taken_codes) == 1:
            conditions.append(f"action_taken = '{action_taken_codes[0]}'")
        else:
            codes_str = "', '".join(action_taken_codes)
            conditions.append(f"action_taken IN ('{codes_str}')")
    
    if loan_purpose_codes:
        if len(loan_purpose_codes) == 1:
            conditions.append(f"loan_purpose = '{loan_purpose_codes[0]}'")
        else:
            codes_str = "', '".join(loan_purpose_codes)
            conditions.append(f"loan_purpose IN ('{codes_str}')")
    
    if additional_filters:
        for field, value in additional_filters.items():
            if isinstance(value, (list, tuple)):
                values_str = "', '".join(str(v) for v in value)
                conditions.append(f"{field} IN ('{values_str}')")
            else:
                conditions.append(f"{field} = '{value}'")
    
    return " AND ".join(conditions)

