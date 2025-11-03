"""
Parse social media posts from markdown file and schedule for Buffer

Extracts posts by platform, assigns optimal posting times, and generates
Buffer-ready JSON/CSV files.
"""

import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Optimal posting times by platform (ET timezone)
OPTIMAL_TIMES = {
    'bluesky': {  # Similar to Twitter
        'best_days': [1, 2, 3],  # Tue, Wed, Thu
        'best_hours': [9, 10, 11, 12, 13, 14],  # 9 AM - 2 PM
        'time_format': 'ET'
    },
    'facebook': {
        'best_days': [2],  # Wednesday
        'best_hours': [9, 10, 11, 12, 13, 14, 15, 16, 17, 18],  # 9 AM - 6 PM
        'time_format': 'ET'
    },
    'linkedin': {
        'best_days': [1, 2],  # Tue, Wed
        'best_hours': [10, 11, 12],  # 10 AM - 12 PM
        'time_format': 'ET'
    }
}


def parse_markdown_posts(markdown_path: Path) -> Dict[str, List[Dict]]:
    """
    Parse markdown file to extract posts by platform.
    
    Returns:
        Dict with platform as key, list of posts as value
    """
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    posts_by_platform = {
        'bluesky': [],
        'facebook': [],
        'linkedin': []
    }
    
    # Extract BlueSky posts (300 char limit section)
    bluesky_section = re.search(r'## BlueSky Posts.*?## Facebook Posts', content, re.DOTALL)
    if bluesky_section:
        bluesky_content = bluesky_section.group(0)
        bluesky_posts = re.findall(r'### ([^\n]+)\n(.*?)(?=\n### |\n## |$)', bluesky_content, re.DOTALL)
        for title, text in bluesky_posts:
            post_text = text.strip()
            # Extract URL and hashtags
            url_match = re.search(r'(https://[^\s]+)', post_text)
            url = url_match.group(1) if url_match else ''
            
            # Extract hashtags for Tags column (remove # for Buffer's internal tags)
            # Note: Hashtags stay in text, Tags column is for Buffer's organization
            hashtags = re.findall(r'#(\w+)', post_text)
            tags = ','.join(hashtags) if hashtags else ''  # Tags without # symbol
            
            posts_by_platform['bluesky'].append({
                'title': title.strip(),
                'text': post_text,
                'url': url,
                'tags': tags,
                'platform': 'bluesky'
            })
    
    # Extract Facebook posts (1500 char limit section)
    facebook_section = re.search(r'## Facebook Posts.*?## LinkedIn Posts', content, re.DOTALL)
    if facebook_section:
        facebook_content = facebook_section.group(0)
        facebook_posts = re.findall(r'### ([^\n]+)\n(.*?)(?=\n### |\n## |$)', facebook_content, re.DOTALL)
        for title, text in facebook_posts:
            post_text = text.strip()
            # Extract URL and hashtags
            url_match = re.search(r'(https://[^\s]+)', post_text)
            url = url_match.group(1) if url_match else ''
            
            # Extract hashtags for Tags column (remove # for Buffer's internal tags)
            # Note: Hashtags stay in text, Tags column is for Buffer's organization
            hashtags = re.findall(r'#(\w+)', post_text)
            tags = ','.join(hashtags) if hashtags else ''  # Tags without # symbol
            
            posts_by_platform['facebook'].append({
                'title': title.strip(),
                'text': post_text,
                'url': url,
                'tags': tags,
                'platform': 'facebook'
            })
    
    # Extract LinkedIn posts (1500 char limit section)
    linkedin_section = re.search(r'## LinkedIn Posts.*?$', content, re.DOTALL)
    if linkedin_section:
        linkedin_content = linkedin_section.group(0)
        linkedin_posts = re.findall(r'### ([^\n]+)\n(.*?)(?=\n### |$)', linkedin_content, re.DOTALL)
        for title, text in linkedin_posts:
            post_text = text.strip()
            # Extract URL and hashtags
            url_match = re.search(r'(https://[^\s]+)', post_text)
            url = url_match.group(1) if url_match else ''
            
            # Extract hashtags for Tags column (remove # for Buffer's internal tags)
            # Note: Hashtags stay in text, Tags column is for Buffer's organization
            hashtags = re.findall(r'#(\w+)', post_text)
            tags = ','.join(hashtags) if hashtags else ''  # Tags without # symbol
            
            posts_by_platform['linkedin'].append({
                'title': title.strip(),
                'text': post_text,
                'url': url,
                'tags': tags,
                'platform': 'linkedin'
            })
    
    return posts_by_platform


