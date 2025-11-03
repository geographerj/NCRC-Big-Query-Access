# What This DREAM Project Enables

## Overview: Community Reinvestment Act (CRA) Lending Analysis

This project allows you to analyze bank lending patterns to identify potential discrimination, redlining, and disparities in lending to minority and low-income communities. This is crucial work for holding banks accountable under the Community Reinvestment Act.

---

## What You Can Do Now (That You Couldn't Before)

### 1. **Analyze Bank Lending Patterns**

**What it means:**
- See where banks are making loans geographically
- Compare a bank's lending in different neighborhoods
- Identify if banks are avoiding certain areas

**Real-world use:**
- "Is Fifth Third Bank making loans in predominantly Black neighborhoods?"
- "Does this bank lend in low-income areas?"
- "How does Bank A compare to its peers in lending to Hispanic borrowers?"

**Example Output:**
- Excel report showing: "Fifth Third made 15% of loans to Black borrowers, while peer banks averaged 22%" → This suggests a disparity

---

### 2. **Detect Redlining Patterns**

**What it means:**
- Redlining = systematic refusal to lend in certain neighborhoods (historically minority/LMI areas)
- This project identifies if banks are avoiding:
  - Minority-majority census tracts (>50% or >80% minority)
  - Low-to-moderate income (LMI) tracts
  - Combined minority+LMI tracts

**Real-world use:**
- Evidence for CRA exams
- Community complaints
- Advocacy reports
- Regulatory filings

**Example Output:**
- "Fifth Third made 200 loans in white neighborhoods but only 50 in Black neighborhoods of similar income levels" → Redlining indicator

---

### 3. **Compare Banks to Their Peers**

**What it means:**
- You don't just look at one bank in isolation
- Compare to similar banks (peer banks) in the same market
- Identifies if disparities are bank-specific or market-wide

**Real-world use:**
- If a bank is doing worse than peers → stronger case for discrimination
- If all banks have similar patterns → might be a broader market issue

**Example Output:**
- Excel showing: "Subject bank: 10% loans to Black borrowers | Peer average: 25%" → Clear disparity

---

### 4. **Generate Professional Reports Automatically**

**What it means:**
- BigQuery provides raw data (millions of loan records)
- This project converts it into polished Excel reports
- Reports formatted for:
  - Regulatory filings
  - Community presentations
  - Internal analysis
  - Public advocacy

**Before:** Manually analyzing millions of records in Excel (weeks of work)  
**Now:** Run one script, get professional report in minutes

---

### 5. **Analyze Borrower Demographics**

**What it means:**
- See the race/ethnicity breakdown of borrowers who got loans
- Compare: "Who is the bank lending to?" vs "Who lives in the area?"
- Identifies if certain groups are being excluded

**Real-world use:**
- Evidence that a bank is not serving minority communities proportionally
- Supports fair lending complaints

**Example Metrics:**
- Hispanic% of loans
- Black% of loans
- Asian% of loans
- Low-to-Moderate Income Borrower% (LMIB%)

---

### 6. **Examine Geographic Patterns**

**What it means:**
- Analyze lending by:
  - Metropolitan areas (CBSAs)
  - Counties
  - Census tracts (neighborhoods)
- See where banks are active vs. absent

**Real-world use:**
- "This bank has branches in City A but makes no loans there" → Branch presence without lending
- "All this bank's loans are in wealthy suburbs, none in the city center" → Redlining pattern

---

### 7. **Track Changes Over Time**

**What it means:**
- Compare lending patterns year-over-year (2018-2024)
- See if banks are improving or getting worse
- Track progress after community advocacy

**Real-world use:**
- "Bank X promised to improve. Did they?"
- Historical analysis for enforcement actions
- Trends over time for advocacy reports

---

## Practical Workflows Enabled

### Workflow 1: Bank Exam Preparation

**Scenario:** You need to prepare for a CRA exam or file a complaint

**What you can do:**
1. Run SQL query for the bank's lending data
2. Generate Excel report automatically
3. Identify specific disparities
4. Compare to peer banks
5. Present findings in professional format

**Time:** Hours instead of weeks

---

### Workflow 2: Community Advocacy

**Scenario:** A community group says "Bank X isn't lending in our neighborhood"

**What you can do:**
1. Get HMDA data for that bank in that area
2. Compare to peer banks
3. Calculate demographic shares
4. Generate report showing the disparity
5. Use as evidence for advocacy

**Output:** Clear evidence: "Bank X made 50 loans here, peers averaged 200"

---

### Workflow 3: Multi-Bank Analysis

**Scenario:** Analyzing multiple banks (like CBA banks) at once

**What you can do:**
1. Run queries for multiple banks
2. Generate comparative reports
3. Rank banks by performance
4. Identify worst offenders

**Output:** "Worst Lenders" or "CBA Banks" analysis reports

---

## Key Capabilities Breakdown

