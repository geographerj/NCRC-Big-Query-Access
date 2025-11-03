"""
Buffer Helper Utilities

Since Buffer doesn't have a public API, this module provides:
1. CSV generation for Buffer's bulk upload feature
2. Format validation for social media posts

Based on Buffer's official format:
https://support.buffer.com/article/926-how-to-upload-posts-in-bulk-to-buffer

Buffer CSV format requires these columns (case-sensitive):
- Text (required if Image URL is empty)
- Image URL (required if Text is empty)
- Tags (optional, comma-separated)
- Posting Time (optional, format: YYYY-MM-DD HH:mm)
- Board Name (only for Pinterest)
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Union


def format_posting_time(dt: Union[str, datetime]) -> str:
    """
    Convert datetime to Buffer's posting time format: YYYY-MM-DD HH:MM (24-hour, zero-padded)
    
    Buffer requires exact format: YYYY-MM-DD HH:MM (e.g., "2025-11-04 09:00")
    
    Args:
        dt: datetime object or ISO string
        
    Returns:
        Formatted string like "2025-11-04 09:00" (strict format)
    """
    if isinstance(dt, str):
        dt_str = dt.strip()
        # Try to parse ISO format or Buffer format
        try:
            # Try ISO format first
            if 'T' in dt_str or '+' in dt_str or dt_str.endswith('Z'):
                dt_obj = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            else:
                # Try Buffer format: YYYY-MM-DD HH:MM
                dt_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            # Format with strict zero-padding
            return dt_obj.strftime("%Y-%m-%d %H:%M")
        except ValueError as e:
            raise ValueError(f"Could not parse datetime string '{dt_str}': {e}")
    
    if isinstance(dt, datetime):
        # Ensure strict formatting with zero-padding
        return dt.strftime("%Y-%m-%d %H:%M")
    
    raise ValueError(f"Invalid datetime type: {type(dt)}")


def create_buffer_csv(
    posts: List[Dict[str, Union[str, Optional[str]]]],
    output_path: Union[str, Path],
    is_pinterest: bool = False
) -> Path:
    """
    Create a CSV file formatted for Buffer's bulk upload feature.
    
    Based on Buffer's official format:
    https://support.buffer.com/article/926-how-to-upload-posts-in-bulk-to-buffer
    
    Args:
        posts: List of dictionaries with post data. Each dict should have:
            - 'text' (required if image_url is empty): Post content
            - 'image_url' (required if text is empty): Direct image URL
            - 'tags' (optional): Comma-separated tags (must exist in Buffer)
            - 'posting_time' (optional): Datetime string or datetime object
            - 'board_name' (optional, Pinterest only): Board name
        output_path: Where to save the CSV file
        is_pinterest: If True, include "Board Name" column for Pinterest
        
    Returns:
        Path to the created CSV file
    """
    output_path = Path(output_path)
    
    # Prepare rows for DataFrame
    rows = []
    for i, post in enumerate(posts):
        # Validate: must have text or image_url
        text = post.get('text', '').strip()
        image_url = post.get('image_url', '').strip()
        
        if not text and not image_url:
            raise ValueError(
                f"Post {i+1} must have either 'text' or 'image_url' "
                "(at least one is required)"
            )
        
        row = {
            'Text': text,
            'Image URL': image_url,
            'Tags': '',  # Leave empty - tags must be created in Buffer first
            'Posting Time': '',
        }
        
        # Handle posting_time - convert to Buffer format
        posting_time = post.get('posting_time')
        if posting_time:
            try:
                # Format strictly as YYYY-MM-DD HH:MM
                formatted_time = format_posting_time(posting_time)
                # Validate format matches exactly
                if not isinstance(formatted_time, str) or len(formatted_time) != 16:
                    raise ValueError(f"Invalid format: {formatted_time}")
                row['Posting Time'] = formatted_time
            except Exception as e:
                raise ValueError(f"Post {i+1} has invalid posting_time '{posting_time}': {e}")
        
        # Add Board Name for Pinterest
        if is_pinterest:
            row['Board Name'] = post.get('board_name', '')
        
        rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Ensure column order matches Buffer's expected format (case-sensitive!)
    if is_pinterest:
        columns = ['Text', 'Image URL', 'Tags', 'Posting Time', 'Board Name']
    else:
        columns = ['Text', 'Image URL', 'Tags', 'Posting Time']
    
    df = df[columns]
    
    # Save to CSV as UTF-8 (required for emoji support)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"[OK] Created Buffer CSV with {len(posts)} posts: {output_path}")
    print(f"  Format: {', '.join(columns)}")
    return output_path


def create_posts_from_list(
    post_texts: List[str],
    image_urls: Optional[List[Optional[str]]] = None,
    tags: Optional[List[Optional[str]]] = None,
    posting_times: Optional[List[Union[str, datetime]]] = None,
    board_names: Optional[List[Optional[str]]] = None
) -> List[Dict]:
    """
    Create a list of post dictionaries from simple lists.
    
    Args:
        post_texts: List of post text content (at least text or image_url required per post)
        image_urls: Optional list of direct image URLs (must end in .jpg, .png, etc.)
        tags: Optional list of comma-separated tags (must exist in Buffer account)
        posting_times: Optional list of scheduled times (can be single datetime/string or list)
        board_names: Optional list of board names for Pinterest
        
    Returns:
        List of post dictionaries ready for create_buffer_csv
    """
    num_posts = len(post_texts)
    
    # Handle image_urls - allow single string for all posts
    if image_urls is None:
        image_urls = [None] * num_posts
    elif isinstance(image_urls, str):
        image_urls = [image_urls] * num_posts
    elif len(image_urls) != num_posts:
        raise ValueError(f"image_urls length ({len(image_urls)}) must match post_texts length ({num_posts})")
    
    # Handle tags
    if tags is None:
        tags = [None] * num_posts
    elif isinstance(tags, str):
        tags = [tags] * num_posts
    elif len(tags) != num_posts:
        raise ValueError(f"tags length ({len(tags)}) must match post_texts length ({num_posts})")
    
    # Handle posting_times
    if posting_times is None:
        posting_times = [None] * num_posts
    elif isinstance(posting_times, (str, datetime)):
        posting_times = [posting_times] * num_posts
    elif len(posting_times) != num_posts:
        raise ValueError(f"posting_times length ({len(posting_times)}) must match post_texts length ({num_posts})")
    
    # Handle board_names (Pinterest)
    if board_names is None:
        board_names = [None] * num_posts
    elif isinstance(board_names, str):
        board_names = [board_names] * num_posts
    elif len(board_names) != num_posts:
        raise ValueError(f"board_names length ({len(board_names)}) must match post_texts length ({num_posts})")
    
    # Create posts
    posts = []
    for i, text in enumerate(post_texts):
        post = {}
        
        # Text (can be empty if image_url is provided)
        if text:
            post['text'] = text
        
        # Image URL (can be empty if text is provided)
        if image_urls[i]:
            post['image_url'] = image_urls[i]
        
        # Tags (comma-separated)
        if tags[i]:
            post['tags'] = tags[i]
        
        # Posting time
        if posting_times[i]:
            post['posting_time'] = posting_times[i]
        
        # Board name (Pinterest)
        if board_names[i]:
            post['board_name'] = board_names[i]
        
        posts.append(post)
    
    return posts


def load_posts_from_json(json_path: Union[str, Path]) -> List[Dict]:
    """
    Load posts from a JSON file.
    
    JSON format should be:
    [
        {
            "text": "Post content here",  // required if image_url is empty
            "image_url": "https://...",  // required if text is empty (must be direct URL)
            "tags": "tag1,tag2",  // optional, comma-separated
            "posting_time": "2025-07-29 13:29",  // optional, format: YYYY-MM-DD HH:mm
            "board_name": "My Board"  // optional, for Pinterest only
        },
        ...
    ]
    
    Note: For posting_time, you can also use ISO format which will be converted.
    """
    import json
    
    json_path = Path(json_path)
    with open(json_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    return posts

