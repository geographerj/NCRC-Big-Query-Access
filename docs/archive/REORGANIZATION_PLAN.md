# Project Reorganization Plan

## Overview
This document outlines the proposed reorganization of the DREAM Analysis project folder to improve maintainability and scalability for future reports.

## Proposed Structure

```
DREAM Analysis/
├── README.md                          # Main project documentation
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore file
│
├── config/                            # Configuration files
│   └── credentials/                   # Credentials (keep out of git!)
│       └── hdma1-242116-74024e2eb88f.json
│
├── scripts/                           # Python report generators
│   ├── __init__.py
│   ├── fifth_third_cba_report.py
│   ├── generate_fifth_third_report.py
│   ├── ncrc_worst_lenders_analysis_v4.py
│   ├── cba_banks_analysis_v4_FINAL.py
│   ├── find_top_cbsas.py
│   └── check_excel_sheets.py
│
├── queries/                           # SQL query files
│   ├── fifth_third/                   # Fifth Third specific queries
│   │   ├── FIFTH_THIRD_COMBINED_FULL_QUERY.sql
│   │   ├── FIFTH_THIRD_DEMOGRAPHICS_QUERY.sql
│   │   ├── FIFTH_THIRD_REDLINING_FULL_QUERY.sql
│   │   ├── fifth_third_top_cbsas.sql
│   │   └── fifth_third_tract_demographics_query.sql
│   └── README.md                      # Query documentation
│
├── data/                              # Data files
│   ├── raw/                           # BigQuery exports (CSV files)
│   │   └── (all bquxjob_*.csv files)
│   └── reference/                     # Reference/mapping data
│       ├── CBSA_to_County_Mapping.csv
│       └── Lenders_and_LEI_Numbers.csv
│
├── reports/                           # Generated Excel reports
│   ├── fifth_third/                   # Fifth Third reports
│   │   └── Fifth_Third_CBA_Report.xlsx
│   ├── cba_banks/                     # CBA Banks reports
│   │   └── CBA_Banks_Analysis.xlsx
│   ├── worst_lenders/                 # Worst Lenders reports
│   │   └── NCRC_Worst_Lenders_Analysis.xlsx
│   └── archive/                       # Old reports (optional)
│
├── batch/                             # Batch/command scripts
│   ├── install_packages.bat
│   ├── run_cmd.bat
│   ├── run_find_cbsas.bat
│   └── run_excel_generator.bat
│
├── tests/                             # Test scripts
│   ├── test_connection.py
│   └── test_simple.py
│
├── docs/                              # All documentation
│   ├── guides/                        # How-to guides
│   │   ├── QUICK_START_FIFTH_THIRD.md
│   │   ├── RUN_FIFTH_THIRD_REPORT.md
│   │   ├── HOW_TO_ASK_FOR_HMDA_QUERIES.md
│   │   └── GITHUB_AUTH_GUIDE.md
│   ├── technical/                     # Technical documentation
│   │   ├── TRACT_DEMOGRAPHIC_METRICS_REQUIREMENTS.md
│   │   ├── FINAL_IMPLEMENTATION_SUMMARY.md
│   │   └── IMPLEMENTATION_SUMMARY.md
│   └── archive/                       # Old/temporary docs
│       ├── DO_THIS_NOW.md
│       ├── RUN_THIS.txt
│       ├── RUN_THIS_NOW.txt
│       ├── STEP_BY_STEP.txt
│       └── (other temporary docs)
│
├── Lending and Branch Analysis/       # Existing module (keep as is)
│   └── (current structure)
│
└── archive/                           # Old/unused items
    └── NCRC-Big-Query-Access/         # If this is duplicate
```

## Benefits

1. **Clear Separation of Concerns**
   - Scripts separate from data
   - Reports organized by project/bank
   - Documentation centralized

2. **Scalability**
   - Easy to add new reports (create new folder in reports/)
   - Easy to add new queries (organize by project in queries/)
   - Clear structure for new team members

3. **Security**
   - Credentials in dedicated folder (can be gitignored)
   - Config files separated

4. **Maintainability**
   - Related files grouped together
   - Archive folders for old/temporary files
   - Clear naming conventions

## Migration Steps

1. Create new folder structure
2. Move files according to plan
3. Update any hardcoded paths in scripts
4. Test scripts still work
5. Update documentation
6. Commit changes

## Notes

- The `Lending and Branch Analysis/` folder structure is preserved as it appears to be a working module
- The `NCRC-Big-Query-Access/` folder appears to be a duplicate - consider archiving
- All batch files consolidated in `batch/` folder
- Reports organized by project type for easy finding
