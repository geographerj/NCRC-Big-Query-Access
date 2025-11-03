# Bank Merger Analysis Guide

## Overview

This guide explains how to perform comprehensive bank merger analysis, combining:
1. **Individual lending reports** (like Fifth Third report)
2. **Branch network analysis** 
3. **Market overlap detection**
4. **HHI calculations** (pre- and post-merger)

## Example: Fifth Third Bank + Comerica Bank Merger

### Required Information

Before running analysis, you need:

1. **Bank 1 (Fifth Third)**:
   - HMDA Name: "Fifth Third Bank"
   - LEI: `QFROUN1UWUYU0DVIWD51`
   - **SOD Name**: Must verify manually! (e.g., "Fifth Third Bank, National Association")

2. **Bank 2 (Comerica)**:
   - HMDA Name: "Comerica Bank"
   - LEI: Need to find Comerica's LEI
   - **SOD Name**: Must verify manually! (e.g., "Comerica Bank")

3. **SOD Table**: Which table has your year range? (verify 2017-2025)

### Step 1: Verify Bank Names in SOD

**CRITICAL**: You must manually verify SOD names before running analysis!

```bash
# Run the bank name matching tool
python scripts/verify_bank_name_matches.py
```

This creates an Excel file for you to verify:
- "Fifth Third Bank" (HMDA) = ? (SOD)
- "Comerica Bank" (HMDA) = ? (SOD)

**Mark matches and save the crosswalk file.**

### Step 2: Run Merger Analysis

```python
from scripts.merger_analysis_framework import BankMergerAnalysis

# Initialize with VERIFIED names
analysis = BankMergerAnalysis(
    bank1_name="Fifth Third Bank",
    bank1_lei="QFROUN1UWUYU0DVIWD51",
    bank1_sod_name="Fifth Third Bank, National Association",  # VERIFIED!
    bank2_name="Comerica Bank",
    bank2_lei="COMERICA_LEI_HERE",  # Find Comerica's LEI
    bank2_sod_name="Comerica Bank",  # VERIFIED!
    years=[2018, 2019, 2020, 2021, 2022, 2023, 2024],
    sod_table='sod25'  # VERIFY THIS!
)

# Generate comprehensive report
report_path = analysis.generate_full_report(
    output_dir="reports/merger_analysis"
)
```

### Step 3: Review Report Outputs

The report includes:

#### 1. Executive Summary
- Bank names and identifiers
- Analysis parameters
- Report metadata

#### 2. Overlapping Markets
- CBSAs where both banks operate
- Lending volumes for each bank
- Branch counts for each bank
- Combined totals

#### 3. HHI Analysis
**Key Sheet!** Shows for each overlapping market:
- **HHI Pre-Merger**: Market concentration before merger
- **HHI Post-Merger**: Market concentration after merger (banks combined)
- **HHI Change**: Increase in concentration
- **Antitrust Concern**: Flag if HHI > 1,800 AND change > 100

**Interpretation**:
- Markets with **antitrust_concern = True** are problematic
- These require closer scrutiny or potential divestitures

#### 4. Branch Networks
- Bank 1 branches by location
- Bank 2 branches by location
- Summary by CBSA showing branch overlap

#### 5. Lending Comparison
- Top CBSAs for each bank
- Origination volumes
- Loan amounts

## Detailed Analysis Components

### A. Finding Overlapping Markets

The analysis identifies CBSAs where:
- **Both banks have branches**, OR
- **Both banks have significant lending**

This is where the merger will have the most impact.

### B. HHI Calculation Process

For each overlapping market:

