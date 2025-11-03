# Community Profile Report Integration

## Overview

Community Profile reports provide valuable demographic and population change data over time that should be referenced in member reports to provide context for lending patterns.

## Community Profile File Location

Community Profile reports are stored in:
- `supporting_files/Community Profile of [Community Name].pdf`

Example:
- `supporting_files/Community Profile of Out-Stickey.pdf`

## Key Data to Extract from Community Profiles

### 1. Population Demographics Over Time

Extract and note:
- **Total population** trends (increasing/decreasing/stable)
- **Racial/ethnic composition** changes:
  - Black/African American percentage
  - Hispanic/Latino percentage
  - Asian percentage
  - White percentage
  - Other racial groups
- **Time period** covered (typically 2010-2020 or similar Census periods)

### 2. Income Trends

- **Median household income** changes
- **Poverty rates** over time
- **Income distribution** shifts
- **Cost of living** changes (if available)

### 3. Housing Market Data

- **Homeownership rates** by race/ethnicity
- **Housing values** trends
- **Rental costs** trends
- **Housing stock** changes

### 4. Geographic Context

- **Neighborhood boundaries** (if defined)
- **Census tract identifiers**
- **Adjacent communities** (for comparison)
- **Historical context** (redlining history, disinvestment patterns)

## How to Use in Member Reports

### In Key Findings Section

Reference community profile data to:
- **Provide demographic context**: "The community profile shows that [Community] has experienced [demographic change] over the past decade..."
- **Explain lending patterns**: "Given that [Community]'s population is [X]% [demographic], the lending patterns show..."
- **Highlight disparities**: "While [Community] is [demographic description], lending to [demographic] borrowers represents only [X]%..."

### In Methodology Section

Document:
- "Community demographic data from [Source] covering [years]"
- "Population characteristics were analyzed using [Community Profile Report Name]"

### In Recommendations Section

Use community profile data to:
- **Recommend targeted interventions** based on demographic needs
- **Suggest community-specific solutions**
- **Highlight population changes** that require banking response

## Formatting Community Profile Data in Reports

### Population Percentages
- Format as: "The community profile shows that [Community] is [X.X]% [demographic]..."
- Use percentage format: `##.#` (e.g., 45.2%)

### Population Changes
- "Between [Year1] and [Year2], [Community]'s [demographic] population [increased/decreased] from [X.X]% to [X.X]%"
- Cite specific numbers only for key trends

### Income Data
- "Median household income in [Community] is $[amount], [above/below/at] the [comparison] level"
- Format currency as: $#,###,###

## Examples of Integration

### Example 1: Demographic Context

**Without Community Profile:**
"The lender made [X] loans to Black borrowers in this market."

**With Community Profile:**
"While the community profile shows that [Community] is 52.3% Black, lending to Black borrowers represents only 18.5% of the lender's originations—a gap of -33.8 percentage points compared to the community's demographic composition."

### Example 2: Income Context

**Without Community Profile:**
"The lender made [X] loans in low-to-moderate income tracts."

**With Community Profile:**
"According to the community profile, median household income in [Community] declined from $45,200 in 2010 to $42,800 in 2020. Despite this increase in lower-income households, lending in Low-to-Moderate Income Census Tracts (LMICT) represents only 28.3% of originations, compared to 35.2% in peer lending."

### Example 3: Historical Context

**With Community Profile:**
"The community profile documents [Community]'s history of redlining and disinvestment, which aligns with current patterns showing underperformance in majority-minority census tracts."

## Data Sources in Community Profiles

Common sources cited in community profile reports:
- **U.S. Census Bureau** (Decennial Census, American Community Survey)
- **Local planning departments**
- **Community development organizations**
- **Academic research**

## Citation Format

When referencing community profile data:

"In the [Community Name] Community Profile ([year]), the community's demographic composition shows..."

Or:

"According to the Community Profile of [Community Name] ([year]), [specific data point]..."

## Checklist for Using Community Profiles

- [ ] Extract key demographic percentages (by race/ethnicity)
- [ ] Note population trends (increasing/decreasing)
- [ ] Identify income trends (median income, poverty rates)
- [ ] Note housing market context (homeownership, values)
- [ ] Review historical context (redlining, disinvestment)
- [ ] Identify time period covered
- [ ] Cite data source appropriately
- [ ] Use data to explain lending patterns
- [ ] Format percentages as `##.#` format
- [ ] Format currency as `$,###,###`
- [ ] Only cite key data points (let tables show detailed data)

## Storing Extracted Data

Consider creating structured data files when processing community profiles:
- `data/processed/[Community]_demographics.csv` - Extracted demographic data
- `data/processed/[Community]_income.csv` - Extracted income data
- `data/processed/[Community]_housing.csv` - Extracted housing data

This allows for consistent referencing across multiple reports.

## Integration with Report Generator

The report generator automatically:
1. **Prioritizes Census API** over PDF extraction:
   - Fetches current ACS data (demographics, income, housing)
   - Fetches 2000, 2010, 2020 Decennial Census data for trend analysis
   - Falls back to JSON file if API unavailable
   - Falls back to PDF extraction if both fail

2. **Analyzes demographic trends**:
   - Compares 2000 → 2010 → 2020 → current data
   - Identifies rising populations (Hispanic, Asian)
   - Identifies stagnant populations (Black)
   - Identifies declining populations (White)

3. **Includes trend context** in market patterns narrative:
   - Provides historical context at start of analysis
   - Explains lending patterns in context of demographic changes
   - Highlights long-term trends (e.g., "rising influence of Hispanic residents")

4. **References appropriately**:
   - Cites Census Bureau data when using API
   - Cites Community Profile when using extracted data
   - Includes methodology note about data sources

5. **Uses data for gap analysis**:
   - Compares lending shares to population percentages
   - Highlights disparities with demographic context
   - Explains patterns using population trends

---

*Last Updated: 2025-01-15*

