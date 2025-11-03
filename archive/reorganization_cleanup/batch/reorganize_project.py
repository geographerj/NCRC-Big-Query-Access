"""
Script to reorganize the DREAM Analysis project folder structure.
This script moves files into organized folders according to the reorganization plan.
"""

import os
import shutil
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.absolute()

print(f"Reorganizing project in: {project_root}")
print("=" * 60)

# Create all necessary directories
directories = [
    "config/credentials",
    "queries/fifth_third",
    "data/raw",
    "data/reference",
    "reports/fifth_third",
    "reports/cba_banks",
    "reports/worst_lenders",
    "reports/archive",
    "batch",
    "tests",
    "docs/guides",
    "docs/technical",
    "docs/archive",
    "archive",
    "scripts"  # Python scripts go here
]

print("\n1. Creating folder structure...")
for dir_path in directories:
    full_path = project_root / dir_path
    full_path.mkdir(parents=True, exist_ok=True)
    print(f"   Created: {dir_path}")

# File movements: (source, destination)
moves = []

# Python scripts -> scripts/
python_scripts = [
    "fifth_third_cba_report.py",
    "generate_fifth_third_report.py",
    "ncrc_worst_lenders_analysis_v4.py",
    "cba_banks_analysis_v4_FINAL.py",
    "find_top_cbsas.py",
    "check_excel_sheets.py"
]

for script in python_scripts:
    if (project_root / script).exists():
        moves.append((script, f"scripts/{script}"))

# SQL queries -> queries/fifth_third/
sql_files = [
    "FIFTH_THIRD_COMBINED_FULL_QUERY.sql",
    "FIFTH_THIRD_DEMOGRAPHICS_QUERY.sql",
    "FIFTH_THIRD_REDLINING_FULL_QUERY.sql",
    "fifth_third_top_cbsas.sql",
    "fifth_third_tract_demographics_query.sql"
]

for sql_file in sql_files:
    if (project_root / sql_file).exists():
        moves.append((sql_file, f"queries/fifth_third/{sql_file}"))

# Excel reports -> reports/ by type
reports = [
    ("Fifth_Third_CBA_Report.xlsx", "reports/fifth_third/"),
    ("CBA_Banks_Analysis.xlsx", "reports/cba_banks/"),
    ("NCRC_Worst_Lenders_Analysis.xlsx", "reports/worst_lenders/")
]

for report_file, dest_folder in reports:
    src = project_root / report_file
    if src.exists():
        moves.append((report_file, f"{dest_folder}{report_file}"))

# Also move the one in reports/ subfolder if different
reports_subfolder = project_root / "reports" / "Fifth_Third_CBA_Report.xlsx"
if reports_subfolder.exists() and not (project_root / "Fifth_Third_CBA_Report.xlsx").exists():
    moves.append(("reports/Fifth_Third_CBA_Report.xlsx", "reports/fifth_third/Fifth_Third_CBA_Report.xlsx"))

# CSV data files -> data/raw/ (BigQuery exports)
csv_files_raw = [
    "bquxjob_23df12f4_19a37d0b6c8.csv",
    "bquxjob_4acd409e_19a380e9436.csv",
    "bquxjob_6ea7f286_19a37c2dff0.csv",
    "bquxjob_CBA_Bank_Data.csv",
    "bquxjob_Worst_Lenders_Data.csv"
]

for csv_file in csv_files_raw:
    if (project_root / csv_file).exists():
        moves.append((csv_file, f"data/raw/{csv_file}"))

# Move CSV from data/ subfolder if exists
data_csv = project_root / "data" / "bquxjob_6b80582_19a3827d225.csv"
if data_csv.exists():
    moves.append(("data/bquxjob_6b80582_19a3827d225.csv", "data/raw/bquxjob_6b80582_19a3827d225.csv"))

# Reference CSV files -> data/reference/
reference_csvs = [
    "CBSA_to_County_Mapping.csv",
    "Lenders_and_LEI_Numbers.csv"
]

