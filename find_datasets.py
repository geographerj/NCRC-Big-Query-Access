"""
Find all datasets and tables to locate LEI mapping
"""

from google.cloud import bigquery

def main():
    key_path = "hdma1-242116-74024e2eb88f.json"
    project_id = "hdma1-242116"
    
    print("Connecting to BigQuery...")
    client = bigquery.Client.from_service_account_json(key_path, project=project_id)
    print("✓ Connected")
    print()
    
    print("="*80)
    print("DATASETS AND TABLES IN PROJECT")
    print("="*80)
    print()
    
    datasets = list(client.list_datasets())
    
    for dataset in datasets:
        dataset_id = dataset.dataset_id
        print(f"📁 Dataset: {dataset_id}")
        
        tables = list(client.list_tables(dataset.reference))
        for table in tables:
            table_ref = client.get_table(table.reference)
            print(f"  ├─ {table.table_id:30} ({table_ref.num_rows:,} rows)")
        print()

if __name__ == "__main__":
    main()
