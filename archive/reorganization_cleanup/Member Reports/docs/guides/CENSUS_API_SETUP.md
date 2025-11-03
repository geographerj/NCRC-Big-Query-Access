# Census API Setup Guide

Using the U.S. Census Bureau API provides accurate, structured demographic data without PDF parsing.

## Benefits

- **Accurate Data**: Direct from Census Bureau, no parsing errors
- **Real-time**: Latest available data
- **Reproducible**: Consistent results every time
- **Complete**: All demographic, income, and housing variables

## Setup

### 1. Install Required Packages

```bash
pip install census us
```

### 2. Get a Free API Key

1. Visit: https://api.census.gov/data/key_signup.html
2. Fill out the form (free, no approval needed)
3. Copy your API key

### 3. Set API Key

**Option A: Environment Variable (Recommended)**
```bash
# Windows PowerShell
$env:CENSUS_API_KEY = "your-api-key-here"

# Windows CMD
set CENSUS_API_KEY=your-api-key-here

# Linux/Mac
export CENSUS_API_KEY=your-api-key-here
```

**Option B: Pass in Code**
```python
from utils.census_api_client import get_census_data_for_county

data = get_census_data_for_county(
    county_fips='031',
    state_fips='24',
    api_key='your-api-key-here'
)
```

## Usage

The Census API integration automatically attempts to fetch data when generating reports. It falls back to JSON files if the API is unavailable.

### County FIPS Codes

Common county FIPS codes:
- **Montgomery County, MD**: state='24', county='031'
- **Hillsborough County, FL** (Tampa): state='12', county='057'

Find FIPS codes at: https://www.census.gov/library/reference/code-lists/ansi.html

### Variables Retrieved

The integration automatically fetches:
- **Current Data** (ACS 5-Year Estimates):
  - **Demographics**: Total population, White %, Black %, Asian %, Hispanic %, Native American %, HoPI %
  - **Income**: Median household income, Poverty rate
  - **Housing**: Homeownership rate

- **Historical Comparison Data** (Decennial Census):
  - **2000 Decennial Census**: Race/ethnicity percentages for long-term trend analysis
  - **2010 Decennial Census**: Race/ethnicity percentages for mid-term trends
  - **2020 Decennial Census**: Race/ethnicity percentages for recent comparison

### Data Source

- **Current Data**: **ACS 5-Year Estimates** (most comprehensive, latest available year by default)
- **Historical Data**: **Decennial Census** (2000, 2010, 2020) for demographic trend analysis

### Demographic Trend Analysis

The system automatically analyzes long-term demographic trends using 2000, 2010, 2020, and current ACS data to provide context for lending patterns:

- **Rising Populations**: Identifies groups with substantial growth (e.g., Hispanic, Asian populations)
- **Stagnant Populations**: Identifies groups with little change over 20+ years (e.g., Black population)
- **Declining Populations**: Identifies groups with significant decreases (e.g., White population)

This historical context helps explain lending trends:
- Expanding Hispanic lending may reflect population growth
- Stagnant Black lending may reflect stable population share
- Demographic shifts provide context for interpreting lending patterns

**Example Output:**
> "Census data shows that Montgomery County's Hispanic and Latino population has grown substantially over the past two decades, increasing from 12.5% in 2000 to 15.8% in 2010, 20.5% in 2020, and 20.0% in recent ACS data. This 7.5 percentage point increase since 2000 reflects the rising influence of Hispanic residents..."

> "In contrast, the Black or African American population has remained relatively stable over this period, comprising 18.2% in 2000, 18.1% in 2010, 18.1% in 2020, and 18.2% in recent data. This long-term stagnation in the Black population share highlights persistent demographic patterns..."

## Integration

The report scripts automatically try Census API first, then fall back to JSON files:

```python
# In create_montgomery_report.py (and others)
def load_community_profile_data():
    # Tries Census API first
    # Falls back to JSON file if API unavailable
    # Returns empty dict if both fail
```

## Troubleshooting

**No data returned?**
- Verify API key is set correctly
- Check FIPS codes are correct
- Ensure `census` package is installed: `pip install census us`

**Package not found?**
```bash
pip install census us
```

**API errors?**
- Check internet connection
- Verify API key is valid
- Census API is free but has rate limits

## Advantages Over PDF Extraction

| Feature | Census API | PDF Extraction |
|---------|-----------|----------------|
| Accuracy | ✅ 100% accurate | ⚠️ Parsing errors possible |
| Speed | ✅ Fast | ⚠️ Slower, requires PDF processing |
| Reliability | ✅ Consistent | ⚠️ Depends on PDF format |
| Data Completeness | ✅ All variables | ⚠️ Limited to what's in PDF |
| Reproducibility | ✅ Same results always | ⚠️ May vary by PDF format |

---

For more information: https://www.census.gov/data/developers/data-sets.html

