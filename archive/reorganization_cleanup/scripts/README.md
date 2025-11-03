# Scripts Directory

This directory contains all Python scripts for the DREAM Analysis project.

## 📁 Organization

### Standard Scripts (Most Used)

**Analysis Reports** (numbered for easy sorting):
- `01_worst_lenders_analysis_v2.py` - Worst lenders redlining analysis (use v2)
- `02_fifth_third_cba_report.py` - Fifth Third Bank CBA enforcement report
- `03_generate_merger_analysis.py` - Merger impact analysis
- `04_generate_weekly_branch_report.py` - Weekly FDIC branch changes

**Utilities** (numbered for easy sorting):
- `05_find_bank_lei.py` - Find LEI for a bank
- `06_validate_worst_lenders_data_v2.py` - Validate data before analysis
- `07_find_top_cbsas.py` - Find top CBSAs for a lender
- `08_check_excel_sheets.py` - Validate Excel structure

### Project-Specific Scripts

- `comerica_cba_report.py` - Comerica Bank analysis
- `fifth_third_sb_report.py` - Small business analysis
- `merger_branch_hhi_analysis.py` - Merger HHI calculations

### Legacy/Version History

- `worst_lenders_analysis.py` - v1 (pre-2022 boundaries)
- `ncrc_worst_lenders_analysis_v4.py` - Legacy version
- `cba_banks_analysis_v4_FINAL.py` - Legacy CBA analysis

## 🔍 Quick Find

**Need to analyze worst lenders?**
→ `01_worst_lenders_analysis_v2.py`

**Need to find a bank's LEI?**
→ `05_find_bank_lei.py`

**Need to validate data?**
→ `06_validate_worst_lenders_data_v2.py`

**Need to generate a report?**
→ Check `*_report.py` scripts

## 📚 Full Reference

See `docs/guides/STANDARD_SCRIPTS.md` for:
- Complete list of standard scripts
- Usage examples
- Input/output specifications
- Version differences

## 🎯 Naming Conventions

**Standard scripts use number prefixes** (01_, 02_, etc.) to sort to the top:
- `NN_*_analysis_v2.py` - Analysis scripts (v2 = post-2022 boundaries)
- `NN_*_report.py` - Report generators
- `NN_find_*.py` - Lookup utilities
- `NN_check_*.py` - Validation scripts
- `NN_generate_*.py` - Generator scripts

**Other scripts** (project-specific, legacy, test):
- `*_analysis.py` - Legacy or project-specific analysis
- `test_*.py` - Test scripts
- `check_*.py` - Validation scripts (without numbers)

## 💡 Tips

- **Numbered scripts (01_, 02_, etc.) are standard** - they appear at the top of file listings
- **Always use v2 scripts** when available (they handle 2022 census boundary changes)
- **Check docstrings** in scripts for usage: `python scripts/script_name.py --help`
- **Validate data first** with validation scripts before running analysis
- **Version numbers** indicate major changes - read header comments for differences

