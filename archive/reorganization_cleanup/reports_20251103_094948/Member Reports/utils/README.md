# Utilities Directory

Helper functions and utilities for report generation.

## Core Utilities

### `ncrc_branding.py` ⭐ **ESSENTIAL**
NCRC branding standards and implementations.

**Functions:**
- Color constants (NCRC_ORANGE, NCRC_BLUE, etc.)
- Font definitions (Helvetica family)
- Header/footer creation functions
- Gap analysis color coding
- Methodology template

**Key Functions:**
- `get_logo_path()` - Find NCRC logo file
- `get_methodology_template()` - Standard methodology text
- `apply_gap_coloring()` - Color-code gap analysis in Excel

**Usage:**
```python
from utils.ncrc_branding import NCRC_ORANGE, get_logo_path
```

---

### `report_formatting.py`
Number and percentage formatting utilities.

**Functions:**
- `format_percentage()` - Format as `##.#` (12.5%)
- `format_integer()` - Format as `#,###` (1,234)
- `format_gap()` - Format percentage points (-5.2pp)
- `format_currency()` - Format currency ($1,234.56)
- Common acronym definitions

**Usage:**
```python
from utils.report_formatting import format_percentage, format_integer
percent_str = format_percentage(0.125)  # "12.5%"
num_str = format_integer(1234)  # "1,234"
```

---

### `bigquery_client.py`
BigQuery connection helper.

**Functions:**
- `get_bigquery_client()` - Create BigQuery client connection
- Helper functions for querying HMDA data

**Requirements:**
- Service account key file: `hdma1-242116-74024e2eb88f.json`
- Access to `hdma1-242116.hmda.hmda` table

---

### `community_profile.py`
Community profile data handling.

**Functions:**
- `find_community_profile()` - Locate community profile PDF
- `get_community_context()` - Extract demographic context
- `format_demographic_context()` - Format for narratives
- `extract_from_pdf()` - Extract data from PDF (placeholder)

**Note:** PDF extraction is limited; manual data entry recommended (see `docs/guides/MANUAL_COMMUNITY_PROFILE_DATA.md`)

---

### `lender_background_search.py`
Lender background information extraction.

**Functions:**
- `extract_location_from_search()` - Extract headquarters location
- `extract_history_from_search()` - Extract company history
- `extract_mergers_from_search()` - Extract merger information
- `extract_violations_from_search()` - Extract fair lending violations
- `extract_redlining_from_search()` - Extract redlining complaints
- `parse_search_results()` - Parse web search results

**Usage:**
See `scripts/enhance_lender_background.py` for example.

**Data Storage:** `data/lender_background_info.json`

---

### `web_search.py`
Web search utility (placeholder).

**Note:** Actual web searching is performed by AI assistant using available tools.

---

## Usage Patterns

### Branding in Reports
```python
from utils.ncrc_branding import NCRC_BLUE, get_logo_path

logo_path = get_logo_path()
# Use NCRC_BLUE for table headers
```

### Formatting Numbers
```python
from utils.report_formatting import format_percentage, format_integer

# In narratives
text = f"Lending share was {format_percentage(0.338)}"
text = f"Total loans: {format_integer(5421)}"
```

### Community Profile Integration
```python
from utils.community_profile import get_community_context

community_data = get_community_context("Tampa", "FL")
# Use in narrative generation
```

---

## Integration Points

These utilities are used throughout the system:

- **PDF Generator**: Uses `ncrc_branding.py` for colors, fonts, logo
- **Excel Generator**: Uses `ncrc_branding.py` for styling
- **Data Processor**: Uses `report_formatting.py` for output formatting
- **Narrative Generation**: Uses `community_profile.py` and `report_formatting.py`
- **Lender Analysis**: Uses `lender_background_search.py` for background info

---

## Extension Notes

To add new utilities:

1. Create new Python file in `utils/`
2. Add appropriate docstrings
3. Import in `__init__.py` if needed
4. Update this README with usage examples

---

## Dependencies

- `openpyxl` - Excel styling (in `ncrc_branding.py`)
- `pdfplumber` - PDF extraction (optional, in `community_profile.py`)
- `google-cloud-bigquery` - BigQuery access (in `bigquery_client.py`)


