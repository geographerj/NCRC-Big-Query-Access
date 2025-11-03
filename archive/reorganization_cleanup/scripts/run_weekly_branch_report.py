"""
Weekly FDIC Branch Changes Report Runner

This script is designed to run on Fridays for the previous week's branch changes.
Since files update on Thursdays, running on Friday captures the previous week's data.

Calculates date range automatically:
- End date: Previous Friday (last complete week)
- Start date: Previous Saturday (start of that week)
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fdic_branch_changes_report import main as generate_report
import argparse

def get_previous_week_dates():
    """
    Calculate previous week's date range
    - Week is Sunday to Saturday
    - Files update on Thursdays, so we run on Friday/Saturday for the previous week
    - For today (Saturday Oct 25, 2025), range is Sunday Oct 19 to Saturday Oct 25
    """
    today = datetime.now()
    
    # Find the most recent Saturday
    # weekday(): Monday=0, Tuesday=1, ..., Saturday=5, Sunday=6
    days_since_saturday = (today.weekday() + 2) % 7  # Saturday is weekday 5
    if days_since_saturday == 0:
        # Today is Saturday, use this Saturday
        last_saturday = today
    else:
        # Find previous Saturday
        last_saturday = today - timedelta(days=days_since_saturday)
    
    # Previous week: Sunday (6 days before last Saturday) to Saturday (last Saturday)
    previous_week_start = last_saturday - timedelta(days=6)  # Sunday
    previous_week_end = last_saturday  # Saturday
    
    return previous_week_start, previous_week_end

def main():
    parser = argparse.ArgumentParser(description='Run Weekly FDIC Branch Changes Report')
    parser.add_argument('--start-date', help='Override start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='Override end date (YYYY-MM-DD)')
    parser.add_argument('--test', action='store_true', help='Test with last week (Oct 24-31, 2024)')
    
    args = parser.parse_args()
    
    if args.test:
        # Test mode: use current week (Oct 19-25, 2025) - Sunday to Saturday
        start_date = datetime(2025, 10, 19)  # Sunday
        end_date = datetime(2025, 10, 25)    # Saturday
        print("\n" + "="*80)
        print("TEST MODE: Using October 19-25, 2025 (Sunday to Saturday)")
        print("="*80)
    elif args.start_date and args.end_date:
        # Manual date override
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    else:
        # Automatic: previous week (Sunday to Saturday)
        start_date, end_date = get_previous_week_dates()
        print("\n" + "="*80)
        print("AUTOMATIC MODE: Previous Week (Sunday to Saturday)")
        print(f"Week: {start_date.strftime('%Y-%m-%d')} (Sunday) to {end_date.strftime('%Y-%m-%d')} (Saturday)")
        print("="*80)
    
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

