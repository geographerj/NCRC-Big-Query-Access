# Huntington National Bank + Cadence Bank CBA Report Guide

## Available Resources

### ✅ Previous CBA Report Examples

**Location**: `reports/fifth_third_merger/`

1. **Fifth_Third_CBA_Report.xlsx** - Complete CBA report example with:
   - One sheet per CBSA (top 10 markets)
   - Borrower demographics metrics (Hispanic%, Black%, Asian%, etc.)
   - Redlining metrics (MMCT 50%, MMCT 80%, Black Tract 50%, etc.)
   - Peer comparisons with statistical significance
   - Methods sheet documenting methodology

2. **Comerica_CBA_Report.xlsx** - Same format, adapted for Comerica Bank

3. **FifthThird_Comerica_Merger_Analysis_20251031_071656.xlsx** - Complete merger analysis with:
   - Executive Summary
   - Branch Overlap by CBSA
   - HHI Analysis (pre/post merger with antitrust flags)
   - Branch summaries for both banks
   - Detailed branch listings

### ✅ Guides Available

1. **MERGER_ANALYSIS_GUIDE.md** (`docs/reference/MERGER_ANALYSIS_GUIDE.md`)
   - Comprehensive guide on bank merger analysis
   - HHI calculation methodology
   - Branch overlap detection
   - Antitrust concern identification

2. **QUICK_START_MERGER_ANALYSIS.md** (`docs/reference/QUICK_START_MERGER_ANALYSIS.md`)
   - Quick reference for running merger analysis
   - Step-by-step instructions
   - Key features explanation

3. **GENERATE_MERGER_ANALYSIS.md** (`docs/reference/GENERATE_MERGER_ANALYSIS.md`)
   - Complete workflow for generating merger analysis
   - Output descriptions
   - Example results

### ✅ Scripts Available

1. **scripts/02_fifth_third_cba_report.py** - CBA report generator (can be adapted)
2. **scripts/comerica_cba_report.py** - Example of adapted CBA report script
3. **scripts/03_generate_merger_analysis.py** - Merger analysis generator (HHI + branch overlap)

## Bank Information Needed

### Huntington National Bank
- **LEI**: `2WHM8VNJH63UN14OL754` ✅ (found in `data/reference/Lenders_and_LEI_Numbers.csv`)
- **RSSD**: ⏳ **Need to find** (for branch data matching)
- **HMDA Name**: "The Huntington National Bank"

### Cadence Bank
- **LEI**: `Q7C315HKI8VX0SSKBS64` ✅ (found in `data/reference/Lenders_and_LEI_Numbers.csv`)
- **RSSD**: ⏳ **Need to find** (for branch data matching)
- **HMDA Name**: "Cadence Bank"

## Steps to Create CBA Report for Huntington + Cadence

### Step 1: Find RSSD Numbers

You'll need RSSD numbers for both banks to query branch data. Options:

**Option A: Use existing script**
```bash
python scripts/05_find_bank_lei.py --bank "The Huntington National Bank"
python scripts/05_find_bank_lei.py --bank "Cadence Bank"
```

**Option B: Query BigQuery directly**
```sql
-- Find RSSD for Huntington (using LEI to find HMDA data, then match to branch data)
SELECT DISTINCT lei, respondent_name
FROM `hdma1-242116.hmda.hmda`
WHERE lei = '2WHM8VNJH63UN14OL754'
LIMIT 5;

-- Find RSSD in branch data (search by name)
SELECT DISTINCT rssd, institution_name
FROM `hdma1-242116.branches.sod25`
WHERE LOWER(institution_name) LIKE '%huntington%'
  AND year = 2025
LIMIT 10;
```

### Step 2: Get Lending Data from BigQuery

You'll need to run two queries for each bank:

**Query 1: Demographics Query** (similar to Fifth Third demographics query)
- Location: `queries/fifth_third/FIFTH_THIRD_DEMOGRAPHICS_QUERY.sql`
- Adapt by replacing LEI with:
  - Huntington: `2WHM8VNJH63UN14OL754`
  - Cadence: `Q7C315HKI8VX0SSKBS64`
- Export results to CSV:
  - `data/raw/huntington_demographics.csv`
  - `data/raw/cadence_demographics.csv`

**Query 2: Redlining Query** (similar to Fifth Third redlining query)
- Location: `queries/fifth_third/FIFTH_THIRD_REDLINING_FULL_QUERY.sql`
- Adapt by replacing LEI
- Export results to CSV:
  - `data/raw/huntington_redlining.csv`
  - `data/raw/cadence_redlining.csv`

### Step 3: Create CBA Report Scripts

You'll need to create two new scripts (similar to `comerica_cba_report.py`):

**Option A: Create individual scripts**
- `scripts/huntington_cba_report.py`
- `scripts/cadence_cba_report.py`

**Option B: Use a generic script** (adapt existing)

Both scripts should:
1. Load the demographics and redlining CSV files
2. Calculate metrics (borrower demographics, redlining metrics)
3. Create Excel workbook with one sheet per CBSA
4. Add Methods sheet

