# Local Market Analysis Guide

## Overview

The **Local Market Analysis** is a standard, repeatable analysis that compares two banks planning to merge and sets statewide performance goals for their post-merger performance. This analysis can be recreated at any time using the same methodology and scripts. It is used to understand how the banks perform relative to each other and to their peers, and to establish benchmarks for improvement.

**Key Point**: This analysis is fully automated and can be regenerated whenever needed by running the main workflow script with the appropriate merger research ticket.

## Key Components

### 1. Input Data Sources

#### A. Merger Research Ticket Excel
- **File Format**: Excel file with bank information and filter settings
- **Sheets**:
  - "Bank Details": Contains acquirer and target bank information (names, LEI, RSSD, etc.)
  - "LMA Ticket Filters": Contains filter settings for years, HMDA filters, occupancy, action taken, units, construction method, loan purpose
- **Parser**: `scripts/parse_ticket_excel.py`

#### B. Assessment Area Documents
- **Purpose**: Define which specific counties are included in each CBSA/MSA assessment area
- **Key Point**: Assessment areas are CBSA/MSA-based but **do NOT always include all counties** in the CBSA
- **Format**: PDF, CSV, or Excel
- **Parser**: `scripts/parse_assessment_areas.py`
- **Manual Template**: `scripts/create_assessment_area_template.py` (if needed for manual entry)

#### C. Local Market Analysis Template Excel
- **Purpose**: Final report template with formulas that must be preserved
- **Structure**: Multiple sheets, each with specific data requirements
- **Critical**: Formulas must remain intact when populating with SQL data
- **Note**: The template is standardized and can be reused for any merger analysis

### 2. Data Extraction (SQL Queries)

#### HMDA Data Requirements
- **Table**: `hdma1-242116.hmda.hmda`
- **Filters** (from ticket):
  - Years: Specified in ticket
  - Occupancy: Owner-occupied (`occupancy_type = '1'`)
  - Action Taken: Originations (`action_taken = '1'`)
  - Units: 1-4 unit properties
  - Construction: Site-built (`construction_method = '1'`)
  - Loan Purpose: Specified in ticket
  - Exclude reverse mortgages

#### Geographic Filtering
- Filter to **specific counties** within each assessment area CBSA/MSA
- Counties identified from assessment area documents
- Use county GEOIDs for precise matching

#### Peer Comparison
- Identify peer banks operating in the same assessment areas
- Compare performance metrics:
  - Lending to minority communities
  - Lending in majority-minority tracts
  - Origination rates by demographics
  - Geographic distribution of lending

### 3. Analysis Components

#### A. Bank Comparison
- Compare acquirer vs. target bank performance in overlapping markets
- Identify differences in:
  - Lending patterns
  - Geographic focus
  - Demographic outreach
  - Market share

#### B. Peer Benchmarking
- Compare combined entity performance to peer banks
- Calculate performance gaps
- Identify improvement opportunities

#### C. Goal Setting (Post-Merger Performance Targets)
- Set statewide goals for post-merger performance
- Based on:
  - Combined entity current performance
  - Peer bank benchmarks
  - Assessment area needs
  - Historical trends

### 4. Excel Template Population

#### Requirements
- **Preserve all formulas**: Use `openpyxl` with `data_only=False`
- **Identify data insertion points**: Map SQL output to specific cells/ranges
- **Maintain structure**: Keep sheet layouts, formatting, and calculations intact
- **Handle dependencies**: Ensure formula references remain valid after data insertion

#### Approach
1. Load template with formulas intact
2. Identify which cells/ranges need data (not formulas)
3. Insert SQL query results into appropriate locations
4. Verify formulas still work correctly
5. Save as new file (preserve original template)

## Workflow

```
1. Parse Merger Ticket
   └─> Extract bank info (LEI, RSSD, names)
   └─> Extract filter settings

2. Parse Assessment Areas
   └─> Extract specific counties per CBSA/MSA
   └─> Generate county GEOID list

3. Query HMDA Data
   └─> Query acquirer bank data (filtered by counties)
   └─> Query target bank data (filtered by counties)
   └─> Query peer bank data (for comparison)

4. Populate Template
   └─> Load template (preserve formulas)
   └─> Insert data into designated cells/ranges
   └─> Verify formulas
   └─> Save populated report

5. Review & Adjust
   └─> Open populated report in Excel
   └─> Review calculations and results
   └─> Adjust goals if needed
```

## Scripts

### Standard Scripts
- `scripts/goal_setting_analysis_main.py`: Main script that orchestrates the complete Local Market Analysis workflow. This script can be run at any time to regenerate the analysis for any merger.
- `reports/Local Markets Analyses/_shared/queries/`: SQL query builders that generate optimized queries for HMDA, Small Business, and Branch data
- `reports/Local Markets Analyses/_shared/utils/`: Utility functions for parsing tickets, mapping counties, and generating Excel reports

### Helper Scripts (Already Created)
- `scripts/parse_ticket_excel.py`: Parse merger ticket Excel
- `scripts/parse_assessment_areas.py`: Parse assessment area documents
- `scripts/create_assessment_area_template.py`: Create manual input template
- `scripts/inspect_goal_setting_template.py`: Inspect template structure (WIP)

## Notes

- **Assessment Areas**: Always check which specific counties are included - never assume all counties in a CBSA are included
- **Formulas**: The template Excel contains critical formulas that drive the analysis - these must never be overwritten
- **County Matching**: Use GEOIDs for precise county matching when filtering HMDA data
- **Peer Selection**: Peer banks should be similar in size and geographic focus to the merging banks

## Related Documentation

- `HOW_TO_ASK_FOR_HMDA_QUERIES.md`: Guide for requesting HMDA queries
- `FIX_APOSTROPHE_PATH_ISSUE.md`: Handling paths with apostrophes
- `MERGER_ANALYSIS_GUIDE.md`: General merger analysis workflow


