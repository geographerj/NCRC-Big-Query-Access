# DREAM Project Reorganization Plan

## Goal
Organize all files into four main report folders at root level:
1. **Merger Report**
2. **Underperforming Lenders Analysis**
3. **Member Report**
4. **CBA Bank Analysis**

## Key Principle

**Top-level folders (data/, queries/, scripts/, utils/) contain ONLY templates and reusable components.**

**Actual data files, queries, scripts used for a specific report are stored INSIDE that report's folder under reports/**

Each report folder structure:
```
reports/ReportName_YYYYMMDD/
├── [report Excel/PDF]
├── data/          # Actual data files for this specific report
├── queries/       # Actual queries used for this report
├── scripts/       # Scripts used to generate this report
├── supporting_files/
└── data_exports/
```

## Folder Structure

```
C:\DREAM\
├── 1_Merger_Report\
│   ├── data\             # Template data files only (reusable)
│   ├── queries\          # Template queries only (reusable)
│   ├── scripts\          # Template/utility scripts only (reusable)
│   ├── utils\            # Utility functions only (reusable)
│   ├── docs\             # Documentation
│   └── reports\          # All merger reports stored here
│       ├── YYMMDD_BankA_BankB_Merger\
│       │   ├── [report Excel]
│       │   ├── data\             # Actual data files for this report
│       │   ├── queries\           # Actual queries used for this report
│       │   ├── scripts\            # Scripts used to generate this report
│       │   ├── supporting_files\
│       │   └── data_exports\
│       └── ...
│
├── 2_Underperforming_Lenders_Analysis\
│   ├── data\             # Template data files only (reusable)
│   ├── queries\          # Template queries only (reusable)
│   ├── scripts\          # Template/utility scripts only (reusable)
│   ├── utils\            # Utility functions only (reusable)
│   ├── docs\             # Documentation
│   └── reports\          # All underperforming lenders reports stored here
│       ├── YYYYMMDD_Analysis_Name\
│       │   ├── [report Excel]
│       │   ├── data\             # Actual data files for this report
│       │   ├── queries\           # Actual queries used for this report
│       │   ├── scripts\            # Scripts used to generate this report
│       │   ├── supporting_files\
│       │   └── data_exports\
│       └── ...
│
├── 3_Member_Report\
│   ├── data\             # Template data files only (reusable)
│   ├── queries\          # Template queries only (reusable)
│   ├── scripts\          # Template/utility scripts only (reusable)
│   ├── utils\            # Utility functions only (reusable)
│   ├── docs\             # Documentation
│   ├── generators\        # Template generators (reusable)
│   ├── configs\          # Template configs (reusable)
│   └── reports\          # All member reports stored here
│       ├── Location_MemberName\
│       │   ├── [PDF report]
│       │   ├── [Excel data]
│       │   ├── data\             # Actual data files for this report
│       │   ├── queries\           # Actual queries used for this report
│       │   ├── scripts\            # Scripts used to generate this report
│       │   ├── supporting_files\
│       │   └── data_exports\
│       └── ...
│
├── 4_CBA_Bank_Analysis\
│   ├── data\             # Template data files only (reusable)
│   ├── queries\          # Template queries only (reusable)
│   ├── scripts\          # Template/utility scripts only (reusable)
│   ├── utils\            # Utility functions only (reusable)
│   ├── docs\             # Documentation
│   └── reports\          # All CBA bank reports stored here
│       ├── BankName_CBA_YYYYMMDD\
│       │   ├── [report Excel]
│       │   ├── data\             # Actual data files for this report
│       │   ├── queries\           # Actual queries used for this report
│       │   ├── scripts\            # Scripts used to generate this report
│       │   ├── supporting_files\
│       │   └── data_exports\
│       └── ...
│
├── config\                    [SHARED - stays at root]
├── data\
│   └── reference\            [SHARED - stays at root]
├── Lending and Branch Analysis\  [SHARED - stays at root]
├── utils\                     [SHARED - stays at root]
├── tests\                     [SHARED - stays at root]
├── docs\                      [SHARED - general docs]
├── archive\                   [ARCHIVE - old files]
└── requirements.txt           [SHARED - stays at root]
```

## File Assignments

### 1. Merger Report
**Location**: `1_Merger_Report/`

**Scripts** (Templates/Utilities only):
- `scripts/goal_setting_analysis_main.py` - Main template script
- `scripts/goal_setting_analysis_workflow.py` - Workflow template
- `scripts/setup_merger_folder.py` - Utility for creating report folders
- `scripts/create_huntington_cadence_ticket.py` - Example template
- `scripts/inspect_sample_goal_analysis.py` - Utility script

**Queries** (Templates only):
- `queries/goal_setting_hmda_query_builder.py` - Query builder template
- `queries/goal_setting_hmda_query.sql` - Query template

**Reports Folder**:
- `reports/Local Markets Analyses/` → move contents to `1_Merger_Report/reports/`
  - Each merger analysis already has its own dated folder (YYMMDD_BankA_BankB_Merger)
  - Each report folder contains: Excel + data/ + queries/ + scripts/ + supporting_files + data_exports
  - Actual data/queries/scripts for each report stay in that report's folder

**Docs**:
- `docs/guides/LOCAL_MARKET_ANALYSIS_QUICK_REFERENCE.md`
- `docs/guides/LOCAL_MARKET_GOAL_SETTING_ANALYSIS.md`
- `docs/guides/GOAL_SETTING_REQUIREMENTS.md`
- `docs/guides/GOAL_SETTING_COMPLETE_REQUIREMENTS.md`
- `docs/reference/HUNTINGTON_CADENCE_GOAL_SETTING_GUIDE.md`

