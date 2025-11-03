# Scripts Directory

Main execution scripts for generating member reports.

## Primary Scripts

### `create_tampa_report.py` ⭐ **START HERE**
**Full-featured report generator for Tampa, FL**

This is the most complete and up-to-date script. Use it as a template for other locations.

**Features:**
- Complete market overview analysis
- Top 10 lender analysis with background information
- Community profile integration
- CBA detection and linking
- National trend references
- Full narrative generation

**Usage:**
```bash
python scripts/create_tampa_report.py
```

**Output:** `outputs/Tampa_FL_Sample_Member/`

---

### `generate_member_report_interactive.py`
**Interactive setup for new reports**

Prompts for all required information and generates a report configuration, then calls the main generator.

**Usage:**
```bash
python scripts/generate_member_report_interactive.py
```

---

### `generate_member_report.py`
**General-purpose report generator**

Uses configuration files to generate reports. More generic than Tampa-specific script.

**Usage:**
```bash
python scripts/generate_member_report.py --config configs/your_report.json
```

---

## Utility Scripts

### `extract_community_profile_data.py`
Extracts demographic and income data from community profile PDFs.

**Usage:**
```bash
python scripts/extract_community_profile_data.py
```

**Output:** `data/processed/[location]_community_profile_data.json`

---

### `enhance_lender_background.py`
Searches for and updates lender background information.

**Usage:**
```bash
python scripts/enhance_lender_background.py
```

**Updates:** `data/lender_background_info.json`

---

### `setup_new_report.py`
Interactive script to create a new report configuration.

**Usage:**
```bash
python scripts/setup_new_report.py
```

**Output:** `configs/[report_name]_config.json`

---

## Development/Testing Scripts

### `process_tampa_data.py`
Standalone data processing for Tampa market.

**Purpose:** Test data processing logic independently.

---

### `check_tampa_data.py`
Data validation and inspection tool.

**Purpose:** Verify data quality and check metric calculations.

---

### `extract_tampa_tracts.py`
Extract census tracts from Tampa community profile PDF.

**Purpose:** Extract geographic boundaries from PDF.

---

### `inspect_tampa_pdf.py`
Inspect structure of community profile PDF.

**Purpose:** Development tool for understanding PDF structure.

---

## Legacy/Old Scripts

These scripts are older versions or experimental:

- `create_tampa_report_NEW_NARRATIVES.py` - Development version
- `generate_tampa_report.py` - Older version

**Recommendation:** Use `create_tampa_report.py` instead.

---

## Creating Reports for New Locations

**Recommended approach:**

1. Copy `create_tampa_report.py` to `create_[location]_report.py`
2. Update:
   - Census tract list
   - Location name variables
   - Community profile file path
   - Output folder name
3. Test and refine

---

## Script Organization

| Script | Status | Use For |
|--------|--------|---------|
| `create_tampa_report.py` | ✅ **Primary** | Tampa reports (template for others) |
| `generate_member_report_interactive.py` | ✅ Active | Interactive setup |
| `generate_member_report.py` | ✅ Active | General reports |
| `extract_community_profile_data.py` | ✅ Active | Data extraction |
| `enhance_lender_background.py` | ✅ Active | Lender research |
| `setup_new_report.py` | ✅ Active | Config creation |
| `process_tampa_data.py` | 🔧 Testing | Development |
| `check_tampa_data.py` | 🔧 Testing | Validation |
| `create_tampa_report_NEW_NARRATIVES.py` | 🗄️ Legacy | Don't use |
| `generate_tampa_report.py` | 🗄️ Legacy | Don't use |

---

## Notes

- All scripts should be run from the `Member Reports/` directory
- Most scripts require BigQuery access (service account key)
- Check script docstrings for specific requirements
- See main `README.md` for system overview


