#!/usr/bin/env python3
"""
Demo script showing the ISS Search API capabilities
"""

import requests
import json
import time

def demo_search():
    """Demonstrate various search capabilities"""
    base_url = "http://localhost:5001"
    
    print("🚀 ISS Image Search API Demo")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "astronauts in cupola viewing earth",
        "space shuttle mission",
        "EVA training underwater", 
        "aurora from space",
        "robotic arm operations",
        "earth observation",
        "crew activities",
        "sunrise from space",
        "Samantha Cristoforetti",
        "space station modules"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i:2d}. Query: '{query}'")
        print("-" * 50)
        
        try:
            response = requests.post(f"{base_url}/search", json={
                'query': query,
                'top_k': 3
            }, timeout=10)
            
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Found {results['total_results']} results")
                
                for j, image in enumerate(results['results'], 1):
                    print(f"   {j}. {image['nasa_id']} (Score: {image['similarity_score']:.3f})")
                    print(f"      Category: {image.get('category', 'N/A')}")
                    print(f"      Description: {image['description'][:80]}...")
            else:
                print(f"❌ Search failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(0.5)  # Small delay between requests
    
    print(f"\n🎉 Demo completed! {len(test_queries)} queries tested")

if __name__ == "__main__":
    demo_search()