**Utils** (from shared folder):
- `reports/Local Markets Analyses/_shared/utils/` → `1_Merger_Report/utils/`
- `reports/Local Markets Analyses/_shared/queries/` → `1_Merger_Report/queries/`

---

### 2. Underperforming Lenders Analysis
**Location**: `2_Underperforming_Lenders_Analysis/`

**Scripts** (Templates/Utilities only):
- `scripts/01_worst_lenders_analysis_v2.py` - Main template script
- `scripts/worst_lenders_analysis.py` - Legacy template
- `scripts/ncrc_worst_lenders_analysis_v4.py` - Alternative template
- `scripts/06_validate_worst_lenders_data_v2.py` - Validation utility

**Queries** (Templates only):
- `queries/worst_lenders_redlining_query.sql` - Query template
- `queries/worst_lenders_redlining_query_v2.sql` - Query template v2

**Reports Folder**:
- `reports/worst_lenders/` → move contents to `2_Underperforming_Lenders_Analysis/reports/`
  - Each analysis should have its own folder with name including date/identifier
  - Each report folder contains: Excel + data/ + queries/ + scripts/ + supporting_files + data_exports
  - Actual data/queries/scripts for each report stay in that report's folder

**Docs**:
- `docs/reference/WORST_LENDERS_ANALYSIS_GUIDE.md`

---

### 3. Member Report
**Location**: `3_Member_Report/`

**Entire Folder**:
- `Member Reports/` → moved to `3_Member_Report/` (keeps all subfolders as templates)
  - `Member Reports/scripts/`, `queries/`, `utils/`, `generators/` → templates only
- `Member Reports/outputs/` → move contents to `3_Member_Report/reports/`
  - Each member report already has its own folder (Location_MemberName)
  - Each report folder should contain: PDF + Excel + data/ + queries/ + scripts/ + supporting_files
  - Actual data/queries/scripts for each report stay in that report's folder

**Note**: Remove duplicate `reports/Member Reports/` folder (archive it)

---

### 4. CBA Bank Analysis
**Location**: `4_CBA_Bank_Analysis/`

**Scripts** (Templates/Utilities only):
- `scripts/cba_banks_analysis_v4_FINAL.py` - Main template script
- `scripts/02_fifth_third_cba_report.py` - Template example
- `scripts/comerica_cba_report.py` - Template example
- `scripts/fifth_third_sb_report.py` - Template example
- `scripts/generate_fifth_third_report.py` - Template generator
- `scripts/test_cba_ticket_parsing.py` - Utility script
- `scripts/inspect_cba_ticket.py` - Utility script

**Queries** (Templates only):
- `queries/fifth_third/` (template queries folder)
- `queries/comerica/` (template queries folder)
- `queries/sb/` (template queries folder)

**Reports Folders**:
- `reports/cba_banks/` → move contents to `4_CBA_Bank_Analysis/reports/`
- `reports/fifth_third_merger/` → move contents to `4_CBA_Bank_Analysis/reports/`
  - Each CBA bank report should have its own folder named with bank name and date
  - Each report folder contains: Excel + data/ + queries/ + scripts/ + supporting_files + data_exports
  - Actual data/queries/scripts for each report stay in that report's folder

**Data Files** (Move to templates, NOT individual reports):
- `data/raw/comerica_demographics.csv` → `4_CBA_Bank_Analysis/data/templates/` (if template)
- `data/raw/comerica_redlining.csv` → `4_CBA_Bank_Analysis/data/templates/` (if template)
- Note: Actual data files for specific reports should be in `reports/BankName_CBA_YYYYMMDD/data/`

**Docs**:
- `docs/reference/GETTING_STARTED.md` (if CBA-specific)

---

## Files to Archive

**Move to `archive/unused_scripts/`**:
- Old version scripts (v1, v2, etc.) that have been superseded
- Test scripts not tied to specific reports
- Temporary scripts

**Move to `archive/old_reports/`**:
- `reports/Member Reports/` (duplicate of root Member Reports)
- Old report outputs

**Move to `archive/`**:
- `reorganize_dream.py` (old reorganization script)
- `Worst_Lenders_Analysis_v2.xlsx` (if in root)
- Other loose files at root

---

## Shared Files (Stay at Root)

- `config/` - Credentials and configuration
- `data/reference/` - Reference data (crosswalks, mappings)
- `Lending and Branch Analysis/` - Shared utilities module
- `utils/` - Root-level utilities
- `tests/` - Test scripts
- `requirements.txt`
- `README.md`
- `REPORT_TYPE_MAPPING.md`
- `QUICK_REPORT_REFERENCE.md`
- `docs/AI_REPORT_DECISION_GUIDE.md`
- `docs/guides/` - General guides (not report-specific)

---

## Files to Delete

- Duplicate Member Reports folder: `reports/Member Reports/`
- Old reorganization scripts if not needed
- Temporary files in workspace folder (if empty/unused)

---

## Execution Plan

1. **Create four main folders** with subfolder structure
2. **Move files** according to assignments above
3. **Archive old files** to archive folder
4. **Delete duplicates** (after archiving)
5. **Update path references** in scripts that moved
6. **Create README.md** in each report folder
7. **Update main README.md** to reflect new structure

---

## Post-Reorganization Tasks

1. Test each report type to ensure scripts work with new paths
2. Update any hardcoded paths in scripts
3. Update documentation references
4. Verify all imports work correctly
5. Test BigQuery connections still work

---

**Status**: Planning Phase
**Created**: 2025-01-XX
**Ready for Execution**: Awaiting approval

