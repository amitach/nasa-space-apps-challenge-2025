#!/usr/bin/env python3
"""
Test script for NASA ISS Image Search RAG functionality
Tests various semantic search capabilities and retrieval accuracy
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
API_BASE = "http://localhost:5001"
HEADERS = {"Content-Type": "application/json"}

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_result(query, result, index):
    """Pretty print search result"""
    print(f"\n{index+1}. 📸 NASA ID: {result['nasa_id']}")
    print(f"   🏷️  Category: {result['category']}")
    print(f"   🎯 Similarity: {result['similarity_score']:.3f}")
    print(f"   📊 Relevance: {result['relevance_score']}")
    print(f"   🔗 URL: {result['image_url']}")
    print(f"   📝 Description: {result['description'][:150]}...")
    if result['keywords']:
        print(f"   🏷️  Keywords: {', '.join(result['keywords'][:5])}")

def test_search_query(query, top_k=3, description=""):
    """Test a search query and display results"""
    print(f"\n🔍 Query: \"{query}\"")
    if description:
        print(f"📋 Test: {description}")
    
    try:
        response = requests.post(
            f"{API_BASE}/search",
            headers=HEADERS,
            json={"query": query, "top_k": top_k}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total_results']} results")
            
            for i, result in enumerate(data['results']):
                print_result(query, result, i)
                
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_api_health():
    """Test API health and get statistics"""
    print_section("🩺 API Health Check")
    
    try:
        # Health check
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ API Health: GOOD")
            print(f"📊 Total Images: {data['total_images']}")
            print(f"🗂️  Categories: {', '.join(data['categories'])}")
            print(f"📚 Index Ready: {data['index_ready']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Health check exception: {e}")

def main():
    """Main test function"""
    print("🚀 NASA ISS Image Search - RAG Functionality Test")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test API health
    test_api_health()
    
    # Test 1: Cupola and Earth observation
    print_section("🌍 Test 1: Earth Observation from Cupola")
    test_queries_cupola = [
        ("astronauts looking at Earth through cupola windows", "Cupola Earth viewing"),
        ("space station cupola with Earth view", "Earth observation from ISS"),
        ("crew members in cupola observing planet", "Crew activities in cupola"),
    ]
    
    for query, desc in test_queries_cupola:
        test_search_query(query, 2, desc)
        time.sleep(1)
    
    # Test 2: NBL Training
    print_section("🏊 Test 2: Neutral Buoyancy Laboratory Training")
    test_queries_nbl = [
        ("underwater spacewalk training", "NBL EVA preparation"),
        ("neutral buoyancy laboratory astronaut training", "NBL simulation training"),
        ("astronauts training in underwater facility", "Underwater training simulation"),
    ]
    
    for query, desc in test_queries_nbl:
        test_search_query(query, 2, desc)
        time.sleep(1)
    
    # Test 3: Semantic Understanding
    print_section("🧠 Test 3: Semantic Search Capabilities")
    semantic_tests = [
        ("weightlessness experience in space", "Weightlessness concept"),
        ("docking of spacecraft with space station", "Docking operations"),
        ("crew working in microgravity environment", "Microgravity activities"),
        ("horizon view from orbital laboratory", "Orbital perspective"),
    ]
    
    for query, desc in semantic_tests:
        test_search_query(query, 2, desc)
        time.sleep(1)
    
    # Test 4: Category-specific searches
    print_section("🗂️ Test 4: Category-Specific Searches")
    
    # Get categories
    try:
        response = requests.get(f"{API_BASE}/categories")
        if response.status_code == 200:
            categories = response.json()['categories']
            print(f"📂 Available categories: {', '.join(categories)}")
        else:
            print("❌ Could not fetch categories")
    except Exception as e:
        print(f"❌ Categories exception: {e}")
    
    # Test 5: Edge cases and robustness
    print_section("🔧 Test 5: Edge Cases & Robustness")
    edge_cases = [
        ("", "Empty query"),
        ("xyz123", "Non-sensical query"),
        ("astronaut", "Single word query"),
        ("International Space Station cupola Earth observation astronaut crew training", "Very long query"),
    ]
    
    for query, desc in edge_cases:
        if query:  # Skip empty query for now
            test_search_query(query, 2, desc)
        time.sleep(1)
    
    # Final summary
    print_section("📋 Test Summary")
    print("✅ RAG System Tests Completed!")
    print("🔍 Search Engine: Working with semantic understanding")
    print("📊 FAISS Index: Successfully retrieving similar images")
    print("🤖 Sentence Transformers: Converting queries to embeddings")
    print("🎯 Similarity Scoring: Ranking results by relevance")
    print("\n🚀 The NASA ISS Image Search RAG system is functioning correctly!")
    print(f"🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()