for ref_csv in reference_csvs:
    if (project_root / ref_csv).exists():
        moves.append((ref_csv, f"data/reference/{ref_csv}"))

# Batch files -> batch/
batch_files = [
    "install_packages.bat",
    "run_cmd.bat",
    "run_find_cbsas.bat"
]

for batch_file in batch_files:
    if (project_root / batch_file).exists():
        moves.append((batch_file, f"batch/{batch_file}"))

# Move batch files from scripts/ and reports/
if (project_root / "scripts" / "run_excel_generator.bat").exists():
    moves.append(("scripts/run_excel_generator.bat", "batch/run_excel_generator.bat"))

if (project_root / "reports" / "@@run_excel_generator.bat").exists():
    moves.append(("reports/@@run_excel_generator.bat", "batch/run_excel_generator_old.bat"))

# Test files -> tests/
test_files = [
    "test_connection.py",
    "test_simple.py"
]

for test_file in test_files:
    if (project_root / test_file).exists():
        moves.append((test_file, f"tests/{test_file}"))

# Documentation files -> docs/
# Guides
guide_docs = [
    "QUICK_START_FIFTH_THIRD.md",
    "RUN_FIFTH_THIRD_REPORT.md",
    "HOW_TO_ASK_FOR_HMDA_QUERIES.md",
    "GITHUB_AUTH_GUIDE.md",
    "GITHUB_COMMANDS.md"
]

for doc in guide_docs:
    if (project_root / doc).exists():
        moves.append((doc, f"docs/guides/{doc}"))

# Technical docs
technical_docs = [
    "TRACT_DEMOGRAPHIC_METRICS_REQUIREMENTS.md",
    "FINAL_IMPLEMENTATION_SUMMARY.md",
    "IMPLEMENTATION_SUMMARY.md"
]

for doc in technical_docs:
    if (project_root / doc).exists():
        moves.append((doc, f"docs/technical/{doc}"))

# Archive/temporary docs
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
    if (project_root / doc).exists():
        moves.append((doc, f"docs/archive/{doc}"))

# Credentials -> config/credentials/
if (project_root / "hdma1-242116-74024e2eb88f.json").exists():
    moves.append(("hdma1-242116-74024e2eb88f.json", "config/credentials/hdma1-242116-74024e2eb88f.json"))

# Archive the duplicate NCRC-Big-Query-Access folder
if (project_root / "NCRC-Big-Query-Access").exists():
    moves.append(("NCRC-Big-Query-Access", "archive/NCRC-Big-Query-Access"))

# Move HTML file to docs/archive
if (project_root / "Connecting to BigQuery with service account - Claude.html").exists():
    moves.append(("Connecting to BigQuery with service account - Claude.html", 
                  "docs/archive/Connecting to BigQuery with service account - Claude.html"))

# Also move the Claude_files folder if it exists
claude_files = project_root / "Connecting to BigQuery with service account - Claude_files"
if claude_files.exists():
    moves.append(("Connecting to BigQuery with service account - Claude_files", 
                  "docs/archive/Connecting to BigQuery with service account - Claude_files"))

print(f"\n2. Moving {len(moves)} files...")
moved_count = 0
for src, dst in moves:
    src_path = project_root / src
    dst_path = project_root / dst
    
    if not src_path.exists():
        print(f"   SKIP: {src} (not found)")
        continue
    
    try:
        # Create destination directory if needed
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Move the file/folder
        shutil.move(str(src_path), str(dst_path))
        print(f"   MOVED: {src} -> {dst}")
        moved_count += 1
    except Exception as e:
        print(f"   ERROR moving {src}: {e}")

print(f"\n3. Summary: {moved_count} files/folders moved successfully")
print("=" * 60)
print("\nReorganization complete!")
print("\nNext steps:")
print("1. Review the moved files")
print("2. Update any hardcoded paths in scripts")
print("3. Test that scripts still work")
print("4. Commit changes to git")
