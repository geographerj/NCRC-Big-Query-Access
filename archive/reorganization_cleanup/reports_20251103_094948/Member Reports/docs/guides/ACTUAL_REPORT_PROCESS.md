# Actual Report Production Process

**This document describes the actual workflow for HMDA Fair Lending Analysis reports.**

## Data Source and Scope

- **Source**: HMDA data from BigQuery
- **Years**: Typically 2018-2024
- **Loan Filters** (Standard HMDA Filters):
  - **Loan Purpose**: Home purchase loans only (loan_purpose = '1')
  - **Action Taken**: Originations only (action_taken = '1')
  - **Occupancy Type**: Owner-occupied properties (occupancy_type = '1')
  - **Reverse Mortgages**: Excluded (reverse_mortgage != '1')
  - **Construction Method**: Site-built only (construction_method = '1')
  - **Property Units**: 1-4 family units (total_units IN ('1', '2', '3', '4'))
  - **Loan Types**: All loan types included (conventional, FHA, VA, USDA) within these filters

**Note**: These filters are documented in the Methodology section of each report.

## Geographic Definition

- **Geography Type**: Core-Based Statistical Areas (CBSAs)
- **For each metro**: Identify constituent counties and census tracts
- **Tract Classifications**:
  - **LMICT**: Census tracts where median family income ≤80% of area median
  - **MMCT**: Census tracts where non-white population exceeds 50%
- **Note**: Track census boundary changes between 2010 and 2020 geography

## Lender Selection

- **Target Lender**: Identified by Legal Entity Identifier (LEI)
- **Include**: All lending activity for that institution (all subsidiaries and divisions)
- **Comparison Group**: "All other lenders" in same geography (NOT peer group)

## Core Metrics Analysis

**Six standard fair lending metrics** calculated for both target lender and comparison group:

1. **Black homebuyer share**: Black-headed households as percentage of total originations
2. **Latino homebuyer share**: Latino-headed households as percentage of total originations
3. **Asian homebuyer share**: Asian-headed households as percentage of total originations
4. **LMICT lending share**: Originations in low-to-moderate income tracts as percentage of total
5. **MMCT lending share**: Originations in majority-minority tracts as percentage of total

**Note**: For these reports, look at lending by race divided by the number of loans WITH demographic data (exclude missing data from denominator).

## Gap Calculation

For each metric, calculate performance gap:
- **Gap = Target Lender Performance - All Other Lenders Performance**
- Express as **percentage points with one decimal place**
- **Negative values** = underperformance
- **Positive values** = overperformance

## Missing Data Handling

- Track and report:
  - Percentage of applications missing race/ethnicity data
  - Whether missing data rates differ between lender and market
  - Impact on absolute loan volumes
  - Note that geographic concentration patterns remain stable

## Report Structure

Required sections:

1. **Introduction**: Define the geography, years, and sources of the data
2. **Key Findings**: 
   - Scale of problems
   - Geographic patterns
   - Metric-specific performance
   - Temporal trends
3. **Overall Market Patterns**: 
   - Lending that has occurred
   - Share of loans to each metric asked for in the report
4. **Top Lender Analysis**: 
   - Look at the ten lenders with the most originations in the most recent year
   - Analyze their performance over each year
   - Similar to the market analysis for comparison
5. **Methodology**: 
   - Data source and years
   - Scope criteria
   - Statistical approach
   - Metrics analyzed
   - Gap calculation method
6. **How to Read the Data**: 
   - Table column explanations
   - Asterisk meaning
   - Value interpretation
   - Pattern definitions
7. **Metro-Specific Tables**: 
   - One table per metro
   - Show all six metrics, gaps, and significance markers

## Writing Standards

- **Tone**: Direct, factual
- **Acronyms**: Define on first use
- **Formatting**: 
  - Percentages: `##.#%`
  - Integers: `#,###`
- **Data Citations**: Only cite specific data for key discussion points (largest gaps, significant changes)
- **Tables**: Let tables present detailed numbers
- **Language**: Use "demonstrates" or "shows" rather than "proves"
- **Frame**: Present disparities neutrally without attributing intent
- **Recommendations**: Frame as operational improvements
- **Traceability**: Every claim must trace to specific data

## Output Format

- **Primary**: Markdown document with clear section headers
- **Tables**: Include data tables in consistent format
- **Formatting**: Bold key terms in findings
- **Structure**: Use parallel structure in lists
- **Consistency**: Maintain numerical format consistency throughout

## Key Differences from Initial Design

1. **Comparison Group**: "All other lenders" (not peer group with volume matching)
2. **Metrics**: Specific 6 metrics (not all demographics)
3. **Denominator**: Loans WITH demographic data (exclude missing)
4. **Top Lenders**: Top 10 lenders by volume in most recent year
5. **Output**: Markdown format (in addition to PDF/Excel)
6. **Sections**: Specific structure matching actual reports

