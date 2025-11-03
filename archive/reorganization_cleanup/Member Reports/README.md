# NCRC Member Reports System

This system generates comprehensive, branded mortgage lending reports for NCRC members using HMDA data from Google BigQuery.

## Quick Start

1. **Run the interactive report generator:**
   ```bash
   python scripts/create_tampa_report.py
   ```
   
   Or use the interactive setup:
   ```bash
   python scripts/generate_member_report_interactive.py
   ```

2. **Reports are generated in:** `outputs/[Community]_[Member]/`

## Project Structure

```
Member Reports/
├── README.md                          # This file - comprehensive overview
├── QUICK_START.md                     # Quick reference guide
├── REPORT_WRITING_QUICK_REFERENCE.md  # Writing style quick reference
│
├── configs/                           # Report configuration files
│   ├── template_config.json           # Template for new reports
│   └── [report_name]_config.json     # Individual report configs
│
├── scripts/                           # Main execution scripts
│   ├── create_tampa_report.py        # **PRIMARY** Tampa report generator (full featured)
│   ├── generate_member_report.py      # General report generator
│   └── generate_member_report_interactive.py  # Interactive setup
│
├── generators/                        # Core report generation classes
│   ├── pdf_generator.py               # PDF report creation with NCRC branding
│   ├── excel_generator.py             # Excel workbook generation
│   └── data_processor.py              # Metric calculations
│
├── queries/                           # BigQuery SQL query builders
│   ├── tampa_market_query.py          # Tampa-specific queries
│   └── member_report_queries.py       # General query builder
│
├── utils/                             # Utility functions
│   ├── ncrc_branding.py               # NCRC colors, fonts, branding
│   ├── report_formatting.py           # Number/percentage formatting
│   ├── community_profile.py           # Community profile data handling
│   ├── lender_background_search.py    # Lender information extraction
│   └── bigquery_client.py             # BigQuery connection helper
│
├── supporting_files/                  # Reference materials
│   ├── NCRC_Logo.jpg                  # NCRC logo (required)
│   ├── NCRC Style Guide FP.pdf        # Branding guidelines
│   ├── Updated NCRC_Brand Guidelines_V19b.pdf
│   └── Community Profile of [Location].pdf  # Community profile PDFs
│
├── data/                              # Data storage
│   ├── processed/                    # Processed metrics (CSV)
│   ├── raw/                           # Raw HMDA data (CSV)
│   ├── lender_background_info.json    # Lender background data
│   └── [location]_community_profile_data.json  # Extracted profile data
│
├── outputs/                           # Generated reports
│   └── [Community]_[Member]/          # Individual report folders
│       ├── [Report]_Report.pdf        # Final PDF report
│       ├── [Report]_Data.xlsx         # Excel data workbook
│       ├── [metrics].csv              # Processed data files
│       ├── raw_data/                  # Raw HMDA data
│       └── [config].json              # Report configuration copy
│
└── docs/                              # Documentation
    └── guides/                        # Detailed guides
        ├── GETTING_STARTED.md         # Initial setup guide
        ├── CONFIGURATION_REFERENCE.md  # Config file structure
        ├── REPORT_WRITING_GUIDELINES.md # Writing standards
        ├── BRANDING_GUIDELINES.md      # Branding requirements
        ├── COMMUNITY_PROFILE_INTEGRATION.md  # Using community profiles
        ├── LENDER_BACKGROUND_SEARCH.md # Lender research process
        └── MANUAL_COMMUNITY_PROFILE_DATA.md # Manual data entry
```

## Key Features

### Report Generation
- **PDF Reports**: Branded PDFs with NCRC logo, pagination, tables, and narrative analysis
- **Excel Workbooks**: Multi-sheet workbooks with all data, metrics, and methodology
- **Automatic Data Processing**: HMDA data querying, metric calculation, and formatting

### NCRC Branding
- NCRC colors and fonts
- Logo placement on title page
- Consistent table formatting
- Professional pagination

### Analysis Features
- Market overview by year (2018-2024)
- Top 10 lender analysis with individual tables
- Race/ethnicity metrics (Black, Hispanic, Asian, White, Native American, HoPI)
- Geographic metrics (LMIB, LMICT, MMCT)
- Lender background information:
  - Official lender names from GLEIF (Global LEI Index)
  - Headquarters locations (from GLEIF)
  - LEI record URLs for verification
  - Company websites (hyperlinked)
  - Community Benefits Agreements (CBA) status
  - Company history and mergers
  - Fair lending violations and redlining complaints
- Demographic trend analysis:
  - Historical Census data (2000, 2010, 2020, current ACS)
  - Long-term population trend context
  - Rising/stagnant/declining population analysis

### Narrative Generation
- Introduction with demographic context
- Key findings highlighting trends
- Market pattern analysis with community profile integration
- Individual lender narratives with background information

## Requirements

### Python Packages
```bash
pip install reportlab pandas openpyxl google-cloud-bigquery pdfplumber pillow census us requests
```

**Required packages:**
- `reportlab` - PDF generation
- `pandas` - Data processing
- `openpyxl` - Excel generation
- `google-cloud-bigquery` - BigQuery access
- `pdfplumber` - PDF text extraction (for community profiles)
- `pillow` - Image processing (for logo)
- `census` - Census API client
- `us` - U.S. state/county FIPS code utilities
- `requests` - HTTP requests (for GLEIF API, Census API)

See `requirements.txt` in the root directory for complete list.

### BigQuery Access
- Service account key file: `hdma1-242116-74024e2eb88f.json`
- Access to `hdma1-242116.hmda.hmda` table
- Access to `hdma1-242116.hmda.lenders18` table

