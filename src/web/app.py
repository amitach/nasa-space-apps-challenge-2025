#!/usr/bin/env python3
"""
Web Interface for ISS Image Search API
"""

import os
import sys
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import WEB_HOST, WEB_PORT, API_HOST, API_PORT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# API base URL
API_BASE_URL = f"http://{API_HOST}:{API_PORT}"

@app.route('/')
def index():
    """Main search page"""
    return render_template('index.html', api_url=API_BASE_URL)

@app.route('/search')
def search_page():
    """Search results page"""
    query = request.args.get('q', '')
    return render_template('search.html', query=query, api_url=API_BASE_URL)

@app.route('/api/health')
def api_health():
    """Proxy to API health check"""
    try:
        import requests
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 503

@app.route('/api/search')
def api_search():
    """Proxy to API search"""
    try:
        import requests
        query = request.args.get('q', '')
        top_k = request.args.get('top_k', 5)
        
        response = requests.get(f"{API_BASE_URL}/search", params={
            'q': query,
            'top_k': top_k
        }, timeout=10)
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_web_app():
    """Web application factory"""
    return app

if __name__ == '__main__':
    print("🌐 Starting ISS Search Web Interface...")
    print(f"📍 Host: {WEB_HOST}")
    print(f"📍 Port: {WEB_PORT}")
    print(f"🔗 API URL: {API_BASE_URL}")
    
    app.run(host=WEB_HOST, port=WEB_PORT, debug=True)
