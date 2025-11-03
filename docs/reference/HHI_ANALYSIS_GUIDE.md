# HHI (Herfindahl-Hirschman Index) Analysis Guide for Bank Mergers

## Overview

The Herfindahl-Hirschman Index (HHI) is a key metric for analyzing market concentration in bank merger reviews. This guide explains how to use HHI calculations in your CRA and antitrust analysis work.

## What is HHI?

HHI measures market concentration by:
1. Calculating each firm's market share (as percentage)
2. Squaring each market share
3. Summing the squared shares

**Formula**: HHI = Σ(market_share_i)² × 10,000

**Range**: 0 (perfectly competitive) to 10,000 (monopoly)

## DOJ Antitrust Thresholds

Based on [DOJ Antitrust Division guidelines](https://www.justice.gov/atr/herfindahl-hirschman-index):

### Market Concentration Categories

- **HHI < 1,000**: Unconcentrated
- **1,000 ≤ HHI ≤ 1,800**: Moderately Concentrated  
- **HHI > 1,800**: Highly Concentrated

### Merger Impact Thresholds

- **Increase in HHI > 100 points** in highly concentrated markets (HHI > 1,800)
  → **Presumed likely to enhance market power**

This is a key threshold for antitrust enforcement!

## Using HHI for Bank Merger Analysis

### 1. Calculate HHI for Lending Markets

Analyze concentration in:
- **CBSA-level markets**: Metropolitan lending markets
- **County-level markets**: Smaller geographic markets
- **Tract-level markets**: Neighborhood-level analysis (less common)

### 2. Compare Pre- vs Post-Merger

For a proposed merger:
- Calculate HHI **before merger** (separate firms)
- Calculate HHI **after merger** (combined firm)
- Calculate **HHI change** (increase)
- Flag markets where **HHI > 1,800 AND change > 100**

## Example Calculation

### Simple Example

Market with 4 lenders:
- Lender A: 30% share
- Lender B: 30% share  
- Lender C: 20% share
- Lender D: 20% share

**HHI Calculation**:
- HHI = 30² + 30² + 20² + 20² = 900 + 900 + 400 + 400 = **2,600**

**Market Category**: **Highly Concentrated** (HHI > 1,800)

### Merger Example

If Lender A and Lender B merge:
- Combined: 60% share
- Lender C: 20% share
- Lender D: 20% share

**New HHI**: 60² + 20² + 20² = 3,600 + 400 + 400 = **4,400**

**HHI Change**: 4,400 - 2,600 = **+1,800 points**

This merger would be **highly problematic** because:
- Market was already highly concentrated (HHI > 1,800)
- HHI increased by > 100 points
- Result is even more concentrated

## How to Use the HHI Utilities

### Step 1: Prepare HMDA Data

```python
from Lending and Branch Analysis.utils.bigquery_client import create_client
from Lending and Branch Analysis.utils.hhi_analysis import analyze_lending_market_concentration

client = create_client()

# Query HMDA data for a market
query = """
SELECT 
    lei,
    cbsa_code,
    activity_year,
    COUNTIF(action_taken = '1') as originations,
    SUM(CASE WHEN action_taken = '1' THEN loan_amount END) as loan_amount
FROM `hdma1-242116.hmda.hmda`
WHERE activity_year = 2024
  AND cbsa_code = '16980'  -- Chicago
GROUP BY lei, cbsa_code, activity_year
"""

df = client.execute_query(query)
```

### Step 2: Calculate HHI

```python
from Lending and Branch Analysis.utils.hhi_analysis import analyze_lending_market_concentration

# Analyze market concentration
results = analyze_lending_market_concentration(
    hmda_df=df,
    market_level='cbsa',  # or 'county', 'tract'
    volume_metric='originations',  # or 'loan_amount'
    year=2024
)

# View HHI by market
print(results['hhi_by_market'])
# Output:
#   cbsa_code    hhi  concentration_category  number_of_firms
#   16980      2450  Highly Concentrated              15

# View market shares
print(results['market_shares'].head())
# Output shows each lender's market share by CBSA

# View summary
print(results['summary_stats'])
```

### Step 3: Analyze Merger Impact

```python
from Lending and Branch Analysis.utils.hhi_analysis import calculate_merger_hhi_change

# Assuming you have pre- and post-merger data
# (For a proposed merger, you'd simulate post-merger by combining the merging firms)

merging_firms = ['LEI_FIRM_A', 'LEI_FIRM_B']  # LEIs of merging banks

hhi_change = calculate_merger_hhi_change(
    pre_merger_df=pre_merger_data,
    post_merger_df=post_merger_data,  # Or simulated post-merger
    market_column='cbsa_code',
    firm_column='lei',
    volume_column='originations',
    merging_firms=merging_firms
)

# Markets with antitrust concerns
concerns = hhi_change[hhi_change['antitrust_concern'] == True]
print(f"Markets with antitrust concerns: {len(concerns)}")
```

### Step 4: Generate Report

```python
from Lending and Branch Analysis.utils.hhi_analysis import create_hhi_report

writer = create_hhi_report(
    analysis_results=results,
    output_path="reports/hhi_analysis_chicago_2024.xlsx"
)
writer.save()
```

## Integration with Existing Reports

### Add HHI to Fifth Third Report

You could add a new sheet showing:
- HHI for each CBSA where Fifth Third operates
- Market concentration category
- Top 4 lenders in each market (C4 ratio)
- Fifth Third's market share

### Example Workflow

```python
# In your Fifth Third report generator

# 1. Get lending data for top CBSAs
fifth_third_cbsas = ['16980', '19100', ...]  # Your top CBSAs

# 2. Calculate HHI for each CBSA
for cbsa in fifth_third_cbsas:
    market_data = get_hmda_data_for_cbsa(cbsa, year=2024)
    hhi_results = analyze_lending_market_concentration(
        market_data,
        market_level='cbsa',
        volume_metric='originations'
    )
    
    # Add to report
    add_hhi_sheet_to_report(hhi_results, cbsa)
```

## Key Metrics in HHI Analysis

### Market Concentration (HHI)
- **Primary metric** for antitrust analysis
- Lower = more competitive
- Higher = more concentrated

### Market Share
- Individual lender's percentage of market
- Used to calculate HHI
- Also important standalone metric

### C4 Ratio (4-Firm Concentration)
- Sum of top 4 firms' market shares
- Alternative concentration measure
- Often calculated alongside HHI

### Number of Firms
- Count of distinct lenders in market
- More firms = lower HHI (generally)

## Interpreting Results

### For Unconcentrated Markets (HHI < 1,000)
- Generally not problematic
- Merger unlikely to raise concerns
- Many competitors present

### For Moderately Concentrated Markets (1,000-1,800)
- Monitor carefully
- Merger impact depends on change magnitude
- Consider other factors

### For Highly Concentrated Markets (HHI > 1,800)
- **Red flag** for antitrust
- Merger increasing HHI by > 100 points is **presumed problematic**
- Requires detailed analysis
- May require divestitures or remedies

## Best Practices

1. **Define markets carefully**
   - CBSA-level is standard for mortgage lending
   - County-level for smaller markets
   - Consider product-specific markets (residential vs commercial)

2. **Use appropriate volume metric**
   - **Originations count**: Standard for lending
   - **Loan amount**: Alternative measure
   - Be consistent across analysis

3. **Consider multiple time periods**
   - Current year (latest data)
   - Historical trends (HHI over time)
   - Pre/post merger comparison

4. **Account for market entry/exit**
   - New lenders entering market
   - Lenders exiting market
   - Impact on concentration

5. **Compare to benchmarks**
   - National averages
   - Similar-sized markets
   - Historical levels

## Common Use Cases

### 1. Merger Review
- **Question**: Will this merger increase market concentration?
- **Analysis**: Calculate HHI before/after, flag concerns

### 2. Market Monitoring
- **Question**: Are lending markets becoming more concentrated?
- **Analysis**: Track HHI over time by CBSA

### 3. Competitive Analysis
- **Question**: Which markets are most/least competitive?
- **Analysis**: Rank markets by HHI, identify concentration trends

### 4. Advocacy Support
- **Question**: Does this merger harm competition?
- **Analysis**: HHI evidence for regulatory filings

## Next Steps

1. **Test HHI calculations**: Run on sample data
2. **Integrate into reports**: Add HHI sheets to Fifth Third report
3. **Create merger templates**: Standard workflow for merger analysis
4. **Build benchmarks**: Historical HHI trends by market

## References

- [DOJ Antitrust Division: Herfindahl-Hirschman Index](https://www.justice.gov/atr/herfindahl-hirschman-index)
- DOJ & FTC Horizontal Merger Guidelines (2023)
- CRA and antitrust analysis best practices

