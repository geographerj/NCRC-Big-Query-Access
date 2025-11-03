"""
Generate Fifth Third Bank Redlining Report

Focus: Home Purchase loans in top 10 CBSAs (2018-2024)
Metrics: Tract demographic comparisons (MMCT, Black, Hispanic, Combined)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Lending and Branch Analysis'))

from utils.bigquery_client import create_client
import pandas as pd

# Configuration
FIFTH_THIRD_LEI = 'QFROUN1UWUYU0DVIWD51'
YEARS = list(range(2018, 2025))
KEY_PATH = "hdma1-242116-74024e2eb88f.json"

print("="*80)
print("Fifth Third Bank Redlining Report Generator")
print("="*80)

# Initialize BigQuery client
print("\n1. Connecting to BigQuery...")
client = create_client(key_path=KEY_PATH)

# Step 1: Find top 10 CBSAs by home purchase originations
print("\n2. Finding top 10 CBSAs by home purchase originations volume...")
top_cbsas_query = f"""
SELECT 
    cbsa_code,
    COUNTIF(action_taken = '1') as total_originations
FROM `hdma1-242116.hmda.hmda`
WHERE lei = '{FIFTH_THIRD_LEI}'
  AND activity_year BETWEEN 2018 AND 2024
  AND loan_purpose = '1'  -- Home Purchase only
  AND action_taken = '1'  -- Originations only
  AND cbsa_code IS NOT NULL
  AND cbsa_code != ''
  -- Standard filters
  AND occupancy_type = '1'
  AND reverse_mortgage != '1'
  AND construction_method = '1'
  AND total_units IN ('1', '2', '3', '4')
GROUP BY cbsa_code
ORDER BY total_originations DESC
LIMIT 10
"""

top_cbsas_df = client.execute_query(top_cbsas_query)
print(f"\nTop 10 CBSAs found:")
for idx, row in top_cbsas_df.iterrows():
    print(f"  {idx+1}. CBSA {row['cbsa_code']}: {row['total_originations']:,} originations")

cbsa_list = top_cbsas_df['cbsa_code'].tolist()
cbsa_str = "', '".join(cbsa_list)

print(f"\n3. Generating tract demographic analysis...")
print("   This may take 5-10 minutes depending on data size...")

# Main query for tract demographics
main_query = f"""
WITH subject_volume AS (
    -- Get subject bank's volume by CBSA, year
    SELECT
        activity_year,
        cbsa_code,
        COUNT(*) as subject_vol
    FROM `hdma1-242116.hmda.hmda`
    WHERE lei = '{FIFTH_THIRD_LEI}'
      AND action_taken IN ('1', '3')  -- Originations and applications
      AND activity_year BETWEEN 2018 AND 2024
      AND loan_purpose = '1'  -- Home Purchase
      AND cbsa_code IN ('{cbsa_str}')
    GROUP BY activity_year, cbsa_code
),

all_lenders AS (
    -- Get all lenders' volume for peer comparison
    SELECT
        activity_year,
        cbsa_code,
        lei,
        COUNT(*) as lender_vol
    FROM `hdma1-242116.hmda.hmda`
    WHERE action_taken IN ('1', '3')
      AND activity_year BETWEEN 2018 AND 2024
      AND loan_purpose = '1'
      AND cbsa_code IN ('{cbsa_str}')
    GROUP BY activity_year, cbsa_code, lei
),

