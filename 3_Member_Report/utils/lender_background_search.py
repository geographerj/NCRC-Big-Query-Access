"""
Utility functions for extracting background information from web search results
"""

import re
from typing import Optional, Dict, List

def extract_location_from_search(search_results: str, lender_name: str) -> Optional[str]:
    """
    Extract headquarters location from web search results
    
    Looks for patterns like:
    - "headquartered in [City, State]"
    - "based in [City, State]"
    - "[City, State]" near "headquarters"
    """
    if not search_results:
        return None
    
    # Common patterns for location
    patterns = [
        r'headquartered in ([^.,\n]+(?:, [A-Z]{2})?)',
        r'based in ([^.,\n]+(?:, [A-Z]{2})?)',
        r'headquarters[^.]*([A-Z][a-z]+(?:, [A-Z]{2})?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, search_results, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            # Clean up common artifacts
            location = re.sub(r'\s+', ' ', location)
            if len(location) > 5 and len(location) < 50:  # Reasonable location length
                return location
    
    return None


def extract_history_from_search(search_results: str, lender_name: str) -> Optional[str]:
    """
    Extract company history from web search results
    
    Looks for founding dates, key milestones, etc.
    """
    if not search_results:
        return None
    
    # Look for founding dates
    founded_pattern = r'founded in (\d{4})'
    match = re.search(founded_pattern, search_results, re.IGNORECASE)
    if match:
        year = match.group(1)
        return f"Founded in {year}"
    
    return None


def extract_mergers_from_search(search_results: str, lender_name: str) -> Optional[str]:
    """
    Extract merger and acquisition information from web search results
    
    Looks for merger announcements, acquisitions, etc.
    """
    if not search_results:
        return None
    
    # Look for merger/acquisition mentions
    merger_keywords = ['merged', 'acquired', 'merger', 'acquisition', 'purchased']
    
    sentences = []
    for sentence in re.split(r'[.!?]\s+', search_results):
        sentence_lower = sentence.lower()
        if any(keyword in sentence_lower for keyword in merger_keywords):
            # Check if it's relevant (contains lender name or recent dates)
            if lender_name.lower() in sentence_lower or any(year in sentence for year in ['2018', '2019', '2020', '2021', '2022', '2023', '2024']):
                sentences.append(sentence.strip())
    
    if sentences:
        # Return first relevant merger mention
        return sentences[0][:200]  # Limit length
    
    return None


def extract_violations_from_search(search_results: str, lender_name: str) -> Optional[str]:
    """
    Extract fair lending violations from web search results
    
    Looks for CFPB, DOJ, or other regulatory actions
    """
    if not search_results:
        return None
    
    # Keywords related to violations
    violation_keywords = ['settlement', 'violation', 'discrimination', 'CFPB', 'DOJ', 'fair lending', 
                         'consent order', 'enforcement action']
    
    sentences = []
    for sentence in re.split(r'[.!?]\s+', search_results):
        sentence_lower = sentence.lower()
        if any(keyword.lower() in sentence_lower for keyword in violation_keywords):
            if lender_name.lower() in sentence_lower:
                sentences.append(sentence.strip())
    
    if sentences:
        # Return summary of violations
        return sentences[0][:200]  # Limit length
    
    return None


def extract_redlining_from_search(search_results: str, lender_name: str) -> Optional[str]:
    """
    Extract redlining complaints from web search results
    
    Looks for redlining allegations, complaints, or settlements
    """
    if not search_results:
        return None
    
    # Keywords related to redlining
    redlining_keywords = ['redlining', 'redline', 'discrimination', 'minority neighborhoods', 
                         'fair housing', 'HMDA violations']
    
    sentences = []
    for sentence in re.split(r'[.!?]\s+', search_results):
        sentence_lower = sentence.lower()
        if any(keyword.lower() in sentence_lower for keyword in redlining_keywords):
            if lender_name.lower() in sentence_lower:
                sentences.append(sentence.strip())
    
    if sentences:
        # Return summary of redlining issues
        return sentences[0][:200]  # Limit length
    
    return None


def parse_search_results(search_results: Dict) -> Dict[str, Optional[str]]:
    """
    Parse web search results to extract relevant background information
    
    Args:
        search_results: Dictionary with 'snippets' or 'content' from web search
        
    Returns:
        Dictionary with extracted information
    """
    background = {
        'headquarters': None,
        'history': None,
        'mergers': None,
        'fair_lending_violations': None,
        'redlining_complaints': None
    }
    
    # Combine all search result text
    combined_text = ""
    if 'snippets' in search_results:
        combined_text = ' '.join(search_results['snippets'])
    elif 'content' in search_results:
        combined_text = search_results['content']
    elif isinstance(search_results, str):
        combined_text = search_results
    
    if not combined_text:
        return background
    
    # Extract each type of information
    lender_name = search_results.get('lender_name', '')
    background['headquarters'] = extract_location_from_search(combined_text, lender_name)
    background['history'] = extract_history_from_search(combined_text, lender_name)
    background['mergers'] = extract_mergers_from_search(combined_text, lender_name)
    background['fair_lending_violations'] = extract_violations_from_search(combined_text, lender_name)
    background['redlining_complaints'] = extract_redlining_from_search(combined_text, lender_name)
    
    return background


