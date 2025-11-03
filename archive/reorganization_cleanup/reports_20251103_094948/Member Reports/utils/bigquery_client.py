"""
BigQuery Client for Member Reports

Wrapper around BigQuery client for querying HMDA data.
"""

import sys
import os
from pathlib import Path

# Import from Lending and Branch Analysis utils
base_dir = Path(__file__).parent.parent.parent
la_utils_path = base_dir / "Lending and Branch Analysis" / "utils"

if str(la_utils_path) not in sys.path:
    sys.path.insert(0, str(la_utils_path))

try:
    from bigquery_client import create_client, BigQueryClient
except ImportError:
    # Fallback: create minimal client
    from google.cloud import bigquery
    import pandas as pd
    
    def create_client(key_path=None, project_id=None):
        """Create BigQuery client"""
        if key_path is None:
            default_path = base_dir / "config" / "credentials" / "hdma1-242116-74024e2eb88f.json"
            if default_path.exists():
                key_path = str(default_path)
        
        if project_id is None:
            project_id = "hdma1-242116"
        
        client = bigquery.Client.from_service_account_json(key_path, project=project_id)
        
        class Wrapper:
            def __init__(self, client):
                self.client = client
            
            def execute_query(self, query: str):
                """Execute query and return DataFrame"""
                query_job = self.client.query(query)
                results = query_job.result()
                return results.to_dataframe()
        
        return Wrapper(client)

