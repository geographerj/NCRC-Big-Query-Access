# Fifth Third Bank Analysis - Folder Structure

## Recommended Folder Organization

This project uses the following folder structure to keep files organized:

```
DREAM Analysis/
├── data/                      # Input CSV files from BigQuery
│   ├── bquxjob_*.csv         # Place your BigQuery export CSV files here
│   └── ...
├── reports/                   # Output Excel reports
│   ├── Fifth_Third_CBA_Report_*.xlsx
│   └── ...
├── scripts/                   # Batch files and utility scripts
│   └── run_excel_generator.bat
├── SQL/                       # SQL query files (optional, but recommended)
│   ├── FIFTH_THIRD_DEMOGRAPHICS_QUERY.sql
│   └── FIFTH_THIRD_REDLINING_FULL_QUERY.sql
└── fifth_third_cba_report.py  # Main Python script (stays at root)
```

## Folder Purposes

### `data/` Folder
- **Purpose**: Store all input CSV files from BigQuery exports
- **Contents**: 
  - Redlining analysis CSV files (from `FIFTH_THIRD_REDLINING_FULL_QUERY.sql`)
  - Demographics analysis CSV files (from `FIFTH_THIRD_DEMOGRAPHICS_QUERY.sql`)
- **Auto-detection**: The script automatically looks in this folder for CSV files

### `reports/` Folder
- **Purpose**: All generated Excel reports are saved here
- **Naming**: Reports include timestamps (e.g., `Fifth_Third_CBA_Report_20250115_143022.xlsx`)
- **Organization**: Easy to find and review all generated reports

### `scripts/` Folder
- **Purpose**: Batch files and helper scripts
- **Contains**: 
  - `run_excel_generator.bat` - Main batch file to generate reports

### `SQL/` Folder (Optional)
- **Purpose**: Keep all SQL query files organized
- **Contains**: BigQuery SQL queries for different analyses

## How to Use

### Step 1: Organize Your Files
1. **Create folders** (if they don't exist):
   - The script automatically creates `reports/` and `data/` folders when run
   - Or create manually: `mkdir reports data scripts SQL`

2. **Move your CSV files**:
   ```
   Move BigQuery exports to: data/
   ```

### Step 2: Run the Analysis
**Option A: Using the batch file (from scripts folder)**
```cmd
cd scripts
run_excel_generator.bat
```

**Option B: Using the batch file (from project root)**
```cmd
scripts\run_excel_generator.bat
```

**Option C: Directly with Python**
```cmd
python fifth_third_cba_report.py --input "data\your_file.csv"
```

### Step 3: Find Your Results
- Excel reports will be in: `reports/Fifth_Third_CBA_Report_*.xlsx`

## File Path Examples

### Running with specific files:
```cmd
python fifth_third_cba_report.py --input "data\bquxjob_redlining.csv" --input2 "data\bquxjob_demographics.csv"
```

### Auto-detection:
- The script looks in both the current directory and `data/` folder
- Uses the two most recent `bquxjob_*.csv` files found

## Notes
- Folders are created automatically if they don't exist
- CSV files can be in either the root directory or `data/` folder
- Reports always go to `reports/` folder
- Batch file can be run from anywhere (it changes to project root)

