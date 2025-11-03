# Loan Filters Reference

## Standard HMDA Filters

All reports use the following standard filters for HMDA data analysis:

### Required Filters

1. **Loan Purpose**: `loan_purpose = '1'`
   - **Meaning**: Home purchase loans only
   - **Excludes**: Refinances, home improvement loans

2. **Action Taken**: `action_taken = '1'`
   - **Meaning**: Originations only
   - **Excludes**: Denied applications, withdrawn applications, approved but not accepted

3. **Occupancy Type**: `occupancy_type = '1'`
   - **Meaning**: Owner-occupied properties
   - **Excludes**: Investment properties, second homes

4. **Reverse Mortgage**: `reverse_mortgage != '1'`
   - **Meaning**: Excludes reverse mortgages
   - **Includes**: Traditional forward mortgages only

5. **Construction Method**: `construction_method = '1'`
   - **Meaning**: Site-built homes only
   - **Excludes**: Manufactured homes, mobile homes

6. **Property Units**: `total_units IN ('1', '2', '3', '4')`
   - **Meaning**: 1-4 family properties
   - **Excludes**: 5+ unit properties, commercial properties

### Loan Types Included

**All loan types are included** within these filters:
- Conventional loans
- FHA loans
- VA loans
- USDA loans
- Other government-backed loans

**Note**: The filters do NOT exclude by loan type. Any home purchase loan meeting the above criteria is included regardless of loan type.

## Methodology Documentation

These filters **must be documented** in the Methodology section of every report:

```
Loan Filters:
This analysis applies standard HMDA filters to home purchase loan originations:

- Loan Purpose: Home purchase loans only (loan_purpose = '1')
- Action Taken: Originations only (action_taken = '1')
- Occupancy Type: Owner-occupied properties (occupancy_type = '1')
- Reverse Mortgages: Excluded (reverse_mortgage != '1')
- Construction Method: Site-built only (construction_method = '1')
- Property Units: 1-4 family units (total_units IN ('1', '2', '3', '4'))

All loan types (conventional, FHA, VA, USDA) are included within these filters.
```

## Implementation

### In Query Builders

Filters are applied in the SQL query:

```sql
WHERE h.action_taken = '1'  -- Originations only
  AND h.loan_purpose = '1'  -- Home purchase
  AND h.occupancy_type = '1'  -- Owner-occupied
  AND h.reverse_mortgage != '1'  -- Not reverse mortgage
  AND h.construction_method = '1'  -- Site-built
  AND h.total_units IN ('1', '2', '3', '4')  -- 1-4 units
```

### In Report Methodology

Filters are documented in the `generate_methodology_text()` function in each report script.

## Why These Filters?

### Standard Industry Practice

These filters represent standard fair lending analysis practices:
- Focus on **home purchase** (not refinances) shows access to credit for new homeownership
- **Originations only** eliminates incomplete transactions
- **Owner-occupied** focuses on primary residences (not investment properties)
- **Site-built** excludes manufactured homes (different market segment)
- **1-4 units** focuses on residential properties (not commercial)

### Comparable to Industry Standards

These filters align with:
- FFIEC HMDA analysis standards
- CFPB fair lending analysis practices
- Industry peer comparison methodologies

## Consistency Across Reports

**All reports must use these exact same filters** to ensure:
- **Comparability** across different markets
- **Reproducibility** of findings
- **Industry alignment** with standard practices

## Modifications

If a report requires different filters, they must be:
1. **Explicitly documented** in the methodology section
2. **Justified** with a clear explanation
3. **Noted as non-standard** to maintain clarity

---

*Last Updated: 2025-01-XX*