peers AS (
    -- Identify peer lenders (50%-200% of subject's volume)
    SELECT DISTINCT
        av.activity_year,
        av.cbsa_code,
        av.lei
    FROM all_lenders av
    INNER JOIN subject_volume sv
        ON av.activity_year = sv.activity_year
        AND av.cbsa_code = sv.cbsa_code
    WHERE av.lender_vol >= sv.subject_vol * 0.5
      AND av.lender_vol <= sv.subject_vol * 2.0
      AND av.lei != '{FIFTH_THIRD_LEI}'
),

hmda_with_geography AS (
    -- Join HMDA data with tract demographics
    SELECT
        h.activity_year,
        h.cbsa_code,
        h.lei,
        h.action_taken,
        h.tract_minority_population_percent as tract_minority_pct,
        g.black_pct,
        g.hispanic_pct,
        g.black_and_hispanic_pct
    FROM `hdma1-242116.hmda.hmda` h
    LEFT JOIN `hdma1-242116.geo.black_hispanic_majority` g
        ON CAST(h.census_tract AS STRING) = CAST(g.geoid AS STRING)
    WHERE h.action_taken IN ('1', '3')  -- Originations and applications
      AND h.activity_year BETWEEN 2018 AND 2024
      AND h.loan_purpose = '1'  -- Home Purchase
      AND h.cbsa_code IN ('{cbsa_str}')
      -- Standard HMDA filters
      AND h.occupancy_type = '1'  -- Owner-occupied
      AND h.reverse_mortgage != '1'  -- Not reverse mortgage
      AND h.construction_method = '1'  -- Site-built only
      AND h.total_units IN ('1', '2', '3', '4')  -- 1-4 unit properties
),

subject_data AS (
    -- Calculate subject bank metrics
    SELECT
        activity_year,
        cbsa_code,
        COUNT(*) as subject_total_originations,
        -- Applications
        COUNTIF(action_taken = '3') as subject_total_applications,
        -- MMCT metrics
        COUNTIF(action_taken IN ('1', '3') AND tract_minority_pct > 50) as subject_mmct_50_originations,
        COUNTIF(action_taken IN ('1', '3') AND tract_minority_pct > 80) as subject_mmct_80_originations,
        -- Black tract metrics
        COUNTIF(action_taken IN ('1', '3') AND black_pct > 50) as subject_black_tract_50_originations,
        COUNTIF(action_taken IN ('1', '3') AND black_pct > 80) as subject_black_tract_80_originations,
        -- Hispanic tract metrics
        COUNTIF(action_taken IN ('1', '3') AND hispanic_pct > 50) as subject_hispanic_tract_50_originations,
        COUNTIF(action_taken IN ('1', '3') AND hispanic_pct > 80) as subject_hispanic_tract_80_originations,
        -- Black + Hispanic combined metrics
        COUNTIF(action_taken IN ('1', '3') AND black_and_hispanic_pct > 50) as subject_black_hispanic_tract_50_originations,
        COUNTIF(action_taken IN ('1', '3') AND black_and_hispanic_pct > 80) as subject_black_hispanic_tract_80_originations
    FROM hmda_with_geography
    WHERE lei = '{FIFTH_THIRD_LEI}'
    GROUP BY activity_year, cbsa_code
),

peer_data AS (
    -- Calculate peer banks metrics
    SELECT
        activity_year,
        cbsa_code,
        COUNT(*) as peer_total_originations,
        COUNTIF(action_taken = '3') as peer_total_applications,
        -- MMCT metrics
        COUNTIF(action_taken IN ('1', '3') AND tract_minority_pct > 50) as peer_mmct_50_originations,
        COUNTIF(action_taken IN ('1', '3') AND tract_minority_pct > 80) as peer_mmct_80_originations,
        -- Black tract metrics
        COUNTIF(action_taken IN ('1', '3') AND black_pct > 50) as peer_black_tract_50_originations,
        COUNTIF(action_taken IN ('1', '3') AND black_pct > 80) as peer_black_tract_80_originations,
        -- Hispanic tract metrics
        COUNTIF(action_taken IN ('1', '3') AND hispanic_pct > 50) as peer_hispanic_tract_50_originations,
        COUNTIF(action_taken IN ('1', '3') AND hispanic_pct > 80) as peer_hispanic_tract_80_originations,
        -- Black + Hispanic combined metrics
        COUNTIF(action_taken IN ('1', '3') AND black_and_hispanic_pct > 50) as peer_black_hispanic_tract_50_originations,
        COUNTIF(action_taken IN ('1', '3') AND black_and_hispanic_pct > 80) as peer_black_hispanic_tract_80_originations
    FROM hmda_with_geography
    WHERE lei IN (SELECT lei FROM peers)
    GROUP BY activity_year, cbsa_code
)

-- Final output
SELECT
    s.activity_year as activity_year,
    s.cbsa_code as cbsa_code,
    'Fifth Third Bank' as lender_name,
    'Home Purchase' as loan_purpose_category,
    s.subject_total_originations,
    s.subject_total_applications,
    s.subject_mmct_50_originations,
    s.subject_mmct_80_originations,
    s.subject_black_tract_50_originations,
    s.subject_black_tract_80_originations,
    s.subject_hispanic_tract_50_originations,
    s.subject_hispanic_tract_80_originations,
    s.subject_black_hispanic_tract_50_originations,
    s.subject_black_hispanic_tract_80_originations,
    COALESCE(p.peer_total_originations, 0) as peer_total_originations,
    COALESCE(p.peer_total_applications, 0) as peer_total_applications,
    COALESCE(p.peer_mmct_50_originations, 0) as peer_mmct_50_originations,
    COALESCE(p.peer_mmct_80_originations, 0) as peer_mmct_80_originations,
    COALESCE(p.peer_black_tract_50_originations, 0) as peer_black_tract_50_originations,
    COALESCE(p.peer_black_tract_80_originations, 0) as peer_black_tract_80_originations,
    COALESCE(p.peer_hispanic_tract_50_originations, 0) as peer_hispanic_tract_50_originations,
    COALESCE(p.peer_hispanic_tract_80_originations, 0) as peer_hispanic_tract_80_originations,
    COALESCE(p.peer_black_hispanic_tract_50_originations, 0) as peer_black_hispanic_tract_50_originations,
    COALESCE(p.peer_black_hispanic_tract_80_originations, 0) as peer_black_hispanic_tract_80_originations
FROM subject_data s
LEFT JOIN peer_data p
    ON s.activity_year = p.activity_year
    AND s.cbsa_code = p.cbsa_code
ORDER BY s.activity_year, s.cbsa_code
"""

# Execute query and save results
print("\n4. Executing main query...")
result_df = client.execute_query(main_query)

print(f"\n   Query completed! Retrieved {len(result_df):,} rows")

# Save to CSV
output_file = "fifth_third_redlining_report_2018_2024.csv"
result_df.to_csv(output_file, index=False)
print(f"\n5. Saved results to: {output_file}")

print("\n6. Preview of results:")
print("="*80)
print(result_df.head(10).to_string())

print("\n" + "="*80)
print("Query completed successfully!")
print("="*80)
print(f"\nOutput file: {output_file}")
print(f"Total rows: {len(result_df):,}")
print(f"\nNext step: Run Excel generator to create report:")
print(f"  python ncrc_worst_lenders_analysis_v4.py {output_file}")

