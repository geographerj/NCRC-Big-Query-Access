"""Quick test to check sod25 schema"""
import sys
import os
import importlib.util

def load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bigquery_client = load_module(
    "bigquery_client",
    os.path.join(base_dir, "Lending and Branch Analysis", "utils", "bigquery_client.py")
)
create_client = bigquery_client.create_client

creds_path = os.path.join(base_dir, "config", "credentials", "hdma1-242116-74024e2eb88f.json")
client = create_client(key_path=creds_path)

# Get one row to see columns
query = "SELECT * FROM `hdma1-242116.branches.sod25` LIMIT 1"
try:
    df = client.execute_query(query)
    print("Columns in sod25:")
    print(list(df.columns))
    print("\nFirst row:")
    print(df.head())
except Exception as e:
    print(f"Error: {e}")

