import os
import shutil
from pathlib import Path

project_root = Path.cwd()
print(f"Reorganizing project in: {project_root}")

# Create directories
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
    "scripts"
]

print("\n1. Creating folders...")
for dir_path in directories:
    (project_root / dir_path).mkdir(parents=True, exist_ok=True)
    print(f"   {dir_path}")

# Move files
moves = []

# Python scripts
for script in ["fifth_third_cba_report.py", "generate_fifth_third_report.py", "ncrc_worst_lenders_analysis_v4.py", 
               "cba_banks_analysis_v4_FINAL.py", "find_top_cbsas.py", "check_excel_sheets.py"]:
    if (project_root / script).exists():
        moves.append((script, f"scripts/{script}"))

# SQL files
for sql in ["FIFTH_THIRD_COMBINED_FULL_QUERY.sql", "FIFTH_THIRD_DEMOGRAPHICS_QUERY.sql", 
            "FIFTH_THIRD_REDLINING_FULL_QUERY.sql", "fifth_third_top_cbsas.sql", 
            "fifth_third_tract_demographics_query.sql"]:
    if (project_root / sql).exists():
        moves.append((sql, f"queries/fifth_third/{sql}"))

# Excel reports
for report, folder in [("Fifth_Third_CBA_Report.xlsx", "reports/fifth_third"), 
                        ("CBA_Banks_Analysis.xlsx", "reports/cba_banks"),
                        ("NCRC_Worst_Lenders_Analysis.xlsx", "reports/worst_lenders")]:
    if (project_root / report).exists():
        moves.append((report, f"{folder}/{report}"))

# CSV files
for csv in ["bquxjob_23df12f4_19a37d0b6c8.csv", "bquxjob_4acd409e_19a380e9436.csv", 
            "bquxjob_6ea7f286_19a37c2dff0.csv", "bquxjob_CBA_Bank_Data.csv", 
            "bquxjob_Worst_Lenders_Data.csv"]:
    if (project_root / csv).exists():
        moves.append((csv, f"data/raw/{csv}"))

if (project_root / "data/bquxjob_6b80582_19a3827d225.csv").exists():
    moves.append(("data/bquxjob_6b80582_19a3827d225.csv", "data/raw/bquxjob_6b80582_19a3827d225.csv"))

for ref in ["CBSA_to_County_Mapping.csv", "Lenders_and_LEI_Numbers.csv"]:
    if (project_root / ref).exists():
        moves.append((ref, f"data/reference/{ref}"))

# Batch files
for batch in ["install_packages.bat", "run_cmd.bat", "run_find_cbsas.bat"]:
    if (project_root / batch).exists():
        moves.append((batch, f"batch/{batch}"))

# Tests
for test in ["test_connection.py", "test_simple.py"]:
    if (project_root / test).exists():
        moves.append((test, f"tests/{test}"))

# Docs - guides
for doc in ["QUICK_START_FIFTH_THIRD.md", "RUN_FIFTH_THIRD_REPORT.md", "HOW_TO_ASK_FOR_HMDA_QUERIES.md", 
            "GITHUB_AUTH_GUIDE.md", "GITHUB_COMMANDS.md"]:
    if (project_root / doc).exists():
        moves.append((doc, f"docs/guides/{doc}"))

# Docs - technical
for doc in ["TRACT_DEMOGRAPHIC_METRICS_REQUIREMENTS.md", "FINAL_IMPLEMENTATION_SUMMARY.md", 
            "IMPLEMENTATION_SUMMARY.md"]:
    if (project_root / doc).exists():
        moves.append((doc, f"docs/technical/{doc}"))

# Docs - archive
for doc in ["DO_THIS_NOW.md", "RUN_THIS.txt", "RUN_THIS_NOW.txt", "STEP_BY_STEP.txt", 
            "CURSOR_SETTINGS_FIX.md", "POWERSHELL_ISSUE_STATUS.md", "POWERSHELL_WRAPPER_INVESTIGATION.md",
            "README_FOLDER_STRUCTURE.md", "README_FOR_CURSOR_TERMINAL_ISSUE.md", "SESSION_SUMMARY.md",
            "SETUP_FOLDERS.md", "TERMINAL_ISSUE_SUMMARY.md", "USER_NEXT_STEPS.md", "FINAL_INSTRUCTIONS.md"]:
    if (project_root / doc).exists():
        moves.append((doc, f"docs/archive/{doc}"))

# Credentials
if (project_root / "hdma1-242116-74024e2eb88f.json").exists():
    moves.append(("hdma1-242116-74024e2eb88f.json", "config/credentials/hdma1-242116-74024e2eb88f.json"))

# Archive NCRC-Big-Query-Access
if (project_root / "NCRC-Big-Query-Access").exists():
    moves.append(("NCRC-Big-Query-Access", "archive/NCRC-Big-Query-Access"))

# HTML files
html_file = "Connecting to BigQuery with service account - Claude.html"
if (project_root / html_file).exists():
    moves.append((html_file, f"docs/archive/{html_file}"))

html_folder = "Connecting to BigQuery with service account - Claude_files"
if (project_root / html_folder).exists():
    moves.append((html_folder, f"docs/archive/{html_folder}"))

print(f"\n2. Moving {len(moves)} files...")
moved = 0
for src, dst in moves:
    src_path = project_root / src
    dst_path = project_root / dst
    if src_path.exists():
        try:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(dst_path))
            print(f"   {src} -> {dst}")
            moved += 1
        except Exception as e:
            print(f"   ERROR {src}: {e}")
    else:
        print(f"   SKIP {src} (not found)")

print(f"\n3. Moved {moved} files successfully!")
print("Done!")
