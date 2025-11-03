# Testing Guide for Member Report Generation

## Prerequisites

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Required packages:
   - pandas
   - numpy
   - openpyxl
   - reportlab
   - google-cloud-bigquery
   - scipy

2. **BigQuery Credentials**
   - Ensure credentials file exists at: `config/credentials/hdma1-242116-74024e2eb88f.json`
   - Or specify path with `--credentials` flag

3. **Test Configuration**
   - Use `configs/test_config.json` for initial testing
   - Modify as needed for your test scenario

## Quick Test

### Step 1: Test with Query Only (No Reports)

```bash
cd "Member Reports"
python scripts/generate_member_report.py --config configs/test_config.json --query-only
```

This will:
- Load configuration
- Connect to BigQuery
- Execute query
- Save raw data to `data/raw/`
- Skip report generation

**Check:** Verify raw data CSV is created and contains expected columns

### Step 2: Generate Full Reports

```bash
python scripts/generate_member_report.py --config configs/test_config.json
```

This will:
- Query data from BigQuery
- Process data and calculate metrics
- Generate PDF report → `outputs/excel/TEST_REPORT_001_Report.pdf`
- Generate Excel report → `outputs/excel/TEST_REPORT_001_Data.xlsx`
- Save raw data → `data/raw/TEST_REPORT_001_raw.csv`

## What to Check

### PDF Report (`*_Report.pdf`)

- [ ] Title page with NCRC logo (if available)
- [ ] Pagination (page numbers)
- [ ] Introduction section
- [ ] Key Findings/Points section
- [ ] Overview of Lending section
- [ ] Analysis of Top Lenders section
- [ ] Methods and Sources section
- [ ] Header/footer on all pages
- [ ] Proper formatting and spacing

### Excel Report (`*_Data.xlsx`)

- [ ] Sheet for each table in the report
- [ ] Methods sheet with full methodology
- [ ] Header rows formatted (gray background, bold)
- [ ] Gap columns color-coded (if applicable)
- [ ] Column widths auto-adjusted
- [ ] Frozen header rows
- [ ] Proper number formatting

### Data Files

- [ ] Raw data CSV saved to `data/raw/`
- [ ] Data contains expected columns
- [ ] Data has rows (not empty)

## Troubleshooting

### Import Errors

If you get import errors:
```python
# Make sure you're in the Member Reports directory
cd "Member Reports"
python scripts/generate_member_report.py ...
```

Or use absolute paths:
```python
python "C:\DREAM\Member Reports\scripts\generate_member_report.py" ...
```

### BigQuery Connection Errors

- Verify credentials file path
- Check that service account has BigQuery access
- Ensure project ID is correct (`hdma1-242116`)

### Missing Dependencies

```bash
pip install reportlab pandas openpyxl google-cloud-bigquery scipy numpy
```

### PDF Generation Errors

- If logo fails to load, report will continue without logo
- Check that reportlab is installed: `pip install reportlab`

### Excel Generation Errors

- Ensure openpyxl is installed: `pip install openpyxl`
- Check that data has rows (empty DataFrames may cause issues)

## Test Configuration Options

Edit `configs/test_config.json` to test different scenarios:

### Test with Specific Lender
```json
"subject_lender": {
  "lei": "YOUR_LEI_HERE"
}
```

### Test with Different Geography
```json
"geography": {
  "type": "county",
  "county_codes": ["36047", "36061"]
}
```

### Test Different Years
```json
"years": [2022, 2023, 2024]
```

### Test Different Metrics
```json
"metrics": {
  "borrower_demographics": {
    "enabled": true,
    "include": ["black", "hispanic"]
  }
}
```

## Expected Output Structure

```
Member Reports/
├── outputs/
│   └── excel/
│       ├── TEST_REPORT_001_Report.pdf
│       └── TEST_REPORT_001_Data.xlsx
├── data/
│   └── raw/
│       └── TEST_REPORT_001_raw.csv
└── logs/
    └── [timestamp]_log.txt (if logging enabled)
```

## Next Steps After Testing

Once testing is successful:
1. Create production configuration for actual member request
2. Review and customize narrative generation
3. Add community profile data integration
4. Customize PDF/Excel formatting as needed
5. Test with actual member data

---

*For issues or questions, check the logs in `logs/` directory or review error messages.*

