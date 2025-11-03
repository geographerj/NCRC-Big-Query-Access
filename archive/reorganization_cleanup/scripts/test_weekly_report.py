"""
Test script to run weekly branch changes report for last week
Tests the complete workflow including baseline loading
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fdic_branch_changes_report import main as generate_report

def main():
    """Test weekly report for last week (Oct 19-25, 2025)"""
    
    # Last week: Sunday Oct 19 to Saturday Oct 25, 2025
    start_date = datetime(2025, 10, 19)  # Sunday
    end_date = datetime(2025, 10, 25)    # Saturday
    
    print("="*80)
    print("TEST: WEEKLY BRANCH CHANGES REPORT")
    print("="*80)
    print(f"\nTest date range: {start_date.strftime('%Y-%m-%d')} (Sunday) to {end_date.strftime('%Y-%m-%d')} (Saturday)")
    print("\nNote: Since web scraping may not work, you'll need to:")
    print("1. Export CSV from FDIC website for this date range")
    print("2. Run: python scripts/fdic_branch_changes_report.py --csv-file <exported_file>.csv")
    print("\nOr test with sample data if available.")
    
    # Build arguments for main script
    sys.argv = [
        'fdic_branch_changes_report.py',
        '--start-date', start_date.strftime('%Y-%m-%d'),
        '--end-date', end_date.strftime('%Y-%m-%d')
    ]
    
    # Run the report generator
    generate_report()

if __name__ == "__main__":
    main()

