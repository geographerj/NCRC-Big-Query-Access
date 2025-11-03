"""
Test script to explore FDIC API structure for branch changes
"""

import requests
import json

def test_fdic_endpoints():
    """Test various FDIC API endpoints to find OSCR data"""
    
    base_url = "https://banks.data.fdic.gov/api"
    
    # Test different possible endpoints
    endpoints_to_test = [
        "/oscr",
        "/offices/changes",
        "/structure/changes",
        "/branches/changes",
    ]
    
    # Test date range (last week)
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    print("Testing FDIC API endpoints...")
    print(f"Date range: {start_str} to {end_str}")
    print()
    
    for endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        print(f"Testing: {url}")
        
        # Try with basic parameters
        params = {
            'filters': f'PROCDATE:[{start_str} TO {end_str}]',
            'format': 'json',
            'limit': 10
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  Success! Response keys: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
                    
                    # Save sample response
                    with open(f"fdic_test_{endpoint.replace('/', '_')}.json", 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"  Sample saved to: fdic_test_{endpoint.replace('/', '_')}.json")
                    
                except json.JSONDecodeError:
                    print(f"  Response is not JSON")
                    print(f"  First 200 chars: {response.text[:200]}")
            
        except Exception as e:
            print(f"  Error: {e}")
        
        print()
    
    # Also check API documentation
    print("\nChecking API documentation...")
    doc_url = "https://api.fdic.gov/banks/docs/"
    print(f"Documentation: {doc_url}")
    
    try:
        response = requests.get("https://api.fdic.gov/banks/docs/", timeout=10)
        if response.status_code == 200:
            print("  Documentation accessible")
            # Look for OSCR mentions
            if 'oscr' in response.text.lower() or 'structure' in response.text.lower():
                print("  Found references to structure/OSCR")
    except:
        pass

if __name__ == "__main__":
    test_fdic_endpoints()

