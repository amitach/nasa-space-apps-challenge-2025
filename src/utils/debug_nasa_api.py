import requests
import json

def debug_nasa_api():
    """Debug the NASA API response to understand the correct URL format"""
    url = "https://images-api.nasa.gov/search?q=nbl&media_type=image&year_start=1920&year_end=2025&page_size=3&page=1"
    
    print("Fetching NASA API response...")
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        items = data.get('collection', {}).get('items', [])
        
        print(f"Found {len(items)} items")
        
        for i, item in enumerate(items):
            print(f"\n--- Item {i+1} ---")
            nasa_id = item['data'][0]['nasa_id']
            print(f"NASA ID: {nasa_id}")
            
            print("Available links:")
            for link in item.get('links', []):
                print(f"  {link['rel']}: {link['href']}")
            
            # Test different URL formats
            test_urls = [
                f"https://images-assets.nasa.gov/image/{nasa_id}/{nasa_id}~orig.jpg",
                f"https://images-assets.nasa.gov/image/{nasa_id}/{nasa_id}~medium.jpg",
                f"https://images-assets.nasa.gov/image/{nasa_id}/{nasa_id}~small.jpg",
                f"https://images-assets.nasa.gov/image/{nasa_id}/{nasa_id}~thumb.jpg"
            ]
            
            print("Testing URL formats:")
            for test_url in test_urls:
                try:
                    resp = requests.head(test_url, timeout=5)
                    print(f"  {test_url}: {resp.status_code} - {resp.headers.get('content-type', 'unknown')}")
                except Exception as e:
                    print(f"  {test_url}: Error - {e}")
    else:
        print(f"API Error: {response.status_code}")

if __name__ == "__main__":
    debug_nasa_api()
