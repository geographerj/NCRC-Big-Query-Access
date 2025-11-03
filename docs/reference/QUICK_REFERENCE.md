# Quick Reference Card

## 🚀 Most Common Tasks

### Generate Fifth Third Report
```bash
# Auto-detect CSV files in data/raw/
python scripts\02_fifth_third_cba_report.py

# Specify files
python scripts\02_fifth_third_cba_report.py --input data\raw\demo.csv --input2 data\raw\redline.csv
```

### Install Dependencies
```bash
pip install -r requirements.txt
# OR
batch\install_packages.bat
```

### Find Top CBSAs for a Lender
```bash
# In BigQuery, run:
queries\fifth_third\fifth_third_top_cbsas.sql
```

## 📁 File Locations

| What | Where |
|------|-------|
| Put BigQuery CSV exports | `data\raw\` |
| Find generated Excel reports | `reports\[project]\` |
| Find SQL queries | `queries\[project]\` |
| Python scripts | `scripts\` |
| BigQuery credentials | `config\credentials\` |

## 🔑 Key Files

- **Standard Scripts**: See `docs\guides\STANDARD_SCRIPTS.md` for full list
- **Main Scripts**: `scripts\01_worst_lenders_analysis_v2.py`, `scripts\02_fifth_third_cba_report.py`
- **SQL Queries**: `queries\fifth_third\*.sql`, `queries\worst_lenders_redlining_query_v2.sql`
- **Utilities**: `Lending and Branch Analysis\utils\`
- **Examples**: `Lending and Branch Analysis\examples\test_fifth_third.py`

## ⚠️ Common Issues

| Problem | Solution |
|---------|----------|
| Module not found | Run `pip install -r requirements.txt` |
| Credentials error | Check `config\credentials\hdma1-242116-74024e2eb88f.json` exists |
| File not found | Use backslashes: `data\raw\file.csv` |
| Query too slow | Add year/CBSA filters, test with `LIMIT 100` |

## 📊 Report Types

1. **Worst Lenders Analysis** (v2): Redlining analysis, 2022-2024 qualification
2. **Fifth Third CBA Report**: Borrower demographics + redlining analysis
3. **Merger Analysis**: Branch and market concentration analysis
4. **Weekly Branch Report**: FDIC branch changes tracking

## 🔍 Need Help?

- Full guide: `GETTING_STARTED.md`
- Project docs: `docs\guides\`
- Technical docs: `docs\technical\`

