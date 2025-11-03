# Peer Matching Methodology

## Summary

**Peer Matching Method:** Volume-based peer matching within each CBSA-year combination

## Detailed Methodology

### Peer Definition
Peers are defined as lenders that have **50% to 200% of the subject bank's origination volume** in the same:
- **CBSA** (Core Based Statistical Area)
- **Year**
- **Loan Type** (Home Purchase only)

### Calculation Process

1. **Calculate Subject Bank Volume**
   - Count total home purchase originations by subject bank for each CBSA-year
   - Filter: Home Purchase loans only (`loan_purpose = '1'`)
   - Standard HMDA filters applied (owner-occupied, site-built, 1-4 units, etc.)

2. **Calculate All Lenders' Volumes**
   - Count total home purchase originations by each lender (LEI) for each CBSA-year
   - Same filters applied as subject bank

3. **Identify Peers**
   - For each CBSA-year combination:
     - Compare each lender's volume to subject bank's volume
     - Include lender if: `subject_vol * 0.5 ≤ lender_vol ≤ subject_vol * 2.0`
     - Exclude subject bank itself from peer group

4. **Aggregate Peer Metrics**
   - Combine all peer lenders' loans for each metric
   - Calculate peer shares as: `(peer_metric_count / peer_total_originations) × 100`

### Key Characteristics

- **Market-Specific**: Each CBSA has its own peer group
- **Year-Specific**: Peer groups can change from year to year
- **Volume Range**: 50%-200% of subject's volume (4:1 ratio range)
- **Subject Excluded**: Subject bank never included in peer calculations
- **Dynamic**: Peer group size varies by market and year

### Example

If Fifth Third Bank has 100 originations in Chicago in 2024:
- **Included as peers**: Lenders with 50-200 originations in Chicago 2024
- **Excluded**: 
  - Lenders with <50 originations (too small)
  - Lenders with >200 originations (too large)
  - Fifth Third Bank itself

### Applied To

- **Fifth Third Bank Reports**: Uses this methodology for all CBSA analyses
- **Comerica Bank Reports**: Uses identical methodology
- **All Metrics**: Same peer group used for:
  - Borrower demographics (Hispanic%, Black%, etc.)
  - Income metrics (LMIB%, LMICT%)
  - Redlining metrics (MMCT%, Black Tract%, etc.)

### SQL Implementation

```sql
peers AS (
    -- Identify peer lenders (50%-200% of subject's volume)
    SELECT DISTINCT
        al.activity_year,
        al.cbsa_code,
        al.lei
    FROM all_lenders al
    INNER JOIN subject_volume sv
        ON al.activity_year = sv.activity_year
        AND al.cbsa_code = sv.cbsa_code
    WHERE al.lender_vol >= sv.subject_vol * 0.5
      AND al.lender_vol <= sv.subject_vol * 2.0
      AND al.lei != '[SUBJECT_LEI]'  -- Exclude subject bank
)
```

### Rationale

This methodology:
- Ensures peers are of similar scale in each market
- Accounts for market-specific competition dynamics
- Allows peer groups to vary by market size and competitiveness
- Provides consistent comparison across all metrics

