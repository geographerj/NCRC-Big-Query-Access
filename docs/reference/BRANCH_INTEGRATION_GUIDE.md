# Branch Data Integration Guide

## Overview: Adding Branch Analysis to CRA Reports

This guide discusses how to integrate bank branch data (Summary of Deposits) into your CRA lending analysis reports. Branch data helps answer critical questions like:
- Does the bank have branches where it makes loans?
- Are branches closing in minority/LMI communities?
- Is branch presence aligned with lending activity?

---

## Your Branch Data Tables

You mentioned having these tables:
- **`sod`** - Summary of Deposits (main branch data)
- **`sod25`** - 2025 Summary of Deposits data  
- **`sod_legacy`** - Legacy/historical branch data

**IMPORTANT CONSTRAINTS:**
- **No reliable join column**: RSSD exists in SOD but NOT in HMDA
- **Bank name matching required**: Names differ between datasets (e.g., "Wells Fargo" vs "Wells Fargo Bank")
- **Manual verification needed**: Always ask user to confirm name matches
- **Table overlap**: Three SOD tables overlap - must avoid double counting
- **Use table with 2017-2025 data**: Need to identify which table has this range
- **Deduplication**: `uninumbr` is unique per branch per year - use for deduplication

These appear to be in: `hdma1-242116.branches.*`

---

## Key Questions Branch Data Can Answer

### 1. **Branch Presence vs. Lending**
- **Question**: "Does the bank have branches in areas where it makes loans?"
- **Analysis**: Compare branch locations (by CBSA) to lending locations
- **Metric**: Branch count per CBSA vs. loan originations per CBSA

### 2. **Branch Closings in Minority/LMI Communities**
- **Question**: "Is the bank closing branches in minority or low-income neighborhoods?"
- **Analysis**: Track branch closings by census tract demographics
- **Metric**: Branch closures by tract demographics (% minority, % LMI)

### 3. **Branch Coverage**
- **Question**: "How well does branch presence match the community demographics?"
- **Analysis**: Branch count/locations by CBSA demographics
- **Metric**: Branches per capita in minority vs. white neighborhoods

### 4. **Deposit Concentration**
- **Question**: "Where are the bank's deposits concentrated?"
- **Analysis**: Total deposits by CBSA, county, or census tract
- **Metric**: Deposit share by geographic area

---

## Branch Metrics to Add to Reports

### Basic Branch Metrics (by CBSA, by Year)

1. **Branch Count**
   - Total branches per CBSA
   - Subject bank branches vs. peer bank branches

2. **Branch Density**
   - Branches per capita (requires population data)
   - Branches per square mile

3. **Deposits**
   - Total deposits per CBSA
   - Average deposits per branch
   - Deposit concentration

4. **Branch Openings/Closings**
   - Net branch change (openings - closings)
   - Branch closures in minority/LMI tracts

5. **Branch-to-Loan Ratio**
   - Loans per branch
   - Branch presence score (has branches vs. no branches)

---

## How to Connect Branch Data with Lending Data

### Connection Methods

**Method 1: By Institution Name**
- Match: `sod.institution_name` with HMDA `respondent_name`
- **Challenge**: Names might not match exactly ("Fifth Third Bank" vs "Fifth Third Bank, National Association")

**Method 2: By LEI (Legal Entity Identifier)**
- Match: Need a crosswalk from `institution_name` to `lei`
- **Better**: More reliable matching
- **Required**: Crosswalk table or manual mapping

**Method 3: By CBSA + Year**
- Match: Analyze by geographic area and time period
- **Use case**: "Branch presence in CBSA X in 2024" vs "Lending in CBSA X in 2024"

---

## Proposed Branch Integration Strategies

### Strategy 1: Add Branch Sheet to Existing Reports

**For Fifth Third Report:**
- Add a new sheet: "Branch Analysis"
- Show for each CBSA:
  - Branch count (subject vs peers)
  - Total deposits
  - Branch-to-loan ratio
  - Branch openings/closings over time

### Strategy 2: Add Branch Metrics to Existing Sheets

**For Fifth Third Report:**
- Add columns to existing CBSA sheets:
  - "Branch Count" per year
  - "Branches in Minority Tracts"
  - "Deposit Share"
- Compare subject bank to peers

### Strategy 3: Standalone Branch Report

**Create new report type:**
- "Branch Presence Analysis"
- Focus on:
  - Geographic distribution of branches
  - Closures in minority/LMI areas
  - Branch density analysis

---

## Technical Implementation

### Step 1: Query Branch Data

