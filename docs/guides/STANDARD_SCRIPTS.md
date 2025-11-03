# Standard Scripts Reference

This guide lists the **standard, reusable scripts** that are commonly used across multiple analyses. For project-specific scripts, see the project guides.

## 🎯 Standard Analysis Scripts

These scripts are production-ready and used regularly:

### Core Analysis Reports

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| **`01_worst_lenders_analysis_v2.py`** | Worst lenders redlining analysis (post-2022 boundaries) | CSV from `worst_lenders_redlining_query_v2.sql` | Excel in `reports/` |
| **`02_fifth_third_cba_report.py`** | Fifth Third Bank CBA enforcement report | CSV from Fifth Third queries | Excel in `reports/fifth_third/` |
| **`03_generate_merger_analysis.py`** | Merger impact analysis | CSV from merger queries | Excel in `reports/` |
| **`04_generate_weekly_branch_report.py`** | Weekly FDIC branch changes report | CSV from FDIC BankFind | Excel in `reports/branch_changes/` |

### Utility Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| **`05_find_bank_lei.py`** | Find LEI for a bank name | `python scripts/05_find_bank_lei.py "Bank Name"` |
| **`07_find_top_cbsas.py`** | Find top CBSAs for a lender | `python scripts/07_find_top_cbsas.py --lei LEI123` |
| **`06_validate_worst_lenders_data_v2.py`** | Validate worst lenders data | `python scripts/06_validate_worst_lenders_data_v2.py input.csv` |
| **`08_check_excel_sheets.py`** | Validate Excel file structure | `python scripts/08_check_excel_sheets.py file.xlsx` |

### Data Processing Utilities

| Script | Purpose | Usage |
|--------|---------|-------|
| **`process_fdic_csvs.py`** | Process FDIC BankFind CSVs | `python scripts/process_fdic_csvs.py --input folder/` |
| **`load_rssd_crosswalk.py`** | Load RSSD to LEI crosswalk | Used by other scripts |

## 📋 Script Categories

### ✅ Production Scripts (Standard)
- `01_worst_lenders_analysis_v2.py` - v2 uses 2022-2024 qualification
- `worst_lenders_analysis.py` - v1 (legacy, kept for comparison)
- `02_fifth_third_cba_report.py`
- `03_generate_merger_analysis.py`
- `04_generate_weekly_branch_report.py`
- `comerica_cba_report.py`
- `comerica_sb_report.py`

### 🔧 Utility Scripts (Standard)
- `05_find_bank_lei.py`
- `07_find_top_cbsas.py`
- `06_validate_worst_lenders_data_v2.py`
- `08_check_excel_sheets.py`
- `check_report_files.py`

### 📊 Analysis-Specific Scripts
These are tied to specific projects or one-off analyses:
- `fifth_third_sb_report.py` - Small business analysis
- `merger_branch_hhi_analysis.py` - Merger HHI calculations
- Various test/debug scripts

### 🧪 Development/Test Scripts
- `test_*.py` - Test scripts
- `check_*.py` - Validation scripts
- `explore_*.py` - Data exploration

## 🔍 Finding Scripts

### By Task

**Want to analyze worst lenders?**
→ `01_worst_lenders_analysis_v2.py` (use v2 for 2022-2024 data)

**Want to analyze a specific bank?**
→ `02_fifth_third_cba_report.py` or `comerica_cba_report.py`

**Want to find a bank's LEI?**
→ `05_find_bank_lei.py`

**Want to validate data before analysis?**
→ `06_validate_worst_lenders_data_v2.py` or `08_check_excel_sheets.py`

### By File Naming Pattern

- `*_analysis.py` - Main analysis scripts
- `*_report.py` - Report generators
- `find_*.py` - Lookup/utility scripts
- `check_*.py` - Validation scripts
- `test_*.py` - Test scripts
- `generate_*.py` - Generator scripts

## 🚀 Quick Start Commands

```bash
# Worst Lenders Analysis (v2 - standard)
python scripts/01_worst_lenders_analysis_v2.py --input data/raw/worst_lenders.csv

# Fifth Third Report
python scripts/02_fifth_third_cba_report.py

# Find a bank's LEI
python scripts/05_find_bank_lei.py "Bank Name"

# Validate data
python scripts/06_validate_worst_lenders_data_v2.py data/raw/file.csv
```

## 📝 Adding New Standard Scripts

When creating a new standard script:

1. **Use clear naming with number prefix**: `NN_purpose_action.py` (e.g., `01_worst_lenders_analysis_v2.py`)
2. **Add to this guide**: Update the table above
3. **Include docstring**: Document purpose, inputs, outputs
4. **Add to README.md**: If it's a main workflow script
5. **Version control**: Use `_v2`, `_v3` suffixes for major revisions

## 🔄 Script Versioning

- **Current version**: Use `_v2`, `_v3` for major changes
- **Keep old versions**: Don't delete, they may be needed for historical data
- **Document changes**: Note version differences in script header

## 📚 Related Documentation

- **Main README**: `README.md` - Project overview
- **Getting Started**: `GETTING_STARTED.md` - Setup guide
- **Quick Reference**: `QUICK_REFERENCE.md` - Command cheat sheet
- **Project Guides**: `docs/guides/` - Specific workflow guides

