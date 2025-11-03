# Assessment Areas Extraction Status

## Summary

### ✅ Cadence Bank - SUCCESSFULLY EXTRACTED
- **142 counties** extracted from PDF
- **48 unique CBSAs** across 9 states:
  - Alabama, Arkansas, Florida, Georgia, Louisiana, Mississippi, Missouri, Tennessee, Texas
- Data has been added to Excel ticket

### ⚠️ Huntington National Bank - NEEDS MANUAL ENTRY
- **0 counties** extracted automatically
- The CRA PE document (7745.pdf) is 352 pages
- Extraction found city/region names rather than county names
- Manual entry required OR need better source document

## Current Ticket Status

**File**: `Huntington+Cadence merger research ticket.xlsx`

**Assessment Areas Sheet**:
- ✅ Headers: Bank Name, CBSA Name, CBSA Code, State Name, County Name, County Code (GEOID)
- ✅ **142 Cadence Bank entries** (complete)
- ⚠️ **0 Huntington entries** (needs manual entry)

## Next Steps for Huntington

### Option 1: Manual Entry
1. Open the CRA PE document (7745.pdf)
2. Find the assessment area summary/listing (usually in early pages)
3. Manually enter counties into the Assessment Areas sheet in Excel
4. Format: Bank Name = "The Huntington National Bank", plus CBSA, State, County info

### Option 2: Alternative Source
- Check if Huntington has a separate assessment area listing document
- May be more structured than the CRA PE

### Option 3: Query BigQuery
- Could query branch data for Huntington (RSSD: 12311) to find counties where they have branches
- Then cross-reference with assessment areas

## Sample Cadence Counties Extracted

Alabama:
- Lee County (CBSA 12220 - Auburn-Opelika)
- Jefferson, Blount, St. Clair, Shelby (CBSA 13820 - Birmingham)
- Baldwin County (CBSA 19300 - Daphne-Fairhope-Foley)
- And many more...

[Full list available in Excel ticket]

## Verification

To verify the extraction:
1. Open `Huntington+Cadence merger research ticket.xlsx`
2. Go to "Assessment Areas" sheet
3. Filter by "Cadence Bank" to see all 142 entries
4. Review for accuracy