1. **Pre-Merger**: Calculate HHI with banks as separate entities
   - Each bank's market share calculated separately
   - HHI = sum of (each lender's share)²

2. **Post-Merger**: Calculate HHI with banks combined
   - Combine the two banks' volumes
   - Recalculate all market shares
   - Calculate new HHI

3. **HHI Change**: Difference between post and pre

4. **Antitrust Flag**: 
   - Pre-merger HHI > 1,800 (highly concentrated)
   - AND HHI change > 100 points
   - → Antitrust concern!

### C. Branch Overlap Analysis

The analysis shows:
- Where each bank has branches
- Markets with branches from both banks
- Branch count and deposit totals
- Geographic overlap areas

### D. Market Share Analysis

Shows each bank's market share in overlapping markets:
- Bank 1's share pre-merger
- Bank 2's share pre-merger
- Combined share post-merger
- Impact on market concentration

## Example Output Interpretation

### Market: Chicago (CBSA 16980)

**Pre-Merger**:
- Fifth Third: 5% market share
- Comerica: 3% market share
- Total lenders: 50
- HHI: 1,200 (Moderately Concentrated)

**Post-Merger**:
- Combined: 8% market share
- HHI: 1,350
- HHI Change: +150 points

**Result**: Market stays moderately concentrated, change is significant but below 1,800 threshold. **May need review** but not automatic concern.

### Market: Detroit (CBSA 19820)

**Pre-Merger**:
- Fifth Third: 12% market share
- Comerica: 15% market share
- Total lenders: 20
- HHI: 2,100 (Highly Concentrated)

**Post-Merger**:
- Combined: 27% market share
- HHI: 3,200
- HHI Change: +1,100 points

**Result**: **🚨 MAJOR ANTITRUST CONCERN**
- Market already highly concentrated (HHI > 1,800)
- HHI increases by > 100 points
- Combined bank would control 27% of market
- **Requires divestitures or remedies**

## Using Results for Advocacy

### For CRA/Fair Lending Advocacy

1. **Identify vulnerable markets**: Markets where both banks operate and serve minority/LMI communities

2. **Track branch closures**: Monitor if merger leads to branch closures in vulnerable areas

3. **Lending patterns**: Compare lending to minority/LMI borrowers in overlapping markets

### For Antitrust Advocacy

1. **Flag high HHI markets**: Markets with antitrust_concern = True

2. **Calculate competitive impact**: Show how merger reduces competition

3. **Support divestiture requests**: Use HHI evidence to argue for branch or market divestitures

### For Regulatory Filings

1. **Document market concentration**: Provide HHI evidence to regulators

2. **Identify problem markets**: Clear list of markets requiring attention

3. **Support community concerns**: Show impact on competition and access

## Workflow Checklist

- [ ] **Verify SOD names** for both banks (use matching tool)
- [ ] **Find LEIs** for both banks (check HMDA data or crosswalk file)
- [ ] **Identify SOD table** with your year range (2017-2025)
- [ ] **Run merger analysis** script
- [ ] **Review overlapping markets** - are they expected?
- [ ] **Check HHI results** - which markets have concerns?
- [ ] **Review branch overlap** - where do networks overlap?
- [ ] **Validate results** - do numbers make sense?
- [ ] **Export for advocacy** - use in filings/comments

## Next Steps After Analysis

1. **Deep dive into high-HHI markets**
   - Detailed lending analysis by demographic
   - Branch network analysis
   - Competitive impact assessment

2. **Develop remedies recommendations**
   - Divestiture targets
   - Branch retention requirements
   - Lending commitments

3. **Prepare advocacy materials**
   - Summary of findings
   - Key markets of concern
   - Recommended actions

4. **File comments with regulators**
   - CFPB, Fed, OCC comments
   - Community hearings
   - Congressional testimony support

## Common Questions

**Q: What if banks don't have exact SOD name matches?**
A: Use the bank name matching tool to find closest matches, then manually verify. Update the script with verified names.

**Q: What years should I analyze?**
A: Typically 3-5 years of recent data (2019-2024). More years = better trend analysis.

**Q: Should I include all CBSAs or just overlapping ones?**
A: Focus on overlapping markets for HHI analysis, but you can analyze all markets for each bank individually.

**Q: How do I interpret HHI changes under 100 points?**
A: Changes < 100 points in moderately/unconcentrated markets are generally acceptable, but still review for other factors.

**Q: What if a market has very few lenders?**
A: Markets with < 5-10 lenders will naturally have high HHI. Focus on markets with meaningful competition where merger impact is significant.

## Technical Notes

- **Deduplication**: Branch data is deduplicated using `uninumbr` + `year`
- **Market definition**: Uses CBSA-level markets (standard for mortgage lending)
- **Volume metric**: Uses originations count (can modify to loan amount)
- **Matching**: GEOID from branches can join to HMDA census_tract for tract-level analysis

## References

- DOJ Antitrust Guidelines: https://www.justice.gov/atr/herfindahl-hirschman-index
- CRA merger review process
- Fair lending in merger context

