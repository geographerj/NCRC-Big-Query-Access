# NCRC Branding Guidelines for Member Reports

This document outlines how NCRC branding standards are applied to member reports.

## Brand Files

The following brand guideline files are referenced:
- `supporting_files/Updated NCRC_Brand Guidelines_V19b.pdf`
- `supporting_files/NCRC Style Guide FP.pdf`
- `supporting_files/NCRC Letterhead.docx`

## Color Scheme

### Status Colors (Gap Analysis)

These colors are used to indicate performance relative to peers:

- **Green** (`#C6EFCE`): Positive gap - Bank outperforms peers
- **Yellow** (`#FFEB9C`): Minor negative gap (0 to -2.0 percentage points)
- **Orange** (`#FFC000`): Moderate negative gap (-2.0 to -5.0 percentage points)
- **Light Red** (`#FFC7CE`): Large negative gap (-5.0 to -10.0 percentage points)
- **Red** (`#FF0000`): Severe negative gap (<-10.0 percentage points)
- **Red with White Bold Text**: Severe negative gap + statistically significant

### Brand Colors

- **NCRC Blue**: `#003366` (Primary brand color)
- **NCRC Light Blue**: `#4A90A4` (Accent)
- **NCRC Orange**: `#FF6B35` (Primary accent)

### Neutral Colors

- **Header Gray**: `#D3D3D3` (For table headers)
- **White**: `#FFFFFF`
- **Black**: `#000000`

## Typography

### Font Family

- **Primary**: Calibri (Excel-compatible sans-serif, similar to Helvetica Neue)
- Based on brand guidelines showing HelveticaNeueLTStd usage

### Font Sizes

- **Title**: 16pt (bold)
- **Header**: 12pt (bold)
- **Subheader**: 11pt (bold)
- **Body**: 10pt
- **Footnote**: 9pt

### Font Styles

- Headers: Bold, center-aligned
- Body text: Regular weight, appropriate alignment
- Significant gaps: White bold text on red background

## Report Structure

### Header

Standard NCRC report header includes:
1. Organization name: "National Community Reinvestment Coalition"
2. Report title (centered, bold, 16pt)
3. Member organization (if applicable): "Prepared for: [Organization Name]"
4. Report date: "Report Date: YYYY-MM-DD"

### Footer

Standard footer includes:
- Contact information: "For questions about this report, contact: research@ncrc.org"
- Website: www.ncrc.org

### Table Formatting

- **Headers**: Gray background (`#D3D3D3`), bold text, center-aligned, thin borders
- **Data Cells**: Appropriate alignment based on data type (text=left, numbers=right)
- **Gap Columns**: Color-coded based on gap value (see Status Colors above)

## Logo Usage

- NCRC logo should be included in header when logo file is available
- Logo path checked in: `supporting_files/NCRC_Logo.png` or `.jpg`
- Logo placement: Top-left or top-center of first sheet

## Methodology Section

All reports include a "Methods" sheet with:
- Purpose of analysis
- Data sources
- Loan filters applied
- Race/ethnicity classification methodology (NCRC standard)
- Peer comparison methodology
- Statistical significance testing
- Color coding legend
- Contact information

## Implementation

Branding is implemented through the `utils/ncrc_branding.py` module, which provides:
- Color constants
- Font definitions
- Fill (background) functions
- Header/footer creation functions
- Formatting utilities

## Usage in Reports

```python
from Member Reports.utils import (
    format_header_row,
    apply_gap_coloring,
    create_report_header,
    create_report_footer,
    get_methodology_template
)

# Format headers
format_header_row(worksheet, row=1)

# Apply gap coloring
apply_gap_coloring(worksheet, gap_column=5, start_row=2, 
                   end_row=10, dataframe=df, gap_column_name='black_gap')

# Create header
create_report_header(worksheet, "Report Title", 
                    member_org="Organization Name", 
                    report_date="2025-01-15")
```

## Updating Guidelines

When brand guidelines are updated:
1. Update color constants in `utils/ncrc_branding.py`
2. Update font definitions if typography changes
3. Update this documentation
4. Test with sample reports to ensure consistency

