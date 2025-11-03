# Configuration Reference

Complete reference for Member Report configuration files.

## Configuration Schema

### report_metadata

Report identification and metadata.

```json
{
  "report_metadata": {
    "report_title": "Mortgage Lending in Queens, New York",
    "member_organization": "Organization Name",
    "report_id": "MEMBER_001",
    "report_date": "2025-01-15",
    "analyst": "NCRC Research",
    "description": "Analysis of mortgage lending patterns...",
    "years": [2018, 2019, 2020, 2021, 2022, 2023, 2024],
    "date_range": {
      "start_year": 2018,
      "end_year": 2024
    }
  }
}
```

**Fields:**
- `report_title` (string, required): Title for the report
- `member_organization` (string): Name of requesting organization
- `report_id` (string, required): Unique identifier (used in filenames)
- `report_date` (string): Report generation date (ISO format)
- `analyst` (string): Analyst name
- `description` (string): Report description
- `years` (array, required): Years to analyze (2018-2024 typical)
- `date_range` (object): Alternative to years array

### geography

Geographic scope for analysis.

**Type: CBSA**
```json
{
  "geography": {
    "type": "cbsa",
    "cbsa_codes": ["35620", "16980"],
    "cbsa_names": []
  }
}
```

**Type: County**
```json
{
  "geography": {
    "type": "county",
    "county_codes": ["36047", "36061"]
  }
}
```

**Type: Custom**
```json
{
  "geography": {
    "type": "custom",
    "custom_filter": "c.cbsa_name LIKE '%New York%'"
  }
}
```

### subject_lender

Subject lender identification.

```json
{
  "subject_lender": {
    "lei": "ABCD1234EFGH5678IJKL",
    "name": null,
    "rssd": null
  }
}
```

**Fields:**
- `lei` (string, preferred): Legal Entity Identifier
- `name` (string): Lender name (requires crosswalk)
- `rssd` (string): RSSD ID (requires crosswalk)

### metrics

Which metrics to calculate and include.

```json
{
  "metrics": {
    "borrower_demographics": {
      "enabled": true,
      "include": ["hispanic", "black", "asian", "native_american", "hopi", "minb"]
    },
    "income_metrics": {
      "enabled": true,
      "include": ["lmib_percentage", "lmict_percentage", "lmib_amount"]
    },
    "redlining": {
      "enabled": true,
      "include": ["mmct_50", "mmct_80", "black_tract_50", "black_tract_80"]
    }
  }
}
```

### loan_filters

HMDA loan filters.

```json
{
  "loan_filters": {
    "standard_hmda_filters": true,
    "loan_purpose": "1",
    "occupancy_type": "1",
    "reverse_mortgage": "exclude",
    "construction_method": "1",
    "total_units": [1, 2, 3, 4],
    "action_taken": "1"
  }
}
```

**Common Values:**
- `loan_purpose`: `"1"` (home purchase), `null` (all)
- `action_taken`: `"1"` (originations only)
- `occupancy_type`: `"1"` (owner-occupied)
- `reverse_mortgage`: `"exclude"` or `null`

### peer_definition

Peer lender identification.

```json
{
  "peer_definition": {
    "enabled": true,
    "method": "volume_based",
    "volume_range": {
      "min_multiplier": 0.5,
      "max_multiplier": 2.0
    },
    "exclude_subject": true,
    "min_peers": 3
  }
}
```

### output

Output configuration.

```json
{
  "output": {
    "format": "excel",
    "file_name": null,
    "output_directory": "outputs/excel",
    "include_methods_sheet": true,
    "include_raw_data": false,
    "excel_formatting": {
      "color_code_gaps": true,
      "highlight_significant": true,
      "freeze_panes": true
    }
  }
}
```

## Complete Example

See `configs/template_config.json` for a complete example configuration.

