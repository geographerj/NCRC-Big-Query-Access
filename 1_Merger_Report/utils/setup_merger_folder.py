"""
Setup folder structure for a merger analysis.
Creates a dated folder with bank names in the Local Markets Analyses directory.
"""

from pathlib import Path
from datetime import datetime
import re

def sanitize_folder_name(name):
    """Sanitize bank name for use in folder name"""
    # Remove special characters, keep only alphanumeric and spaces
    name = re.sub(r'[^\w\s-]', '', str(name))
    # Replace spaces with underscores, limit length
    name = name.replace(' ', '_')
    # Remove multiple underscores
    name = re.sub(r'_+', '_', name)
    return name.strip('_').strip()

def create_merger_folder(bank_a_name, bank_b_name, base_dir=None):
    """
    Create a folder for the merger analysis.
    
    Args:
        bank_a_name: Name of acquirer bank (Bank A)
        bank_b_name: Name of target bank (Bank B)
        base_dir: Base directory (defaults to reports/Local Markets Analyses)
    
    Returns:
        Path object for the created folder
    """
    if base_dir is None:
        base_dir = Path('reports') / 'Local Markets Analyses'
    else:
        base_dir = Path(base_dir)
    
    # Create base directory if it doesn't exist
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Format date
    date_str = datetime.now().strftime('%y%m%d')
    
    # Sanitize bank names
    bank_a_clean = sanitize_folder_name(bank_a_name)
    bank_b_clean = sanitize_folder_name(bank_b_name)
    
    # Create folder name: YYMMDD_BankA_BankB_Merger
    folder_name = f"{date_str}_{bank_a_clean}_{bank_b_clean}_Merger"
    
    # Create the folder
    merger_folder = base_dir / folder_name
    merger_folder.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories for organization
    (merger_folder / 'supporting_files').mkdir(exist_ok=True)
    (merger_folder / 'data_exports').mkdir(exist_ok=True)
    
    return merger_folder

def main():
    """Example usage"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python setup_merger_folder.py <bank_a_name> <bank_b_name>")
        print("\nExample:")
        print('  python setup_merger_folder.py "Bank A Name" "Bank B Name"')
        sys.exit(1)
    
    bank_a = sys.argv[1]
    bank_b = sys.argv[2]
    
    folder = create_merger_folder(bank_a, bank_b)
    
    print(f"\nCreated merger folder: {folder}")
    print(f"\nFolder structure:")
    print(f"  {folder}/")
    print(f"    supporting_files/")
    print(f"    data_exports/")
    print(f"\nOutput Excel file and supporting files should be saved here.")

if __name__ == "__main__":
    main()


