"""
Report Formatting Utilities

Formatting functions for numbers, text, and data according to NCRC
report writing guidelines.
"""

from typing import Optional, Union
import pandas as pd


# =============================================================================
# NUMBER FORMATTING
# =============================================================================

def format_percentage(value: Union[float, int, None], decimal_places: int = 1) -> str:
    """
    Format percentage according to report guidelines: ##.#
    
    Args:
        value: Percentage value (as decimal or whole number)
        decimal_places: Number of decimal places (default 1)
    
    Returns:
        Formatted string with % symbol, or "—" if None/NaN
    """
    if value is None or pd.isna(value):
        return "—"
    
    try:
        # If value is already a percentage (0-100), use as is
        if value > 1.0:
            formatted = f"{value:,.{decimal_places}f}"
        # If value is decimal (0-1), convert to percentage
        elif value <= 1.0:
            formatted = f"{value * 100:,.{decimal_places}f}"
        else:
            formatted = f"{value:,.{decimal_places}f}"
        return f"{formatted}%"
    except (ValueError, TypeError):
        return "—"


def format_integer(value: Union[int, float, None]) -> str:
    """
    Format integer according to report guidelines: #,###
    
    Args:
        value: Integer value
    
    Returns:
        Formatted string with commas, or "—" if None/NaN
    """
    if value is None or pd.isna(value):
        return "—"
    
    try:
        # Convert to int and format with commas
        int_value = int(float(value))
        return f"{int_value:,}"
    except (ValueError, TypeError):
        return "—"


def format_gap(value: Union[float, None], include_sign: bool = True) -> str:
    """
    Format gap as percentage points with one decimal: -5.2pp, +3.1pp
    
    Args:
        value: Gap value in percentage points
        include_sign: Whether to include + sign for positive values
    
    Returns:
        Formatted string with "pp" suffix, or "—" if None/NaN
    """
    if value is None or pd.isna(value):
        return "—"
    
    try:
        gap_value = float(value)
        if gap_value >= 0 and include_sign:
            return f"+{gap_value:.1f}pp"
        else:
            return f"{gap_value:.1f}pp"
    except (ValueError, TypeError):
        return "—"


def format_currency(value: Union[float, int, None]) -> str:
    """
    Format currency value: $#,###,###
    
    Args:
        value: Currency amount
    
    Returns:
        Formatted string with $ and commas, or "—" if None/NaN
    """
    if value is None or pd.isna(value):
        return "—"
    
    try:
        amount = float(value)
        return f"${amount:,.0f}"
    except (ValueError, TypeError):
        return "—"


# =============================================================================
# TEXT FORMATTING
# =============================================================================

def format_key_term(text: str) -> str:
    """
    Format key terms for emphasis (bold in markdown/HTML context)
    Note: Actual bold formatting is applied in Excel/Word
    
    Args:
        text: Text to format
    
    Returns:
        Text with formatting markers (or plain text for Excel)
    """
    return text  # Bold formatting applied via openpyxl Font


def format_missing_data() -> str:
    """
    Return em-dash for missing data per guidelines
    
    Returns:
        Em-dash character
    """
    return "—"


# =============================================================================
# PANDAS FORMATTING
# =============================================================================

def format_dataframe_percentages(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Format specified columns as percentages with one decimal
    
    Args:
        df: DataFrame to format
        columns: List of column names to format
    
    Returns:
        DataFrame with formatted columns
    """
    df_formatted = df.copy()
    for col in columns:
        if col in df_formatted.columns:
            df_formatted[col] = df_formatted[col].apply(format_percentage)
    return df_formatted


def format_dataframe_integers(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Format specified columns as integers with commas
    
    Args:
        df: DataFrame to format
        columns: List of column names to format
    
    Returns:
        DataFrame with formatted columns
    """
    df_formatted = df.copy()
    for col in columns:
        if col in df_formatted.columns:
            df_formatted[col] = df_formatted[col].apply(format_integer)
    return df_formatted


def format_dataframe_gaps(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Format specified columns as gap values (percentage points)
    
    Args:
        df: DataFrame to format
        columns: List of column names to format
    
    Returns:
        DataFrame with formatted columns
    """
    df_formatted = df.copy()
    for col in columns:
        if col in df_formatted.columns:
            df_formatted[col] = df_formatted[col].apply(format_gap)
    return df_formatted


# =============================================================================
# ACRONYM HANDLING
# =============================================================================

COMMON_ACRONYMS = {
    'HMDA': 'Home Mortgage Disclosure Act',
    'MMCT': 'Majority-Minority Census Tract',
    'LMIB': 'Low-to-Moderate Income Borrower',
    'LMICT': 'Low-to-Moderate Income Census Tract',
    'CBSA': 'Core Based Statistical Area',
    'CRA': 'Community Reinvestment Act',
    'FFIEC': 'Federal Financial Institutions Examination Council',
    'NCRC': 'National Community Reinvestment Coalition',
    'HoPI': 'Native Hawaiian or Pacific Islander'
}


def define_acronym(acronym: str, definition: Optional[str] = None) -> str:
    """
    Format acronym with definition on first use
    
    Args:
        acronym: Acronym to define
        definition: Definition text, or use common definitions if None
    
    Returns:
        Formatted string: "Full Name (ACRONYM)"
    """
    if definition is None:
        definition = COMMON_ACRONYMS.get(acronym, acronym)
    
    return f"{definition} ({acronym})"


def apply_acronym_definitions(text: str, acronyms_used: set) -> str:
    """
    Automatically apply acronym definitions to text on first use
    
    Args:
        text: Text to process
        acronyms_used: Set of acronyms already defined
    
    Returns:
        Text with acronyms defined
    """
    # This is a placeholder - actual implementation would parse text
    # and replace first occurrence of each acronym
    return text