You'll need queries that:
1. Get branch data for subject bank (by name or LEI)
2. Get branch data for peer banks
3. Aggregate by CBSA and year
4. Join with lending data

**Example Query Structure:**
```sql
-- Get branch counts by CBSA for a lender
SELECT 
    cbsa_code,
    year,
    COUNT(*) as branch_count,
    SUM(deposits) as total_deposits,
    AVG(deposits) as avg_branch_deposits
FROM `hdma1-242116.branches.sod`
WHERE UPPER(institution_name) LIKE '%FIFTH THIRD%'
  AND year BETWEEN 2018 AND 2024
GROUP BY cbsa_code, year
ORDER BY cbsa_code, year
```

### Step 2: Join with Lending Data

**Option A: Separate queries, merge in Python**
- Query branches separately
- Query lending separately
- Merge by CBSA + year in Python

**Option B: Single SQL query with JOIN**
- Join SOD with HMDA by CBSA + year
- More complex but single source

### Step 3: Calculate Branch Metrics

**Metrics to calculate:**
- Branch count per CBSA (subject vs peers)
- Branch-to-loan ratio
- Branch density (if population data available)
- Branch presence indicator (binary: has branches or not)

### Step 4: Add to Excel Report

**Modify `fifth_third_cba_report.py`:**
- Add branch data loading
- Add branch metrics calculation
- Add branch sheet or columns to existing sheets
- Format and style branch metrics

---

## Specific Integration Ideas

### Idea 1: Branch Presence Indicator

Add to each CBSA sheet:
```
Branch Presence:
- Subject Bank: 5 branches
- Peer Average: 3.2 branches
- Branch-to-Loan Ratio: 2.1 loans per branch (subject) vs 1.8 (peers)
```

### Idea 2: Branch Closures Analysis

Track branch closings in minority/LMI tracts:
```
Branch Closures 2018-2024:
- Subject: 3 branches closed in >50% minority tracts
- Subject: 1 branch closed in >50% LMI tracts
- Peer Average: 2.1 branches closed in minority tracts
```

### Idea 3: Branch-Lending Alignment

Show if branch presence aligns with lending:
```
Branch-Lending Alignment:
- Markets with branches AND high lending: 8 CBSAs
- Markets with branches BUT low lending: 2 CBSAs (red flag)
- Markets without branches but high lending: 0 CBSAs
```

---

## Questions to Answer First

Before we implement, let's clarify:

1. **Which SOD table should we use?**
   - `sod` for current data?
   - `sod25` for 2025 projections?
   - `sod_legacy` for historical?

2. **How do we match institutions?**
   - Institution name matching (fuzzy)?
   - Do you have an LEI crosswalk?
   - Should we create one?

3. **What branch metrics matter most?**
   - Branch count? Deposits? Closings? Density?

4. **Where should branch data appear?**
   - New sheet per report?
   - Additional columns in existing sheets?
   - Separate branch-only reports?

5. **What years of branch data do we have?**
   - Same years as HMDA (2018-2024)?
   - Do we need historical data?

---

## Next Steps

1. **Explore the branch tables** - Run sample queries to understand structure
2. **Identify matching strategy** - How to connect branches to lenders
3. **Define key metrics** - What branch data answers your questions
4. **Prototype integration** - Add branch data to one report as a test
5. **Full implementation** - Roll out to all reports

---

## Current Branch Query Functions Available

You already have these functions in `Lending and Branch Analysis/queries/branch_queries.py`:

- `get_branches_by_cbsa()` - Get all branches in a CBSA
- `get_lender_branches()` - Get branches for a lender (by name)
- `get_lender_branch_presence_by_cbsa()` - Branch summary by CBSA
- `get_branch_openings_closings()` - Track branch changes over time

These can be extended or used as templates for your specific needs.

---

## Example Workflow

1. **Query branch data for Fifth Third:**
   ```python
   query = branch_queries.get_lender_branch_presence_by_cbsa(
       lender_name="Fifth Third",
       year=2024
   )
   ```

2. **Query lending data** (already doing this)

3. **Merge by CBSA:**
   ```python
   merged = lending_df.merge(
       branch_df,
       on=['cbsa_code', 'year'],
       how='left'
   )
   ```

4. **Calculate branch metrics:**
   - Branch count
   - Branch-to-loan ratio
   - Branch presence indicator

5. **Add to Excel report**

---

**Ready to discuss implementation? Let me know:**
- Which branch metrics you want to include
- How you want them displayed in reports
- Any specific branch analysis questions you need answered