### Supporting Files
- NCRC Logo: `supporting_files/NCRC_Logo.jpg`
- Community Profile PDF: `supporting_files/Community Profile of [Location].pdf` (optional)

### API Keys
- **Census API Key** (recommended): Set `CENSUS_API_KEY` environment variable
  - Get free key at: https://api.census.gov/data/key_signup.html
  - Enables automatic fetching of current and historical Census data (2000, 2010, 2020)
  - Falls back to JSON files if API unavailable

## Usage Guide

### Creating a New Report

1. **Prepare Community Profile** (optional but recommended):
   - Place community profile PDF in `supporting_files/`
   - Extract census tracts from the profile
   - Run extraction script if needed:
     ```bash
     python scripts/extract_community_profile_data.py
     ```

2. **Create Configuration**:
   - Copy `configs/template_config.json` to `configs/[report_name]_config.json`
   - Fill in:
     - Geographic scope (census tracts)
     - Time period (years)
     - Loan filters
     - Member organization name

3. **Generate Report**:
   ```bash
   python scripts/create_tampa_report.py
   ```
   
   Or use the Tampa report as a template and modify for your location.

### Report Sections

Every report includes:

1. **Title Page**: Logo, title, member organization, date
2. **Introduction**: Community demographics and context
3. **Key Findings**: Trend highlights
4. **Market Overview**: Tables showing lending patterns by year
5. **Top Lenders Analysis**: Individual analysis of top 10 lenders
6. **Methods and Sources**: Methodology and data sources

## Documentation Files

- **README.md** (this file): System overview and structure
- **QUICK_START.md**: Fast reference for common tasks
- **REPORT_WRITING_QUICK_REFERENCE.md**: Writing style reminders
- **docs/guides/GETTING_STARTED.md**: Detailed setup instructions
- **docs/guides/REPORT_WRITING_GUIDELINES.md**: Comprehensive writing standards
- **docs/guides/BRANDING_GUIDELINES.md**: Branding specifications
- **docs/guides/CONFIGURATION_REFERENCE.md**: Config file documentation

## Key Scripts

### Primary Scripts (Use These)
- `scripts/create_tampa_report.py` - Full-featured Tampa report (use as template for other locations)
- `scripts/generate_member_report_interactive.py` - Interactive setup for new reports

### Utility Scripts
- `scripts/extract_community_profile_data.py` - Extract data from community profile PDFs
- `scripts/enhance_lender_background.py` - Search and update lender background information

### Development/Testing Scripts
- `scripts/process_tampa_data.py` - Standalone data processing
- `scripts/check_tampa_data.py` - Data validation

## Data Flow

1. **Configuration** → Defines report parameters (location, years, filters)
2. **Query Builder** → Generates BigQuery SQL for HMDA data
3. **Data Processor** → Calculates metrics (race shares, geographic metrics)
4. **Report Generator** → Creates PDF and Excel outputs
5. **Output** → Organized folder with all files

## NCRC Methodology

Reports follow NCRC's HMDA methodology:
- **Race Classification**: Hispanic checked first, then first explicit race code
- **Missing Data**: Excluded from race denominator calculations
- **Geographic Metrics**: All originations as denominator
- **Borrower Metrics**: Only loans with demographic data as denominator

See: https://ncrc.org/ncrcs-hmda-2018-methodology-how-to-calculate-race-and-ethnicity/

## Branding Standards

- **Colors**: NCRC Orange (#FF6B35), NCRC Blue
- **Fonts**: Helvetica family
- **Logo**: Upper left corner, 10 points from edges, title page only
- **Tables**: NCRC blue headers, alternating row colors, proper formatting

## Community Profile Integration

Community profiles provide:
- Demographic data (race/ethnicity percentages)
- Income data (median income, poverty rates)
- Housing data (homeownership rates)
- Population trends

Extracted data stored in: `data/processed/[location]_community_profile_data.json`

## Lender Background Information

System automatically:
- **GLEIF Integration** (primary source):
  - Looks up official lender names using LEI numbers
  - Retrieves headquarters locations (city, state)
  - Generates LEI record URLs for verification
  - Corrects name formatting (removes entity suffixes, fixes capitalization)
- **CBA Status**: Checks for Community Benefits Agreements with NCRC
- **Web Search** (secondary source):
  - Searches for company history and mergers
  - Extracts website URLs for hyperlinks
  - Finds fair lending violations and redlining complaints
- **Data Storage**: Stores data in `data/lender_background_info.json` for future use

## Output Files

Each report generates:
- `[Report]_Report.pdf` - Branded PDF with all sections
- `[Report]_Data.xlsx` - Excel workbook with:
  - Market Overview sheet
  - Individual lender sheets (top 10)
  - Methods sheet
- CSV files with processed metrics
- Raw data CSV files
- Configuration JSON copy

## Troubleshooting

### Logo Not Appearing
- Check that `supporting_files/NCRC_Logo.jpg` exists
- Verify file path in `utils/ncrc_branding.py` or `generators/pdf_generator.py`

### BigQuery Errors
- Verify service account key file exists
- Check BigQuery table access permissions
- Ensure table names are correct

### Data Issues
- Run `scripts/check_tampa_data.py` to validate data
- Check census tract format (should be strings)
- Verify year format in configuration

## Support

For questions or issues:
- NCRC Research Department: research@ncrc.org
- Documentation: See `docs/guides/` for detailed guides
- Examples: Check `outputs/Tampa_FL_Sample_Member/` for sample report

## Version History

This system was developed to standardize NCRC member report generation, incorporating:
- NCRC branding and style guidelines
- HMDA methodology compliance
- Automated narrative generation
- Community profile integration
- Lender background research
- Professional PDF/Excel output

---

**Last Updated**: 2025-01-XX
**Maintained By**: NCRC Research Department
