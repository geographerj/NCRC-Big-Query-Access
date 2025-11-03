# Member Reports - Quick Start Guide

## Generate a Report (3 Steps)

### 1. Prepare Your Configuration
- Copy `configs/template_config.json` to `configs/[your_report]_config.json`
- Update:
  - Geographic scope (census tracts)
  - Years (e.g., 2018-2024)
  - Member organization name
  - Loan filters (if different from defaults)

### 2. Add Supporting Files (Optional but Recommended)
- **NCRC Logo**: `supporting_files/NCRC_Logo.jpg` (required)
- **Community Profile PDF**: `supporting_files/Community Profile of [Location].pdf` (optional)
- **Census API Key**: Set `CENSUS_API_KEY` environment variable (recommended)
  ```bash
  set CENSUS_API_KEY=your-api-key-here
  ```
  - Get free key: https://api.census.gov/data/key_signup.html
  - Enables automatic fetching of current and historical Census data (2000, 2010, 2020, current ACS)
  - Falls back to JSON files if API unavailable

**Note**: The system automatically:
- Looks up official lender names from GLEIF (using LEI numbers)
- Fetches demographic data from Census API (with historical trends)
- Formats lender names correctly (removes entity suffixes, proper capitalization)

### 3. Generate Report
```bash
python scripts/create_tampa_report.py
```

**Report location:** `outputs/[Community]_[Member]/[Report]_Report.pdf`

## For New Locations

**Best approach:** Use Tampa report as template (`scripts/create_tampa_report.py`)

1. Copy `scripts/create_tampa_report.py` → `scripts/create_[location]_report.py`
2. Update:
   - Census tract list
   - Location name throughout
   - Community profile path
3. Run your new script

## Key Files to Know

| File | Purpose |
|------|---------|
| `scripts/create_tampa_report.py` | **Main report generator** - Use as template |
| `scripts/create_montgomery_report.py` | Example: County-level report (uses entire county, Census API) |
| `configs/template_config.json` | Configuration template |
| `supporting_files/NCRC_Logo.jpg` | Required logo file |
| `data/lender_background_info.json` | Lender information database (GLEIF + web search) |
| `utils/census_api_client.py` | Census API integration (fetches 2000, 2010, 2020, current) |
| `docs/guides/REPORT_WRITING_GUIDELINES.md` | Writing standards |
| `docs/guides/GLEIF_INTEGRATION.md` | GLEIF lender name lookup guide |
| `docs/guides/CENSUS_API_SETUP.md` | Census API setup guide |
| `docs/guides/LOAN_FILTERS_REFERENCE.md` | Standard HMDA filters documentation |

## Common Commands

```bash
# Generate Tampa report
python scripts/create_tampa_report.py

# Extract community profile data
python scripts/extract_community_profile_data.py

# Check data quality
python scripts/check_tampa_data.py

# Interactive report setup
python scripts/generate_member_report_interactive.py
```

## Report Outputs

Each report creates a folder: `outputs/[Community]_[Member]/`

Contains:
- `[Report]_Report.pdf` - Final PDF report
- `[Report]_Data.xlsx` - Excel workbook with all data
- CSV files with metrics
- Configuration copy
- Raw data files

## Quick Troubleshooting

**Logo missing?** → Check `supporting_files/NCRC_Logo.jpg` exists

**BigQuery error?** → Verify service account key file and table access

**Wrong data?** → Check census tract/county format in config

**Lender names showing as LEIs?** → GLEIF lookup may have failed; check internet connection

**Census data wrong?** → Set `CENSUS_API_KEY` environment variable for accurate data

**Formatting issues?** → See `docs/guides/BRANDING_GUIDELINES.md`

**Loan filters unclear?** → See `docs/guides/LOAN_FILTERS_REFERENCE.md`

## Writing Style Reminders

- Plain English for general audience
- Minimal data citations (tables show the data)
- Format percentages: `##.#` (12.5%, not 12.50%)
- Format numbers: `#,###` (1,234, not 1234)

See `REPORT_WRITING_QUICK_REFERENCE.md` for full guidelines.

## Need More Help?

- **Setup Guide**: `docs/guides/GETTING_STARTED.md`
- **Writing Guide**: `docs/guides/REPORT_WRITING_GUIDELINES.md`
- **Full Documentation**: `README.md`
