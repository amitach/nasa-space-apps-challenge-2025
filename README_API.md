# ISS Image Search API

A Flask-based RAG (Retrieval-Augmented Generation) search API for NASA's International Space Station images using FAISS vector indexing and sentence transformers.

## Features

- 🔍 **Natural Language Search**: Search images using natural language queries
- 🚀 **FAISS Vector Indexing**: Fast similarity search using Facebook's FAISS library
- 🧠 **Sentence Transformers**: Semantic understanding using pre-trained models
- 🌐 **RESTful API**: Clean REST endpoints for easy integration
- 🎨 **Web Interface**: Beautiful web UI for testing and demonstration
- 📊 **Filtering & Categories**: Filter by category, source, and other metadata
- ⚡ **Fast & Local**: All processing happens locally, no external API calls

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
python iss_search_api.py
```

The API will be available at `http://localhost:5000`

### 3. Start the Web Interface (Optional)

```bash
python web_interface.py
```

The web interface will be available at `http://localhost:8080`

### 4. Or Start Both Together

```bash
python start_api.py
```

## API Endpoints

### Search Images

**POST** `/search`
```json
{
  "query": "astronauts in cupola viewing earth",
  "top_k": 5
}
```

**GET** `/search?q=astronauts+in+cupola+viewing+earth&top_k=5`

### Get Image by ID

**GET** `/images/{nasa_id}`

Example: `/images/iss043e122274`

### List Images with Filtering

**GET** `/images?category=earth_observation&source=cupola&limit=10`

### Get Available Categories

**GET** `/categories`

### Health Check

**GET** `/health`

## Image URLs

The API returns complete image data including direct URLs to high-resolution NASA images:

```json
{
  "results": [
    {
      "nasa_id": "iss040e006000",
      "image_url": "https://images-assets.nasa.gov/image/iss040e006000/iss040e006000~orig.jpg",
      "description": "ISS040-E-006000 (29 May 2014) --- One of the six Expedition 40 crew members...",
      "similarity_score": 0.707,
      "keywords": ["iss", "cupola", "expedition", "space station"],
      "category": "earth_observation"
    }
  ]
}
```

**Key Fields:**
- `image_url`: Direct URL to the high-resolution NASA image (ready to use in `<img>` tags)
- `nasa_id`: Unique NASA identifier for the image
- `description`: Detailed description of the image
- `similarity_score`: Relevance score (0-1, higher is more relevant)
- `keywords`: Extracted keywords from the description
- `category`: Image category (earth_observation, crew_activities, etc.)

## Example Usage

### Python Client

```python
import requests

# Search for images
response = requests.post('http://localhost:5000/search', json={
    'query': 'astronauts in cupola viewing earth',
    'top_k': 5
})

results = response.json()
print(f"Found {results['total_results']} images")

for image in results['results']:
    print(f"- {image['nasa_id']}: {image['description'][:100]}...")
    print(f"  Image URL: {image['image_url']}")
    print(f"  Similarity: {image['similarity_score']:.3f}")
```

### cURL Examples

```bash
# Search for images
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "space shuttle mission", "top_k": 3}'

# Get specific image
curl http://localhost:5000/images/iss043e122274

# List all categories
curl http://localhost:5000/categories

# Health check
curl http://localhost:5000/health
```

## Search Examples

Try these example queries:

- `"astronauts in cupola viewing earth"`
- `"space shuttle mission"`
- `"EVA training underwater"`
- `"aurora from space"`
- `"robotic arm operations"`
- `"earth observation"`
- `"crew activities"`
- `"sunrise from space"`

## Architecture

### Components

1. **Sentence Transformer**: Converts text to embeddings using `all-MiniLM-L6-v2`
2. **FAISS Index**: Fast similarity search using cosine similarity
3. **Flask API**: RESTful endpoints for search and retrieval
4. **Web Interface**: HTML/JavaScript frontend for testing

### Data Flow

1. **Indexing**: Images are loaded and their metadata is converted to searchable text
2. **Embedding**: Text is converted to vectors using sentence transformers
3. **Indexing**: Vectors are stored in FAISS index for fast retrieval
4. **Search**: Query is embedded and searched against the index
5. **Results**: Similar images are returned with similarity scores

### File Structure

```
├── iss_search_api.py          # Main Flask API
├── web_interface.py           # Web interface server
├── test_search_api.py         # API test client
├── start_api.py              # Startup script
├── static/
│   └── index.html            # Web interface
├── requirements.txt          # Python dependencies
└── README_API.md            # This file
```

## Configuration

### Model Selection

The default model is `all-MiniLM-L6-v2` which provides a good balance of speed and accuracy. You can change it in the `ISSSearchEngine` class:

```python
search_engine = ISSSearchEngine(model_name='all-MiniLM-L6-v2')
```

Other good options:
- `all-mpnet-base-v2` (more accurate, slower)
- `paraphrase-MiniLM-L6-v2` (good for semantic similarity)

### Search Parameters

- `top_k`: Number of results to return (1-20)
- `similarity_threshold`: Minimum similarity score (optional)

## Performance

- **Indexing Time**: ~2-3 seconds for 40 images
- **Search Time**: ~50-100ms per query
- **Memory Usage**: ~50MB for the full index
- **Model Size**: ~90MB for the sentence transformer

## Troubleshooting

### Common Issues

1. **"No valid images data file found"**
   - Ensure `iss_images_organized.json` exists
   - Check file permissions

2. **"Failed to build vector index"**
   - Check if all required packages are installed
   - Verify the JSON file structure

3. **"API is not running"**
   - Check if port 5000 is available
   - Look for error messages in the console

### Debug Mode

Run with debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Development

### Adding New Images

1. Add images to the JSON file
2. Restart the API server
3. The index will be rebuilt automatically

### Customizing Search

Modify the `create_searchable_text` method to include additional metadata fields in the search.

### Extending the API

Add new endpoints by extending the Flask app in `iss_search_api.py`.

## License

This project is part of the NASA Space Apps Challenge 2025.

## Support

For issues or questions, please check the troubleshooting section or create an issue in the project repository.
