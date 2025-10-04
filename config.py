"""
Configuration settings for ISS Image Search API
"""

import os

# API Configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 5001))
API_DEBUG = os.getenv('API_DEBUG', 'False').lower() == 'true'

# Data Configuration
DATA_FILE = os.getenv('DATA_FILE', 'src/data/iss_images_organized.json')
IMAGES_DIR = os.getenv('IMAGES_DIR', 'images')

# Search Configuration
DEFAULT_TOP_K = int(os.getenv('DEFAULT_TOP_K', 5))
MAX_TOP_K = int(os.getenv('MAX_TOP_K', 20))
MODEL_NAME = os.getenv('MODEL_NAME', 'all-MiniLM-L6-v2')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Web Interface Configuration
WEB_HOST = os.getenv('WEB_HOST', '0.0.0.0')
WEB_PORT = int(os.getenv('WEB_PORT', 8080))
