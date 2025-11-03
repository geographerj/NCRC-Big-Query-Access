"""
COMPREHENSIVE FILE REORGANIZATION SCRIPT
Run this script manually: python MOVE_FILES_NOW.py

This will move all files to their new organized locations.
"""

import os
import shutil
from pathlib import Path

project_root = Path(__file__).parent.absolute()

print("="*80)
print("DREAM ANALYSIS PROJECT REORGANIZATION")
print("="*80)
print(f"Working directory: {project_root}\n")

# Track moves
moves_made = []
errors = []

def move_file(src, dst):
    """Move a file/folder with error handling"""
    src_path = project_root / src
    dst_path = project_root / dst
    
    if not src_path.exists():
        print(f"  SKIP: {src} (not found)")
        return False
    
    try:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dst_path))
        print(f"  ✓ {src} -> {dst}")
        moves_made.append((src, dst))
        return True
    except Exception as e:
        error_msg = f"  ✗ ERROR moving {src}: {e}"
        print(error_msg)
        errors.append((src, dst, str(e)))
        return False

print("1. Moving Python scripts to scripts/...")
scripts = [
    "fifth_third_cba_report.py",
    "generate_fifth_third_report.py", 
    "ncrc_worst_lenders_analysis_v4.py",
    "cba_banks_analysis_v4_FINAL.py",
    "find_top_cbsas.py",
    "check_excel_sheets.py"
]
for script in scripts:
    move_file(script, f"scripts/{script}")

print("\n2. Moving SQL queries to queries/fifth_third/...")
sql_files = [
    "FIFTH_THIRD_COMBINED_FULL_QUERY.sql",
    "FIFTH_THIRD_DEMOGRAPHICS_QUERY.sql",
    "FIFTH_THIRD_REDLINING_FULL_QUERY.sql",
    "fifth_third_top_cbsas.sql",
    "fifth_third_tract_demographics_query.sql"
]
for sql_file in sql_files:
    move_file(sql_file, f"queries/fifth_third/{sql_file}")

print("\n3. Moving Excel reports...")
reports = [
    ("Fifth_Third_CBA_Report.xlsx", "reports/fifth_third/"),
    ("CBA_Banks_Analysis.xlsx", "reports/cba_banks/"),
    ("NCRC_Worst_Lenders_Analysis.xlsx", "reports/worst_lenders/"),
]
for report, folder in reports:
    move_file(report, f"{folder}{report}")

# Also move the one in reports/ subfolder
if (project_root / "reports" / "Fifth_Third_CBA_Report.xlsx").exists():
    move_file("reports/Fifth_Third_CBA_Report.xlsx", "reports/fifth_third/Fifth_Third_CBA_Report.xlsx")

print("\n4. Moving CSV data files to data/raw/...")
csv_files = [
    "bquxjob_23df12f4_19a37d0b6c8.csv",
    "bquxjob_4acd409e_19a380e9436.csv",
    "bquxjob_6ea7f286_19a37c2dff0.csv",
    "bquxjob_CBA_Bank_Data.csv",
    "bquxjob_Worst_Lenders_Data.csv"
]
for csv_file in csv_files:
    move_file(csv_file, f"data/raw/{csv_file}")

# Move CSV from data/ subfolder
if (project_root / "data" / "bquxjob_6b80582_19a3827d225.csv").exists():
    move_file("data/bquxjob_6b80582_19a3827d225.csv", "data/raw/bquxjob_6b80582_19a3827d225.csv")

print("\n5. Moving reference CSV files to data/reference/...")
ref_csvs = [
    "CBSA_to_County_Mapping.csv",
    "Lenders_and_LEI_Numbers.csv"
]
for ref_csv in ref_csvs:
    move_file(ref_csv, f"data/reference/{ref_csv}")

print("\n6. Moving batch files to batch/...")
batch_files = [
    "install_packages.bat",
    "run_cmd.bat",
    "run_find_cbsas.bat"
]
for batch_file in batch_files:
    move_file(batch_file, f"batch/{batch_file}")

