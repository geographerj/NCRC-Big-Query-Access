# Complete Project Structure

Full file tree and organization guide for the NCRC Member Reports system.

## Directory Tree

```
C:\DREAM\Member Reports\
│
├── README.md                          ⭐ Main overview and guide
├── QUICK_START.md                     📖 Quick reference
├── REPORT_WRITING_QUICK_REFERENCE.md  📝 Writing style reminders
├── PROJECT_STRUCTURE.md               📋 This file
│
├── configs/                           ⚙️ Configuration files
│   ├── README.md                      📖 Config documentation
│   ├── template_config.json           📄 Template for new reports
│   ├── tampa_market_report.json       📄 Tampa example
│   └── test_config.json               📄 Test configuration
│
├── scripts/                           🚀 Execution scripts
│   ├── README.md                      📖 Scripts documentation
│   ├── create_tampa_report.py         ⭐ PRIMARY - Use as template
│   ├── generate_member_report.py       🔧 General generator
│   ├── generate_member_report_interactive.py  🔧 Interactive setup
│   ├── extract_community_profile_data.py     🔧 Data extraction
│   ├── enhance_lender_background.py          🔧 Lender research
│   └── [other utility scripts]        🔧 Various helpers
│
├── generators/                        📊 Report generation classes
│   ├── README.md                      📖 Generators documentation
│   ├── pdf_generator.py               ⭐ PDF report generation
│   ├── excel_generator.py             ⭐ Excel workbook generation
│   └── data_processor.py              ⭐ Metric calculations
│
├── queries/                           🔍 BigQuery SQL builders
│   ├── README.md                      📖 Queries documentation
│   ├── tampa_market_query.py          ⭐ Tampa queries (template)
│   └── member_report_queries.py       🔧 General query builder
│
├── utils/                             🛠️ Utility functions
│   ├── README.md                      📖 Utils documentation
│   ├── ncrc_branding.py               ⭐ Branding standards
│   ├── report_formatting.py            📝 Number formatting
│   ├── community_profile.py           📊 Community data handling
│   ├── lender_background_search.py    🔍 Lender research
│   └── bigquery_client.py             🔌 BigQuery connection
│
├── supporting_files/                  📁 Reference materials
│   ├── README.md                      📖 Supporting files guide
│   ├── NCRC_Logo.jpg                  ⭐ REQUIRED logo
│   ├── NCRC Style Guide FP.pdf        📖 Brand guidelines
│   ├── Updated NCRC_Brand Guidelines_V19b.pdf  📖 Current guidelines
│   ├── Community Profile of [Location].pdf     📊 Community data
│   ├── assessment_areas/              📁 Optional
│   ├── crosswalks/                    📁 Optional
│   └── tickets/                       📁 Optional
│
├── data/                              💾 Data storage
│   ├── processed/                     📊 Processed metrics (CSV)
│   │   ├── tampa_market_metrics.csv
│   │   └── tampa_top_10_lenders_metrics.csv
│   ├── raw/                           📥 Raw HMDA data (CSV)
│   │   ├── tampa_market_data.csv
│   │   └── tampa_top_lenders_2024.csv
│   ├── lender_background_info.json    💾 Lender database
│   └── [location]_community_profile_data.json  📊 Extracted profiles
│
├── outputs/                           📤 Generated reports
│   └── [Community]_[Member]/          📁 Individual reports
│       ├── [Report]_Report.pdf        📄 Final PDF
│       ├── [Report]_Data.xlsx         📊 Excel workbook
│       ├── [metrics].csv              📊 Data files
│       ├── raw_data/                   📁 Raw data copy
│       └── [config].json               ⚙️ Config copy
│
├── docs/                              📚 Documentation
│   ├── INDEX.md                       📑 Documentation index
│   └── guides/                        📖 Detailed guides
│       ├── GETTING_STARTED.md         🚀 Setup guide
│       ├── CONFIGURATION_REFERENCE.md ⚙️ Config docs
│       ├── REPORT_WRITING_GUIDELINES.md  ✍️ Writing standards
│       ├── BRANDING_GUIDELINES.md     🎨 Brand specs
│       ├── COMMUNITY_PROFILE_INTEGRATION.md  📊 Profile usage
│       ├── LENDER_BACKGROUND_SEARCH.md  🔍 Lender research
│       └── [other guides]             📖 Additional docs
│
└── logs/                              📝 Execution logs (optional)
```

