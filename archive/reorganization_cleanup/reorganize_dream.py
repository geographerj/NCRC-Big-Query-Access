"""
Reorganize C:/DREAM directory structure for better organization.

This script will:
1. Move root-level PDFs and JSON files to appropriate folders
2. Consolidate duplicate folders
3. Move analysis folders to reports/
4. Clean up temporary/reorganization scripts
5. Organize loose files
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\DREAM")

# Define reorganization mappings
REORGANIZATION_PLAN = {
    # Root-level PDFs → data/raw/pdfs/
    "root_pdfs": {
        "412025 List of Census Tracts - Public File.pdf": "data/raw/pdfs/",
        "7745.pdf": "data/raw/pdfs/",
    },
    
    # Root-level JSON files (assessment areas) → data/reference/
    "root_json": {
        "assessment_areas_extracted_final.json": "data/reference/",
        "assessment_areas_extracted.json": "data/reference/",
        "cadence_assessment_areas_final.json": "data/reference/",
        "cadence_assessment_areas_parsed.json": "data/reference/",
        "cadence_tables_sample.json": "data/reference/",
        "huntington_assessment_areas_final.json": "data/reference/",
        "huntington_assessment_areas_parsed.json": "data/reference/",
    },
    
    # Root-level Excel tickets → data/reference/tickets/
    "root_excel_tickets": {
        "Huntington+Cadence merger research ticket.xlsx": "data/reference/tickets/",
        "assessment_area_template.xlsx": "data/reference/templates/",
    },
    
    # Analysis folders at root → reports/
    "root_analysis_folders": {
        "CBA Bank Analysis": "reports/cba_banks/",
        "Local Market Analysis": "reports/Local Markets Analyses/",  # Consolidate
        "Worst Lenders Analysis": "reports/worst_lenders/",
    },
    
    # Duplicate Member Reports folders → consolidate
    "member_reports": {
        "Member Reports": None,  # Will be handled specially - merge into reports/Member Reports
    },
    
    # Temporary/reorganization scripts → archive/scripts/
    "temp_scripts": {
        "_organize_pnc_files.py": "archive/scripts/",
        "_run_organize.py": "archive/scripts/",
        "execute_now.py": "archive/scripts/",
        "execute_organize_files_inline.py": "archive/scripts/",
        "organize_pnc_files_DIRECT.py": "archive/scripts/",
        "organize_pnc_onedrive_files.py": "archive/scripts/",
        "run_organize_now.py": "archive/scripts/",
        "RUN_REORGANIZATION.bat": "archive/scripts/",
    },
    
    # Test/debug files → archive/tests/
    "test_files": {
        "TEST_APOSTROPHE_FIX.bat": "archive/tests/",
        "TEST_PATH_ISSUE.bat": "archive/tests/",
    },
    
    # Weekly reports → reports/branch_changes/weekly/
    "weekly_reports": {
        "Weekly BankFind Branch Changes Reports": "reports/branch_changes/weekly/",
    },
    
    # Credentials files that shouldn't be at root
    "credentials_root": {
        "hdma1-242116-74024e2eb88f.json": "config/credentials/",
        "workspace/hdma1-242116-74024e2eb88f.json": "config/credentials/workspace_backup/",
    },
    
    # HTML debug files → archive/debug/
    "debug_files": {
        "fdic_response_debug.html": "archive/debug/",
    },
    
    # Misc files → archive/misc/
    "misc_files": {
        "social_media_posts_comprehensive.md": "archive/misc/",
        "python": "archive/misc/",  # If it's a file
    },
}

def create_directory(path: Path):
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)

def move_file(source: Path, dest: Path, dry_run: bool = False):
    """Move file from source to destination."""
    if not source.exists():
        print(f"  SKIP: {source.name} - File does not exist")
        return False
    
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    if dest.exists():
        # Add timestamp to avoid overwriting
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = dest.stem
        suffix = dest.suffix
        dest = dest.parent / f"{stem}_{timestamp}{suffix}"
        print(f"  WARNING: Destination exists, using: {dest.name}")
    
    if not dry_run:
        try:
            if source.is_file():
                shutil.move(str(source), str(dest))
            elif source.is_dir():
                shutil.move(str(source), str(dest))
            print(f"  MOVED: {source.name} -> {dest}")
            return True
        except Exception as e:
            print(f"  ERROR moving {source.name}: {e}")
            return False
    else:
        print(f"  [DRY RUN] Would move: {source.name} -> {dest}")
        return True

def merge_directories(source: Path, dest: Path, dry_run: bool = False):
    """Merge source directory into destination directory."""
    if not source.exists() or not source.is_dir():
        print(f"  SKIP: {source.name} - Not a directory")
        return
    
    if not dest.exists():
        dest.mkdir(parents=True, exist_ok=True)
        if not dry_run:
            print(f"  Created: {dest}")
    
    # Copy files from source to destination
    for item in source.iterdir():
        source_item = item
        dest_item = dest / item.name
        
        if dest_item.exists():
            # Add timestamp to avoid overwriting
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if dest_item.is_file():
                stem = dest_item.stem
                suffix = dest_item.suffix
                dest_item = dest_item.parent / f"{stem}_{timestamp}{suffix}"
            else:
                dest_item = dest_item.parent / f"{dest_item.name}_{timestamp}"
            print(f"  WARNING: {item.name} exists, using: {dest_item.name}")
        
        if dry_run:
            print(f"  [DRY RUN] Would move: {source_item} -> {dest_item}")
        else:
            try:
                if source_item.is_file():
                    shutil.copy2(str(source_item), str(dest_item))
                elif source_item.is_dir():
                    shutil.copytree(str(source_item), str(dest_item))
                    print(f"  COPIED: {item.name} -> {dest_item.parent.name}/{dest_item.name}")
            except Exception as e:
                print(f"  ERROR copying {item.name}: {e}")
    
    # After successful copy, remove source (only if not dry run)
    if not dry_run:
        try:
            shutil.rmtree(str(source))
            print(f"  REMOVED source directory: {source}")
        except Exception as e:
            print(f"  WARNING: Could not remove {source}: {e}")

def reorganize(dry_run: bool = True):
    """Perform the reorganization."""
    print("=" * 80)
    print("DREAM Directory Reorganization")
    print("=" * 80)
    print(f"Base directory: {BASE_DIR}")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (making changes)'}")
    print("=" * 80)
    print()
    
    total_moves = 0
    total_errors = 0
    
    # Process each category
    for category, mappings in REORGANIZATION_PLAN.items():
        print(f"\n[{category.upper()}]")
        print("-" * 80)
        
        for source_name, dest_path in mappings.items():
            source = BASE_DIR / source_name
            
            if dest_path is None:
                # Special handling - merge operation
                if source_name == "Member Reports":
                    dest = BASE_DIR / "reports" / "Member Reports"
                    merge_directories(source, dest, dry_run)
                continue
            
            dest = BASE_DIR / dest_path / source.name
            
            if move_file(source, dest, dry_run):
                total_moves += 1
            else:
                total_errors += 1
    
    # Handle "Local Market Analysis" vs "Local Markets Analyses" consolidation
    print(f"\n[CONSOLIDATING LOCAL MARKET ANALYSIS FOLDERS]")
    print("-" * 80)
    local_market_root = BASE_DIR / "Local Market Analysis"
    local_market_reports = BASE_DIR / "reports" / "Local Markets Analyses"
    
    if local_market_root.exists() and local_market_root.is_dir():
        print(f"Merging 'Local Market Analysis' into 'reports/Local Markets Analyses'")
        merge_directories(local_market_root, local_market_reports, dry_run)
    
    # Handle workspace folder cleanup
    print(f"\n[CLEANING UP WORKSPACE FOLDER]")
    print("-" * 80)
    workspace_dir = BASE_DIR / "workspace"
    if workspace_dir.exists():
        # Move any remaining files from workspace
        for item in workspace_dir.iterdir():
            if item.name.endswith('.json'):
                dest = BASE_DIR / "config" / "credentials" / "workspace_backup" / item.name
                move_file(item, dest, dry_run)
        
        # If workspace is now empty, we could remove it, but let's leave it for now
        if not dry_run and not any(workspace_dir.iterdir()):
            print(f"  Workspace folder is now empty")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files processed: {total_moves}")
    print(f"Errors: {total_errors}")
    if dry_run:
        print("\nThis was a DRY RUN. No files were actually moved.")
        print("Run with dry_run=False to perform the actual reorganization.")
    else:
        print("\nReorganization complete!")
    print("=" * 80)

if __name__ == "__main__":
    import sys
    
    # Check for --live flag to actually perform the reorganization
    dry_run = "--live" not in sys.argv
    
    if dry_run:
        print("\n[DRY RUN MODE] - No files will be moved")
        print("Add --live flag to perform actual reorganization\n")
    
    reorganize(dry_run=dry_run)

