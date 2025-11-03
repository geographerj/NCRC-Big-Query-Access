# 🚀 START HERE - Member Reports System

## Quick Navigation

**New to the system?** Start here:

1. **[README.md](README.md)** - Complete system overview
2. **[QUICK_START.md](QUICK_START.md)** - Fast reference guide
3. **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - File organization guide

## Generate Your First Report

### Option 1: Use Tampa as Template (Recommended)
```bash
cd "C:\DREAM\Member Reports"
python scripts/create_tampa_report.py
```

**Output:** `outputs/Tampa_FL_Sample_Member/Tampa_FL_Sample_Member_Report.pdf`

### Option 2: Interactive Setup
```bash
python scripts/generate_member_report_interactive.py
```

## Essential Files

| File | Purpose |
|------|---------|
| `scripts/create_tampa_report.py` | ⭐ **Main report generator** - Use as template |
| `configs/template_config.json` | Configuration template |
| `supporting_files/NCRC_Logo.jpg` | Required logo file |
| `docs/guides/REPORT_WRITING_GUIDELINES.md` | Writing standards |

## Key Directories

- **`scripts/`** - Execution scripts (start here)
- **`generators/`** - PDF/Excel generation
- **`queries/`** - BigQuery SQL builders
- **`utils/`** - Helper functions
- **`docs/guides/`** - Complete documentation
- **`outputs/`** - Generated reports

## Documentation Index

📚 **All Guides:** `docs/guides/INDEX.md`

**Most Important:**
- [Getting Started](docs/guides/GETTING_STARTED.md) - Setup instructions
- [Report Writing Guidelines](docs/guides/REPORT_WRITING_GUIDELINES.md) - Writing standards
- [Configuration Reference](docs/guides/CONFIGURATION_REFERENCE.md) - Config file structure
- [Quick Reference](REPORT_WRITING_QUICK_REFERENCE.md) - Style reminders

## Creating Reports for New Locations

**Best Practice:**
1. Copy `scripts/create_tampa_report.py` → `scripts/create_[location]_report.py`
2. Update census tracts and location name
3. Update community profile path (if available)
4. Run your new script

## Requirements

✅ **Required:**
- Python 3.x
- BigQuery service account key
- NCRC Logo: `supporting_files/NCRC_Logo.jpg`

📦 **Python Packages:**
```bash
pip install reportlab pandas openpyxl google-cloud-bigquery pdfplumber pillow
```

## Common Tasks

| Task | Command/File |
|------|-------------|
| Generate Tampa report | `python scripts/create_tampa_report.py` |
| Extract community data | `python scripts/extract_community_profile_data.py` |
| Update lender info | `python scripts/enhance_lender_background.py` |
| View sample output | `outputs/Tampa_FL_Sample_Member/` |

## Need Help?

1. **Setup Issues?** → [Getting Started Guide](docs/guides/GETTING_STARTED.md)
2. **Writing Questions?** → [Writing Guidelines](docs/guides/REPORT_WRITING_GUIDELINES.md)
3. **Config Questions?** → [Configuration Reference](docs/guides/CONFIGURATION_REFERENCE.md)
4. **System Overview?** → [Main README](README.md)

## Project Status

✅ **Fully Functional**
- Report generation working
- NCRC branding implemented
- Community profile integration
- Lender background research
- PDF and Excel output
- Complete documentation

**Last Updated:** 2025-01-XX

---

**Ready to create a report?** → See [QUICK_START.md](QUICK_START.md)


