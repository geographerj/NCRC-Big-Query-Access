"""
Check HMDA table schema
"""

from google.cloud import bigquery

def main():
    print("Checking HMDA table schema...")
    print()
    
    key_path = "hdma1-242116-74024e2eb88f.json"
    project_id = "hdma1-242116"
    
    client = bigquery.Client.from_service_account_json(key_path, project=project_id)
    
    # Get table schema
    table_ref = client.dataset("hmda", project="hdma1-242116").table("hmda")
    table = client.get_table(table_ref)
    
    print(f"Table: {table.full_table_id}")
    print(f"Rows: {table.num_rows:,}")
    print()
    print("Columns:")
    print("-" * 60)
    
    for field in table.schema:
        print(f"  {field.name:40} {field.field_type}")
    
    print()
    print("Looking for name-related columns:")
    for field in table.schema:
        if 'name' in field.name.lower() or 'lei' in field.name.lower():
            print(f"  ✓ {field.name}")

if __name__ == "__main__":
    main()
