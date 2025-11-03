"""
Extract image URLs from report pages linked in posts.

Visits each URL in the posts and extracts image URLs (JPG, PNG, etc.)
from Open Graph tags, meta tags, or page content.
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import time

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Missing required packages.")
    print("Please install: pip install requests beautifulsoup4")
    sys.exit(1)


def extract_image_from_page(url: str, timeout: int = 10) -> Optional[str]:
    """
    Extract image URL from a webpage.
    
    Looks for images in this priority order:
    1. Open Graph image (og:image)
    2. Twitter card image (twitter:image)
    3. Meta image tags
    4. First large image on the page
    
    Returns:
        Direct image URL or None if not found
    """
    try:
        print(f"  Fetching: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        # Don't raise on 404 - pages may still have metadata
        if response.status_code >= 500:
            raise requests.exceptions.HTTPError(f"Server error: {response.status_code}")
        
        if not response.text or len(response.text) < 100:
            print(f"    Warning: Page has very little content ({len(response.text)} chars)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Priority 1: Open Graph image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            img_url = og_image['content']
            # Make absolute URL if relative
            img_url = urljoin(url, img_url)
            # Always use OG image if found (most reliable)
            print(f"    Found OG image: {img_url}")
            return img_url
        
        # Priority 2: Twitter card image
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            img_url = twitter_image['content']
            img_url = urljoin(url, img_url)
            if is_direct_image_url(img_url):
                print(f"    Found Twitter image: {img_url}")
                return img_url
        
        # Priority 3: Other meta image tags
        meta_images = soup.find_all('meta', attrs={'name': re.compile(r'image', re.I)})
        for meta in meta_images:
            if meta.get('content'):
                img_url = meta['content']
                img_url = urljoin(url, img_url)
                if is_direct_image_url(img_url):
                    print(f"    Found meta image: {img_url}")
                    return img_url
        
        # Priority 4: Look for featured image or first large image
        # Check for common image selectors
        featured_selectors = [
            'img[class*="featured"]',
            'img[class*="hero"]',
            'img[class*="banner"]',
            'img[class*="header"]',
            'img[class*="cover"]',
            '.featured-image img',
            '.hero-image img',
            '.wp-post-image',
            'article img:first-of-type',
            'main img:first-of-type',
            '.content img:first-of-type',
            '.entry-content img:first-of-type',
            'article img',
            'main img',
            '.content img'
        ]
        
        for selector in featured_selectors:
            images = soup.select(selector)
            for img in images:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
                if src:
                    img_url = urljoin(url, src)
                    if is_direct_image_url(img_url) and is_large_image(img_url, img):
                        print(f"    Found page image: {img_url}")
                        return img_url
        
        # Priority 5: Check for background images in CSS
        style_tags = soup.find_all(['div', 'section', 'article'], style=True)
        for tag in style_tags:
            style = tag.get('style', '')
            bg_match = re.search(r'background-image:\s*url\(["\']?([^"\']+)["\']?\)', style, re.I)
            if bg_match:
                img_url = urljoin(url, bg_match.group(1))
                if is_direct_image_url(img_url):
                    print(f"    Found background image: {img_url}")
                    return img_url
        
        # Priority 6: Any direct image link in page (prefer larger ones)
        all_images = soup.find_all('img')
        # Sort by likely size (check width/height or class names)
        scored_images = []
        for img in all_images:
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
            if src:
                img_url = urljoin(url, src)
                if is_direct_image_url(img_url):
                    # Skip small icons, logos, avatars
                    skip_patterns = ['icon', 'logo', 'avatar', 'thumbnail', 'small', '32x32', '16x16', 'favicon']
                    if not any(pattern in img_url.lower() for pattern in skip_patterns):
                        score = 0
                        # Higher score for larger images
                        width = img.get('width')
                        height = img.get('height')
                        if width and height:
                            try:
                                w, h = int(width), int(height)
                                score = w * h
                            except:
                                pass
                        scored_images.append((score, img_url))
        
        if scored_images:
            # Return image with highest score
            scored_images.sort(reverse=True, key=lambda x: x[0])
            print(f"    Found fallback image: {scored_images[0][1]}")
            return scored_images[0][1]
        
        print(f"    No image found on page")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"    Error fetching page: {e}")
        return None
    except Exception as e:
        print(f"    Error parsing page: {e}")
        return None


def is_direct_image_url(url: str) -> bool:
    """Check if URL points directly to an image file."""
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
    parsed = urlparse(url.lower())
    path = parsed.path.lower()
    
    # Check if path ends with image extension
    if any(path.endswith(ext) for ext in image_extensions):
        return True
    
    # Check query parameters (some CDNs use query params)
    if any(ext.replace('.', '') in url.lower() for ext in image_extensions):
        # Make sure it's not just in domain name
        if '/image' in url.lower() or 'format=' in url.lower():
            return True
    
    return False


def is_large_image(url: str, img_tag) -> bool:
    """Heuristic to determine if image is likely a featured/large image."""
    # Check width/height attributes
    width = img_tag.get('width')
    height = img_tag.get('height')
    
    if width and height:
        try:
            w, h = int(width), int(height)
            # Assume it's large if width or height > 300px
            if w > 300 or h > 300:
                return True
        except (ValueError, TypeError):
            pass
    
    # Check class names
    class_name = img_tag.get('class', [])
    if isinstance(class_name, list):
        class_str = ' '.join(class_name).lower()
    else:
        class_str = str(class_name).lower()
    
    # Skip if it's clearly a small image
    if any(skip in class_str for skip in ['icon', 'logo', 'avatar', 'thumbnail', 'small']):
        return False
    
    return True


def extract_urls_from_posts(posts: List[Dict]) -> Dict[str, List[int]]:
    """
    Extract all unique URLs from posts.
    
    Returns:
        Dict mapping URL to list of post indices
    """
    url_to_posts = {}
    url_pattern = re.compile(r'https?://[^\s\)]+')
    
    for i, post in enumerate(posts):
        text = post.get('text', '')
        urls = url_pattern.findall(text)
        
        for url in urls:
            # Clean URL (remove trailing punctuation)
            url = url.rstrip('.,;:!?)')
            if url not in url_to_posts:
                url_to_posts[url] = []
            url_to_posts[url].append(i)
    
    return url_to_posts


def update_posts_with_images(posts: List[Dict], url_to_image: Dict[str, str]) -> List[Dict]:
    """Update posts with extracted image URLs."""
    url_pattern = re.compile(r'https?://[^\s\)]+')
    
    updated_posts = []
    for post in posts:
        post_copy = post.copy()
        text = post.get('text', '')
        
        # Find URL in post text
        urls = url_pattern.findall(text)
        for url in urls:
            url = url.rstrip('.,;:!?)')
            if url in url_to_image and url_to_image[url]:
                post_copy['image_url'] = url_to_image[url]
                break  # Use first image found
        
        updated_posts.append(post_copy)
    
    return updated_posts


def main():
    """Main function to extract images from post URLs."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Extract image URLs from report pages linked in posts'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='Member Reports/data/buffer_posts_all.json',
        help='Input JSON file with posts'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output JSON file (default: overwrites input)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='Request timeout in seconds (default: 10)'
    )
    
    args = parser.parse_args()
    
    # Load posts
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        return
    
    print(f"Loading posts from: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    print(f"Loaded {len(posts)} posts")
    
    # Extract unique URLs
    print("\nExtracting URLs from posts...")
    url_to_posts = extract_urls_from_posts(posts)
    unique_urls = list(url_to_posts.keys())
    
    print(f"Found {len(unique_urls)} unique URLs:")
    for url in unique_urls:
        print(f"  - {url}")
    
    # Extract images from each URL
    print("\nExtracting images from URLs...")
    url_to_image = {}
    
    for i, url in enumerate(unique_urls):
        print(f"\n[{i+1}/{len(unique_urls)}] Processing: {url}")
        image_url = extract_image_from_page(url, timeout=args.timeout)
        url_to_image[url] = image_url
        
        # Be respectful with delays
        if i < len(unique_urls) - 1:
            time.sleep(args.delay)
    
    # Summary
    found_count = sum(1 for img in url_to_image.values() if img)
    print(f"\n{'='*80}")
    print(f"SUMMARY:")
    print(f"  Total URLs processed: {len(unique_urls)}")
    print(f"  Images found: {found_count}")
    print(f"  Images not found: {len(unique_urls) - found_count}")
    print(f"{'='*80}")
    
    # Update posts with image URLs
    print("\nUpdating posts with image URLs...")
    updated_posts = update_posts_with_images(posts, url_to_image)
    
    # Save updated posts
    output_path = Path(args.output) if args.output else input_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(updated_posts, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Updated posts saved to: {output_path}")
    
    # Show which posts got images
    posts_with_images = sum(1 for p in updated_posts if p.get('image_url'))
    print(f"  Posts with images: {posts_with_images}/{len(updated_posts)}")
    
    # Generate CSV files if platform-specific JSONs exist
    if 'all' in str(input_path):
        # Try to update platform-specific files too
        data_dir = input_path.parent
        for platform in ['bluesky', 'facebook', 'linkedin']:
            json_path = data_dir / f'buffer_posts_{platform}.json'
            if json_path.exists():
                print(f"\nUpdating {platform} posts...")
                with open(json_path, 'r', encoding='utf-8') as f:
                    platform_posts = json.load(f)
                
                updated_platform_posts = update_posts_with_images(platform_posts, url_to_image)
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(updated_platform_posts, f, indent=2, ensure_ascii=False)
                
                posts_with_images = sum(1 for p in updated_platform_posts if p.get('image_url'))
                print(f"  [OK] {json_path.name}: {posts_with_images}/{len(updated_platform_posts)} posts with images")


if __name__ == "__main__":
    main()