def generate_optimal_schedule(
    posts: List[Dict],
    platform: str,
    start_date: datetime,
    posts_per_day: int = 1,
    min_hours_between: int = 4
) -> List[datetime]:
    """
    Generate optimal posting schedule for posts based on platform best practices.
    
    Args:
        posts: List of post dicts
        platform: Platform name (bluesky, facebook, linkedin)
        start_date: When to start scheduling
        posts_per_day: Maximum posts per day
        min_hours_between: Minimum hours between posts
    
    Returns:
        List of datetime objects for posting times
    """
    if platform not in OPTIMAL_TIMES:
        platform = 'bluesky'  # Default
    
    config = OPTIMAL_TIMES[platform]
    best_days = config['best_days']
    best_hours = config['best_hours']
    
    schedule = []
    current_date = start_date
    
    post_index = 0
    while post_index < len(posts):
        # Find next optimal day
        while current_date.weekday() not in best_days:
            current_date += timedelta(days=1)
        
        # Schedule posts for this day
        posts_today = 0
        hour_index = 0
        
        while posts_today < posts_per_day and post_index < len(posts):
            if hour_index >= len(best_hours):
                # Move to next day
                break
            
            hour = best_hours[hour_index]
            post_time = current_date.replace(hour=hour, minute=0, second=0)
            
            schedule.append(post_time)
            post_index += 1
            posts_today += 1
            hour_index += (min_hours_between // min(1, max(1, len(best_hours) // posts_per_day)))
        
        # Move to next day
        current_date += timedelta(days=1)
    
    return schedule


def extract_image_url_from_post(post_text: str, url: str) -> str:
    """
    Attempt to extract or construct image URL from post.
    
    For report links, we can't automatically extract images, but we'll note
    that Buffer can pull link previews. For CSV format, we may need
    manual image URLs or use the link itself.
    
    Returns:
        Empty string (user will need to add image URLs manually)
    """
    # Check if post contains explicit image URL
    image_patterns = [
        r'(https?://[^\s]+\.(?:jpg|jpeg|png|gif|webp))',
        r'(!\[.*?\]\()([^\)]+)',
    ]
    
    for pattern in image_patterns:
        match = re.search(pattern, post_text, re.IGNORECASE)
        if match:
            return match.group(1) if len(match.groups()) == 0 else match.group(2)
    
    # No explicit image URL found
    # Note: Buffer will generate link previews from URLs, but CSV needs direct image URLs
    return ''


def create_buffer_posts(
    posts_by_platform: Dict[str, List[Dict]],
    start_date: Optional[datetime] = None,
    posts_per_day: int = 1
) -> Dict[str, List[Dict]]:
    """
    Create Buffer-ready post dictionaries with optimal scheduling.
    
    Returns:
        Dict with platform as key, list of Buffer post dicts as value
    """
    if start_date is None:
        # Start next week (Monday)
        start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        days_until_monday = (7 - start_date.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        start_date += timedelta(days=days_until_monday)
    
    buffer_posts = {}
    
    for platform, posts in posts_by_platform.items():
        schedule = generate_optimal_schedule(posts, platform, start_date, posts_per_day)
        
        buffer_posts[platform] = []
        for i, post in enumerate(posts):
            post_time = schedule[i] if i < len(schedule) else None
            
            # Extract image URL (may be empty - user needs to add)
            image_url = extract_image_url_from_post(post['text'], post.get('url', ''))
            
            buffer_post = {
                'text': post['text'],
                'image_url': image_url,
                'tags': post.get('tags', ''),
                'posting_time': post_time.strftime('%Y-%m-%d %H:%M') if post_time else '',
                'url': post.get('url', ''),
                'title': post.get('title', '')
            }
            
            buffer_posts[platform].append(buffer_post)
    
    return buffer_posts


def main():
    """Main function to parse posts and generate Buffer files."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Parse social media posts from markdown and create Buffer schedule'
    )
    parser.add_argument(
        '--input',
        type=str,
        default=r'C:\DREAM\social_media_posts_comprehensive.md',
        help='Input markdown file path'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='Member Reports/data',
        help='Output directory for JSON and CSV files'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        help='Start date for scheduling (YYYY-MM-DD). Default: next Monday'
    )
    parser.add_argument(
        '--posts-per-day',
        type=int,
        default=1,
        help='Maximum posts per day (default: 1)'
    )
    
    args = parser.parse_args()
    
    # Parse markdown
    print(f"Parsing posts from: {args.input}")
    markdown_path = Path(args.input)
    if not markdown_path.exists():
        print(f"Error: File not found: {markdown_path}")
        return
    
    posts_by_platform = parse_markdown_posts(markdown_path)
    
    print(f"\nParsed posts:")
    for platform, posts in posts_by_platform.items():
        print(f"  {platform.upper()}: {len(posts)} posts")
    
    # Determine start date
    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    else:
        start_date = None
    
    # Create Buffer posts with optimal scheduling
    print("\nGenerating optimal schedule...")
    buffer_posts = create_buffer_posts(posts_by_platform, start_date, args.posts_per_day)
    
    # Save JSON files
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving files to: {output_dir}")
    
    # Save individual platform JSON files
    for platform, posts in buffer_posts.items():
        json_path = output_dir / f'buffer_posts_{platform}.json'
        
        # Format for Buffer (remove internal fields)
        buffer_format = []
        for post in posts:
            buffer_format.append({
                'text': post['text'],
                'image_url': post['image_url'],
                'tags': post['tags'],
                'posting_time': post['posting_time']
            })
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(buffer_format, f, indent=2, ensure_ascii=False)
        
        print(f"  [OK] {json_path.name} ({len(posts)} posts)")
    
    # Save combined JSON
    all_posts = []
    for platform, posts in buffer_posts.items():
        all_posts.extend(posts)
    
    combined_path = output_dir / 'buffer_posts_all.json'
    with open(combined_path, 'w', encoding='utf-8') as f:
        json.dump(all_posts, f, indent=2, ensure_ascii=False)
    
    print(f"  [OK] {combined_path.name} ({len(all_posts)} total posts)")
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("\n1. Review the generated JSON files")
    print("2. Add image URLs if needed (posts have report links but may need direct image URLs)")
    print("3. Generate CSV files for each platform:")
    print("   python Member Reports/scripts/schedule_buffer_posts.py --input data/buffer_posts_bluesky.json --output buffer_bluesky.csv")
    print("   python Member Reports/scripts/schedule_buffer_posts.py --input data/buffer_posts_facebook.json --output buffer_facebook.csv")
    print("   python Member Reports/scripts/schedule_buffer_posts.py --input data/buffer_posts_linkedin.json --output buffer_linkedin.csv")
    print("\n4. Upload each CSV to Buffer for the respective platform")
    print("\nNote: Image URLs are not automatically extracted. You may need to:")
    print("  - Provide direct image URLs from your reports")
    print("  - Use Buffer's link preview feature (may require manual setup)")
    print("  - Leave image_url empty if link previews will be used")


if __name__ == "__main__":
    main()

