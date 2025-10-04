#!/usr/bin/env python3
"""
Simplified ISS Search API for testing
"""

import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from flask import Flask, request, jsonify
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global variables
encoder = None
index = None
images_data = []

def load_data():
    """Load images data and build index"""
    global encoder, index, images_data
    
    try:
        # Load images
        with open('iss_images_organized.json', 'r') as f:
            data = json.load(f)
        
        images_data = data['cupola_images'] + data['nbl_training_images']
        logger.info(f"Loaded {len(images_data)} images")
        
        # Initialize encoder
        encoder = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Encoder loaded")
        
        # Create searchable texts
        texts = []
        for img in images_data:
            text = f"{img['description']} {img['nasa_id']} {' '.join(img.get('keywords', []))}"
            texts.append(text)
        
        # Generate embeddings
        embeddings = encoder.encode(texts)
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        faiss.normalize_L2(embeddings)
        index.add(embeddings.astype('float32'))
        
        logger.info("Index built successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return False

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'total_images': len(images_data),
        'index_ready': index is not None
    })

@app.route('/search', methods=['POST'])
def search():
    """Search images"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Encode query
        query_embedding = encoder.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = index.search(query_embedding.astype('float32'), top_k)
        
        # Prepare results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(images_data):
                image = images_data[idx].copy()
                image['similarity_score'] = float(score)
                image['rank'] = i + 1
                results.append(image)
        
        return jsonify({
            'query': query,
            'total_results': len(results),
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['GET'])
def search_get():
    """Search with GET request"""
    query = request.args.get('q', '')
    top_k = int(request.args.get('top_k', 5))
    
    if not query:
        return jsonify({'error': 'Query parameter q is required'}), 400
    
    # Use POST endpoint logic
    return search()

if __name__ == '__main__':
    print("🚀 Starting ISS Search API...")
    
    if load_data():
        print("✅ Data loaded successfully")
        print("🌐 API running at http://localhost:5001")
        app.run(host='0.0.0.0', port=5001, debug=False)
    else:
        print("❌ Failed to load data")
        exit(1)
