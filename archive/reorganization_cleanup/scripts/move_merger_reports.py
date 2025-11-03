"""
Move all Fifth Third and Comerica reports to a single merger folder
"""
import os
import shutil
from pathlib import Path

def move_merger_reports():
    """Move all Fifth Third and Comerica reports to reports/fifth_third_merger/"""
    base_dir = Path(__file__).parent.parent
    reports_dir = base_dir / "reports"
    
    # Create merger folder
    merger_dir = reports_dir / "fifth_third_merger"
    merger_dir.mkdir(exist_ok=True)
    
    print("="*80)
    print("MOVING MERGER REPORTS")
    print("="*80)
    
    files_moved = []
    
    # Move Fifth Third CBA report
    ft_dir = reports_dir / "fifth_third"
    if ft_dir.exists():
        for file in ft_dir.glob("*.xlsx"):
            dest = merger_dir / file.name
            if dest.exists():
                # Add timestamp to avoid overwrite
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest = merger_dir / f"{file.stem}_{timestamp}{file.suffix}"
            shutil.copy2(file, dest)
            files_moved.append((file, dest))
            print(f"Moved: {file.name} -> {dest.name}")
    
    # Move Comerica CBA report
    com_dir = reports_dir / "comerica"
    if com_dir.exists():
        for file in com_dir.glob("*.xlsx"):
            dest = merger_dir / file.name
            if dest.exists():
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest = merger_dir / f"{file.stem}_{timestamp}{file.suffix}"
            shutil.copy2(file, dest)
            files_moved.append((file, dest))
            print(f"Moved: {file.name} -> {dest.name}")
    
    # Move merger analysis reports
    merger_analysis_dir = reports_dir / "merger_analysis"
    if merger_analysis_dir.exists():
        for file in merger_analysis_dir.glob("FifthThird_Comerica_Merger_Analysis_*.xlsx"):
            dest = merger_dir / file.name
            if dest.exists():
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest = merger_dir / f"{file.stem}_{timestamp}{file.suffix}"
            shutil.copy2(file, dest)
            files_moved.append((file, dest))
            print(f"Moved: {file.name} -> {dest.name}")
    
    print("\n" + "="*80)
    print(f"Moved {len(files_moved)} files to: {merger_dir}")
    print("="*80)
    
    # List final contents
    print(f"\nFiles in {merger_dir}:")
    for file in sorted(merger_dir.glob("*.xlsx")):
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"  - {file.name} ({size_mb:.1f} MB)")

if __name__ == "__main__":
    move_merger_reports()

