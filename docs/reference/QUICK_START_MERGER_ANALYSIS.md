# Quick Start: Merger Analysis

## What You Need

✅ You already have:
- Fifth Third LEI: `QFROUN1UWUYU0DVIWD51`
- Comerica LEI: `70WY0ID1N53Q4254VH70`
- Fifth Third RSSD: `723112` (for branch data)
- Comerica RSSD: `60143` (for branch data)

## Two Simple Steps

### Step 1: Generate Comerica Report (like Fifth Third)

**First**, get Comerica's lending data from BigQuery (same query structure as Fifth Third, but use Comerica's LEI: `70WY0ID1N53Q4254VH70`).

**Then**:
```bash
python scripts/comerica_cba_report.py --input data/raw/comerica_demographics.csv --input2 data/raw/comerica_redlining.csv
```

**Output**: `reports/comerica/Comerica_CBA_Report.xlsx`

### Step 2: Generate Branch + HHI Analysis

**No CSV files needed!** This queries BigQuery directly:

```bash
python scripts/generate_merger_analysis.py
```

**Output**: `reports/merger_analysis/FifthThird_Comerica_Merger_Analysis_[date].xlsx`

## What's in the Merger Analysis Report

1. **Executive Summary** - Overview
2. **Branch Overlap by CBSA** - Markets where both banks have branches
3. **HHI Analysis** ⚠️ **MOST IMPORTANT**:
   - Pre-merger HHI (current market concentration)
   - Post-merger HHI (after merger)
   - HHI increase (change)
   - **Red highlighting** = Antitrust concerns (HHI > 1,800 AND increase > 100)
4. **Fifth Third Branches by CBSA** - Branch counts and deposits
5. **Comerica Branches by CBSA** - Branch counts and deposits
6. **All Branches (detailed)** - Complete branch listings

## Key Features

- **Uses RSSD matching** (no name matching needed!)
- **2025 branch data** (from `sod25` table)
- **HHI based on branch deposits** (not lending data)
- **Automatic overlap detection**
- **Automatic antitrust flagging**

## Understanding HHI

- **< 1,500**: Competitive market
- **1,500-2,500**: Moderately concentrated
- **> 2,500**: Highly concentrated

**Antitrust concern** = HHI > 1,800 AND increase > 100

Markets flagged in RED need close attention!

## Files Created

1. `reports/comerica/Comerica_CBA_Report.xlsx` - Comerica lending analysis (same format as Fifth Third)
2. `reports/merger_analysis/FifthThird_Comerica_Merger_Analysis_[date].xlsx` - Complete merger package

Both ready for regulatory filings! 🎉