## Key Files by Purpose

### ⭐ Start Here
- `README.md` - Complete system overview
- `QUICK_START.md` - Fast reference
- `scripts/create_tampa_report.py` - Primary report generator

### 📖 Documentation
- `docs/guides/` - All detailed guides
- `docs/guides/INDEX.md` - Documentation index
- `REPORT_WRITING_QUICK_REFERENCE.md` - Style reminders

### ⚙️ Configuration
- `configs/template_config.json` - Configuration template
- `configs/tampa_market_report.json` - Complete example

### 🚀 Execution
- `scripts/create_tampa_report.py` - Main report generator
- `scripts/generate_member_report_interactive.py` - Interactive setup

### 📊 Generation
- `generators/pdf_generator.py` - PDF creation
- `generators/excel_generator.py` - Excel creation
- `generators/data_processor.py` - Metrics calculation

### 🔍 Queries
- `queries/tampa_market_query.py` - SQL query builder (template)

### 🛠️ Utilities
- `utils/ncrc_branding.py` - Branding standards
- `utils/report_formatting.py` - Formatting functions

### 📁 Required Files
- `supporting_files/NCRC_Logo.jpg` - Logo (required)
- Service account key for BigQuery (external)

## File Naming Conventions

### Reports
- Config: `[location]_[type]_report.json`
- Output folder: `[Community]_[Member]`
- PDF: `[Report]_Report.pdf`
- Excel: `[Report]_Data.xlsx`

### Data Files
- Processed: `[location]_[type]_metrics.csv`
- Raw: `[location]_[type]_data.csv`
- Community profile: `[location]_community_profile_data.json`

### Scripts
- Location-specific: `create_[location]_report.py`
- General: `generate_[function].py`

## Getting Started Workflow

1. **Read Documentation**
   - `README.md` - System overview
   - `QUICK_START.md` - Quick start guide

2. **Review Example**
   - `scripts/create_tampa_report.py` - Complete example
   - `outputs/Tampa_FL_Sample_Member/` - Sample output

3. **Prepare Files**
   - Add logo: `supporting_files/NCRC_Logo.jpg`
   - Add community profile (optional)
   - Ensure BigQuery access

4. **Create Configuration**
   - Copy `configs/template_config.json`
   - Or use `scripts/setup_new_report.py`

5. **Generate Report**
   - Run `scripts/create_tampa_report.py`
   - Or create location-specific script

6. **Review Output**
   - Check `outputs/[Community]_[Member]/`
   - Verify PDF and Excel formats

## Maintenance

### Adding New Locations
1. Copy `scripts/create_tampa_report.py` → `scripts/create_[location]_report.py`
2. Copy `queries/tampa_market_query.py` → `queries/[location]_query.py`
3. Update census tracts and location names
4. Test and refine

### Updating Branding
1. Update `utils/ncrc_branding.py`
2. Replace logo if needed: `supporting_files/NCRC_Logo.jpg`
3. Check `docs/guides/BRANDING_GUIDELINES.md`

### Adding Documentation
1. Add guide to `docs/guides/`
2. Update `docs/guides/INDEX.md`
3. Link from main `README.md` if major feature

## Notes

- ⭐ = Primary/recommended files
- 🔧 = Utility/helper scripts
- 📖 = Documentation
- 📊 = Data files
- ⚙️ = Configuration

For detailed information on any component, see the README.md in each directory.


