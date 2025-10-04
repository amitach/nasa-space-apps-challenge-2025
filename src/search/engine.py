#!/usr/bin/env python3
"""
ISS Image Search Engine using FAISS and Sentence Transformers
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class ISSSearchEngine:
    """Search engine for ISS images using vector similarity"""
    
    def __init__(self, data_file: str = None):
        self.data_file = data_file
        self.encoder = None
        self.index = None
        self.images_data = []
        self.categories = []
        
    def load_data(self) -> bool:
        """Load image data and build vector index"""
        try:
            # Set default data file if not provided
            if self.data_file is None:
                self.data_file = "src/data/iss_images_organized.json"
            
            # Load images from JSON file
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            # Extract images from both cupola_images and nbl_training_images sections
            self.images_data = data.get('cupola_images', []) + data.get('nbl_training_images', [])
            logger.info(f"Loaded {len(self.images_data)} images")
            
            if not self.images_data:
                logger.warning("No images loaded. Cannot initialize search engine.")
                return False
            
            # Initialize SentenceTransformer model
            logger.info("Initializing SentenceTransformer model...")
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("SentenceTransformer model loaded.")
            
            # Generate embeddings
            descriptions = [img['description'] for img in self.images_data]
            logger.info("Generating embeddings...")
            embeddings = self.encoder.encode(descriptions, show_progress_bar=True)
            embeddings = np.array(embeddings).astype('float32')
            
            # Build FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings)
            logger.info(f"Built FAISS index with {self.index.ntotal} vectors")
            
            # Extract categories
            self.categories = list(set(data.get('collection_info', {}).get('categories', [])))
            if not self.categories:
                # Fallback if 'categories' key is not in collection_info
                self.categories = ["Cupola Images", "NBL Training Images"]
            
            logger.info("Search engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load data or initialize search engine: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar images using vector similarity"""
        if self.index is None or self.encoder is None:
            logger.error("Search engine not initialized")
            return []
        
        try:
            # Encode query
            query_embedding = self.encoder.encode([query]).astype('float32')
            
            # Search
            distances, indices = self.index.search(query_embedding, top_k)
            
            # Prepare results
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.images_data):
                    image = self.images_data[idx].copy()
                    image['similarity_score'] = float(1 / (1 + distance))  # Convert distance to similarity
                    image['rank'] = i + 1
                    results.append(image)
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_image_by_id(self, nasa_id: str) -> Optional[Dict[str, Any]]:
        """Get specific image by NASA ID"""
        for image in self.images_data:
            if image.get('nasa_id') == nasa_id:
                return image
        return None
    
    def get_categories(self) -> List[str]:
        """Get available categories"""
        return self.categories
    
    def get_stats(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        return {
            'total_images': len(self.images_data),
            'index_ready': self.index is not None,
            'categories': self.categories,
            'model_loaded': self.encoder is not None
        }