### Data Access
- ✅ **HMDA Data**: All mortgage lending data from 2018-2024
- ✅ **BigQuery**: Fast queries on millions of records
- ✅ **Automated**: No manual data downloads needed

### Analysis Tools
- ✅ **Demographic Classification**: NCRC methodology for race/ethnicity
- ✅ **Peer Comparison**: Automatic peer bank identification
- ✅ **Geographic Analysis**: CBSA, county, census tract level
- ✅ **Statistical Testing**: Z-tests for significance

### Reporting
- ✅ **Excel Generation**: Professional, formatted reports
- ✅ **Multiple Metrics**: Demographics, income, geography
- ✅ **Multi-Year**: Trend analysis across time
- ✅ **Multiple CBSAs**: One report per metropolitan area

---

## Real-World Impact

### For NCRC's Work:

1. **CRA Exam Support**
   - Provide data-driven evidence for examiners
   - Identify patterns regulators might miss
   - Support community comments

2. **Fair Lending Enforcement**
   - Evidence for complaints to CFPB, DOJ
   - Statistical proof of disparities
   - Geographic evidence of redlining

3. **Community Empowerment**
   - Give communities data about their banks
   - Show where advocacy is needed
   - Track improvements over time

4. **Bank Accountability**
   - Public reports showing bank performance
   - Comparisons across banks
   - Pressure for improvement

---

## What Makes This Special

### Before This Project:
- ❌ Manual data extraction (weeks)
- ❌ Manual Excel calculations (error-prone)
- ❌ No standardized methodology
- ❌ No peer comparison automation
- ❌ Difficult to analyze multiple banks
- ❌ Hard to track changes over time

### With This Project:
- ✅ Automated data queries (minutes)
- ✅ Automated report generation
- ✅ Standardized NCRC methodology
- ✅ Automatic peer identification
- ✅ Batch analysis of multiple banks
- ✅ Built-in year-over-year comparison

---

## Example Use Cases

### Case 1: Fifth Third Bank Analysis
**Question:** "Is Fifth Third serving minority communities in its top markets?"

**Process:**
1. Identify top 10 markets where Fifth Third operates
2. Analyze lending in each market
3. Calculate demographic shares
4. Compare to peer banks
5. Generate report showing disparities

**Output:** Excel report with one sheet per market, showing:
- Subject bank's lending by race/ethnicity
- Peer bank averages
- Gap analysis
- Statistical significance

### Case 2: Worst Lenders Identification
**Question:** "Which banks are performing worst in serving minority communities?"

**Process:**
1. Query lending data for multiple banks
2. Calculate demographic shares for each
3. Compare to market demographics
4. Rank by disparity

**Output:** Report identifying worst offenders with specific metrics

### Case 3: Redlining Detection
**Question:** "Is this bank avoiding minority neighborhoods?"

**Process:**
1. Get lending data by census tract
2. Identify minority-majority tracts (50%+, 80%+)
3. Compare loan volume to white tracts
4. Compare to peer banks

**Output:** Evidence of geographic lending disparities

---

## Technical Capabilities Unlocked

### 1. **BigQuery Integration**
- Access to massive HMDA database
- Fast queries (minutes, not hours)
- No need to download entire datasets

### 2. **Automated Processing**
- Demographic classification (race/ethnicity)
- Peer bank identification
- Statistical calculations
- Report formatting

### 3. **Reproducible Analysis**
- Same methodology every time
- Consistent results
- Audit trail via SQL queries
- Version control for scripts

### 4. **Scalability**
- Analyze one bank or many
- One market or many
- One year or multiple years
- Same process scales up

---

## For Someone New to This Work

### What You're Learning:

1. **HMDA Data**: How mortgage lending data is structured
2. **CRA Analysis**: How to measure bank performance
3. **Fair Lending**: Identifying discrimination patterns
4. **Data Analysis**: Using Python, SQL, and Excel together
5. **Advocacy**: How data supports policy work

### Skills You're Building:

- ✅ Data analysis and interpretation
- ✅ Statistical comparison (z-tests, ratios)
- ✅ Report generation
- ✅ Understanding banking regulations
- ✅ Community advocacy support

---

## Bottom Line

**This project turns you from:**
- Manual data wrangler (weeks per analysis)
- Into: Data analyst with automated tools (hours per analysis)

**It enables:**
- Fast, consistent, professional analysis
- Multiple banks, multiple markets, multiple years
- Evidence-based advocacy and enforcement
- Reproducible, auditable work

**The fix we just completed:**
- Allows all of this to work smoothly
- No more path errors blocking your work
- Reliable, consistent execution

---

## Next Steps for You

1. **Learn the workflow**: Run a test analysis (Fifth Third report)
2. **Understand the data**: Review what HMDA contains
3. **Read reports**: Understand what the Excel outputs mean
4. **Practice queries**: Modify SQL queries for different banks
5. **Build expertise**: Use for real advocacy work

---

**You now have a powerful tool for CRA and fair lending analysis!** 🚀

