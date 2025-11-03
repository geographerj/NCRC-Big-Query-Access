# Small Business (SB) Data Guide

## Overview

Small Business Lending data (Community Reinvestment Act - CRA) tracks small business loans by financial institutions.

## Data Structure

**Dataset**: `hdma1-242116.sb`

**Tables**:
- `disclosure` - Small business loan data by geography and lender
- `lenders` - Lender information

**Join Key**: `disclosure.respondent_id` = `lenders.sb_resid`

## Key Metrics

### 1. SB Loans (Total Count)
**Formula**: `num_under_100k + num_100k_250k + num_250k_1m`

Total count of small business loans across all size categories.

### 2. LMICT (Low-to-Moderate Income Census Tract)
**Formula**: Count where `income_group_total IN (101, 102, 1, 2, 3, 4, 5, 6, 7, 8)`

Loans made in census tracts with low-to-moderate income populations.

**Income Group Codes**:
- `101` = Low-income tract
- `102` = Moderate-income tract  
- `1-8` = Low-to-moderate income categories

### 3. Avg SB LMICT Loan Amount
**Formula**: `SUM(amount_of_LMICT_loans) / COUNT(num_LMICT_loans)`

Average loan amount for small business loans in LMICT tracts.

**Calculation**:
- Filter loans where `income_group_total IN (101, 102, 1, 2, 3, 4, 5, 6, 7, 8)`
- Sum: `amt_under_100k + amt_100k_250k + amt_250k_1m` (for LMICT loans only)
- Count: `num_under_100k + num_100k_250k + num_250k_1m` (for LMICT loans only)
- Average = Sum / Count

### 4. Loans Rev Under $1m
**Formula**: `numsbrev_under_1m`

Count of small business loans with revenue under $1 million.

### 5. Avg Loan Amt for RUM SB
**Formula**: `amtsbrev_under_1m / numsbrev_under_1m`

Average loan amount for small business loans to businesses with revenue under $1 million.

**Note**: If `numsbrev_under_1m = 0`, this metric cannot be calculated.

## Disclosure Table Columns

| Column | Description |
|--------|-------------|
| `respondent_id` | Unique lender identifier (joins to `lenders.sb_resid`) |
| `geoid5` | State + County code (5 digits) |
| `year` | Reporting year |
| `msamd` | Metropolitan Statistical Area / Metropolitan Division (CBSA code) |
| `num_under_100k` | Count of loans <$100k |
| `amt_under_100k` | Total amount of loans <$100k |
| `num_100k_250k` | Count of loans $100k-$250k |
| `amt_100k_250k` | Total amount of loans $100k-$250k |
| `num_250k_1m` | Count of loans $250k-$1m |
| `amt_250k_1m` | Total amount of loans $250k-$1m |
| `numsbrev_under_1m` | Count of loans to businesses with revenue <$1m |
| `amtsbrev_under_1m` | Total amount of loans to businesses with revenue <$1m |
| `income_group_total` | Income group code (101=Low, 102=Moderate, 1-8=LMI categories) |
| `cbsa` | CBSA name |
| `county`, `state` | Geographic identifiers |

## Lenders Table Columns

| Column | Description |
|--------|-------------|
| `sb_resid` | Respondent ID (joins to `disclosure.respondent_id`) |
| `sb_rssd` | RSSD ID (same as branch/HMDA data!) |
| `sb_lender` | Lender name |
| `sb_year` | Year |
| `sb_assets` | Bank assets |

## Fifth Third & Comerica Identifiers

### Fifth Third Bank
- `respondent_id`: `0000025190` or `0000723112`
- `rssd`: `723112`
- Data available: Multiple years

### Comerica Bank
- `respondent_id`: `0000060143`
- `rssd`: `60143`
- Data available: 17 years (2007-2023)

## Example Queries

### Get SB Loans by CBSA
```sql
SELECT 
    msamd as cbsa_code,
    cbsa as cbsa_name,
    year,
    SUM(num_under_100k + num_100k_250k + num_250k_1m) as total_sb_loans,
    SUM(amt_under_100k + amt_100k_250k + amt_250k_1m) as total_sb_amount
FROM `hdma1-242116.sb.disclosure`
WHERE respondent_id = '0000025190'  -- Fifth Third
  AND year = 2023
GROUP BY msamd, cbsa, year
ORDER BY total_sb_loans DESC
```

### Get LMICT Loans
```sql
SELECT 
    msamd as cbsa_code,
    year,
    SUM(CASE WHEN income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
        THEN (num_under_100k + num_100k_250k + num_250k_1m) ELSE 0 END) as lmict_loan_count,
    SUM(CASE WHEN income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
        THEN (amt_under_100k + amt_100k_250k + amt_250k_1m) ELSE 0 END) as lmict_loan_amount
FROM `hdma1-242116.sb.disclosure`
WHERE respondent_id = '0000060143'  -- Comerica
  AND year = 2023
GROUP BY msamd, year
```

