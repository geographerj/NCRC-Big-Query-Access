"""
BigQuery Client Utilities for Lending and Branch Analysis

This module provides helper functions for connecting to BigQuery and executing queries.
"""

from google.cloud import bigquery
import pandas as pd
import os
from typing import Optional, List, Dict, Any


class BigQueryClient:
    """Wrapper class for BigQuery operations"""
    
    def __init__(self, key_path: str, project_id: str):
        """
        Initialize BigQuery client
        
        Args:
            key_path: Path to service account JSON file
            project_id: BigQuery project ID
        """
        self.key_path = key_path
        self.project_id = project_id
        self.client = bigquery.Client.from_service_account_json(key_path, project=project_id)
        print(f"✓ Connected to BigQuery project: {project_id}")
    
    def execute_query(self, query: str, max_results: Optional[int] = None) -> pd.DataFrame:
        """
        Execute a SQL query and return results as pandas DataFrame
        
        Args:
            query: SQL query string
            max_results: Optional limit on number of rows to return
            
        Returns:
            DataFrame with query results
        """
        print(f"Executing query...")
        print(f"  Query length: {len(query)} characters")
        
        query_job = self.client.query(query)
        
        # Wait for job to complete
        results = query_job.result(max_results=max_results)
        
        # Convert to DataFrame
        df = results.to_dataframe()
        
        print(f"✓ Query completed: {len(df):,} rows returned")
        return df
    
    def list_datasets(self) -> List[str]:
        """List all datasets in the project"""
        datasets = list(self.client.list_datasets())
        return [dataset.dataset_id for dataset in datasets]
    
    def list_tables(self, dataset_id: str) -> List[str]:
        """List all tables in a dataset"""
        dataset_ref = self.client.dataset(dataset_id)
        tables = list(self.client.list_tables(dataset_ref))
        return [table.table_id for table in tables]
    
    def get_table_info(self, dataset_id: str, table_id: str) -> Dict[str, Any]:
        """Get information about a table"""
        table_ref = self.client.dataset(dataset_id).table(table_id)
        table = self.client.get_table(table_ref)
        
        return {
            'num_rows': table.num_rows,
            'num_bytes': table.num_bytes,
            'schema': [field.name for field in table.schema],
            'created': table.created,
            'modified': table.modified
        }
    
    def export_to_csv(self, df: pd.DataFrame, output_path: str, index: bool = False):
        """
        Export DataFrame to CSV file
        
        Args:
            df: DataFrame to export
            output_path: Path where CSV will be saved
            index: Whether to include index column
        """
        df.to_csv(output_path, index=index)
        print(f"✓ Exported {len(df):,} rows to: {output_path}")
    
    def query_to_csv(self, query: str, output_path: str, max_results: Optional[int] = None):
        """
        Execute query and save results directly to CSV
        
        Args:
            query: SQL query string
            output_path: Path where CSV will be saved
            max_results: Optional limit on number of rows to return
        """
        df = self.execute_query(query, max_results=max_results)
        self.export_to_csv(df, output_path)
        return df


def create_client(key_path: Optional[str] = None, project_id: Optional[str] = None) -> BigQueryClient:
    """
    Convenience function to create a BigQuery client
    
    Args:
        key_path: Path to service account JSON (defaults to hdma1-242116-74024e2eb88f.json)
        project_id: BigQuery project ID (defaults to hdma1-242116)
    
    Returns:
        BigQueryClient instance
    """
    if key_path is None:
        # Default to common location
        default_key_path = "hdma1-242116-74024e2eb88f.json"
        if os.path.exists(default_key_path):
            key_path = default_key_path
        else:
            raise FileNotFoundError(f"Service account key file not found: {default_key_path}")
    
    if project_id is None:
        project_id = "hdma1-242116"
    
    return BigQueryClient(key_path, project_id)

