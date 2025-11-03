# Generators Directory

Core classes for generating PDF and Excel reports.

## Files

### `pdf_generator.py` ⭐ **PRIMARY**
**PDFReportGenerator class** - Creates branded PDF reports

**Features:**
- NCRC branding (logo, colors, fonts)
- Title page with logo
- Pagination with page numbers
- Table formatting with `KeepTogether` to prevent splits
- Hyperlink support (lender websites, external links)
- Multi-section reports (Introduction, Key Findings, Overview, Top Lenders, Methods)

**Key Methods:**
- `generate_report()` - Main entry point
- `_create_title_page()` - Title page generation
- `_create_key_points_section()` - Key findings
- `_create_overview_section()` - Market overview tables
- `_create_top_lenders_section()` - Individual lender analysis
- `_create_methods_section()` - Methodology with hyperlinks
- `_header_footer()` - Logo and page numbers

**Logo Placement:**
- Title page only (page 1)
- Upper left corner
- 10 points from left and top edges
- Aspect ratio preserved

---

### `excel_generator.py`
**ExcelReportGenerator class** - Creates Excel workbooks

**Features:**
- Multi-sheet workbooks
- NCRC branding and formatting
- Market overview sheet
- Individual lender sheets (top 10)
- Methods sheet with methodology

**Key Methods:**
- `generate_report()` - Main entry point
- `_create_market_overview_sheet()` - Market data
- `_create_lender_sheet()` - Individual lender data
- `_create_methods_sheet()` - Methodology documentation

---

### `data_processor.py`
**MemberReportDataProcessor class** - Processes HMDA data and calculates metrics

**Features:**
- Race/ethnicity metric calculations
- Geographic metric calculations (LMIB, LMICT, MMCT)
- Missing data handling
- Year-over-year aggregation

**Key Methods:**
- `calculate_metrics()` - Calculate all fair lending metrics
- `process_market_data()` - Process market-level data
- `process_lender_data()` - Process lender-level data

---

## Usage

### PDF Generation
```python
from generators.pdf_generator import PDFReportGenerator

generator = PDFReportGenerator(logo_path="supporting_files/NCRC_Logo.jpg")
generator.generate_report(
    output_path="outputs/report.pdf",
    report_title="Market Report Title",
    report_data={...},  # See create_tampa_report.py for structure
    member_org="Sample Member",
    report_date="2025-01-15"
)
```

### Excel Generation
```python
from generators.excel_generator import ExcelReportGenerator

generator = ExcelReportGenerator()
generator.generate_report(
    output_path="outputs/report.xlsx",
    report_data={...}
)
```

### Data Processing
```python
from generators.data_processor import MemberReportDataProcessor

processor = MemberReportDataProcessor()
metrics = processor.calculate_metrics(df)  # DataFrame with HMDA data
```

---

## Report Data Structure

Reports expect a specific data structure:

```python
report_data = {
    'introduction': str,  # Introduction text
    'key_points': list,   # List of key finding strings
    'overview': {
        'lead_in': str,
        'analysis': str,
        'race_table': pd.DataFrame,  # Race/ethnicity metrics by year
        'geographic_table': pd.DataFrame  # LMIB/LMICT/MMCT by year
    },
    'top_lenders': {
        'lead_in': str,
        'analysis': str,
        'tables': dict,  # {lender_name: pd.DataFrame}
        'narratives': dict  # {lender_name: {'lead_in': str, 'analysis': str}}
    },
    'methods': {
        'text': str  # Methodology text
    }
}
```

See `scripts/create_tampa_report.py` for complete example.

---

## Branding Integration

Generators use utilities from `utils/ncrc_branding.py`:

- **Colors**: NCRC Orange, NCRC Blue
- **Fonts**: Helvetica family
- **Table Styles**: NCRC blue headers, alternating rows
- **Formatting**: Consistent number and percentage formats

---

## Notes

- PDF generator requires `reportlab` library
- Excel generator requires `openpyxl` library
- Logo path is optional but recommended
- Tables are wrapped in `KeepTogether` to prevent page splits
- Hyperlinks are converted to clickable links in PDF

---

## Dependencies

- `reportlab` - PDF generation
- `pandas` - Data manipulation
- `openpyxl` - Excel generation
- `PIL/Pillow` - Image handling for logo


