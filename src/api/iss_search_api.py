import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from flask import Flask, request, jsonify
import os
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ISSSearchEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """Initialize the ISS search engine with FAISS vector index"""
        self.model_name = model_name
        self.encoder = SentenceTransformer(model_name)
        self.index = None
        self.images_data = []
        self.image_metadata = {}
        
    def load_images_data(self, json_file_path: str):
        """Load images data from JSON file"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both organized and flat JSON structures
            if isinstance(data, dict) and 'cupola_images' in data:
                # Organized structure
                self.images_data = data['cupola_images'] + data['nbl_training_images']
                self.image_metadata = data.get('metadata', {})
            elif isinstance(data, list):
                # Flat structure
                self.images_data = data
            else:
                raise ValueError("Unsupported JSON structure")
            
            logger.info(f"Loaded {len(self.images_data)} images")
            return True
            
        except Exception as e:
            logger.error(f"Error loading images data: {e}")
            return False
    
    def create_searchable_text(self, image_data: Dict[str, Any]) -> str:
        """Create searchable text from image metadata"""
        text_parts = []
        
        # Add description
        if 'description' in image_data:
            text_parts.append(image_data['description'])
        
        # Add NASA ID
        if 'nasa_id' in image_data:
            text_parts.append(f"NASA ID: {image_data['nasa_id']}")
        
        # Add keywords
        if 'keywords' in image_data:
            text_parts.append(f"Keywords: {', '.join(image_data['keywords'])}")
        
        # Add category
        if 'category' in image_data:
            text_parts.append(f"Category: {image_data['category']}")
        
        # Add source
        if 'source' in image_data:
            text_parts.append(f"Source: {image_data['source']}")
        
        return " ".join(text_parts)
    
    def build_vector_index(self):
        """Build FAISS vector index from images data"""
        if not self.images_data:
            logger.error("No images data loaded")
            return False
        
        try:
            # Create searchable texts
            searchable_texts = []
            for i, image_data in enumerate(self.images_data):
                text = self.create_searchable_text(image_data)
                searchable_texts.append(text)
                logger.debug(f"Image {i}: {text[:100]}...")
            
            # Generate embeddings
            logger.info("Generating embeddings...")
            embeddings = self.encoder.encode(searchable_texts)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add embeddings to index
            self.index.add(embeddings.astype('float32'))
            
            logger.info(f"Built FAISS index with {self.index.ntotal} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Error building vector index: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar images using vector similarity"""
        if self.index is None:
            logger.error("Vector index not built")
            return []
        
        try:
            # Encode query
            query_embedding = self.encoder.encode([query])
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            # Prepare results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.images_data):
                    image_data = self.images_data[idx].copy()
                    image_data['similarity_score'] = float(score)
                    image_data['rank'] = i + 1
                    results.append(image_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []

# Initialize Flask app
app = Flask(__name__)

# Global search engine instance
search_engine = ISSSearchEngine()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'ISS Search API is running',
        'index_loaded': search_engine.index is not None,
        'total_images': len(search_engine.images_data)
    })

@app.route('/search', methods=['POST'])
def search_images():
    """Search for images using natural language queries"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Query parameter is required',
                'example': {'query': 'astronauts in cupola viewing earth'}
            }), 400
        
        query = data['query']
        top_k = data.get('top_k', 5)
        
        if not isinstance(query, str) or not query.strip():
            return jsonify({
                'error': 'Query must be a non-empty string'
            }), 400
        
        if not isinstance(top_k, int) or top_k < 1 or top_k > 20:
            return jsonify({
                'error': 'top_k must be an integer between 1 and 20'
            }), 400
        
        # Perform search
        results = search_engine.search(query, top_k)
        
        return jsonify({
            'query': query,
            'total_results': len(results),
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/search', methods=['GET'])
def search_images_get():
    """Search for images using GET request with query parameter"""
    try:
        query = request.args.get('q', '')
        top_k = int(request.args.get('top_k', 5))
        
        if not query.strip():
            return jsonify({
                'error': 'Query parameter "q" is required',
                'example': '/search?q=astronauts+in+cupola+viewing+earth&top_k=5'
            }), 400
        
        if top_k < 1 or top_k > 20:
            return jsonify({
                'error': 'top_k must be between 1 and 20'
            }), 400
        
        # Perform search
        results = search_engine.search(query, top_k)
        
        return jsonify({
            'query': query,
            'total_results': len(results),
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error in search GET endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/images/<nasa_id>', methods=['GET'])
def get_image_by_id(nasa_id):
    """Get specific image by NASA ID"""
    try:
        for image_data in search_engine.images_data:
            if image_data.get('nasa_id') == nasa_id:
                return jsonify({
                    'found': True,
                    'image': image_data
                })
        
        return jsonify({
            'found': False,
            'message': f'Image with NASA ID "{nasa_id}" not found'
        }), 404
        
    except Exception as e:
        logger.error(f"Error getting image by ID: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/images', methods=['GET'])
def list_images():
    """List all images with optional filtering"""
    try:
        category = request.args.get('category')
        source = request.args.get('source')
        limit = int(request.args.get('limit', 50))
        
        filtered_images = search_engine.images_data
        
        if category:
            filtered_images = [img for img in filtered_images if img.get('category') == category]
        
        if source:
            filtered_images = [img for img in filtered_images if img.get('source') == source]
        
        # Limit results
        filtered_images = filtered_images[:limit]
        
        return jsonify({
            'total_images': len(filtered_images),
            'filters': {
                'category': category,
                'source': source,
                'limit': limit
            },
            'images': filtered_images
        })
        
    except Exception as e:
        logger.error(f"Error listing images: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/categories', methods=['GET'])
def get_categories():
    """Get all available categories and sources"""
    try:
        categories = set()
        sources = set()
        
        for image_data in search_engine.images_data:
            if 'category' in image_data:
                categories.add(image_data['category'])
            if 'source' in image_data:
                sources.add(image_data['source'])
        
        return jsonify({
            'categories': sorted(list(categories)),
            'sources': sorted(list(sources)),
            'total_images': len(search_engine.images_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

def initialize_search_engine():
    """Initialize the search engine with images data"""
    # Try to load organized structure first, then fallback to flat structure
    json_files = [
        'iss_images_organized.json',
        'final_iss_images.json',
        'selected_iss_images.json'
    ]
    
    for json_file in json_files:
        if os.path.exists(json_file):
            logger.info(f"Loading images from {json_file}")
            if search_engine.load_images_data(json_file):
                if search_engine.build_vector_index():
                    logger.info("Search engine initialized successfully")
                    return True
                else:
                    logger.error("Failed to build vector index")
            else:
                logger.error(f"Failed to load images from {json_file}")
    
    logger.error("No valid images data file found")
    return False

if __name__ == '__main__':
    # Initialize search engine
    if initialize_search_engine():
        logger.info("Starting ISS Search API...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        logger.error("Failed to initialize search engine. Exiting.")
        exit(1)
