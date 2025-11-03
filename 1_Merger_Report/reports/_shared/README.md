# Local Market Analysis - Shared Resources

This folder contains reusable scripts and utilities for the **Local Market Analysis** workflow. The Local Market Analysis is a standard, repeatable analysis that can be recreated at any time using these shared resources.

## Structure

```
_shared/
├── queries/          # SQL query builders
├── utils/           # Utility functions and parsers
└── README.md        # This file
```

## Files

### Queries (`queries/`)

- **`goal_setting_hmda_query_builder.py`**: Generates optimized HMDA SQL queries for subject banks. Handles string formatting, GEOID5 filtering, and metric calculations.

- **`goal_setting_branch_query_builder.py`**: Generates branch data queries comparing subject bank to **ALL other lenders** in the CBSA (no peer selection rule). Calculates LMICT and MMCT percentages for subject bank and market average. Uses `sod25` table for 2025 data.

### Utilities (`utils/`)

- **`extract_ticket_info.py`**: Parses the merger research ticket Excel file to extract:
  - Bank names (acquirer and target)
  - LEI and RSSD numbers
  - Year ranges (HMDA and Small Business)
  - Filter settings

- **`parse_assessment_areas_from_ticket.py`**: Extracts assessment area counties and CBSAs from the "Assessment Areas" sheet in the ticket Excel file.

- **`map_counties_to_geoid.py`**: Maps county names and state names to GEOID5 codes using the CBSA-to-County crosswalk. Handles counties that exist in multiple states and fuzzy matching for edge cases.

- **`setup_merger_folder.py`**: Creates the merger-specific folder structure with date prefix and bank names (format: `YYMMDD_BankA_BankB_Merger`).

## Usage

These utilities are imported by the main workflow script (`scripts/goal_setting_analysis_main.py`) using dynamic module loading. They can also be used standalone for testing and development.

**To run a Local Market Analysis:**
```bash
python scripts/goal_setting_analysis_main.py "BankA+BankB merger research ticket.xlsx"
```

The analysis can be recreated at any time by running this command with the appropriate ticket file.

## Dependencies

- `openpyxl`: For reading Excel files
- `pandas`: For data manipulation
- `pathlib`: For robust file path handling (especially with apostrophes in paths)

## Documentation

- **`DEFAULT_FILTERS.md`**: Documents the standard default HMDA filters used in queries and how they are extracted from the ticket Excel file.

## Notes

- All file paths should use `pathlib.Path` to handle apostrophes in OneDrive paths
- Years, LEI, and RSSD are treated as strings in SQL queries
- Assessment area parsing prioritizes the Excel ticket over PDFs when available
- Standard filters are hard-coded in query builders; loan purpose can be overridden per sheet type
