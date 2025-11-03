# Manual Community Profile Data Entry Guide

Since automated PDF extraction may miss data, you can manually add community profile information to enhance the market analysis.

## Location of Data File

The community profile data is stored in:
- `Member Reports/data/processed/tampa_community_profile_data.json`

Or more generally:
- `Member Reports/data/processed/[community_name]_community_profile_data.json`

## Data Structure

Edit the JSON file to include the following information from the community profile PDF:

```json
{
  "community_name": "Tampa, FL (City)",
  "profile_year": "2020",
  "demographics": {
    "total_population": 384959,
    "black_percentage": 26.3,
    "hispanic_percentage": 29.5,
    "white_percentage": 56.9,
    "asian_percentage": 4.2,
    "native_american_percentage": 0.3,
    "hawaiian_pacific_islander_percentage": 0.1
  },
  "income": {
    "median_household_income": 52438,
    "mean_household_income": 69852,
    "poverty_rate": 21.3,
    "per_capita_income": 31363
  },
  "housing": {
    "homeownership_rate": 52.1,
    "median_home_value": 235000,
    "median_gross_rent": 1150
  },
  "trends": {
    "population_change_percent": 12.5,
    "population_trend": "increasing",
    "demographic_shifts": [
      "Growing Hispanic population",
      "Declining White population share",
      "Stable Black population"
    ]
  }
}
```

## How This Data Enhances Reports

### 1. Introduction Section
- **Population demographics**: "According to the Community Profile of Tampa, FL (City, 2020), Tampa city's population is composed of 29.5% Hispanic or Latino, 26.3% Black or African American, 56.9% White..."
- **Income context**: "The community profile reports a median household income of $52,438..."
- **Population trends**: References to demographic shifts over time

### 2. Market Patterns Analysis
- **Demographic comparisons**: Compares lending percentages to community demographics
  - Example: "While the community profile shows Tampa is 26.3% Black, lending to Black borrowers represents only 7.0% of originations—a gap of -19.3 percentage points below the community's demographic composition."
- **Income context for LMIB/LMICT**: 
  - Uses poverty rate to contextualize lending to low-income borrowers
  - Uses median income to explain need for credit access
- **Geographic patterns**: References poverty rates and income data when discussing LMICT lending

### 3. Key Findings
- Can reference population trends to explain lending patterns
- Can compare lending to demographics to identify gaps

## Finding Data in Community Profile PDF

### Demographics Section
Look for tables or text showing:
- Total population
- Race/ethnicity percentages (Black, Hispanic, White, Asian, etc.)
- Population changes over time (2010-2020, etc.)

### Income Section
Look for:
- Median household income (usually in dollars)
- Poverty rate (percentage)
- Income distribution data
- Changes in income over time

### Housing Section
Look for:
- Homeownership rates (overall and by race/ethnicity if available)
- Median home values
- Rental costs
- Housing stock information

### Trends Section
Look for information about:
- Population growth/decline over time periods
- Demographic composition changes
- Income trends
- Housing market trends

## Example: Finding Data

If the PDF shows:
```
Population Demographics (2020 Census)
Total Population: 384,959
Black or African American: 26.3%
Hispanic or Latino: 29.5%
White (non-Hispanic): 56.9%
Asian: 4.2%

Income (2020)
Median Household Income: $52,438
Poverty Rate: 21.3%
```

You would enter:
```json
"demographics": {
  "total_population": 384959,
  "black_percentage": 26.3,
  "hispanic_percentage": 29.5,
  "white_percentage": 56.9,
  "asian_percentage": 4.2
},
"income": {
  "median_household_income": 52438,
  "poverty_rate": 21.3
}
```

## After Adding Data

1. Save the JSON file
2. Regenerate the report: `python scripts/create_tampa_report.py`
3. The report will automatically incorporate the community profile data into:
   - Introduction section
   - Market patterns lead-in
   - Market patterns analysis
   - Demographic comparisons throughout

## Tips

- **Be consistent**: Use the same year as referenced in the community profile title
- **Check units**: Income should be in dollars (no commas), percentages as decimals (26.3, not 0.263)
- **Population totals**: Make sure population numbers match the geographic area (city boundaries, not metro area)
- **Trends**: Note any significant demographic shifts mentioned in the profile