# Move batch files from subfolders
if (project_root / "scripts" / "run_excel_generator.bat").exists():
    move_file("scripts/run_excel_generator.bat", "batch/run_excel_generator.bat")

if (project_root / "reports" / "@@run_excel_generator.bat").exists():
    move_file("reports/@@run_excel_generator.bat", "batch/run_excel_generator_old.bat")

print("\n7. Moving test files to tests/...")
test_files = [
    "test_connection.py",
    "test_simple.py"
]
for test_file in test_files:
    move_file(test_file, f"tests/{test_file}")

print("\n8. Moving documentation files...")
guide_docs = [
    "QUICK_START_FIFTH_THIRD.md",
    "RUN_FIFTH_THIRD_REPORT.md",
    "HOW_TO_ASK_FOR_HMDA_QUERIES.md",
    "GITHUB_AUTH_GUIDE.md",
    "GITHUB_COMMANDS.md"
]
for doc in guide_docs:
    move_file(doc, f"docs/guides/{doc}")

technical_docs = [
    "TRACT_DEMOGRAPHIC_METRICS_REQUIREMENTS.md",
    "FINAL_IMPLEMENTATION_SUMMARY.md",
    "IMPLEMENTATION_SUMMARY.md"
]
for doc in technical_docs:
    move_file(doc, f"docs/technical/{doc}")

archive_docs = [
    "DO_THIS_NOW.md",
    "RUN_THIS.txt",
    "RUN_THIS_NOW.txt",
    "STEP_BY_STEP.txt",
    "CURSOR_SETTINGS_FIX.md",
    "POWERSHELL_ISSUE_STATUS.md",
    "POWERSHELL_WRAPPER_INVESTIGATION.md",
    "README_FOLDER_STRUCTURE.md",
    "README_FOR_CURSOR_TERMINAL_ISSUE.md",
    "SESSION_SUMMARY.md",
    "SETUP_FOLDERS.md",
    "TERMINAL_ISSUE_SUMMARY.md",
    "USER_NEXT_STEPS.md",
    "FINAL_INSTRUCTIONS.md"
]
for doc in archive_docs:
    move_file(doc, f"docs/archive/{doc}")

print("\n9. Moving credentials to config/credentials/...")
move_file("hdma1-242116-74024e2eb88f.json", "config/credentials/hdma1-242116-74024e2eb88f.json")

print("\n10. Archiving NCRC-Big-Query-Access folder...")
if (project_root / "NCRC-Big-Query-Access").exists():
    move_file("NCRC-Big-Query-Access", "archive/NCRC-Big-Query-Access")

print("\n11. Moving HTML documentation...")
if (project_root / "Connecting to BigQuery with service account - Claude.html").exists():
    move_file("Connecting to BigQuery with service account - Claude.html", 
              "docs/archive/Connecting to BigQuery with service account - Claude.html")

if (project_root / "Connecting to BigQuery with service account - Claude_files").exists():
    move_file("Connecting to BigQuery with service account - Claude_files",
              "docs/archive/Connecting to BigQuery with service account - Claude_files")

# Move reorganization scripts themselves to batch folder
print("\n12. Cleaning up reorganization scripts...")
reorg_scripts = [
    "reorganize_project.py",
    "_execute_reorganize.py",
    "run_reorganize.bat"
]
for script in reorg_scripts:
    if (project_root / script).exists():
        move_file(script, f"batch/{script}")

print("\n" + "="*80)
print("REORGANIZATION COMPLETE!")
print("="*80)
print(f"\nFiles moved: {len(moves_made)}")
if errors:
    print(f"Errors: {len(errors)}")
    print("\nErrors encountered:")
    for src, dst, err in errors:
        print(f"  {src}: {err}")
else:
    print("No errors!")

print("\nNext steps:")
print("1. Review the moved files in their new locations")
print("2. Update any hardcoded paths in scripts if needed")
print("3. Test that scripts still work from new locations")
print("4. Update .gitignore to exclude config/credentials/")
print("5. Commit changes to git")

