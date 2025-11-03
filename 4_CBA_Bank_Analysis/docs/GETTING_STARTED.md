# Getting Started with DREAM Analysis Project

Welcome! This guide will help you understand and use the DREAM analysis project for CRA (Community Reinvestment Act) lending analysis.

## What This Project Does

This project analyzes bank lending patterns using HMDA (Home Mortgage Disclosure Act) data from BigQuery. It helps you:
- Analyze lending patterns by bank, geographic area (CBSA), and demographics
- Generate Excel reports comparing subject banks to peer banks
- Calculate demographic shares and disparities
- Identify redlining patterns

## Project Structure Overview

```
C:\DREAM\
├── scripts/              # Python scripts to generate Excel reports
├── queries/              # SQL queries to run in BigQuery
├── data/
│   ├── raw/             # Place BigQuery CSV exports here
│   └── reference/       # Crosswalk files (CBSA names, lender names, etc.)
├── reports/             # Generated Excel reports appear here
├── config/credentials/  # BigQuery service account JSON (keep secure!)
├── batch/               # Batch files for easy script execution
└── Lending and Branch Analysis/  # Reusable analysis modules
```

## Setup (First Time Only)

### 1. Install Python Dependencies

Run:
```bash
pip install -r requirements.txt
```

Or use the batch file:
```bash
batch\install_packages.bat
```

### 2. Verify BigQuery Credentials

Make sure your BigQuery service account JSON file is in:
```
config\credentials\hdma1-242116-74024e2eb88f.json
```

If you don't have it, ask your team lead for the credentials file.

## Common Workflows

### Workflow 1: Generate a Fifth Third Bank Report

**Step 1: Get Top CBSAs**
- Open BigQuery Console: https://console.cloud.google.com/bigquery
- Run the query from: `queries\fifth_third\fifth_third_top_cbsas.sql`
- Note the top 10 CBSA codes from results

**Step 2: Run Main Demographics Query**
- Open `queries\fifth_third\FIFTH_THIRD_DEMOGRAPHICS_QUERY.sql`
- Update the CBSA codes in the query (replace the placeholder)
- Run in BigQuery (may take 10-30 minutes)
- Export results to CSV
- Save CSV to: `data\raw\fifth_third_demographics.csv`

**Step 3: Run Redlining Query (Optional)**
- Open `queries\fifth_third\FIFTH_THIRD_REDLINING_FULL_QUERY.sql`
- Update CBSA codes
- Run and export to CSV
- Save to: `data\raw\fifth_third_redlining.csv`

**Step 4: Generate Excel Report**

If you have both files:
```bash
python scripts\fifth_third_cba_report.py --input data\raw\fifth_third_demographics.csv --input2 data\raw\fifth_third_redlining.csv
```

Or if auto-detecting files:
```bash
python scripts\fifth_third_cba_report.py
```

Or use the batch file:
```bash
batch\run_excel_generator.bat data\raw\fifth_third_demographics.csv data\raw\fifth_third_redlining.csv
```

**Output**: Excel file in `reports\fifth_third\Fifth_Third_CBA_Report.xlsx`

---

### Workflow 2: Analyze CBA Banks

**Step 1: Run Query in BigQuery**
- Use a SQL query to get CBA bank data
- Export to CSV
- Save to: `data\raw\cba_banks_data.csv`

**Step 2: Generate Report**
```bash
python scripts\cba_banks_analysis_v4_FINAL.py --input data\raw\cba_banks_data.csv
```

**Output**: Excel file in `reports\cba_banks\CBA_Banks_Analysis.xlsx`

---

### Workflow 3: Analyze Worst Lenders

**Step 1: Run Query in BigQuery**
- Export results to CSV
- Save to: `data\raw\worst_lenders_data.csv`

**Step 2: Generate Report**
```bash
python scripts\ncrc_worst_lenders_analysis_v4.py --input data\raw\worst_lenders_data.csv
```

**Output**: Excel file in `reports\worst_lenders\NCRC_Worst_Lenders_Analysis.xlsx`

---

### Workflow 4: Use the Analysis Module (Advanced)

The `Lending and Branch Analysis` folder contains reusable utilities:

