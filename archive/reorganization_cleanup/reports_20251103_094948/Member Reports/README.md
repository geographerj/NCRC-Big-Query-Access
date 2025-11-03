# NCRC Member Report Process

This directory contains the framework for generating customized member reports in response to member data requests.

## Overview

The Member Report process provides a flexible, configurable system for generating analytical reports based on member-specific requirements. Each report is unique but follows a standardized structure.

## Directory Structure

```
reports/Member Reports/
├── README.md                          # This file
├── configs/                            # Report configuration files (JSON)
│   └── template_config.json           # Template configuration
├── queries/                           # SQL query builders
│   ├── __init__.py
│   ├── member_report_queries.py      # Query generation functions
│   └── peer_analysis.py              # Peer comparison queries
├── generators/                        # Report generation modules
│   ├── __init__.py
│   ├── excel_generator.py            # Excel report generation
│   └── data_processor.py            # Data processing and calculations
├── utils/                             # Utility functions
│   ├── __init__.py
│   └── config_validator.py           # Configuration validation
├── examples/                          # Example configurations
│   └── queens_ny_example.json        # Example: Queens, NY report
└── scripts/                           # Execution scripts
    ├── generate_member_report.py     # Main execution script
    └── setup_new_report.py            # Helper for creating new report configs
```

## Quick Start

### Step 1: Create a Report Configuration

Create a JSON configuration file in `configs/` or use the template:

```bash
python reports/Member\ Reports/scripts/setup_new_report.py --name "Member_Request_001"
```

### Step 2: Customize the Configuration

Edit the generated configuration file with:
- Geographic scope (CBSAs, counties, or custom areas)
- Time period (years)
- Subject lender (LEI or name)
- Metrics to include
- Loan filters
- Output preferences

### Step 3: Generate the Report

```bash
python reports/Member\ Reports/scripts/generate_member_report.py --config configs/Member_Request_001.json
```

## Report Structure

### Standard Sections

1. **Executive Summary** - Overview of findings
2. **Geographic Analysis** - Analysis by CBSA, county, or custom geography
3. **Borrower Demographics** - Race/ethnicity metrics
4. **Income Metrics** - LMIB%, LMICT%
5. **Redlining Analysis** - Tract-level demographics
6. **Peer Comparison** - Subject bank vs. peer lenders
7. **Time Series** - Trends over time (if multi-year)
8. **Methods** - Methodology documentation

### Available Metrics

#### Borrower Demographics
- Hispanic%
- Black%
- Asian%
- Native American%
- HoPI% (Native Hawaiian/Pacific Islander)
- MINB% (Combined Minority)

#### Income-Based
- LMIB% (Low-to-Moderate Income Borrowers)
- LMICT% (Low-to-Moderate Income Census Tracts)

#### Redlining (Tract Demographics)
- MMCT 50% (Majority-Minority Census Tracts >50%)
- MMCT 80% (Majority-Minority Census Tracts >80%)
- Black Tract 50%/80%
- Hispanic Tract 50%/80%
- Black+Hispanic Tract 50%/80%

## Configuration Schema

See `configs/template_config.json` for the full schema.

Key fields:
- `report_metadata`: Report title, description, date range
- `geography`: CBSA codes, county codes, or custom geographic filters
- `subject_lender`: LEI, name, or RSSD
- `years`: Array of years to analyze
- `metrics`: Which metrics to include
- `loan_filters`: Standard HMDA filters
- `peer_definition`: How to define peer lenders
- `output`: Output format and file naming

## Workflow

1. **Request Intake**: Member makes data request
2. **Config Creation**: Create configuration file with requirements
3. **Data Query**: System queries BigQuery based on config
4. **Data Processing**: Calculate metrics, peer comparisons
5. **Report Generation**: Generate Excel/PDF with formatted tables
6. **Review**: Review report for accuracy
7. **Delivery**: Deliver to member

## Examples

See `examples/` directory for example configurations.

## Support

For questions or issues:
- Check configuration validation errors
- Review query logs in `data/logs/`
- Contact NCRC Research Department

