"""
Reorganize DREAM project into four main report folders:
1. Merger Report
2. Underperforming Lenders Analysis  
3. Member Report
4. CBA Bank Analysis

EXECUTES THE REORGANIZATION - removes old files/folders from root
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\DREAM")

# Define the four report folders
REPORT_FOLDERS = {
    "1_Merger_Report": {
        "description": "Merger Report - Compares two banks, sets mortgage goals, compares small business, analyzes branches",
        "files_to_move": {
            "scripts": [
                "goal_setting_analysis_main.py",
                "goal_setting_analysis_workflow.py",
                "setup_merger_folder.py",
                "create_huntington_cadence_ticket.py",
                "inspect_sample_goal_analysis.py",
            ],
            "queries": [
                "goal_setting_hmda_query_builder.py",
                "goal_setting_hmda_query.sql",
            ],
            "reports_src": "reports/Local Markets Analyses",
            "utils_src": "reports/Local Markets Analyses/_shared",
            "docs": [
                "docs/guides/LOCAL_MARKET_ANALYSIS_QUICK_REFERENCE.md",
                "docs/guides/LOCAL_MARKET_GOAL_SETTING_ANALYSIS.md",
                "docs/guides/GOAL_SETTING_REQUIREMENTS.md",
                "docs/guides/GOAL_SETTING_COMPLETE_REQUIREMENTS.md",
                "docs/reference/HUNTINGTON_CADENCE_GOAL_SETTING_GUIDE.md",
            ]
        }
    },
    "2_Underperforming_Lenders_Analysis": {
        "description": "Underperforming Lenders Analysis - Worst lenders across geographic/temporal periods (mortgages only)",
        "files_to_move": {
            "scripts": [
                "01_worst_lenders_analysis_v2.py",
                "worst_lenders_analysis.py",
                "ncrc_worst_lenders_analysis_v4.py",
                "06_validate_worst_lenders_data_v2.py",
            ],
            "queries": [
                "worst_lenders_redlining_query.sql",
                "worst_lenders_redlining_query_v2.sql",
            ],
            "reports_src": "reports/worst_lenders",
            "docs": [
                "docs/reference/WORST_LENDERS_ANALYSIS_GUIDE.md",
            ]
        }
    },
    "3_Member_Report": {
        "description": "Member Report - Reports for NCRC members (mortgage, small business, branches as needed)",
        "files_to_move": {
            "member_reports_src": "Member Reports",  # Move entire folder
        }
    },
    "4_CBA_Bank_Analysis": {
        "description": "CBA Bank Analysis - Specific bank across metros/years by mortgage and small business since CBA",
        "files_to_move": {
            "scripts": [
                "cba_banks_analysis_v4_FINAL.py",
                "02_fifth_third_cba_report.py",
                "comerica_cba_report.py",
                "fifth_third_sb_report.py",
                "generate_fifth_third_report.py",
                "test_cba_ticket_parsing.py",
                "inspect_cba_ticket.py",
            ],
            "queries": [
                "fifth_third",
                "comerica",
                "sb",
            ],
            "reports_src": ["reports/cba_banks", "reports/fifth_third_merger"],
            "docs": [
                "docs/reference/GETTING_STARTED.md",
            ]
        }
    }
}

# Files/folders to keep at root
KEEP_AT_ROOT = {
    "config",
    "data/reference",
    "Lending and Branch Analysis",
    "utils",
    "tests",
    "requirements.txt",
    "README.md",
    "REPORT_TYPE_MAPPING.md",
    "QUICK_REPORT_REFERENCE.md",
    "docs",
    "archive",
}

# Files/folders to remove from root after reorganization
REMOVE_FROM_ROOT = [
    "scripts",  # Will be moved to report folders
    "queries",  # Will be moved to report folders
    "reports",  # Will be moved to report folders
    "Member Reports",  # Will be moved to 3_Member_Report
    "batch",  # Old batch scripts
    "reorganize_dream.py",  # Old reorganization script
    "Worst_Lenders_Analysis_v2.xlsx",  # If exists at root
    "workspace",  # If empty/unused
    "CREATE_SYMBOLIC_LINK.bat",
    "README_POWERSHELL_FIX.md",
    "reorganize_to_four_reports.py",  # This script itself (move to archive at end)
]

def create_folder_structure(report_folder_path):
    """Create standard subfolder structure for a report"""
    subfolders = ["data", "queries", "scripts", "utils", "docs", "reports"]
    for subfolder in subfolders:
        (report_folder_path / subfolder).mkdir(parents=True, exist_ok=True)

def move_file_safely(source, dest, dry_run=False):
    """Move a file safely, creating parent directories if needed"""
    source_path = BASE_DIR / source if not Path(source).is_absolute() else Path(source)
    dest_path = BASE_DIR / dest if not Path(dest).is_absolute() else Path(dest)
    
    if not source_path.exists():
        print(f"  WARNING: Source not found: {source_path}")
        return False
    
    if dry_run:
        print(f"  [DRY RUN] Would move: {source_path} -> {dest_path}")
        return True
    
    # Create parent directory
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Move file
    try:
        if dest_path.exists():
            # Rename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = dest_path.stem
            suffix = dest_path.suffix
            dest_path = dest_path.parent / f"{stem}_{timestamp}{suffix}"
        
        shutil.move(str(source_path), str(dest_path))
        print(f"  OK Moved: {source_path.name} -> {dest_path}")
        return True
    except Exception as e:
        print(f"  ERROR moving {source_path}: {e}")
        return False

def move_folder_safely(source, dest, dry_run=False):
    """Move an entire folder safely"""
    source_path = BASE_DIR / source if not Path(source).is_absolute() else Path(source)
    dest_path = BASE_DIR / dest if not Path(dest).is_absolute() else Path(dest)
    
    if not source_path.exists():
        print(f"  ⚠️  Source folder not found: {source_path}")
        return False
    
    if dry_run:
        print(f"  [DRY RUN] Would move folder: {source_path} -> {dest_path}")
        return True
    
    # Create parent directory
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Move folder
    try:
        if dest_path.exists():
            # Rename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_path = dest_path.parent / f"{dest_path.name}_{timestamp}"
        
        shutil.move(str(source_path), str(dest_path))
        print(f"  OK Moved folder: {source_path.name} -> {dest_path}")
        return True
    except Exception as e:
        print(f"  ERROR moving folder {source_path}: {e}")
        return False

def copy_folder_contents(source, dest, dry_run=False):
    """Copy all contents from source folder to dest folder"""
    source_path = BASE_DIR / source if not Path(source).is_absolute() else Path(source)
    dest_path = BASE_DIR / dest if not Path(dest).is_absolute() else Path(dest)
    
    if not source_path.exists() or not source_path.is_dir():
        print(f"  ⚠️  Source folder not found: {source_path}")
        return False
    
    if dry_run:
        print(f"  [DRY RUN] Would copy contents from: {source_path} -> {dest_path}")
        return True
    
    dest_path.mkdir(parents=True, exist_ok=True)
    
    try:
        for item in source_path.iterdir():
            dest_item = dest_path / item.name
            if item.is_dir():
                if dest_item.exists():
                    # Merge folders recursively
                    for subitem in item.rglob('*'):
                        rel_path = subitem.relative_to(item)
                        dest_subitem = dest_item / rel_path
                        dest_subitem.parent.mkdir(parents=True, exist_ok=True)
                        if subitem.is_file():
                            shutil.copy2(subitem, dest_subitem)
                else:
                    shutil.copytree(str(item), str(dest_item))
            else:
                shutil.copy2(str(item), str(dest_item))
        print(f"  OK Copied contents: {source_path} -> {dest_path}")
        return True
    except Exception as e:
        print(f"  ERROR copying contents {source_path}: {e}")
        return False

def organize_report(report_name, report_config, dry_run=False):
    """Organize files for a specific report type"""
    print(f"\n{'='*80}")
    print(f"ORGANIZING: {report_name}")
    print(f"Description: {report_config['description']}")
    print(f"{'='*80}")
    
    report_folder = BASE_DIR / report_name
    create_folder_structure(report_folder)
    
    files_config = report_config["files_to_move"]
    
    # Move scripts
    if "scripts" in files_config:
        print("\n[MOVING SCRIPTS - TEMPLATES]")
        for script in files_config["scripts"]:
            source = f"scripts/{script}"
            dest = f"{report_name}/scripts/{script}"
            move_file_safely(source, dest, dry_run)
    
    # Move queries
    if "queries" in files_config:
        print("\n[MOVING QUERIES - TEMPLATES]")
        for query in files_config["queries"]:
            source = f"queries/{query}"
            dest = f"{report_name}/queries/{query}"
            if Path(BASE_DIR / source).is_file():
                move_file_safely(source, dest, dry_run)
            elif Path(BASE_DIR / source).is_dir():
                move_folder_safely(source, dest, dry_run)
    
    # Move utils from shared folder
    if "utils_src" in files_config:
        print("\n[MOVING UTILS]")
        utils_src = files_config["utils_src"]
        if Path(BASE_DIR / utils_src / "utils").exists():
            copy_folder_contents(f"{utils_src}/utils", f"{report_name}/utils", dry_run)
        if Path(BASE_DIR / utils_src / "queries").exists():
            copy_folder_contents(f"{utils_src}/queries", f"{report_name}/queries", dry_run)
    
    # Move reports folder contents (not the folder itself - merge into reports/)
    if "reports_src" in files_config:
        print("\n[MOVING REPORTS]")
        reports_src = files_config["reports_src"]
        if isinstance(reports_src, list):
            for report_path in reports_src:
                src_path = BASE_DIR / report_path
                if src_path.exists() and src_path.is_dir():
                    # Move contents of the reports folder
                    for item in src_path.iterdir():
                        dest_item = BASE_DIR / report_name / "reports" / item.name
                        if item.is_dir():
                            move_folder_safely(str(item), str(dest_item), dry_run)
                        else:
                            move_file_safely(str(item), str(dest_item), dry_run)
        else:
            src_path = BASE_DIR / reports_src
            if src_path.exists() and src_path.is_dir():
                # Move contents of the reports folder
                for item in src_path.iterdir():
                    dest_item = BASE_DIR / report_name / "reports" / item.name
                    if item.is_dir():
                        move_folder_safely(str(item), str(dest_item), dry_run)
                    else:
                        move_file_safely(str(item), str(dest_item), dry_run)
    
    # Move entire member reports folder
    if "member_reports_src" in files_config:
        print("\n[MOVING MEMBER REPORTS FOLDER]")
        member_reports_src = files_config["member_reports_src"]
        # Copy the entire folder structure
        copy_folder_contents(member_reports_src, report_name, dry_run)
        # Move outputs to reports
        outputs_path = BASE_DIR / report_name / "outputs"
        reports_path = BASE_DIR / report_name / "reports"
        if outputs_path.exists():
            print("\n[MOVING OUTPUTS TO REPORTS]")
            if not dry_run:
                # Move all contents from outputs to reports
                for item in outputs_path.iterdir():
                    dest_item = reports_path / item.name
                    if item.is_dir():
                        if dest_item.exists():
                            # Merge folders
                            for subitem in item.rglob('*'):
                                rel_path = subitem.relative_to(item)
                                dest_subitem = dest_item / rel_path
                                dest_subitem.parent.mkdir(parents=True, exist_ok=True)
                                if subitem.is_file():
                                    shutil.copy2(subitem, dest_subitem)
                        else:
                            shutil.move(str(item), str(dest_item))
                    else:
                        shutil.move(str(item), str(dest_item))
                # Try to remove empty outputs folder
                if outputs_path.exists():
                    try:
                        if not list(outputs_path.iterdir()):
                            outputs_path.rmdir()
                            print(f"  OK Removed empty outputs/ folder")
                        else:
                            print(f"  WARNING: outputs/ folder still has content, leaving it")
                    except (OSError, PermissionError) as e:
                        print(f"  WARNING: Could not remove outputs/ folder: {e}")
                print(f"  OK Moved outputs/ contents to reports/")
            else:
                print(f"  [DRY RUN] Would move outputs/ contents to reports/")
    
    # Move docs
    if "docs" in files_config:
        print("\n[MOVING DOCS]")
        for doc in files_config["docs"]:
            source = doc
            dest = f"{report_name}/docs/{Path(doc).name}"
            move_file_safely(source, dest, dry_run)
    
    # Create README
    readme_content = f"""# {report_name.replace('_', ' ').title()}

