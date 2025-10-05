#!/usr/bin/env python3
"""
Example showing how to use the RAG API to get images and display them
"""

import requests
import json
from typing import List, Dict, Any

class ISSSearchClient:
    """Client for the ISS Search API"""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
    
    def search_images(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for images and return results with image URLs"""
        try:
            response = requests.post(f"{self.base_url}/search", json={
                'query': query,
                'top_k': top_k
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                print(f"Search failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error searching: {e}")
            return []
    
    def get_image_urls(self, query: str, top_k: int = 5) -> List[str]:
        """Get just the image URLs from search results"""
        results = self.search_images(query, top_k)
        return [result.get('image_url') for result in results if result.get('image_url')]
    
    def search_with_details(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Search and return detailed results including image URLs"""
        results = self.search_images(query, top_k)
        
        return {
            'query': query,
            'total_found': len(results),
            'images': [
                {
                    'nasa_id': result.get('nasa_id'),
                    'image_url': result.get('image_url'),
                    'description': result.get('description'),
                    'similarity_score': result.get('similarity_score'),
                    'keywords': result.get('keywords', [])
                }
                for result in results
            ]
        }

def example_usage():
    """Example of how to use the API to get images"""
    client = ISSSearchClient()
    
    print("🚀 ISS Image Search API Usage Examples")
    print("=" * 50)
    
    # Example 1: Get image URLs for a query
    print("\n1. Getting image URLs for 'astronauts in cupola':")
    image_urls = client.get_image_urls("astronauts in cupola", top_k=3)
    for i, url in enumerate(image_urls, 1):
        print(f"   {i}. {url}")
    
    # Example 2: Get detailed search results
    print("\n2. Detailed search results for 'space station modules':")
    results = client.search_with_details("space station modules", top_k=2)
    print(f"   Query: {results['query']}")
    print(f"   Found: {results['total_found']} images")
    
    for img in results['images']:
        print(f"\n   📸 {img['nasa_id']}")
        print(f"      URL: {img['image_url']}")
        print(f"      Score: {img['similarity_score']:.3f}")
        print(f"      Description: {img['description'][:80]}...")
    
    # Example 3: HTML generation example
    print("\n3. HTML generation example:")
    results = client.search_images("EVA training", top_k=2)
    
    html_snippet = """
    <div class="image-gallery">
    """
    
    for result in results:
        image_url = result.get('image_url')
        nasa_id = result.get('nasa_id')
        description = result.get('description', '')
        
        if image_url:
            html_snippet += f"""
        <div class="image-item">
            <img src="{image_url}" alt="{nasa_id}" />
            <h3>{nasa_id}</h3>
            <p>{description[:100]}...</p>
        </div>
            """
    
    html_snippet += """
    </div>
    """
    
    print("   Generated HTML snippet:")
    print(html_snippet)
    
    # Example 4: JSON for mobile app
    print("\n4. JSON format for mobile app:")
    mobile_data = {
        'search_query': 'astronauts in cupola',
        'images': []
    }
    
    results = client.search_images('astronauts in cupola', top_k=3)
    for result in results:
        mobile_data['images'].append({
            'id': result.get('nasa_id'),
            'url': result.get('image_url'),
            'title': result.get('nasa_id'),
            'description': result.get('description', ''),
            'relevance': result.get('similarity_score', 0)
        })
    
    print(json.dumps(mobile_data, indent=2))

def test_api_connection():
    """Test if the API is running"""
    try:
        response = requests.get("http://localhost:5001/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running and ready!")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API is not running. Start it with: python simple_api.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        return False

if __name__ == '__main__':
    if test_api_connection():
        example_usage()
    else:
        print("\n💡 To start the API, run:")
        print("   python simple_api.py")
        print("\n   Then run this script again.")
