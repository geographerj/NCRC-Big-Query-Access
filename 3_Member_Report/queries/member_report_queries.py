"""
Query builders for NCRC Member Reports

Builds SQL queries based on configuration parameters for:
- Subject lender HMDA data
- Peer lender comparisons
- Geographic filters
- Metric calculations
"""

from typing import Dict, List, Optional, Any


def build_geographic_filter(config: Dict[str, Any]) -> str:
    """
    Build geographic filter clause based on configuration
    
    Args:
        config: Configuration dictionary with geography section
    
    Returns:
        SQL WHERE clause fragment for geography filtering
    """
    geo = config.get('geography', {})
    geo_type = geo.get('type', 'cbsa')
    
    conditions = []
    
    if geo_type == 'cbsa':
        cbsa_codes = geo.get('cbsa_codes', [])
        cbsa_names = geo.get('cbsa_names', [])
        
        if cbsa_codes:
            codes_list = ', '.join([f"'{code}'" for code in cbsa_codes])
            conditions.append(f"c.cbsa_code IN ({codes_list})")
        
        if cbsa_names:
            names_list = ', '.join([f"'{name}'" for name in cbsa_names])
            conditions.append(f"c.cbsa_name IN ({names_list})")
    
    elif geo_type == 'county':
        county_codes = geo.get('county_codes', [])
        if county_codes:
            codes_list = ', '.join([f"'{code}'" for code in county_codes])
            conditions.append(f"CAST(h.county_code AS STRING) IN ({codes_list})")
    
    elif geo_type == 'custom':
        custom_filter = geo.get('custom_filter')
        if custom_filter:
            conditions.append(custom_filter)
    
    if not conditions:
        return ""  # No geographic filter
    
    return " AND " + " AND ".join(conditions)