{report_config['description']}

## Structure

```
{report_name}/
├── data/          # Template data files only (reusable)
├── queries/       # Template queries only (reusable)
├── scripts/       # Template/utility scripts only (reusable)
├── utils/         # Utility functions only (reusable)
├── docs/          # Documentation
└── reports/       # All generated reports stored here
    ├── ReportName_YYYYMMDD/    # Each report has its own folder
    │   ├── [report files]
    │   ├── data/          # Actual data files for this specific report
    │   ├── queries/       # Actual queries used for this report
    │   ├── scripts/       # Scripts used to generate this report
    │   ├── supporting_files/
    │   └── data_exports/
    └── ...
```

Note: Top-level folders contain ONLY templates and reusable components.
Actual data, queries, and scripts for each specific report are stored
inside that report's folder under reports/.
"""

    readme_path = report_folder / "README.md"
    if not dry_run:
        readme_path.write_text(readme_content, encoding='utf-8')
        print(f"\nOK Created README.md for {report_name}")

def cleanup_root(dry_run=False):
    """Remove files and folders from root that are no longer needed"""
    print("\n" + "="*80)
    print("CLEANING UP ROOT FOLDER")
    print("="*80)
    
    archive_dir = BASE_DIR / "archive" / "reorganization_cleanup"
    if not dry_run:
        archive_dir.mkdir(parents=True, exist_ok=True)
    
    for item_name in REMOVE_FROM_ROOT:
        item_path = BASE_DIR / item_name
        
        if not item_path.exists():
            continue
        
        if dry_run:
            print(f"  [DRY RUN] Would remove: {item_path}")
            continue
        
        try:
            if item_path.is_file():
                # Move to archive instead of deleting
                archive_item = archive_dir / item_path.name
                shutil.move(str(item_path), str(archive_item))
                print(f"  OK Archived: {item_path.name} -> archive/reorganization_cleanup/")
            elif item_path.is_dir():
                # Check if folder is empty or only contains expected leftovers
                if item_path.name == "reports":
                    # Check if reports folder has any remaining content
                    remaining = [f for f in item_path.iterdir() if f.name not in ["Member Reports"]]
                    if remaining:
                        print(f"  WARNING: Reports folder still has content: {[f.name for f in remaining]}")
                        # Move remaining to archive
                        for rem in remaining:
                            archive_rem = archive_dir / item_path.name / rem.name
                            archive_rem.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(rem), str(archive_rem))
                        print(f"  OK Archived remaining reports content")
                
                # Remove empty folders
                try:
                    item_path.rmdir()
                    print(f"  OK Removed empty folder: {item_path.name}")
                except OSError:
                    # Not empty, move to archive
                    archive_item = archive_dir / item_path.name
                    if archive_item.exists():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        archive_item = archive_dir / f"{item_path.name}_{timestamp}"
                    shutil.move(str(item_path), str(archive_item))
                    print(f"  OK Archived folder: {item_path.name} -> archive/reorganization_cleanup/")
        except Exception as e:
            print(f"  ERROR removing {item_path}: {e}")

def main():
    """Main reorganization function"""
    print("="*80)
    print("DREAM PROJECT REORGANIZATION")
    print("Organizing into 4 main report folders")
    print("="*80)
    print("\nWARNING: EXECUTING REORGANIZATION")
    print("Files will be moved and root will be cleaned up")
    
    # Organize each report
    for report_name, report_config in REPORT_FOLDERS.items():
        organize_report(report_name, report_config, dry_run=False)
    
    # Cleanup root
    cleanup_root(dry_run=False)
    
    # Move this script to archive
    script_path = BASE_DIR / "reorganize_to_four_reports.py"
    if script_path.exists():
        archive_script = BASE_DIR / "archive" / "reorganization_cleanup" / "reorganize_to_four_reports.py"
        archive_script.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(script_path), str(archive_script))
        print(f"\nOK Moved reorganization script to archive")
    
    print("\n" + "="*80)
    print("REORGANIZATION COMPLETE!")
    print("="*80)
    print("\nNext steps:")
    print("1. Verify the four report folders are created correctly")
    print("2. Check that reports are in the reports/ subfolder of each")
    print("3. Update any hardcoded paths in scripts")
    print("4. Test each report type to ensure they work")

if __name__ == "__main__":
    main()