**Example: Find Top CBSAs for a Lender**
```python
from Lending and Branch Analysis.utils.bigquery_client import create_client
from Lending and Branch Analysis.queries.hmda_queries import get_lender_activity_by_year

client = create_client()
query = get_lender_activity_by_year(year=2024, lender_lei='YOUR_LEI')
df = client.execute_query(query)
```

See `Lending and Branch Analysis\examples\test_fifth_third.py` for more examples.

## Quick Reference

### Where to Put Files

| File Type | Location |
|-----------|----------|
| BigQuery CSV exports | `data\raw\` |
| Generated Excel reports | `reports\[project_name]\` |
| SQL queries | `queries\[project_name]\` |
| Python scripts | `scripts\` |
| Reference data | `data\reference\` |

### Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run Fifth Third report (auto-detect files)
python scripts\fifth_third_cba_report.py

# Run Fifth Third report (specify files)
python scripts\fifth_third_cba_report.py --input file1.csv --input2 file2.csv

# Find top CBSAs for a lender
python scripts\find_top_cbsas.py --lei YOUR_LEI --year 2024
```

### Batch Files (Windows)

All batch files are in the `batch\` folder:
- `install_packages.bat` - Install Python dependencies
- `run_excel_generator.bat` - Generate Fifth Third Excel report
- `run_find_cbsas.bat` - Find top CBSAs for a lender
- `run_cmd.bat` - Run arbitrary Python commands

## Understanding the Reports

### Fifth Third Report Structure
- **One sheet per CBSA**: Each of the top 10 CBSAs gets its own sheet
- **Methods sheet**: Documents filters and methodology
- **Metrics**: Borrower demographics (Hispanic%, Black%, Asian%, etc.) and income metrics (LMIB%, LMICT%)
- **Comparison**: Subject bank vs. peer banks for each metric/year

### Report Metrics Explained
- **Hispanic%**, **Black%**, **Asian%**, etc.: Share of loans to borrowers of that race/ethnicity
- **LMIB%**: Low-to-Moderate Income Borrower percentage
- **LMICT%**: Low-to-Moderate Income Census Tract percentage
- **Subject Share**: The bank you're analyzing
- **Peer Share**: Average of comparable banks
- **Gap**: Difference between Subject and Peer

## Troubleshooting

### "Module not found" error
- Run: `pip install -r requirements.txt`

### "Credentials not found" error
- Check that `config\credentials\hdma1-242116-74024e2eb88f.json` exists
- Ask your team lead for the credentials file if missing

### "File not found" error
- Make sure CSV files are in `data\raw\`
- Check file paths use backslashes on Windows: `data\raw\filename.csv`

### BigQuery query takes too long
- Add more filters (year, CBSA, etc.)
- Use `LIMIT 100` to test queries first
- Check that you're using the correct table: `hdma1-242116.hmda.hmda`

## Getting Help

### Documentation
- **Quick Start Guides**: `docs\guides\`
- **Technical Docs**: `docs\technical\`
- **This Guide**: `GETTING_STARTED.md`

### Common Questions

**Q: Where do I get CBSA codes?**
- Run `queries\fifth_third\fifth_third_top_cbsas.sql` for a specific lender
- Or check reference data in `data\reference\`

**Q: How do I find a lender's LEI?**
- Check `data\reference\Lenders_and_LEI_Numbers.csv`
- Or search in BigQuery: `SELECT DISTINCT lei, respondent_name FROM hdma1-242116.hmda.hmda WHERE respondent_name LIKE '%Bank Name%'`

**Q: What years of data are available?**
- HMDA data: 2018-2024 (and historical)
- Always filter by year in your queries!

## Next Steps

1. ✅ **Set up your environment** (install packages, verify credentials)
2. ✅ **Try a simple workflow** (run Fifth Third report with sample data)
3. ✅ **Explore the SQL queries** (understand the data structure)
4. ✅ **Modify queries** (customize for your analysis needs)
5. ✅ **Generate reports** (use the scripts to create Excel files)

## Contact

NCRC Research Department  
For questions: research@ncrc.org

Happy analyzing! 🚀

