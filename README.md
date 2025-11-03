# DREAM Analysis Project

Community Reinvestment Act (CRA) and lending analysis tools for examining bank lending patterns and demographic disparities.

## Project Structure

```
DREAM Analysis/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
│
├── config/                        # Configuration files
│   └── credentials/               # Credentials (gitignored - DO NOT COMMIT)
│       └── hdma1-242116-74024e2eb88f.json
│
├── scripts/                       # Python report generators
│   ├── fifth_third_cba_report.py
│   ├── generate_fifth_third_report.py
│   ├── ncrc_worst_lenders_analysis_v4.py
│   ├── cba_banks_analysis_v4_FINAL.py
│   ├── find_top_cbsas.py
│   └── check_excel_sheets.py
│
├── queries/                       # SQL query files
│   └── fifth_third/              # Fifth Third specific queries
│       ├── FIFTH_THIRD_COMBINED_FULL_QUERY.sql
│       ├── FIFTH_THIRD_DEMOGRAPHICS_QUERY.sql
│       ├── FIFTH_THIRD_REDLINING_FULL_QUERY.sql
│       ├── fifth_third_top_cbsas.sql
│       └── fifth_third_tract_demographics_query.sql
│
├── data/                          # Data files
│   ├── raw/                       # BigQuery exports (CSV files)
│   │   └── bquxjob_*.csv
│   └── reference/                 # Reference/mapping data
│       ├── CBSA_to_County_Mapping.csv
│       └── Lenders_and_LEI_Numbers.csv
│
├── reports/                       # Generated Excel reports
│   ├── fifth_third/              # Fifth Third reports
│   ├── cba_banks/                # CBA Banks reports
│   ├── worst_lenders/            # Worst Lenders reports
│   └── archive/                  # Old reports
│
├── batch/                         # Batch/command scripts
│   ├── install_packages.bat
│   ├── run_cmd.bat
│   ├── run_find_cbsas.bat
│   └── run_excel_generator.bat
│
├── tests/                         # Test scripts
│   ├── test_connection.py
│   └── test_simple.py
│
├── docs/                          # Documentation
│   ├── guides/                    # How-to guides
│   │   ├── QUICK_START_FIFTH_THIRD.md
│   │   ├── RUN_FIFTH_THIRD_REPORT.md
│   │   ├── HOW_TO_ASK_FOR_HMDA_QUERIES.md
│   │   └── GITHUB_AUTH_GUIDE.md
│   ├── technical/                 # Technical documentation
│   │   ├── TRACT_DEMOGRAPHIC_METRICS_REQUIREMENTS.md
│   │   ├── FINAL_IMPLEMENTATION_SUMMARY.md
│   │   └── IMPLEMENTATION_SUMMARY.md
│   └── archive/                   # Old/temporary docs
│
├── Lending and Branch Analysis/   # Reusable analysis module
│   ├── queries/
│   ├── utils/
│   └── examples/
│
└── archive/                       # Archived items
    └── NCRC-Big-Query-Access/     # Duplicate/old folder
```

## Quick Start

### Setting Up

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure credentials:**
   - Place your BigQuery service account JSON file in `config/credentials/`
   - File should be named: `hdma1-242116-74024e2eb88f.json`
   - **Never commit credentials to git!**

### Running Reports

#### Fifth Third Bank CBA Report

```bash
# From project root
python scripts/02_fifth_third_cba_report.py --input data/raw/your_file.csv

# Or use auto-detection (finds most recent bquxjob_*.csv in data/raw/)
python scripts/02_fifth_third_cba_report.py
```

Output will be saved to `reports/fifth_third/`

#### CBA Banks Analysis

```bash
python scripts/cba_banks_analysis_v4_FINAL.py --input data/raw/cba_banks_data.csv
```

#### Worst Lenders Analysis (v2 - Standard)

```bash
# Use v2 for 2022-2024 qualification (post-census boundary changes)
python scripts/01_worst_lenders_analysis_v2.py --input data/raw/worst_lenders_data.csv
```

## Folder Purposes

### `scripts/`
Python scripts that generate Excel reports from BigQuery CSV exports.

**Standard scripts** (most commonly used - numbered for easy sorting):
- `01_worst_lenders_analysis_v2.py` - Worst lenders redlining analysis (2022-2024)
- `02_fifth_third_cba_report.py` - Fifth Third Bank CBA report
- `03_generate_merger_analysis.py` - Merger impact analysis
- `05_find_bank_lei.py` - Find bank LEI codes
- `06_validate_worst_lenders_data_v2.py` - Data validation

See `docs/guides/STANDARD_SCRIPTS.md` for complete reference.

### `queries/`
SQL queries organized by project/bank. Use these in BigQuery to generate the CSV files that go into `data/raw/`.

### `data/`
- `raw/`: Place BigQuery export CSV files here
- `reference/`: Reference data files (crosswalks, mappings, etc.)

### `reports/`
All generated Excel reports, organized by project type.

### `batch/`
Batch files and utility scripts for running analyses.

### `config/credentials/`
**SECURITY WARNING**: This folder contains sensitive credentials and is gitignored. Never commit files in this folder.

## Data Workflow

1. **Generate SQL Query** → Run in BigQuery
2. **Export Results** → Save CSV to `data/raw/`
3. **Run Python Script** → Generate Excel report in `reports/`

## Documentation

- **Guides**: Step-by-step instructions (`docs/guides/`)
- **Technical**: Detailed technical documentation (`docs/technical/`)
- **Archive**: Old/temporary documentation (`docs/archive/`)

## Notes

- All CSV files are gitignored (they contain sensitive data)
- All Excel reports are gitignored (they contain analysis results)
- Credentials are gitignored (security)
- The `Lending and Branch Analysis/` folder is a reusable module

## Contact

NCRC Research Department  
National Community Reinvestment Coalition  
For questions: research@ncrc.org

