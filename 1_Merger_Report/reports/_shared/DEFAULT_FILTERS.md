# Default HMDA Filters for Goal-Setting Analysis

This document outlines the standard default filters used in the Goal-Setting Analysis. These filters can be specified in the "LMA Ticket Filters" sheet of the merger research ticket Excel file.

## Standard Default Filters

These are the **standard filters** applied to all HMDA queries unless otherwise specified in the ticket:

1. **Occupancy Type**: `occupancy_type = '1'` (Owner-occupied)
2. **Action Taken**: `action_taken = '1'` (Originations only)
3. **Construction Method**: `construction_method = '1'` (Site-built)
4. **Total Units**: `total_units IN ('1', '2', '3', '4')` (1-4 unit properties)
5. **Reverse Mortgage**: `reverse_mortgage != '1'` (Exclude reverse mortgages)

## Loan Purpose Filters

The loan purpose filter varies depending on the sheet:

### Mortgage Data Sheets (Individual Bank Sheets)
- **Default**: `loan_purpose = '1'` (Home Purchase only)
- **Rationale**: Mortgage Data sheets typically show one loan type per sheet
- **Can be overridden**: If the ticket specifies a different loan purpose, use that

### Mortgage Goals Sheet
- **Structure**: Separate columns for each loan type group (NOT combined into one column)
- **Loan Type Groups**:
  1. **Home Purchase**: `loan_purpose = '1'` (one column)
  2. **Refinance**: `loan_purpose IN ('31', '32')` (one column for both refinance types)
     - `'31'` = Cash-out Refinance
     - `'32'` = No Cash-out Refinance
  3. **Home Equity**: `loan_purpose IN ('2', '4', '5')` (one column for home improvement, home equity, and other)
     - `'2'` = Home Improvement
     - `'4'` = Home Equity
     - `'5'` = Other
- **Rationale**: Goals sheet shows each loan type group in its own column for detailed statewide goal-setting
- **Note**: Data is NOT aggregated across loan types - each group gets separate columns that can be combined later by Excel formulas

## Filter Extraction from Ticket

The `extract_ticket_info.py` script parses the "LMA Ticket Filters" sheet and extracts:

```python
{
    'filters': {
        'hmda_years': {
            'default': '2020 - 2024',
            'range': [2020, 2021, 2022, 2023, 2024]
        },
        'sb_years': {
            'default': '2020 - 2023',
            'range': [2020, 2021, 2022, 2023]
        },
        'occupancy': {
            'default': 'Owner-occupied (1)'
        },
        'action_taken': {
            'default': 'Originations (1)'
        },
        'units': {
            'default': '1-4 units'
        },
        'construction_method': {
            'default': 'Site-built (1)'
        },
        'loan_purpose': {
            'default': 'Home Purchase (1)'  # For Mortgage Data sheets
        }
    }
}
```

## Using Filters in Query Builders

When building queries, apply filters as follows:

1. **Always apply standard filters** (occupancy, action_taken, construction, units, reverse_mortgage)
2. **Apply loan purpose filter based on sheet type**:
   - Mortgage Data sheets: Use single loan purpose (default '1' for home purchase)
   - Goals sheet: Use all loan types ('1', '2', '4', '31', '32')
3. **Apply year filters** from ticket (separate for HMDA vs Small Business)
4. **Apply assessment area county filter** (GEOID5 codes)

## Example Usage

```python
from reports.Local Markets Analyses._shared.queries.goal_setting_hmda_query_builder import build_hmda_query

# For Mortgage Data sheet (home purchase only)
query_mortgage_data = build_hmda_query(
    subject_lei='BANK_LEI',
    assessment_area_geoids=['12345', '67890'],
    years=['2020', '2021', '2022', '2023', '2024'],
    loan_purpose='1'  # Home purchase only
)

# For Goals sheet - separate queries for each loan type group (separate columns)
# Home Purchase column
query_goals_home_purchase = build_hmda_query(
    subject_lei='BANK_LEI',
    assessment_area_geoids=['12345', '67890'],
    years=['2020', '2021', '2022', '2023', '2024'],
    loan_purpose_group='home_purchase'
)

# Refinance column
query_goals_refinance = build_hmda_query(
    subject_lei='BANK_LEI',
    assessment_area_geoids=['12345', '67890'],
    years=['2020', '2021', '2022', '2023', '2024'],
    loan_purpose_group='refinance'
)

# Home Equity column
query_goals_home_equity = build_hmda_query(
    subject_lei='BANK_LEI',
    assessment_area_geoids=['12345', '67890'],
    years=['2020', '2021', '2022', '2023', '2024'],
    loan_purpose_group='home_equity'
)
```

## Notes

- All standard filters are **hard-coded** in the query builder
- Loan purpose can be **overridden** by passing `loan_purpose` parameter
- Years are **extracted from ticket** and can differ for HMDA vs Small Business
- Assessment area counties are **required** and must be passed as GEOID5 codes

