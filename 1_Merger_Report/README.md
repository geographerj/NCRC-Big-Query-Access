# 1 Merger Report

Merger Report - Compares two banks, sets mortgage goals, compares small business, analyzes branches

## Structure

```
1_Merger_Report/
├── data/          # Template data files only (reusable)
├── queries/       # Template queries only (reusable)
├── scripts/       # Template/utility scripts only (reusable)
├── utils/         # Utility functions only (reusable)
├── docs/          # Documentation
└── reports/       # All generated reports stored here
    ├── ReportName_YYYYMMDD/    # Each report has its own folder
    │   ├── [report files]
    │   ├── data/          # Actual data files for this specific report
    │   ├── queries/       # Actual queries used for this report
    │   ├── scripts/       # Scripts used to generate this report
    │   ├── supporting_files/
    │   └── data_exports/
    └── ...
```

Note: Top-level folders contain ONLY templates and reusable components.
Actual data, queries, and scripts for each specific report are stored
inside that report's folder under reports/.
