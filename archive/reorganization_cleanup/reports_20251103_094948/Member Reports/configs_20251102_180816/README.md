# Configuration Files

Report configuration JSON files define all parameters for report generation.

## Template

**`template_config.json`** - Template for creating new reports

Copy this file and modify for your specific report.

## Example Configurations

- **`tampa_market_report.json`** - Complete Tampa, FL market report configuration
- **`test_config.json`** - Testing configuration
- **`member_report_template.json`** - Alternative template format

## Configuration Structure

See **[Configuration Reference](../docs/guides/CONFIGURATION_REFERENCE.md)** for complete documentation.

### Key Sections

1. **Metadata**
   - Report title
   - Member organization
   - Report date

2. **Geography**
   - Census tracts (list of strings)
   - Location name

3. **Time Period**
   - Start year
   - End year

4. **Loan Filters**
   - Loan purpose
   - Occupancy type
   - Construction method
   - Reverse mortgage exclusion

5. **Metrics**
   - Which metrics to calculate
   - Peer comparison settings

6. **Output**
   - Output folder name
   - File naming conventions

## Creating a New Configuration

### Method 1: Copy Template
```bash
cp configs/template_config.json configs/my_report_config.json
# Edit my_report_config.json
```

### Method 2: Interactive Setup
```bash
python scripts/setup_new_report.py
```

### Method 3: Use Tampa as Template
```bash
cp configs/tampa_market_report.json configs/my_location_config.json
# Update census tracts and location name
```

## Naming Convention

**Recommended:** `[location]_[type]_report.json`

Examples:
- `tampa_market_report.json`
- `atlanta_city_report.json`
- `philadelphia_cba_report.json`

## Validation

Configuration files are validated when reports are generated. Common issues:

- Census tracts must be strings (not numbers)
- Years must be valid integers (2018-2024 for HMDA)
- Member organization name required
- Geographic scope must match available data

## Location in Reports

Each generated report includes a copy of its configuration file in the output folder:
`outputs/[Community]_[Member]/[config].json`

This ensures reproducibility and documentation of report parameters.


