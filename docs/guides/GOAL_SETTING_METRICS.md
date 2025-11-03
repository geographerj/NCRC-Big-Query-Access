# Local Market Analysis Metrics

## Metrics to Include in Mortgage Data Sheets

Each metric should be calculated and displayed for:
1. Subject bank (PNC or FirstBank)
2. Peer lenders (aggregated)

### Metrics List

1. **Loans** - Number of originations or applications (format to be confirmed: count or dollar volume)

2. **LMICT%** - Low/Moderate Income Census Tract percentage
   - Format: `##.##%`

3. **LMIB%** - Low/Moderate Income Borrower percentage
   - Format: `##.##%`

4. **LMIB$** - Low/Moderate Income Borrower lending in Dollars
   - Format: `$#,###`

5. **MMCT%** - Majority-Minority Census Tract percentage

6. **MINB%** - Minority Borrower percentage (combined minority)

7. **Asian%** - Asian borrower percentage

8. **Black%** - Black borrower percentage

9. **Native American%** - Native American borrower percentage

10. **HoPI%** - Hawaiian or Pacific Islander borrower percentage

11. **Hispanic%** - Hispanic borrower percentage

## Geographic Filtering

- **Only include counties** listed in the Assessment Areas sheet
- Do NOT include all counties in a CBSA - only the specific counties that are part of the bank's assessment area
- Filter HMDA data using county codes (GEOIDs) from the Assessment Areas sheet

## Peer Selection

- Use **50% to 200% volume rule** (same as worst lenders analysis)
- Peers must have 50%-200% of subject bank's origination volume in the same:
  - CBSA
  - Year
  - Assessment area counties (filtered)

## Data Source

- Data comes from the "Local Market Analysis (LMA)" request
- Years: To be specified by user when requesting analysis
- HMDA filters: As specified in the merger research ticket


