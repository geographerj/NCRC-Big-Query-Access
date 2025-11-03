# Demographic Trend Analysis

## Overview

The report generation system now includes automatic analysis of long-term demographic trends using U.S. Census Bureau data from multiple time periods. This provides essential context for interpreting mortgage lending patterns.

## Data Sources

The system fetches demographic data from:

1. **2000 Decennial Census** - Baseline for long-term trends
2. **2010 Decennial Census** - Mid-term comparison point
3. **2020 Decennial Census** - Recent comparison point
4. **Current ACS 5-Year Estimates** - Most recent comprehensive data

## Trend Analysis

The `analyze_demographic_trends()` function automatically identifies:

### Rising Populations

Groups with substantial growth (typically >5 percentage points since 2000):
- **Hispanic/Latino**: Rising influence in community demographics
- **Asian**: Expanding presence in many communities

**Example Context Generated:**
> "Census data shows that Montgomery County's Hispanic and Latino population has grown substantially over the past two decades, increasing from 12.5% in 2000 to 15.8% in 2010, 20.5% in 2020, and 20.0% in recent ACS data. This 7.5 percentage point increase since 2000 reflects the rising influence of Hispanic residents in the county's demographic composition."

### Stagnant Populations

Groups with little change over 20+ years (typically <3 percentage points change):
- **Black/African American**: Long-term stagnation in population share

**Example Context Generated:**
> "In contrast, the Black or African American population has remained relatively stable over this period, comprising 18.2% in 2000, 18.1% in 2010, 18.1% in 2020, and 18.2% in recent data. This long-term stagnation in the Black population share highlights persistent demographic patterns that may influence lending outcomes."

### Declining Populations

Groups with significant decreases (typically >5 percentage points since 2000):
- **White**: Declining share in many diverse communities

## Integration in Reports

### Market Patterns Narrative

The demographic trend analysis appears at the **beginning** of the Market Patterns analysis section, before discussing lending patterns. This provides:

1. **Historical Context**: Explains population changes over 20+ years
2. **Lending Pattern Context**: Helps explain why lending may be expanding/contracting for different groups
3. **Disparity Context**: Highlights when lending patterns don't match demographic trends

### How It Works

```python
# In generate_market_patterns_narrative()
demographic_trends = analyze_demographic_trends(community_data)

# Automatically generates trend paragraphs if data available
if demographic_trends.get('hispanic_trend'):
    # Adds paragraph about rising Hispanic population
if demographic_trends.get('black_trend'):
    # Adds paragraph about stagnant Black population
if demographic_trends.get('asian_trend'):
    # Adds paragraph about rising Asian population
```

## Benefits

### For Report Readers

- **Context**: Understand why lending patterns may be changing
- **Historical Perspective**: See long-term demographic shifts
- **Fair Lending Analysis**: Identify when lending doesn't match population trends

### For Analysis

- **Explainable Trends**: Connect lending changes to population changes
- **Disparity Detection**: Identify when lending gaps exist despite population stability
- **Policy Context**: Provide data for community reinvestment advocacy

## Data Requirements

### Census API (Recommended)

Set `CENSUS_API_KEY` environment variable:
```bash
set CENSUS_API_KEY=your-api-key-here
```

The system automatically fetches:
- 2000, 2010, 2020 Decennial Census data
- Current ACS 5-Year Estimates

### Fallback to JSON

If Census API is unavailable, the system uses:
- `data/processed/[location]_community_profile_data.json`

**Note**: JSON files typically don't include historical comparison years (2000, 2010, 2020), so trend analysis may be limited.

## Example Use Cases

### Case 1: Expanding Hispanic Lending

**Demographic Trend**: Hispanic population increased from 12% (2000) to 20% (current)

**Lending Pattern**: Hispanic lending share increased from 8% (2018) to 15% (2024)

**Narrative Context**: 
> "The expansion in lending to Hispanic borrowers reflects Montgomery County's growing Hispanic population, which has increased by 8 percentage points since 2000..."

### Case 2: Stagnant Black Lending

**Demographic Trend**: Black population stable at ~18% (2000-current)

**Lending Pattern**: Black lending share stable at ~12% (2018-2024)

**Narrative Context**:
> "Despite the long-term stability of Montgomery County's Black population at approximately 18%, lending to Black borrowers has remained relatively stagnant, raising questions about equitable access to homeownership opportunities..."

### Case 3: Declining White Population, Stable White Lending

**Demographic Trend**: White population declined from 60% (2000) to 45% (current)

**Lending Pattern**: White lending share remains at 55% (2018-2024)

**Narrative Context**:
> "While Montgomery County's White population has declined by 15 percentage points since 2000, White borrowers continue to receive the majority of mortgage loans, indicating a potential gap between demographic change and lending patterns..."

## Technical Details

### Function: `analyze_demographic_trends()`

**Location**: `scripts/create_montgomery_report.py`

**Input**: `community_data` dictionary with:
- `demographics` - Current ACS data
- `comparison_years['2000']['demographics']` - 2000 Census data
- `comparison_years['2010']['demographics']` - 2010 Census data
- `comparison_years['2020']['demographics']` - 2020 Census data

**Output**: Dictionary with trend analysis for each demographic group:
```python
{
    'hispanic_trend': {
        'direction': 'rising',
        'change': 7.5,  # percentage points
        '2000': 12.5,
        '2010': 15.8,
        '2020': 20.5,
        'current': 20.0
    },
    'black_trend': {
        'direction': 'stagnant',
        'change': 0.0,
        '2000': 18.2,
        '2010': 18.1,
        '2020': 18.1,
        'current': 18.2
    },
    # ... etc
}
```

### Thresholds

- **Rising**: Change >5 percentage points since 2000
- **Stagnant**: Change <3 percentage points since 2000
- **Declining**: Change <-5 percentage points since 2000

These thresholds can be adjusted in `analyze_demographic_trends()` function.

## Citation Format

When demographic trend data is used, the report automatically cites:

- "Census data shows..." (when using Census API)
- "According to U.S. Census Bureau American Community Survey data..." (for current data)
- "According to [Year] Decennial Census..." (for historical data)

## Best Practices

1. **Always use Census API** when available (most accurate, includes all years)
2. **Include trend analysis** in market patterns section (provides essential context)
3. **Connect trends to lending** (explain patterns using demographic changes)
4. **Highlight disparities** (when lending doesn't match population trends)
5. **Cite sources** (Census Bureau vs Community Profile vs extracted data)

---

*Last Updated: 2025-01-XX*

