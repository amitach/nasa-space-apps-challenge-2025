import requests
import json
import time

class ISSSearchClient:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
    
    def health_check(self):
        """Check if the API is running"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def search(self, query, top_k=5, method='POST'):
        """Search for images using natural language"""
        try:
            if method.upper() == 'POST':
                response = requests.post(f"{self.base_url}/search", json={
                    'query': query,
                    'top_k': top_k
                })
            else:
                response = requests.get(f"{self.base_url}/search", params={
                    'q': query,
                    'top_k': top_k
                })
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_image_by_id(self, nasa_id):
        """Get specific image by NASA ID"""
        try:
            response = requests.get(f"{self.base_url}/images/{nasa_id}")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def list_images(self, category=None, source=None, limit=10):
        """List images with optional filtering"""
        try:
            params = {'limit': limit}
            if category:
                params['category'] = category
            if source:
                params['source'] = source
            
            response = requests.get(f"{self.base_url}/images", params=params)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_categories(self):
        """Get available categories and sources"""
        try:
            response = requests.get(f"{self.base_url}/categories")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def test_api():
    """Test the ISS Search API with various queries"""
    client = ISSSearchClient()
    
    print("🚀 Testing ISS Search API")
    print("=" * 50)
    
    # Health check
    print("\n1. Health Check:")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    
    if 'error' in health:
        print("❌ API is not running. Please start the server first:")
        print("   python iss_search_api.py")
        return
    
    # Get categories
    print("\n2. Available Categories:")
    categories = client.get_categories()
    print(json.dumps(categories, indent=2))
    
    # Test searches
    test_queries = [
        "astronauts in cupola viewing earth",
        "space shuttle mission",
        "EVA training underwater",
        "aurora from space",
        "robotic arm operations",
        "earth observation",
        "crew activities",
        "sunrise from space"
    ]
    
    print("\n3. Testing Search Queries:")
    print("=" * 30)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 40)
        
        result = client.search(query, top_k=3)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Found {result['total_results']} results")
            for j, image in enumerate(result['results'], 1):
                print(f"   {j}. {image['nasa_id']} (Score: {image['similarity_score']:.3f})")
                print(f"      Category: {image.get('category', 'N/A')}")
                print(f"      Description: {image['description'][:80]}...")
    
    # Test specific image lookup
    print("\n4. Testing Image Lookup:")
    print("=" * 30)
    
    test_nasa_id = "iss043e122274"  # Samantha Cristoforetti in Cupola
    image_result = client.get_image_by_id(test_nasa_id)
    
    if image_result.get('found'):
        print(f"✅ Found image: {test_nasa_id}")
        print(f"   Description: {image_result['image']['description'][:100]}...")
    else:
        print(f"❌ Image not found: {test_nasa_id}")
    
    # Test filtering
    print("\n5. Testing Image Filtering:")
    print("=" * 30)
    
    # Filter by category
    earth_obs = client.list_images(category='earth_observation', limit=3)
    print(f"Earth Observation images: {earth_obs.get('total_images', 0)}")
    
    # Filter by source
    cupola_images = client.list_images(source='cupola', limit=3)
    print(f"Cupola images: {cupola_images.get('total_images', 0)}")

if __name__ == "__main__":
    test_api()
