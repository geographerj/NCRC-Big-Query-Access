# GLEIF Integration for Lender Information

## Overview

The Global Legal Entity Identifier (LEI) Index (GLEIF) provides authoritative information about legal entities. The report generation system uses GLEIF as the primary source for accurate lender names and headquarters locations.

## What is GLEIF?

GLEIF is the official registry maintained by the Global LEI Foundation, providing:
- **Official legal entity names** (correct spelling, proper case)
- **Headquarters addresses** (city, state, country)
- **Registration information** (jurisdiction, status, dates)
- **Direct LEI record URLs** for verification

## Benefits

### Accurate Lender Names

- **Corrects BigQuery errors**: BigQuery data may have formatting issues (e.g., "1ST HOME" instead of "First Home Mortgage")
- **Proper capitalization**: Uses official Title Case names from GLEIF
- **Entity suffix removal**: Automatically removes ", LLC", ", INC.", ", National Association", etc.
- **Ordinal fixing**: Corrects "1 ST" → "1ST" spacing issues

### Authoritative Data

- **Official source**: GLEIF is the recognized global standard for legal entity identification
- **Verified information**: All data is validated by LEI issuing organizations
- **Up-to-date**: Regular updates ensure current information

### Enhanced Reports

- **Professional appearance**: Correct lender names throughout
- **Hyperlinks**: LEI record URLs for verification
- **Headquarters data**: Accurate location information

## How It Works

### 1. LEI Lookup

During report generation, the system:

```python
# For each lender in top 10
for lei in top_10_leis:
    gleif_info = lookup_lender_info_by_lei(lei)
    # Returns: name, headquarters, lei_url, etc.
```

### 2. Name Formatting

The `format_lender_name()` function:
- Preserves GLEIF capitalization (Title Case)
- Removes entity suffixes (", LLC", ", INC.", ", National Association", "Corporation")
- Fixes spacing issues
- Converts all-caps to Title Case if needed

### 3. Integration

GLEIF data is used:
- **Before table creation** - Ensures correct names in all tables
- **In narratives** - Lender names use official GLEIF names
- **In hyperlinks** - LEI URLs link to GLEIF records

## API Endpoint

```
GET https://api.gleif.org/api/v1/lei-records/{LEI}
```

### Response Structure

```json
{
  "data": {
    "attributes": {
      "entity": {
        "legalName": {
          "name": "First Heritage Mortgage, LLC"
        },
        "headquartersAddress": {
          "city": "Fairfax",
          "region": "US-VA",
          "country": "US",
          "addressLines": ["3201 Jermantown Road", "Suite 800"],
          "postalCode": "22030"
        }
      }
    }
  }
}
```

### Function: `lookup_lender_info_by_lei()`

**Location**: `scripts/create_montgomery_report.py`

**Returns**:
```python
{
    'name': 'First Heritage Mortgage, LLC',
    'headquarters': 'Fairfax, Virginia',  # Formatted as "City, State"
    'headquarters_address': '3201 Jermantown Road, Suite 800, Fairfax, Virginia, 22030',
    'country': 'US',
    'lei_url': 'https://search.gleif.org/#/record/549300EM8ID8J7F8OM55'
}
```

## Name Formatting Examples

| BigQuery Name | GLEIF Name | Formatted for Report |
|---------------|------------|---------------------|
| "1ST HOME" | "FIRST HOME MORTGAGE CORPORATION" | "First Home Mortgage" |
| "1 ST HOME" | "First Home Mortgage, LLC" | "First Home Mortgage" |
| "JPMORGAN CHASE BANK" | "JPMorgan Chase Bank, National Association" | "JPMorgan Chase Bank" |
| "TOWNE BANK" | "TowneBank" | "TowneBank" |
| "1ST HERITAGE MORTGAGE" | "First Heritage Mortgage, LLC" | "First Heritage Mortgage" |

## State Code Conversion

GLEIF returns region codes like "US-VA". The system automatically converts to full state names:

```python
us_states = {
    'VA': 'Virginia',
    'MD': 'Maryland',
    'FL': 'Florida',
    # ... all 50 states + DC
}
```

## Integration Priority

The system uses information in this order (highest priority first):

1. **GLEIF** - Official names, headquarters
2. **BigQuery lenders18 table** - Fallback if GLEIF unavailable
3. **Web search** - Additional background (history, mergers, violations)
4. **Manual JSON** - `data/lender_background_info.json` (for curated data)

## Example Workflow

```python
# 1. Look up LEI in GLEIF
gleif_info = lookup_lender_info_by_lei('549300EM8ID8J7F8OM55')
# Returns: {'name': 'First Heritage Mortgage, LLC', 'headquarters': 'Fairfax, Virginia', ...}

# 2. Format name
official_name = format_lender_name(gleif_info['name'])
# Returns: 'First Heritage Mortgage'

# 3. Store for use in tables and narratives
lei_to_official_name[lei] = official_name
lei_to_gleif_info[lei] = gleif_info

# 4. Use in report generation
lender_narratives[official_name] = {
    'headquarters': gleif_info['headquarters'],
    'lei_url': gleif_info['lei_url'],
    # ... other background info
}
```

## Entity Suffixes Removed

The system automatically removes:
- ", LLC" / ", L.L.C."
- ", INC." / ", INC" / ", INCORPORATED"
- ", CORP." / ", CORPORATION"
- ", NATIONAL ASSOCIATION" / ", NA"
- ", LP" / ", L.P."
- ", LTD." / ", LIMITED"
- ", PC" / ", P.C."

**Note**: Suffixes are only removed if they appear at the end of the name.

## Troubleshooting

### GLEIF API Not Responding

- **Check internet connection**
- **Verify LEI format** (20 characters, alphanumeric)
- **Rate limits**: GLEIF API is free but may have rate limits
- **Fallback**: System uses BigQuery names if GLEIF unavailable

### Incorrect Names Still Appearing

- **Verify GLEIF lookup is running**: Check console output for "Looking up official lender information from GLEIF..."
- **Check LEI numbers**: Ensure BigQuery has correct LEI values
- **Manual override**: Update `data/lender_background_info.json` if needed

### Headquarters Not Found

- **GLEIF data**: Some entities may not have headquarters address in GLEIF
- **Fallback**: System uses web search or manual JSON data
- **Manual entry**: Add to `data/lender_background_info.json`

## Best Practices

1. **Always use GLEIF first** - Most authoritative source
2. **Verify LEI numbers** - Ensure BigQuery LEI values are correct
3. **Check formatted names** - Review console output to verify name formatting
4. **Manual corrections** - If GLEIF name is wrong, manually update `lender_background_info.json`
5. **Cite sources** - GLEIF data is official, cite appropriately in reports

## Related Documentation

- [Lender Background Search](LENDER_BACKGROUND_SEARCH.md) - Complete background search process
- [Census API Setup](CENSUS_API_SETUP.md) - For demographic data
- [Community Profile Integration](COMMUNITY_PROFILE_INTEGRATION.md) - For geographic context

## GLEIF Resources

- **GLEIF Website**: https://www.gleif.org/
- **GLEIF Search Portal**: https://search.gleif.org/
- **GLEIF API Documentation**: https://www.gleif.org/en/meta/lei-api/

---

*Last Updated: 2025-01-XX*

