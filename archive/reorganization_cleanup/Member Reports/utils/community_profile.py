"""
Community Profile Data Utilities

Functions for extracting and using community profile data in member reports.
"""

import os
from typing import Dict, Optional, List
from pathlib import Path
import json


def find_community_profile(community_name: str) -> Optional[str]:
    """
    Find community profile PDF file for a given community name
    
    Args:
        community_name: Name of the community
    
    Returns:
        Path to PDF file if found, None otherwise
    """
    supporting_files_dir = Path("Member Reports/supporting_files")
    if not supporting_files_dir.exists():
        supporting_files_dir = Path("supporting_files")
    
    # Try various filename formats
    possible_names = [
        f"Community Profile of {community_name}.pdf",
        f"Community Profile of {community_name.replace(' ', '-')}.pdf",
        f"{community_name} Community Profile.pdf",
        f"{community_name.replace(' ', '_')}_Community_Profile.pdf"
    ]
    
    for filename in possible_names:
        file_path = supporting_files_dir / filename
        if file_path.exists():
            return str(file_path)
    
    return None


def get_community_context(community_name: str) -> Dict:
    """
    Get community context data (placeholder - would extract from PDF)
    
    Args:
        community_name: Name of the community
    
    Returns:
        Dictionary with community demographic data
    """
    # This is a placeholder structure
    # In practice, would extract from PDF or load from processed CSV
    
    return {
        "community_name": community_name,
        "demographics": {
            "black_percentage": None,
            "hispanic_percentage": None,
            "asian_percentage": None,
            "white_percentage": None,
            "total_population": None,
            "year": None
        },
        "income": {
            "median_household_income": None,
            "poverty_rate": None,
            "year": None
        },
        "housing": {
            "homeownership_rate": None,
            "median_home_value": None,
            "year": None
        },
        "trends": {
            "population_change": None,  # "increasing", "decreasing", "stable"
            "income_change": None,
            "demographic_shifts": []
        },
        "profile_file": find_community_profile(community_name)
    }


def format_demographic_context(community_data: Dict, metric_name: str) -> str:
    """
    Format demographic context for narrative inclusion
    
    Args:
        community_data: Community context dictionary
        metric_name: Metric being discussed (e.g., "Black borrowers", "LMICT")
    
    Returns:
        Formatted narrative text
    """
    demographics = community_data.get("demographics", {})
    community_name = community_data.get("community_name", "the community")
    
    # Example format
    text_parts = []
    
    if demographics.get("black_percentage"):
        text_parts.append(f"{community_name} is {demographics['black_percentage']:.1f}% Black/African American")
    
    if demographics.get("hispanic_percentage"):
        text_parts.append(f"{demographics['hispanic_percentage']:.1f}% Hispanic/Latino")
    
    if demographics.get("total_population"):
        text_parts.append(f"with a total population of {demographics['total_population']:,}")
    
    if text_parts:
        return f"The community profile shows that {', '.join(text_parts)}."
    
    return f"According to the community profile, {community_name} [demographic data should be extracted from PDF]."


def cite_community_profile(community_name: str, year: Optional[str] = None) -> str:
    """
    Format citation for community profile
    
    Args:
        community_name: Name of the community
        year: Year of the profile (if available)
    
    Returns:
        Formatted citation string
    """
    if year:
        return f"Community Profile of {community_name} ({year})"
    return f"Community Profile of {community_name}"


def get_demographic_comparison_text(community_data: Dict, lending_percentage: float, 
                                   demographic_type: str) -> str:
    """
    Generate comparison text between community demographics and lending patterns
    
    Args:
        community_data: Community context dictionary
        lending_percentage: Percentage of loans to demographic group
        demographic_type: Type of demographic ("black", "hispanic", etc.)
    
    Returns:
        Formatted comparison text
    """
    demographics = community_data.get("demographics", {})
    community_name = community_data.get("community_name", "the community")
    
    demographic_key = f"{demographic_type}_percentage"
    community_percentage = demographics.get(demographic_key)
    
    if community_percentage is None:
        return f"Lending to {demographic_type.title()} borrowers represents {lending_percentage:.1f}% of originations."
    
    gap = lending_percentage - community_percentage
    
    if gap < 0:
        gap_text = f"a gap of {abs(gap):.1f} percentage points below"
    elif gap > 0:
        gap_text = f"a gap of {gap:.1f} percentage points above"
    else:
        gap_text = "aligned with"
    
    return (f"While the community profile shows that {community_name} is "
            f"{community_percentage:.1f}% {demographic_type.title()}, lending to "
            f"{demographic_type.title()} borrowers represents {lending_percentage:.1f}% "
            f"of the lender's originations—{gap_text} the community's demographic composition.")


def extract_key_community_facts(community_data: Dict) -> List[str]:
    """
    Extract key facts from community profile for report inclusion
    
    Args:
        community_data: Community context dictionary
    
    Returns:
        List of key fact strings
    """
    facts = []
    demographics = community_data.get("demographics", {})
    income = community_data.get("income", {})
    trends = community_data.get("trends", {})
    
    # Demographic facts
    if demographics.get("black_percentage"):
        facts.append(f"Black/African American: {demographics['black_percentage']:.1f}%")
    
    if demographics.get("hispanic_percentage"):
        facts.append(f"Hispanic/Latino: {demographics['hispanic_percentage']:.1f}%")
    
    # Income facts
    if income.get("median_household_income"):
        facts.append(f"Median household income: ${income['median_household_income']:,}")
    
    # Trend facts
    if trends.get("population_change"):
        facts.append(f"Population trend: {trends['population_change']}")
    
    return facts


# Placeholder for PDF extraction (would require pdfplumber or similar)
def extract_from_pdf(pdf_path: str) -> Dict:
    """
    Extract data from community profile PDF
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        Dictionary with extracted data
    
    Note: This is a placeholder. Actual implementation would use:
    - pdfplumber for text extraction
    - Regular expressions for data parsing
    - Table extraction libraries for structured data
    """
    # TODO: Implement PDF extraction
    # Example using pdfplumber:
    # import pdfplumber
    # with pdfplumber.open(pdf_path) as pdf:
    #     text = ""
    #     for page in pdf.pages:
    #         text += page.extract_text()
    #     # Parse text for demographic data
    #     # Extract tables
    #     # Parse numbers and percentages
    
    return {
        "status": "not_implemented",
        "message": "PDF extraction not yet implemented. Extract data manually and store in processed/ directory."
    }

