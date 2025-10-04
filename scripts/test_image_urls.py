#!/usr/bin/env python3
"""
Test script to demonstrate that the RAG API returns image URLs
"""

import requests
import json
import time

def test_image_urls():
    """Test that the API returns image URLs in the JSON response"""
    base_url = "http://localhost:5001"
    
    print("🔍 Testing RAG API Image URL Response")
    print("=" * 50)
    
    # Wait for server to be ready
    print("⏳ Waiting for server...")
    time.sleep(2)
    
    # Test search query
    query = "astronauts in cupola viewing earth"
    print(f"\n🔎 Searching for: '{query}'")
    
    try:
        response = requests.post(f"{base_url}/search", json={
            'query': query,
            'top_k': 3
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            print(f"✅ Found {len(results)} results")
            print("\n📋 JSON Response Structure:")
            print("-" * 30)
            
            for i, result in enumerate(results, 1):
                print(f"\n{i}. Image Result:")
                print(f"   NASA ID: {result.get('nasa_id')}")
                print(f"   Image URL: {result.get('image_url')}")
                print(f"   Similarity Score: {result.get('similarity_score', 0):.3f}")
                print(f"   Description: {result.get('description', '')[:80]}...")
                print(f"   Keywords: {result.get('keywords', [])}")
                
                # Show that the image URL is accessible
                image_url = result.get('image_url')
                if image_url:
                    print(f"   🌐 Image URL Status: {image_url}")
            
            print(f"\n📊 Complete JSON Response:")
            print(json.dumps(data, indent=2))
            
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Is it running?")
        print("Run: python simple_api.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_direct_image_access():
    """Test accessing images directly from URLs"""
    print("\n\n🖼️  Testing Direct Image Access")
    print("=" * 50)
    
    base_url = "http://localhost:5001"
    
    try:
        response = requests.post(f"{base_url}/search", json={
            'query': 'space station modules',
            'top_k': 1
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            if results:
                image_url = results[0].get('image_url')
                print(f"🖼️  Testing image URL: {image_url}")
                
                # Test if the image URL is accessible
                img_response = requests.head(image_url, timeout=5)
                if img_response.status_code == 200:
                    print(f"✅ Image is accessible!")
                    print(f"   Content-Type: {img_response.headers.get('content-type', 'Unknown')}")
                    print(f"   Content-Length: {img_response.headers.get('content-length', 'Unknown')} bytes")
                else:
                    print(f"❌ Image not accessible: {img_response.status_code}")
            else:
                print("❌ No results found")
        else:
            print(f"❌ Search failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing image access: {e}")

if __name__ == '__main__':
    test_image_urls()
    test_direct_image_access()
