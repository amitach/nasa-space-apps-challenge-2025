#!/usr/bin/env python3
"""
Main entry point for ISS Image Search API
"""

import sys
import os
import logging
from config import API_HOST, API_PORT, API_DEBUG, LOG_LEVEL, LOG_FORMAT

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api.app import create_app

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper()),
        format=LOG_FORMAT
    )

def main():
    """Main entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("🚀 Starting ISS Image Search API...")
    print(f"📍 Host: {API_HOST}")
    print(f"📍 Port: {API_PORT}")
    print(f"🔧 Debug: {API_DEBUG}")
    
    app = create_app()
    
    # Check if search engine is ready
    from src.api.app import search_engine
    if not search_engine.index:
        print("❌ Search engine not initialized. Check data file and try again.")
        sys.exit(1)
    
    print("✅ Search engine ready")
    
    try:
        app.run(host=API_HOST, port=API_PORT, debug=API_DEBUG)
    except KeyboardInterrupt:
        print("\n👋 Shutting down ISS Search API...")
    except Exception as e:
        logger.error(f"Failed to start API: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
