from google.cloud import bigquery

def main():
    print("Starting script...")
    
    # Path to the service account json file
    key_path = "hdma1-242116-74024e2eb88f.json"
    project_id = "hdma1-242116"
    
    print(f"Attempting to connect to project: {project_id}")
    print(f"Using credentials file: {key_path}")

    try:
        # Create a BigQuery client using a service account file
        client = bigquery.Client.from_service_account_json(key_path, project=project_id)
        print("✓ Client created successfully")
        
        # List all datasets
        print(f"\nListing datasets in project {project_id}...")
        datasets = list(client.list_datasets())
        print(f"✓ Found {len(datasets)} dataset(s)")
        
        if not datasets:
            print("  No datasets found.")
            return

        for dataset in datasets:
            dataset_id = dataset.dataset_id
            print(f"\n📁 Dataset: {dataset_id}")

            tables = list(client.list_tables(dataset.reference))
            if not tables:
                print("  No tables found in this dataset.")
                continue

            for table in tables:
                table_ref = f"{dataset_id}.{table.table_id}"
                # Get table metadata to retrieve number of rows
                bq_table = client.get_table(table.reference)
                print(f"  • {table.table_id} | Rows: {bq_table.num_rows:,}")
                
        print("\n✓ Script completed successfully")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()