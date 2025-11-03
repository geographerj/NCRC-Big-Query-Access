"""Quick test to see what images are on a page"""
import requests
from bs4 import BeautifulSoup

urls = [
    'https://ncrc.org/mortgage-market-part-1',
    'https://ncrc.org/mortgage-market-part-2',
    'https://ncrc.org/mortgage-market-part-3',
    'https://ncrc.org/mortgage-market-part-4',
    'https://ncrc.org/labor-market-october-2025'
]

for url in urls:
    print(f"\n{'='*80}")
    print(f"URL: {url}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    print(f"Status: {r.status_code}")
    print(f"Content length: {len(r.text)}")
    print(f"\nOpen Graph tags:")
    og_image = soup.find('meta', property='og:image')
    if og_image:
        print(f"  og:image: {og_image.get('content')}")
    else:
        print("  No og:image found")
    
    print(f"\nAll images on page ({len(soup.find_all('img'))} total):")
    for i, img in enumerate(soup.find_all('img')[:5]):
        src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
        alt = img.get('alt', '')
        print(f"  {i+1}. {src}")

