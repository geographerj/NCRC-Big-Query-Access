# Lending and Branch Analysis Project

This project provides utilities and query templates for analyzing lending and branch data from BigQuery.

## Project Structure

```
Lending and Branch Analysis/
├── utils/                    # Utility modules
│   ├── bigquery_client.py   # BigQuery connection and query utilities
│   └── crosswalk_utils.py   # Crosswalk file utilities
├── queries/                  # SQL query templates
│   ├── hmda_queries.py      # HMDA (lending) data queries
│   └── branch_queries.py    # Branch/banking data queries
├── examples/                 # Example scripts
│   └── example_usage.py     # How to use the utilities
├── data/                     # Data files (CSV exports, crosswalks)
└── README.md                 # This file
```

## Quick Start

### 1. Connect to BigQuery

```python
from utils import create_client

# Uses default credentials (hdma1-242116-74024e2eb88f.json)
client = create_client()

# Or specify your own
client = create_client(
    key_path="path/to/your/key.json",
    project_id="your-project-id"
)
```

### 2. Execute a Query

```python
from queries import hmda_queries

# Get a query template
query = hmda_queries.get_lender_activity_by_year(year=2024)

# Execute and save to CSV
df = client.query_to_csv(query, "data/results.csv")
```

### 3. Work with Crosswalks

```python
from utils import load_crosswalk, save_crosswalk

# Load a crosswalk file
crosswalk = load_crosswalk("path/to/crosswalk.csv")

# Create and save a crosswalk (how to share data with the AI!)
my_crosswalk = pd.DataFrame({
    'cbsa_code': ['33860'],
    'cbsa_name': ['Montgomery AL'],
    'county_code': ['01001']
})
save_crosswalk(my_crosswalk, "data/my_crosswalk.csv")
```

## Common Datasets

### HMDA (Home Mortgage Disclosure Act) Data
- **Location**: `hdma1-242116.hmda.hmda`
- **Years available**: 2018-2024 (and historical data)
- **Key fields**: `lei`, `activity_year`, `cbsa_code`, `census_tract`, `loan_amount`, `action_taken`, `loan_purpose`, race/ethnicity fields
- **Use cases**: Lending pattern analysis, demographic disparities, peer comparisons

### Branch Data (Summary of Deposits)
- **Location**: `hdma1-242116.branches.sod`
- **Related tables**: `branches.openings`, `branches.closings`
- **Key fields**: `institution_name`, `branch_name`, `cbsa_code`, `county_code`, `deposits`, `year`
- **Use cases**: Branch presence analysis, branch openings/closings, geographic coverage

### Geographic Crosswalks
- **CBSA to County**: Available in project root as `CBSA_to_County_Mapping.csv`
- **Other crosswalks**: May be in `hdma1-242116.geo.*` or `hdma1-242116.hud.*` datasets
- **Use cases**: Merging geographic identifiers, converting between geographic units

## How to Share Data with the AI Assistant

When you need help analyzing data, you can share it with me in these ways:

### Option 1: CSV Files (Recommended)
1. **Export query results to CSV**:
   ```python
   client.query_to_csv(query, "data/my_analysis.csv")
   ```

2. **Share the CSV file**: Simply tell me the file path, or if the file is in your workspace, I can read it directly!

### Option 2: Create Crosswalk Files
If you need me to understand a mapping or relationship:

```python
from utils import save_crosswalk
import pandas as pd

# Create your crosswalk
crosswalk = pd.DataFrame({
    'lei': ['7H6GLXDRUGQFU57RNE97'],
    'lender_name': ['JPMorgan Chase Bank'],
    'cbsa_code': ['33860'],
    # ... other fields
})

# Save it
save_crosswalk(crosswalk, "data/lei_to_cbsa_crosswalk.csv")
```

Then I can load it and use it in analysis!

### Option 3: Describe the Data Structure
If you can't export the data, just describe:
- What tables/columns you're using
- What the relationships are
- What analysis you want to do

I can help write queries or provide guidance.

## Common Query Patterns

### Get Lender Activity
```python
from queries import hmda_queries

query = hmda_queries.get_lender_activity_by_year(
    year=2024,
    lender_lei='7H6GLXDRUGQFU57RNE97'  # Optional
)
```

### Analyze CBSA Lending
```python
query = hmda_queries.get_cbsa_lending_patterns(
    cbsa_code='33860',  # Montgomery, AL
    year=2024
)
```

### Get Branch Data
```python
from queries import branch_queries

query = branch_queries.get_branches_by_cbsa(
    cbsa_code='33860',
    year=2024
)
```

### Find Peer Lenders
```python
query = hmda_queries.get_peer_lenders(
    subject_lei='7H6GLXDRUGQFU57RNE97',
    year=2024,
    cbsa_code='33860',
    volume_range=0.5  # 50% to 200% of subject volume
)
```

## Customizing Queries

The query templates are starting points. You can:

1. **Modify them directly**: Edit the functions in `queries/hmda_queries.py` or `queries/branch_queries.py`
2. **Write custom queries**: Use `client.execute_query()` with your own SQL
3. **Combine queries**: Use CTEs or subqueries to combine multiple query patterns

## Tips for Working with BigQuery

1. **Test queries first**: Use `LIMIT 100` or similar to test before running full queries
2. **Use specific filters**: Always filter by year, CBSA, or other dimensions to limit data size
3. **Export large results**: For large datasets, use `query_to_csv()` to save directly
4. **Preserve data types**: When loading crosswalks, specify `dtype` to preserve leading zeros in codes
5. **Handle missing data**: Be aware that some fields may be NULL or empty strings

## Next Steps

1. Run `examples/example_usage.py` to see the utilities in action
2. Explore the query templates in `queries/`
3. Modify queries for your specific analysis needs
4. Export results to CSV files in the `data/` directory
5. Share CSV files with the AI assistant for analysis help!

## Need Help?

- **Query questions**: Ask about specific query patterns or SQL syntax
- **Data structure**: Ask about available tables, columns, or relationships
- **Analysis help**: Share CSV files or describe what you want to analyze
- **Crosswalk creation**: Use `save_crosswalk()` and share the file

