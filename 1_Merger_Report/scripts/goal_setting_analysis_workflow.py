"""
Master workflow script for Goal-Setting Analysis.
Orchestrates the entire process and ensures all files are saved to the merger folder.
"""

from pathlib import Path
from datetime import datetime
import sys
import json
import shutil

# Import our helper scripts
import importlib.util

def load_script_module(script_path):
    """Load a Python script as a module"""
    spec = importlib.util.spec_from_file_location("module", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def setup_merger_workspace(bank_a_name, bank_b_name, base_dir=None):
    """
    Create merger folder structure and return paths.
    All files will be saved to this folder.
    """
    if base_dir is None:
        base_dir = Path('reports') / 'Local Markets Analyses'
    else:
        base_dir = Path(base_dir)
    
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Format date
    date_str = datetime.now().strftime('%y%m%d')
    
    # Sanitize bank names
    import re
    def sanitize(name):
        name = re.sub(r'[^\w\s-]', '', str(name))
        name = name.replace(' ', '_')
        name = re.sub(r'_+', '_', name)
        return name.strip('_').strip()
    
    bank_a_clean = sanitize(bank_a_name)
    bank_b_clean = sanitize(bank_b_name)
    
    # Create folder name
    folder_name = f"{date_str}_{bank_a_clean}_{bank_b_clean}_Merger"
    merger_folder = base_dir / folder_name
    
    # Create folder structure
    merger_folder.mkdir(parents=True, exist_ok=True)
    (merger_folder / 'supporting_files').mkdir(exist_ok=True)
    (merger_folder / 'data_exports').mkdir(exist_ok=True)
    
    return merger_folder

def move_files_to_merger_folder(source_files, merger_folder, subfolder='supporting_files'):
    """
    Move files to the merger folder's supporting_files or data_exports directory.
    
    Args:
        source_files: List of file paths (Path objects or strings)
        merger_folder: Path to merger folder
        subfolder: 'supporting_files' or 'data_exports'
    """
    target_dir = merger_folder / subfolder
    target_dir.mkdir(exist_ok=True)
    
    moved_files = []
    for source_file in source_files:
        source_path = Path(source_file)
        if source_path.exists():
            target_path = target_dir / source_path.name
            
            # If file already exists, add number suffix
            counter = 1
            while target_path.exists():
                stem = source_path.stem
                suffix = source_path.suffix
                target_path = target_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Copy file (don't move in case original is needed)
            shutil.copy2(source_path, target_path)
            moved_files.append(target_path)
            print(f"  Copied: {source_path.name} -> {target_path}")
        else:
            print(f"  Warning: File not found: {source_path}")
    
    return moved_files

def organize_merger_files(merger_folder, ticket_file, pdf_files=None, parsed_files=None):
    """
    Organize all files related to the merger analysis into the merger folder.
    
    Args:
        merger_folder: Path to the merger folder
        ticket_file: Path to the merger ticket Excel file
        pdf_files: List of PDF files (assessment areas, etc.)
        parsed_files: List of JSON/CSV files created during parsing
    """
    print(f"\n{'='*80}")
    print(f"ORGANIZING FILES FOR MERGER ANALYSIS")
    print(f"{'='*80}\n")
    print(f"Target folder: {merger_folder}\n")
    
    files_to_move = []
    
    # Copy ticket file
    if ticket_file:
        ticket_path = Path(ticket_file)
        if ticket_path.exists():
            files_to_move.append(ticket_path)
    
    # Copy PDF files
    if pdf_files:
        for pdf_file in pdf_files:
            pdf_path = Path(pdf_file)
            if pdf_path.exists():
                files_to_move.append(pdf_path)
    
    # Copy parsed/extracted files (JSON, CSV, etc.)
    if parsed_files:
        for parsed_file in parsed_files:
            parsed_path = Path(parsed_file)
            if parsed_path.exists():
                files_to_move.append(parsed_path)
    
    # Move all files
    moved = move_files_to_merger_folder(files_to_move, merger_folder, 'supporting_files')
    
    print(f"\n  Total files organized: {len(moved)}")
    print(f"  Location: {merger_folder / 'supporting_files'}")
    
    return moved

def create_file_manifest(merger_folder, all_files):
    """
    Create a manifest of all files in the merger folder.
    """
    manifest = {
        'created': datetime.now().isoformat(),
        'folder': str(merger_folder),
        'files': []
    }
    
    for file_path in all_files:
        file_info = {
            'name': file_path.name,
            'path': str(file_path),
            'size': file_path.stat().st_size if file_path.exists() else 0,
            'type': file_path.suffix
        }
        manifest['files'].append(file_info)
    
    manifest_path = merger_folder / 'file_manifest.json'
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nFile manifest created: {manifest_path}")
    return manifest_path

def main():
    """
    Main workflow - this will be called by the goal-setting analysis script.
    """
    print("Goal-Setting Analysis - File Organization Module")
    print("This module ensures all supporting files are organized in the merger folder.")
    
    # Example usage
    if len(sys.argv) < 4:
        print("\nUsage: This script is typically called by the main goal-setting analysis script.")
        print("Standalone usage:")
        print('  python goal_setting_analysis_workflow.py <bank_a> <bank_b> <ticket_file> [pdf_files...]')
        sys.exit(1)
    
    bank_a = sys.argv[1]
    bank_b = sys.argv[2]
    ticket_file = sys.argv[3]
    pdf_files = sys.argv[4:] if len(sys.argv) > 4 else None
    
    # Create merger folder
    merger_folder = setup_merger_workspace(bank_a, bank_b)
    print(f"\nCreated merger folder: {merger_folder}")
    
    # Organize files
    moved = organize_merger_files(merger_folder, ticket_file, pdf_files)
    
    # Create manifest
    create_file_manifest(merger_folder, moved)
    
    print(f"\n✓ All files organized in: {merger_folder}")

if __name__ == "__main__":
    main()


