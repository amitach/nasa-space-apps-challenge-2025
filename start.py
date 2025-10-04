#!/usr/bin/env python3
"""
Startup script for ISS Image Search API and Web Interface
"""

import os
import sys
import time
import subprocess
import signal
import threading
from pathlib import Path

def start_api():
    """Start the API server"""
    print("🚀 Starting ISS Search API...")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 API server stopped")
    except Exception as e:
        print(f"❌ API server error: {e}")

def start_web():
    """Start the web interface"""
    print("🌐 Starting Web Interface...")
    try:
        subprocess.run([sys.executable, "src/web/app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Web interface stopped")
    except Exception as e:
        print(f"❌ Web interface error: {e}")

def main():
    """Main startup function"""
    print("=" * 60)
    print("🚀 ISS Image Search API - Startup Script")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Error: main.py not found. Please run from project root.")
        sys.exit(1)
    
    # Check if data file exists
    if not Path("src/data/iss_images_organized.json").exists():
        print("❌ Error: Data file not found. Please ensure src/data/iss_images_organized.json exists.")
        sys.exit(1)
    
    print("✅ Project structure looks good")
    print("📍 API will run on: http://localhost:5001")
    print("📍 Web interface will run on: http://localhost:8080")
    print("=" * 60)
    
    # Start API in background thread
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    
    # Wait a moment for API to start
    print("⏳ Waiting for API to initialize...")
    time.sleep(5)
    
    # Start web interface in main thread
    try:
        start_web()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        sys.exit(0)

if __name__ == '__main__':
    main()
