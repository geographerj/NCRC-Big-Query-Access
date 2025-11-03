"""
Simple script to find top 10 CBSAs for Fifth Third Bank
"""
from google.cloud import bigquery

# Setup
key_path = "hdma1-242116-74024e2eb88f.json"
project_id = "hdma1-242116"
client = bigquery.Client.from_service_account_json(key_path, project=project_id)

query = """
SELECT 
    cbsa_code,
    COUNTIF(action_taken = '1') as total_originations
FROM `hdma1-242116.hmda.hmda`
WHERE lei = 'QFROUN1UWUYU0DVIWD51'
  AND activity_year BETWEEN 2018 AND 2024
  AND loan_purpose = '1'
  AND action_taken = '1'
  AND cbsa_code IS NOT NULL
  AND cbsa_code != ''
  AND occupancy_type = '1'
  AND reverse_mortgage != '1'
  AND construction_method = '1'
  AND total_units IN ('1', '2', '3', '4')
GROUP BY cbsa_code
ORDER BY total_originations DESC
LIMIT 10
"""

print("Finding top 10 CBSAs...")
result = client.query(query).result().to_dataframe()
print("\nTop 10 CBSAs:")
print(result.to_string())
print(f"\nCBSA codes: {result['cbsa_code'].tolist()}")


