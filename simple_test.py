#!/usr/bin/env python3
"""
Simple test script for the ISS Search API
"""

import requests
import json
import time

def test_api():
    """Test the API with a simple search"""
    base_url = "http://localhost:5001"
    
    print("🚀 Testing ISS Search API")
    print("=" * 40)
    
    # Wait a moment for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Test health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("   Make sure the server is running: python iss_search_api.py")
        return
    
    # Test search
    print("\n2. Testing search...")
    try:
        search_data = {
            "query": "astronauts in cupola viewing earth",
            "top_k": 3
        }
        response = requests.post(f"{base_url}/search", json=search_data, timeout=10)
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Search successful: {results['total_results']} results")
            
            for i, image in enumerate(results['results'], 1):
                print(f"   {i}. {image['nasa_id']} (Score: {image['similarity_score']:.3f})")
                print(f"      {image['description'][:80]}...")
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Search error: {e}")
    
    # Test categories
    print("\n3. Testing categories...")
    try:
        response = requests.get(f"{base_url}/categories", timeout=5)
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Categories loaded: {len(categories['categories'])} categories")
            print(f"   Categories: {', '.join(categories['categories'][:5])}...")
        else:
            print(f"❌ Categories failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Categories error: {e}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_api()
