#!/usr/bin/env python3
"""
ISS Image Search API - Main Flask Application
"""

import logging
from flask import Flask, request, jsonify
from src.search.engine import ISSSearchEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global search engine instance
search_engine = ISSSearchEngine()

# Initialize the search engine
def init_search_engine():
    """Initialize the search engine"""
    global search_engine
    if not search_engine.load_data():
        logger.error("Failed to initialize search engine")
        return False
    logger.info("Search engine initialized successfully")
    return True

# Initialize on module load
init_search_engine()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    stats = search_engine.get_stats()
    return jsonify({
        'status': 'healthy' if stats['index_ready'] else 'unhealthy',
        'index_ready': stats['index_ready'],
        'total_images': stats['total_images'],
        'categories': stats['categories']
    }), 200 if stats['index_ready'] else 503

@app.route('/search', methods=['POST'])
def search_images():
    """Search for images using natural language queries"""
    if not search_engine.index:
        return jsonify({"error": "Search engine not initialized"}), 503
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        if not isinstance(top_k, int) or top_k < 1 or top_k > 20:
            return jsonify({"error": "top_k must be an integer between 1 and 20"}), 400
        
        # Perform search
        results = search_engine.search(query, top_k)
        
        return jsonify({
            'query': query,
            'total_results': len(results),
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['GET'])
def search_images_get():
    """Search for images using GET request with query parameters"""
    if not search_engine.index:
        return jsonify({"error": "Search engine not initialized"}), 503
    
    try:
        query = request.args.get('q', '').strip()
        top_k = int(request.args.get('top_k', 5))
        
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
        
        if top_k < 1 or top_k > 20:
            return jsonify({"error": "top_k must be between 1 and 20"}), 400
        
        # Perform search
        results = search_engine.search(query, top_k)
        
        return jsonify({
            'query': query,
            'total_results': len(results),
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Search GET error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/images/<nasa_id>', methods=['GET'])
def get_image_by_id(nasa_id):
    """Get specific image by NASA ID"""
    try:
        image = search_engine.get_image_by_id(nasa_id)
        if image:
            return jsonify({
                'found': True,
                'image': image
            }), 200
        else:
            return jsonify({
                'found': False,
                'message': f'Image with NASA ID "{nasa_id}" not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting image by ID: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/categories', methods=['GET'])
def get_categories():
    """Get available image categories"""
    try:
        categories = search_engine.get_categories()
        return jsonify({"categories": categories}), 200
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get search engine statistics"""
    try:
        stats = search_engine.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500

def create_app():
    """Application factory"""
    return app

if __name__ == '__main__':
    print("🚀 Starting ISS Search API...")
    
    if search_engine.load_data():
        print("✅ Data loaded successfully")
        print("🌐 API running at http://localhost:5001")
        app.run(host='0.0.0.0', port=5001, debug=False)
    else:
        print("❌ Failed to load data")
        exit(1)
