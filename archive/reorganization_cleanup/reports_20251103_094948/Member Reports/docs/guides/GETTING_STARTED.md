# Getting Started with Member Reports

## Overview

The Member Report process allows you to generate customized analytical reports in response to member data requests. Each report is configured using a JSON configuration file.

## Step-by-Step Guide

### 1. Receive Member Request

When you receive a member request, document it in `supporting_files/tickets/` with:
- Member organization name
- Request date
- Geographic scope requested
- Time period requested
- Specific questions or metrics of interest

### 2. Create Report Configuration

Create a new configuration file:

```bash
python scripts/setup_new_report.py --name "MEMBER_001"
```

Or manually create `configs/MEMBER_001.json` based on `configs/template_config.json`.

### 3. Fill in Configuration

Edit the configuration file with:

**Required Fields:**
- `report_metadata.report_title`: Descriptive title
- `report_metadata.report_id`: Unique identifier (e.g., "MEMBER_001")
- `report_metadata.years`: Array of years to analyze (e.g., `[2018, 2019, 2020, 2021, 2022, 2023, 2024]`)
- `subject_lender.lei`: Subject lender LEI (preferred) or name/RSSD
- `geography`: Either CBSA codes, county codes, or custom filter

**Example Geography - CBSA:**
```json
"geography": {
  "type": "cbsa",
  "cbsa_codes": ["35620", "16980"]
}
```

**Example Geography - County:**
```json
"geography": {
  "type": "county",
  "county_codes": ["36047", "36061", "36081"]
}
```

### 4. Generate Report

Run the report generator:

```bash
python scripts/generate_member_report.py --config configs/MEMBER_001.json
```

The script will:
1. Validate configuration
2. Query BigQuery for HMDA data
3. Process and calculate metrics
4. Generate Excel report
5. Save to `outputs/excel/`

### 5. Review and Deliver

Review the generated report in `outputs/excel/` and deliver to the member.

## Common Configurations

### Home Purchase Only
```json
"loan_filters": {
  "loan_purpose": "1"
}
```

### All Loan Purposes
```json
"loan_filters": {
  "loan_purpose": null
}
```

### Custom Geography (SQL)
```json
"geography": {
  "type": "custom",
  "custom_filter": "c.cbsa_name LIKE '%New York%'"
}
```

## Troubleshooting

**Error: "Must specify subject lender LEI"**
- Add `lei` field to `subject_lender` section
- Or use `name` with crosswalk lookup (requires additional setup)

**Error: "No geographic filter specified"**
- Add CBSA codes, county codes, or custom filter to `geography` section

**Query returns no results**
- Check that years are valid (2018-2024 typically)
- Verify LEI is correct
- Confirm geographic filters match available data

## Next Steps

- See `docs/guides/CONFIGURATION_REFERENCE.md` for full configuration options
- See `docs/guides/ADVANCED_FEATURES.md` for advanced usage

