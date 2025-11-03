# Merger Analysis Folder Structure

## Output Folder Organization

Each merger analysis is saved to its own dated folder with a descriptive name containing both bank names.

## Folder Structure

```
reports/
└── Local Markets Analyses/
    └── YYMMDD_BankA_BankB_Merger/
        ├── YYMMDD_BankA_BankB_GoalSetting_Analysis.xlsx  # Main output file
        └── supporting_files/
            ├── ticket_info_extracted.json                  # Parsed ticket info
            ├── assessment_areas_parsed.csv                 # Parsed assessment areas
            └── [other supporting files]
        └── data_exports/
            └── [SQL query exports if needed]
```

## Folder Naming Convention

- **Format**: `YYMMDD_BankA_BankB_Merger`
- **Date**: Current date in YYMMDD format (e.g., `251101` for November 1, 2025)
- **Bank Names**: Sanitized bank names (special characters removed, spaces replaced with underscores)
- **Example**: `251101_PNC_Bank_FirstBank_Merger`

## Bank Name Sanitization

Bank names are cleaned for use in folder names:
- Special characters removed (e.g., `&`, `,`, `.`)
- Spaces replaced with underscores
- Multiple underscores collapsed to single underscore
- Result is trimmed

## Example

For PNC Bank + FirstBank merger on November 1, 2025:
- Folder: `reports/Local Markets Analyses/251101_PNC_Bank_FirstBank_Merger/`
- Output file: `251101_PNC_Bank_FirstBank_GoalSetting_Analysis.xlsx`

## Supporting Files

The `supporting_files/` subdirectory contains:
- Parsed ticket information (JSON)
- Parsed assessment areas (CSV/Excel)
- Any other intermediate files used in the analysis

The `data_exports/` subdirectory can contain:
- Raw SQL query exports (if debugging needed)
- Intermediate data files