### Step 4: Generate CBA Reports

Once you have the CSV files:

```bash
# Generate Huntington CBA Report
python scripts/huntington_cba_report.py --input data/raw/huntington_demographics.csv --input2 data/raw/huntington_redlining.csv

# Generate Cadence CBA Report
python scripts/cadence_cba_report.py --input data/raw/cadence_demographics.csv --input2 data/raw/cadence_redlining.csv
```

**Output locations:**
- `reports/huntington/Huntington_CBA_Report.xlsx`
- `reports/cadence/Cadence_CBA_Report.xlsx`

### Step 5: Generate Merger Analysis (HHI + Branch Overlap)

Create or adapt `scripts/04_generate_huntington_cadence_merger_analysis.py`:

```python
# Update bank information in script
HUNTINGTON = {
    'name': 'The Huntington National Bank',
    'lei': '2WHM8VNJH63UN14OL754',
    'rssd': 'XXXXXX'  # Replace with actual RSSD
}

CADENCE = {
    'name': 'Cadence Bank',
    'lei': 'Q7C315HKI8VX0SSKBS64',
    'rssd': 'XXXXXX'  # Replace with actual RSSD
}
```

Then run:
```bash
python scripts/04_generate_huntington_cadence_merger_analysis.py
```

**Output**: `reports/merger_analysis/Huntington_Cadence_Merger_Analysis_[timestamp].xlsx`

## Report Structure

### CBA Report (per bank)
- **One sheet per CBSA**: Top 10 CBSAs by loan volume
- **Metrics per sheet**:
  - Borrower Demographics: Hispanic%, Black%, Asian%, Native American%, HoPI%, LMIB%, LMICT%
  - Redlining: MMCT 50%, MMCT 80%, Black Tract 50%, Black Tract 80%, Hispanic Tract 50%, Hispanic Tract 80%, Black+Hispanic Tract 50%, Black+Hispanic Tract 80%
- **Comparisons**: Subject Share vs. Peer Share vs. Gap
- **Statistical Significance**: Z-test results (marked with *)
- **Color Coding**: Green (positive gap), Yellow/Orange/Red (negative gaps)
- **Methods Sheet**: Complete methodology documentation

### Merger Analysis Report
- **Executive Summary**: Bank information and overview
- **Branch Overlap by CBSA**: Markets where both banks operate
- **HHI Analysis** ⚠️ **KEY SHEET**:
  - Pre-merger HHI (current market concentration)
  - Post-merger HHI (after merger)
  - HHI change
  - Antitrust concern flag (RED highlighting if HHI > 1,800 AND increase > 100)
- **Bank Branch Summaries**: Branch counts and deposits by CBSA
- **Detailed Branch Listings**: All branches for each bank

## Key Files Reference

### Example Excel Files
- `reports/fifth_third_merger/Fifth_Third_CBA_Report.xlsx` - Complete CBA report example
- `reports/fifth_third_merger/Comerica_CBA_Report.xlsx` - Another CBA report example
- `reports/fifth_third_merger/FifthThird_Comerica_Merger_Analysis_20251031_071656.xlsx` - Complete merger analysis example

### Scripts to Reference/Adapt
- `scripts/02_fifth_third_cba_report.py` - CBA report generator (975+ lines)
- `scripts/comerica_cba_report.py` - Adapted CBA report (155 lines, imports from Fifth Third script)
- `scripts/03_generate_merger_analysis.py` - Merger analysis generator (522 lines)

### Guides
- `docs/reference/MERGER_ANALYSIS_GUIDE.md` - Comprehensive merger analysis guide
- `docs/reference/QUICK_START_MERGER_ANALYSIS.md` - Quick reference
- `docs/reference/GENERATE_MERGER_ANALYSIS.md` - Step-by-step workflow

### Data Files
- `data/reference/Lenders_and_LEI_Numbers.csv` - Contains LEIs for both banks
- `data/reference/CBSA_to_County_Mapping.csv` - CBSA crosswalk for geographic mapping

## Next Steps Checklist

- [ ] Find RSSD numbers for both banks (for branch data matching)
- [ ] Create/adapt BigQuery queries for Huntington demographics
- [ ] Create/adapt BigQuery queries for Huntington redlining
- [ ] Create/adapt BigQuery queries for Cadence demographics
- [ ] Create/adapt BigQuery queries for Cadence redlining
- [ ] Run queries and export to CSV files
- [ ] Create `scripts/huntington_cba_report.py` (or adapt existing script)
- [ ] Create `scripts/cadence_cba_report.py` (or adapt existing script)
- [ ] Generate Huntington CBA report
- [ ] Generate Cadence CBA report
- [ ] Create/adapt `scripts/04_generate_huntington_cadence_merger_analysis.py`
- [ ] Update bank information (LEI, RSSD) in merger analysis script
- [ ] Generate merger analysis report
- [ ] Review HHI analysis for antitrust concerns
- [ ] Prepare reports for regulatory filings

## Questions?

Refer to the guides above or check the example files in `reports/fifth_third_merger/` for reference.

