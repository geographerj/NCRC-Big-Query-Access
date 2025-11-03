# Report Type Index - Member Reports

This file helps clarify that Member Reports are a DISTINCT report type from other report systems.

## This is a Member Reports Folder

If you're working in `Member Reports/` (root level), this is for:
- ✅ NCRC member data requests
- ✅ Mortgage lending analysis for specific communities
- ✅ PDF + Excel reports with NCRC branding
- ✅ Community profile integration
- ✅ Lender background research

## This is NOT for:

- ❌ Bank merger goal setting → Use `reports/Local Markets Analyses/`
- ❌ CBA banks analysis → Use `reports/cba_banks/`
- ❌ Worst lenders ranking → Use `reports/worst_lenders/`
- ❌ General merger analysis → Use `scripts/merger_analysis_framework.py`

## Quick Reference

**To create a new Member Report:**
1. Copy `scripts/create_tampa_report.py` as template
2. Modify for your location
3. Run the script
4. Output goes to `outputs/[Location]_[Member]/`

**See main documentation:**
- `README.md` - Full system overview
- `QUICK_START.md` - Quick reference
- `REPORT_WRITING_QUICK_REFERENCE.md` - Writing guidelines

**For other report types, see:**
- `../../REPORT_TYPE_MAPPING.md` - Complete mapping guide
- `../../QUICK_REPORT_REFERENCE.md` - Quick lookup

---

**Note:** This folder (`Member Reports/`) at the root level is the PRIMARY location. There is a duplicate at `reports/Member Reports/` which should not be used for new work.

