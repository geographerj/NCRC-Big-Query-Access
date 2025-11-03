# Generate Complete Merger Analysis

## Overview

This generates a complete analysis package for the Fifth Third + Comerica merger:

1. **Comerica CBA Report** (same format as Fifth Third)
2. **Branch Footprint Analysis** (where each bank operates)
3. **Overlap Detection** (markets where both banks have branches)
4. **HHI Analysis** (pre- and post-merger market concentration)

## Quick Start

### Step 1: Generate Comerica CBA Report

**First, get Comerica's lending data from BigQuery** (same queries as Fifth Third, but with Comerica's LEI):

Run the demographics query with Comerica's LEI: `70WY0ID1N53Q4254VH70`

Then generate the report:
```bash
python scripts/comerica_cba_report.py --input data/raw/comerica_demographics.csv --input2 data/raw/comerica_redlining.csv
```

Or if you have both files in `data/raw/`:
```bash
python scripts/comerica_cba_report.py
```

### Step 2: Generate Branch + HHI Analysis

This analyzes branches and calculates HHI:

```bash
python scripts/generate_merger_analysis.py
```

**No CSV files needed!** This script:
- Queries branch data directly using RSSD
- Queries HMDA data for HHI calculations
- Creates comprehensive Excel report

## What You'll Get

### Report 1: Comerica CBA Report
**Location**: `reports/comerica/Comerica_CBA_Report.xlsx`

Same format as Fifth Third report:
- One sheet per CBSA
- Borrower demographics metrics
- Redlining metrics
- Peer comparisons
- Methods sheet

### Report 2: Merger Analysis Report
**Location**: `reports/merger_analysis/FifthThird_Comerica_Merger_Analysis_[timestamp].xlsx`

Contains:
1. **Executive Summary** - Overview of both banks
2. **Branch Overlap by CBSA** - Markets where both operate
3. **HHI Analysis** ⚠️ **KEY SHEET**:
   - Pre-merger HHI
   - Post-merger HHI  
   - HHI change
   - Antitrust concern flag (highlighted in RED)
4. **Fifth Third Branches by CBSA** - Branch counts and deposits
5. **Comerica Branches by CBSA** - Branch counts and deposits
6. **Fifth Third All Branches** - Detailed branch listing
7. **Comerica All Branches** - Detailed branch listing

## Key Features

### Branch Analysis (2025 Data)
- Uses RSSD matching (723112 for Fifth Third, 60143 for Comerica)
- Shows branch counts by CBSA
- Identifies LMI and minority tract branches
- Total deposits by market

### HHI Analysis (2025 Branch Deposits)
- Calculates market concentration using branch deposits (not lending)
- Shows pre- and post-merger HHI based on deposit market share
- Flags antitrust concerns (HHI > 1,800 AND increase > 100)
- Highlights problematic markets in RED

### Overlap Detection
- Identifies CBSAs where both banks have branches
- Shows branch counts for each bank
- Calculates combined presence

## Example Output

```
Branch Footprint:
- Fifth Third: 1,234 branches in 45 markets
- Comerica: 567 branches in 32 markets
- Overlap: 18 markets where both operate

HHI Analysis:
- 18 overlapping markets analyzed
- 3 markets with antitrust concerns ⚠️

Markets Requiring Attention:
  CBSA 19100 (Detroit):
    Pre-merger HHI: 2,100 (Highly Concentrated)
    Post-merger HHI: 3,200
    HHI Increase: +1,100
    Combined Share: 27%
```

## What You Need

✅ **Already have:**
- Fifth Third LEI: `QFROUN1UWUYU0DVIWD51`
- Comerica LEI: `70WY0ID1N53Q4254VH70`
- Fifth Third RSSD: `723112`
- Comerica RSSD: `60143`

⏳ **Need to generate:**
- Comerica lending data CSV (from BigQuery queries)
- Then run the scripts above

## Files Generated

1. `reports/comerica/Comerica_CBA_Report.xlsx` - Comerica lending analysis
2. `reports/merger_analysis/FifthThird_Comerica_Merger_Analysis_[date].xlsx` - Complete merger analysis

Both reports ready for regulatory filings and advocacy!

