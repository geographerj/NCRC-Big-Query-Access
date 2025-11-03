# Lender Background Information Search

## Overview

The member report generation process includes functionality to gather comprehensive background information on each of the top 10 lenders, including:

1. **Official lender name** - From GLEIF (Global LEI Index) using LEI lookup
2. **Headquarters location** - From GLEIF (official source) or web search
3. **LEI record URL** - Direct link to GLEIF record for verification
4. **Company website** - For hyperlinks in reports
5. **Company history** - Founding date, key milestones
6. **Mergers and acquisitions** - Recent merger activity
7. **Community Benefits Agreements (CBAs)** - NCRC CBA status check
8. **Fair lending violations** - CFPB, DOJ settlements or enforcement actions
9. **Redlining complaints** - Redlining allegations or enforcement actions

## GLEIF Integration (Primary Source)

### Overview

The system now uses the **Global Legal Entity Identifier (LEI) Index (GLEIF)** as the authoritative source for lender information. GLEIF is the official registry maintained by the Global LEI Foundation and provides:

- **Official legal entity names** (correct spelling, proper case)
- **Headquarters addresses** (city, state, country)
- **LEI record URLs** (direct links for verification)

### How It Works

1. **Automatic LEI Lookup**: During report generation, the system looks up each lender's LEI in GLEIF's REST API
2. **Name Correction**: Official names from GLEIF replace BigQuery names (which may have errors)
3. **Name Formatting**: 
   - Preserves GLEIF capitalization (proper case)
   - Removes entity suffixes (", LLC", ", INC.", ", National Association", etc.)
   - Fixes ordinal spacing issues ("1 ST" → "1ST")
4. **Headquarters Extraction**: Pulls headquarters city/state from GLEIF data
5. **LEI URL Generation**: Creates clickable links to GLEIF records

### GLEIF API Endpoint

```
https://api.gleif.org/api/v1/lei-records/{LEI}
```

The API returns JSON with:
- `entity.legalName.name` - Official legal name
- `entity.headquartersAddress.city` - Headquarters city
- `entity.headquartersAddress.region` - State (converted to full state name)
- Direct URL: `https://search.gleif.org/#/record/{LEI}`

### Example

For LEI `549300EM8ID8J7F8OM55`:
- **BigQuery name**: "1ST HERITAGE MORTGAGE" (incorrect)
- **GLEIF name**: "First Heritage Mortgage, LLC" (official)
- **Formatted for report**: "First Heritage Mortgage" (suffixes removed, proper case)
- **Headquarters**: "Fairfax, Virginia" (from GLEIF)

## Web Search Integration (Secondary Source)

### During Report Generation

When `create_montgomery_report.py` (or other report scripts) runs, it automatically attempts to gather background information for each lender in the top 10. The system:

1. **First**: Looks up official information from GLEIF (name, headquarters)
2. **Then**: Attempts to load from `data/lender_background_info.json` (manually curated)
3. **Finally**: Falls back to web search if needed (for history, mergers, violations)

## How It Works

### During Report Generation

When `create_tampa_report.py` runs, it automatically attempts to gather background information for each lender in the top 10. The function `search_lender_background_web()` prepares search queries for each lender.

### Web Search Integration (Fallback)

When GLEIF doesn't provide complete information, web searches are performed using the AI assistant's `web_search` tool. For each lender, the following searches are executed:

1. **Headquarters**: `"{lender_name} headquarters location city"` (only if not in GLEIF)
2. **History**: `"{lender_name} history founding year"`
3. **Mergers**: `"{lender_name} mergers acquisitions recent"`
4. **Website**: `"{lender_name} official website"`
5. **Violations**: `"{lender_name} fair lending violations CFPB DOJ settlement"`
6. **Redlining**: `"{lender_name} redlining complaint CFPB DOJ enforcement"`
7. **CBA**: `"{lender_name} NCRC Community Benefits Agreement CBA"`

### Information Extraction

Search results are parsed using utility functions in `utils/lender_background_search.py`:

- `extract_location_from_search()` - Finds headquarters city/state
- `extract_history_from_search()` - Finds founding dates
- `extract_mergers_from_search()` - Identifies merger activity
- `extract_violations_from_search()` - Finds fair lending violations
- `extract_redlining_from_search()` - Identifies redlining complaints

### Integration into Reports

The background information is integrated into:

1. **Lender Names**: Official names from GLEIF (properly formatted, entity suffixes removed)
2. **Lender Lead-in**: Headquarters location (from GLEIF) and CBA status in the 2-sentence lead-in
3. **Hyperlinks**: 
   - Lender names link to official websites (when available)
   - LEI URLs link to GLEIF records
   - CBA mentions link to https://ncrc.org/cba/
4. **Background Storage**: All background info is stored in `lender_narratives[][background_info]` for potential future use

### Lender Name Formatting Rules

The system automatically:
- Uses GLEIF official names as primary source
- Removes entity suffixes: ", LLC", ", INC.", ", National Association", "Corporation", etc.
- Preserves proper capitalization (GLEIF uses Title Case)
- Converts all-caps names to Title Case if needed
- Fixes ordinal spacing ("1 ST" → "1ST")

**Examples:**
- GLEIF: "First Heritage Mortgage, LLC" → Report: "First Heritage Mortgage"
- GLEIF: "JPMorgan Chase Bank, National Association" → Report: "JPMorgan Chase Bank"
- BigQuery: "1ST HOME" → GLEIF: "FIRST HOME MORTGAGE CORPORATION" → Report: "First Home Mortgage"

## Manual Enhancement

If you want to manually enhance background information for specific lenders:

1. Run the report generation script
2. For each lender in the top 10, perform web searches using the queries above
3. Update the `background_info` dictionary for that lender
4. Re-run the narrative generation portion

## Example Search Queries

For **JPMorgan Chase Bank**:
- `"JPMorgan Chase Bank headquarters location city"`
- `"JPMorgan Chase Bank history founding year"`
- `"JPMorgan Chase Bank mergers acquisitions recent"`
- `"JPMorgan Chase Bank fair lending violations CFPB DOJ settlement"`
- `"JPMorgan Chase Bank redlining complaint CFPB DOJ enforcement"`

## Future Enhancements

Potential improvements:
- Cache search results to avoid re-searching for the same lenders
- Add more specific regulatory agency searches (FDIC, OCC, Federal Reserve)
- Include information about market presence and branch networks
- Add information about community reinvestment ratings