def build_member_report_query(
    config: Dict[str, Any],
    include_peer: bool = False
) -> str:
    """
    Build main HMDA query for member report
    
    Args:
        config: Full configuration dictionary
        include_peer: Whether to include peer lenders (False = subject only)
    
    Returns:
        SQL query string
    """
    metadata = config.get('report_metadata', {})
    subject = config.get('subject_lender', {})
    filters = config.get('loan_filters', {})
    metrics = config.get('metrics', {})
    geo_filter = build_geographic_filter(config)
    
    # Extract configuration
    years = metadata.get('years', [2018, 2023, 2024])
    years_list = ', '.join([f"'{str(y)}'" for y in years])
    
    # Subject lender identifier
    subject_lei = subject.get('lei')
    subject_rssd = subject.get('rssd')
    subject_name = subject.get('name')
    
    if not (subject_lei or subject_rssd or subject_name):
        raise ValueError("Must specify subject lender LEI, RSSD, or name")
    
    # Build LEI filter (would need crosswalk for RSSD/name)
    if subject_lei:
        lei_filter = f"h.lei = '{subject_lei}'"
    else:
        # Would need to join with lender crosswalk table
        raise NotImplementedError("RSSD/name lookup requires crosswalk join")
    
    if include_peer:
        lei_filter = ""  # Include all lenders for peer analysis
    else:
        lei_filter = f" AND h.lei = '{subject_lei}'"
    
    # Loan filters
    standard_filters = []
    if filters.get('standard_hmda_filters', True):
        if filters.get('action_taken'):
            standard_filters.append(f"h.action_taken = '{filters['action_taken']}'")
        if filters.get('occupancy_type'):
            standard_filters.append(f"h.occupancy_type = '{filters['occupancy_type']}'")
        if filters.get('reverse_mortgage') == 'exclude':
            standard_filters.append("h.reverse_mortgage != '1'")
        if filters.get('construction_method'):
            standard_filters.append(f"h.construction_method = '{filters['construction_method']}'")
        if filters.get('total_units'):
            units_list = ', '.join([f"'{u}'" for u in filters['total_units']])
            standard_filters.append(f"h.total_units IN ({units_list})")
        if filters.get('loan_purpose'):
            standard_filters.append(f"h.loan_purpose = '{filters['loan_purpose']}'")
    
    filter_clause = " AND " + " AND ".join(standard_filters) if standard_filters else ""
    
    # Metric calculations
    metric_calculations = []
    
    # Borrower demographics
    if metrics.get('borrower_demographics', {}).get('enabled'):
        metric_calculations.extend([
            # Hispanic
            """CASE 
                WHEN h.applicant_ethnicity_1 IN ('1','11','12','13','14')
                    OR h.applicant_ethnicity_2 IN ('1','11','12','13','14')
                    OR h.applicant_ethnicity_3 IN ('1','11','12','13','14')
                    OR h.applicant_ethnicity_4 IN ('1','11','12','13','14')
                    OR h.applicant_ethnicity_5 IN ('1','11','12','13','14')
                THEN 1 ELSE 0 
            END as is_hispanic""",
            # Black
            """CASE 
                WHEN h.applicant_ethnicity_1 NOT IN ('1','11','12','13','14')
                    AND h.applicant_ethnicity_2 NOT IN ('1','11','12','13','14')
                    AND h.applicant_ethnicity_3 NOT IN ('1','11','12','13','14')
                    AND h.applicant_ethnicity_4 NOT IN ('1','11','12','13','14')
                    AND h.applicant_ethnicity_5 NOT IN ('1','11','12','13','14')
                    AND (h.applicant_race_1 = '3' OR h.applicant_race_2 = '3' 
                         OR h.applicant_race_3 = '3' OR h.applicant_race_4 = '3' 
                         OR h.applicant_race_5 = '3')
                THEN 1 ELSE 0 
            END as is_black""",
            # Asian
            """CASE 
                WHEN h.applicant_ethnicity_1 NOT IN ('1','11','12','13','14')
                    AND h.applicant_ethnicity_2 NOT IN ('1','11','12','13','14')
                    AND h.applicant_ethnicity_3 NOT IN ('1','11','12','13','14')
                    AND h.applicant_ethnicity_4 NOT IN ('1','11','12','13','14')
                    AND h.applicant_ethnicity_5 NOT IN ('1','11','12','13','14')
                    AND (h.applicant_race_1 IN ('2','21','22','23','24','25','26','27')
                         OR h.applicant_race_2 IN ('2','21','22','23','24','25','26','27')
                         OR h.applicant_race_3 IN ('2','21','22','23','24','25','26','27')
                         OR h.applicant_race_4 IN ('2','21','22','23','24','25','26','27')
                         OR h.applicant_race_5 IN ('2','21','22','23','24','25','26','27'))
                THEN 1 ELSE 0 
            END as is_asian""",
            # Native American
            """CASE 
                WHEN h.applicant_ethnicity_1 NOT IN ('1','11','12','13','14')
                    AND h.applicant_ethnicity_2 NOT IN ('1','11','12','13','14')
                    AND h.applicant_ethnicity_3 NOT IN ('1','11','12','13','14')
                    AND h.applicant_ethnicity_4 NOT IN ('1','11','12','13','14')
                    AND h.applicant_ethnicity_5 NOT IN ('1','11','12','13','14')
                    AND (h.applicant_race_1 = '1' OR h.applicant_race_2 = '1' 
                         OR h.applicant_race_3 = '1' OR h.applicant_race_4 = '1' 
                         OR h.applicant_race_5 = '1')
                THEN 1 ELSE 0 
            END as is_native_american""",
            # HoPI
            """CASE 
                WHEN h.applicant_ethnicity_1 NOT IN ('1','11','12','13','14')
                    AND h.applicant_ethnicity_2 NOT IN ('1','11','12','13','14')
                    AND h.applicant_ethnicity_3 NOT IN ('1','11','12','13','14')
                    AND h.applicant_ethnicity_4 NOT IN ('1','11','12','13','14')
                    AND h.applicant_ethnicity_5 NOT IN ('1','11','12','13','14')
                    AND (h.applicant_race_1 IN ('4','41','42','43','44')
                         OR h.applicant_race_2 IN ('4','41','42','43','44')
                         OR h.applicant_race_3 IN ('4','41','42','43','44')
                         OR h.applicant_race_4 IN ('4','41','42','43','44')
                         OR h.applicant_race_5 IN ('4','41','42','43','44'))
                THEN 1 ELSE 0 
            END as is_hopi"""
        ])
    
    # Income metrics
    if metrics.get('income_metrics', {}).get('enabled'):
        metric_calculations.extend([
            # LMICT
            """CASE 
                WHEN h.tract_to_msa_income_percentage IS NOT NULL
                    AND CAST(h.tract_to_msa_income_percentage AS FLOAT64) <= 80 
                THEN 1 ELSE 0 
            END as is_lmict""",
            # LMIB
            """CASE 
                WHEN h.income IS NOT NULL
                  AND h.ffiec_msa_md_median_family_income IS NOT NULL
                  AND h.ffiec_msa_md_median_family_income > 0
                  AND (CAST(h.income AS FLOAT64) * 1000.0) / 
                      CAST(h.ffiec_msa_md_median_family_income AS FLOAT64) * 100.0 <= 80.0
                THEN 1 
                ELSE 0 
            END as is_lmib"""
        ])
    
    # Redlining metrics (would need geo table join)
    if metrics.get('redlining', {}).get('enabled'):
        # Note: Redlining metrics require joining with geo table
        # This is a simplified version
        metric_calculations.append(
            """CASE 
                WHEN h.tract_minority_population_percent IS NOT NULL
                    AND CAST(h.tract_minority_population_percent AS FLOAT64) > 50 
                THEN 1 ELSE 0 
            END as is_mmct_50"""
        )
    
    metric_select = ",\n        ".join(metric_calculations) if metric_calculations else ""
    metric_comma = ",\n        " if metric_select else ""
    
    # Build query
    query = f"""
-- Member Report HMDA Query
-- Generated from configuration
-- Years: {years_list}
-- Subject: {subject.get('name', subject_lei or 'Unknown')}

WITH cbsa_crosswalk AS (
    SELECT DISTINCT
        CAST(county_code AS STRING) as county_code,
        cbsa_code,
        cbsa_name
    FROM `hdma1-242116.geo.cbsa_to_county`
),

filtered_hmda AS (
    SELECT 
        CAST(h.activity_year AS STRING) as activity_year,
        c.cbsa_code,
        c.cbsa_name,
        CAST(h.county_code AS STRING) as county_code,
        h.census_tract,
        h.lei,
        h.loan_amount,
        {metric_select}{metric_comma}
        h.tract_minority_population_percent
    FROM `hdma1-242116.hmda.hmda` h
    LEFT JOIN cbsa_crosswalk c
        ON CAST(h.county_code AS STRING) = c.county_code
    WHERE CAST(h.activity_year AS STRING) IN ({years_list})
        {lei_filter}
        {geo_filter}
        {filter_clause}
)

SELECT * FROM filtered_hmda
ORDER BY activity_year, cbsa_code, census_tract
"""
    
    return query


def build_peer_comparison_query(config: Dict[str, Any]) -> str:
    """
    Build peer comparison query
    
    Args:
        config: Full configuration dictionary
    
    Returns:
        SQL query string for peer analysis
    """
    # Use the same base query but include all lenders and add peer identification
    base_query = build_member_report_query(config, include_peer=True)
    
    # Add peer identification logic
    peer_config = config.get('peer_definition', {})
    volume_range = peer_config.get('volume_range', {'min_multiplier': 0.5, 'max_multiplier': 2.0})
    
    # This would be enhanced to add peer grouping
    # For now, return the base query with a note
    return f"""
-- Peer Comparison Query
-- Note: Peer identification should be done in post-processing
-- based on origination volume within each CBSA-year

{base_query}
"""

