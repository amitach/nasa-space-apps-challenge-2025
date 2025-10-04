#!/usr/bin/env python3
"""
ISS Search API Startup Script
This script starts both the search API and web interface
"""

import subprocess
import time
import sys
import os
from threading import Thread

def start_api_server():
    """Start the Flask API server"""
    print("🚀 Starting ISS Search API server...")
    try:
        subprocess.run([sys.executable, "iss_search_api.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 API server stopped")
    except Exception as e:
        print(f"❌ Error starting API server: {e}")

def start_web_interface():
    """Start the web interface server"""
    print("🌐 Starting web interface server...")
    try:
        subprocess.run([sys.executable, "web_interface.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Web interface stopped")
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")

def main():
    """Main startup function"""
    print("=" * 60)
    print("🚀 ISS Image Search System")
    print("=" * 60)
    print()
    
    # Check if required files exist
    required_files = [
        'iss_images_organized.json',
        'iss_search_api.py',
        'web_interface.py',
        'static/index.html'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure all files are present before starting.")
        return
    
    print("✅ All required files found")
    print()
    
    # Start API server in a separate thread
    api_thread = Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    # Wait a moment for API to start
    print("⏳ Waiting for API server to initialize...")
    time.sleep(3)
    
    # Start web interface
    try:
        start_web_interface()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
