# 🖼️ Image URLs in RAG Search API

## ✅ **Image URLs Are Already Included!**

Your RAG search API **already returns image URLs** in the JSON response! Here's what you get:

## 📋 **Complete JSON Response Structure**

When you search the API, you get a complete JSON response that includes:

```json
{
  "query": "astronauts in cupola viewing earth",
  "total_results": 3,
  "results": [
    {
      "nasa_id": "iss040e006000",
      "image_url": "https://images-assets.nasa.gov/image/iss040e006000/iss040e006000~orig.jpg",
      "description": "ISS040-E-006000 (29 May 2014) --- One of the six Expedition 40 crew members positioned himself in the Cupola to photograph this image of Earth's horizon and the blackness of space.",
      "similarity_score": 0.707,
      "rank": 1,
      "keywords": ["iss", "cupola", "orbital outpost", "expedition", "space station"],
      "category": "earth_observation",
      "relevance_score": 38
    }
  ]
}
```

## 🔑 **Key Fields for Image Display**

- **`image_url`**: Direct URL to high-resolution NASA image (ready to use!)
- **`nasa_id`**: Unique NASA identifier
- **`description`**: Detailed image description
- **`similarity_score`**: Relevance score (0-1, higher = more relevant)
- **`keywords`**: Extracted keywords
- **`category`**: Image category

## 🚀 **How to Use Image URLs**

### **1. Direct Image Display (HTML)**
```html
<img src="https://images-assets.nasa.gov/image/iss040e006000/iss040e006000~orig.jpg" 
     alt="ISS Cupola Earth View" />
```

### **2. Python Integration**
```python
import requests

# Search for images
response = requests.post('http://localhost:5001/search', json={
    'query': 'astronauts in cupola viewing earth',
    'top_k': 5
})

results = response.json()
for image in results['results']:
    print(f"Image: {image['image_url']}")
    print(f"Description: {image['description']}")
    print(f"Relevance: {image['similarity_score']:.3f}")
```

### **3. Mobile App Integration**
```json
{
  "search_query": "astronauts in cupola",
  "images": [
    {
      "id": "iss040e006000",
      "url": "https://images-assets.nasa.gov/image/iss040e006000/iss040e006000~orig.jpg",
      "title": "Cupola Earth View",
      "description": "One of the six Expedition 40 crew members...",
      "relevance": 0.707
    }
  ]
}
```

## 🧪 **Test the Image URLs**

Run this to see the image URLs in action:

```bash
# Test the API
python test_image_urls.py

# See usage examples
python example_usage.py
```

## 🌐 **Image URL Examples**

Here are some actual image URLs from the API:

- **Cupola Earth View**: `https://images-assets.nasa.gov/image/iss040e006000/iss040e006000~orig.jpg`
- **Space Shuttle Endeavour**: `https://images-assets.nasa.gov/image/iss022e069156/iss022e069156~orig.jpg`
- **EVA Training**: `https://images-assets.nasa.gov/image/jsc2010e180084/jsc2010e180084~orig.jpg`
- **Aurora from Space**: `https://images-assets.nasa.gov/image/iss042e033478/iss042e033478~orig.jpg`

## ✅ **Image URLs Are Ready to Use!**

The RAG search API is **already complete** with image URLs! You can:

1. **Search** using natural language queries
2. **Get results** with direct image URLs
3. **Display images** immediately in your app
4. **Access high-resolution** NASA images
5. **Use all metadata** (descriptions, keywords, categories)

## 🎯 **Perfect for Your ISS 25th Anniversary App**

Your RAG search system is ready for integration! Users can:

- Search for ISS images using natural language
- Get direct URLs to high-resolution NASA images
- See relevant descriptions and metadata
- Display images immediately in your app

**The image URLs are already there - you're all set!** 🚀
