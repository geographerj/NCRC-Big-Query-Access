"""
Schedule Social Media Posts to Buffer

This script takes a list of posts and generates a CSV file that can be
uploaded to Buffer using their bulk upload feature.

Based on Buffer's official format:
https://support.buffer.com/article/926-how-to-upload-posts-in-bulk-to-buffer

Usage:
    python scripts/schedule_buffer_posts.py --input posts.json --output buffer_posts.csv
    python scripts/schedule_buffer_posts.py --text "Post 1" "Post 2" --output buffer_posts.csv
    python scripts/schedule_buffer_posts.py --input posts.json --output posts.csv --pinterest
"""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add paths
member_reports_dir = Path(__file__).parent.parent
sys.path.insert(0, str(member_reports_dir))

from utils.buffer_helper import (
    create_buffer_csv,
    create_posts_from_list,
    load_posts_from_json
)


def main():
    parser = argparse.ArgumentParser(
        description='Generate CSV file for Buffer bulk upload',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From JSON file:
  python schedule_buffer_posts.py --input posts.json --output buffer_posts.csv
  
  # From command line:
  python schedule_buffer_posts.py --text "First post" "Second post" --output posts.csv
  
  # With profiles and scheduling:
  python schedule_buffer_posts.py --input posts.json --output posts.csv --profile "Twitter" --schedule-start "2024-01-15 09:00"
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        help='Input JSON file with posts (alternative to --text)'
    )
    
    parser.add_argument(
        '--text', '-t',
        nargs='+',
        help='Post texts (alternative to --input)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        required=True,
        help='Output CSV file path'
    )
    
    parser.add_argument(
        '--pinterest',
        action='store_true',
        help='Include Board Name column for Pinterest posts'
    )
    
    parser.add_argument(
        '--schedule-start',
        type=str,
        help='Start time for scheduling (format: "YYYY-MM-DD HH:MM"). Posts will be scheduled at hourly intervals.'
    )
    
    parser.add_argument(
        '--interval-hours',
        type=int,
        default=1,
        help='Hours between posts when using --schedule-start (default: 1)'
    )
    
    args = parser.parse_args()
    
    # Load or create posts
    if args.input:
        if not Path(args.input).exists():
            print(f"Error: Input file not found: {args.input}")
            sys.exit(1)
        posts = load_posts_from_json(args.input)
        print(f"Loaded {len(posts)} posts from {args.input}")
        
    elif args.text:
        # Create posts from text list
        posts = []
        schedule_times = None
        
        # Handle scheduling if requested
        if args.schedule_start:
            try:
                start_time = datetime.strptime(args.schedule_start, "%Y-%m-%d %H:%M")
                schedule_times = [
                    start_time + timedelta(hours=i * args.interval_hours)
                    for i in range(len(args.text))
                ]
            except ValueError:
                print(f"Error: Invalid date format. Use 'YYYY-MM-DD HH:MM'")
                sys.exit(1)
        
        posts = create_posts_from_list(
            post_texts=args.text,
            posting_times=schedule_times
        )
        print(f"Created {len(posts)} posts from command line arguments")
        
    else:
        print("Error: Must provide either --input or --text")
        parser.print_help()
        sys.exit(1)
    
    # Create CSV
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    create_buffer_csv(
        posts=posts,
        output_path=output_path,
        is_pinterest=args.pinterest
    )
    
    print(f"\n[OK] Success! CSV file ready: {output_path}")
    print("\nNext steps:")
    print("1. Log in to Buffer.com")
    print("2. Go to 'Publish' tab")
    print("3. Select the channel you want to post to (left sidebar)")
    print("4. Click the gear icon (settings) next to the channel name")
    print("5. Click 'General' tab")
    print("6. Click 'Bulk Upload' button")
    print(f"7. Click 'Upload File' and select: {output_path}")
    print("8. Review the preview and click 'Add Posts to Queue' or 'Save as Drafts'")
    print("\nNote: Make sure to upload to the correct channel (CSV format is channel-specific)")


if __name__ == "__main__":
    main()

