"""
Execute file organization directly - embeds code inline to bypass all wrapper issues.
"""
from pathlib import Path
import shutil

# Use pathlib to handle apostrophe - don't put path in string
onedrive_folder = Path(r"C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis")

# Verify the path exists
if not onedrive_folder.exists():
    print(f"ERROR: OneDrive folder not found: {onedrive_folder}")
    exit(1)

merger_folder = onedrive_folder / 'reports' / 'Local Markets Analyses' / '251101_PNC_Bank_FirstBank_Merger'
supporting_files = merger_folder / 'supporting_files'
supporting_files.mkdir(parents=True, exist_ok=True)

# Keywords to search for in file names
keywords = ['PNC', 'Pnc', 'pnc', 'FirstBank', 'Firstbank', 'firstbank', 'First Bank', 'First bank', 'first bank']

moved_count = 0
skipped_count = 0

print("=" * 80)
print("Searching for ALL files with PNC or FirstBank in name...")
print(f"Source: {onedrive_folder}")
print(f"Target: {supporting_files}")
print("=" * 80)
print()

# Function to check if file name contains any keyword
def contains_keyword(filename):
    return any(keyword in filename for keyword in keywords)

# Function to move a file
def move_file(source, relative_path=""):
    global moved_count, skipped_count
    try:
        if source.is_file():
            target = supporting_files / source.name
            # Avoid overwriting
            counter = 1
            while target.exists():
                stem = source.stem
                suffix = source.suffix
                target = supporting_files / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Skip if already in merger folder
            if 'merger' in str(source).lower() and '251101_PNC_Bank_FirstBank_Merger' in str(source):
                skipped_count += 1
                return False
            
            shutil.move(str(source), str(target))
            path_display = f"{relative_path}/{source.name}" if relative_path else source.name
            print(f"  OK Moved: {path_display}")
            moved_count += 1
            return True
    except Exception as e:
        path_display = f"{relative_path}/{source.name}" if relative_path else source.name
        print(f"  ERROR moving {path_display}: {e}")
        return False
    return False

# Search root folder
print("Searching root folder...")
for item in onedrive_folder.iterdir():
    if item.is_file() and contains_keyword(item.name):
        move_file(item)

# Search data/raw folder
data_raw = onedrive_folder / 'data' / 'raw'
if data_raw.exists():
    print("\nSearching data/raw folder...")
    for item in data_raw.iterdir():
        if item.is_file() and contains_keyword(item.name):
            move_file(item, "data/raw")

# Search scripts folder
scripts_dir = onedrive_folder / 'scripts'
if scripts_dir.exists():
    print("\nSearching scripts folder...")
    for item in scripts_dir.iterdir():
        if item.is_file() and contains_keyword(item.name):
            move_file(item, "scripts")

# Search queries folder if it exists
queries_dir = onedrive_folder / 'queries'
if queries_dir.exists():
    print("\nSearching queries folder...")
    for item in queries_dir.iterdir():
        if item.is_file() and contains_keyword(item.name):
            move_file(item, "queries")

print("\n" + "=" * 80)
print(f"Completed! Moved {moved_count} files, skipped {skipped_count} files (already in merger folder).")
print(f"\nLocation: {supporting_files}")
print("=" * 80)

