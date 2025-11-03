# Local Market Analysis - Quick Reference

## What is the Local Market Analysis?

The **Local Market Analysis** is a standard, repeatable analysis that compares two banks planning to merge and sets statewide performance goals for their post-merger performance. This analysis can be recreated at any time using the automated workflow scripts.

## Key Features

- **Fully Automated**: Run one script with a merger ticket to generate the complete analysis
- **Repeatable**: Can be recreated at any time with updated data
- **Standardized**: Uses consistent methodology and templates across all mergers
- **Dynamic**: Automatically extracts bank names, years, and filters from the merger ticket

## Quick Start

### Prerequisites

1. **Merger Research Ticket**: Excel file with bank information and filter settings
2. **Template Excel**: Local Market Analysis template (standardized format)
3. **BigQuery Access**: Credentials configured in `config/credentials/`

### Running the Analysis

```bash
python scripts/goal_setting_analysis_main.py "BankA+BankB merger research ticket.xlsx"
```

The script will:
1. Parse the merger ticket to extract bank information
2. Extract assessment areas from the ticket
3. Query BigQuery for HMDA, Small Business, and Branch data
4. Generate peer comparisons
5. Populate the Excel template
6. Save all files to a merger-specific folder

### Output Location

All files are saved to:
```
reports/Local Markets Analyses/YYMMDD_BankA_BankB_Merger/
├── YYMMDD_BankA_BankB_Local_Market_Analysis.xlsx  # Main report
├── supporting_files/                                # Ticket, parsed JSONs, PDFs
├── data_exports/                                    # SQL query exports
└── file_manifest.json                               # List of all files
```

## Main Script

**`scripts/goal_setting_analysis_main.py`**: Orchestrates the complete Local Market Analysis workflow

## Shared Resources

All reusable scripts and utilities are in:
```
reports/Local Markets Analyses/_shared/
├── queries/    # SQL query builders
└── utils/      # Utility functions (parsing, mapping, Excel generation)
```

## Documentation

- **Complete Guide**: `docs/guides/LOCAL_MARKET_GOAL_SETTING_ANALYSIS.md`
- **Requirements**: `docs/guides/GOAL_SETTING_COMPLETE_REQUIREMENTS.md`
- **Metrics**: `docs/guides/GOAL_SETTING_METRICS.md`
- **SQL Optimization**: `docs/guides/SQL_OPTIMIZATION_GUIDELINES.md`

## Notes

- The analysis uses generic "Bank A" and "Bank B" placeholders in the code template, but dynamically populates with actual bank names from the ticket during execution
- All formulas in the Excel template are preserved and wrapped with `IFERROR` to handle division by zero errors
- Peer selection uses the 50%-200% volume rule for HMDA and Small Business data
- Branch data compares the subject bank to ALL other lenders (no peer rule)

