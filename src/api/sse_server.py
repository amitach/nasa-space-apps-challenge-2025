"""
Corrected SSE Server for Tavus Integration
Handles Server-Sent Events and Tavus tool calls properly
"""

import json
import time
import logging
import queue
import threading
from flask import Flask, Response, request, jsonify
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.search.engine import ISSSearchEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
sse_app = Flask(__name__)
CORS(sse_app, origins=['http://localhost:3000', 'http://localhost:3001'])

# Add request logging middleware
@sse_app.before_request
def log_request():
    print("=" * 80)
    print(f"📨 INCOMING REQUEST: {request.method} {request.path}")
    print(f"📨 Headers: {dict(request.headers)}")
    print(f"📨 Remote Address: {request.remote_addr}")
    print(f"📨 User Agent: {request.headers.get('User-Agent', 'Unknown')}")
    if request.is_json:
        print(f"📨 JSON Body: {json.dumps(request.json, indent=2)}")
    elif request.form:
        print(f"📨 Form Data: {dict(request.form)}")
    else:
        print(f"📨 Raw Data: {request.get_data()}")
    print("=" * 80)

# Global variables
clients = []  # List to hold SSE client connections
search_engine = ISSSearchEngine()

def init_sse_search_engine():
    """Initialize the search engine for SSE server"""
    global search_engine
    if not search_engine.load_data():
        logger.error("Failed to initialize search engine for SSE server")
        return False
    logger.info("SSE search engine initialized successfully")
    return True

# Initialize search engine
init_sse_search_engine()

def event_stream():
    """Generate SSE event stream"""
    q = queue.Queue()
    clients.append(q)
    
    # Send initial connection event
    connection_id = f"conn_{int(time.time() * 1000)}_{hash(q) % 10000}"
    initial_message = {
        "type": "connected",
        "connection_id": connection_id,
        "status": "connected",
        "message": "SSE connection established"
    }
    yield f"event: connected\ndata: {json.dumps(initial_message)}\n\n"
    
    try:
        while True:
            message = q.get()
            # Send with appropriate event type
            event_type = message.get('type', 'data')
            yield f"event: {event_type}\ndata: {json.dumps(message)}\n\n"
    except GeneratorExit:
        clients.remove(q)
        logger.info("SSE client disconnected")

def send_sse_event(data):
    """Send event to all connected SSE clients"""
    print(f"📡 SEND_SSE_EVENT CALLED - {len(clients)} connected clients")
    print(f"📡 Data to send: {json.dumps(data, indent=2)}")
    
    if not clients:
        print("⚠️ No SSE clients connected!")
        return
        
    for i, client_q in enumerate(clients):
        try:
            client_q.put(data)
            print(f"✅ Sent to client {i+1}/{len(clients)}")
        except Exception as e:
            print(f"❌ Failed to send to client {i+1}: {e}")
            logger.error(f"Failed to send SSE event to client {i+1}: {e}")

@sse_app.route('/events')
def sse_events():
    """SSE endpoint for real-time updates"""
    response = Response(event_stream(), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Cache-Control"
    return response

@sse_app.route('/api/tavus-webhook', methods=['POST'])
def tavus_webhook():
    """Handle webhooks from Tavus - just log and acknowledge"""
    try:
        payload = request.json
        print(f"🔔 WEBHOOK: {payload.get('event_type', 'unknown')} - {payload.get('message_type', 'unknown')}")
        
        # Just acknowledge - frontend will handle tool calls
        return jsonify({"status": "received"}), 200
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return jsonify({"error": str(e)}), 500


@sse_app.route('/api/tavus-tool-call', methods=['POST'])
def tavus_tool_call_endpoint():
    """Handle tool calls - does the actual work"""
    try:
        payload = request.json
        print("=" * 80)
        print("🔧 TOOL CALL ENDPOINT RECEIVED")
        print("=" * 80)
        print(f"📨 Payload: {json.dumps(payload, indent=2)}")
        print("=" * 80)
        
        # Handle different payload formats
        if payload.get('type') == 'tool_call':
            # Tavus webhook format
            tool_call = payload['tool_call']
            tool_name = tool_call.get('name')
            tool_params = tool_call.get('parameters', {})
            connection_id = payload.get('conversation_id')
        elif payload.get('tool_name'):
            # Direct frontend call format
            tool_name = payload.get('tool_name')
            tool_params = payload.get('tool_params', {})
            connection_id = payload.get('connection_id')
        else:
            return jsonify({"error": "Invalid payload format"}), 400
        
        # Do the actual tool call work
        if tool_name == 'fetch_relevant_image':
            query = tool_params.get('query')
            top_k = tool_params.get('top_k', 5)

            print("=" * 80)
            print("🔍 EXECUTING IMAGE SEARCH")
            print("=" * 80)
            print(f"📝 User query: '{query}'")
            print(f"📊 Requested images: {top_k}")
            print("=" * 80)

            if query:
                print(f"🚀 Starting vector search for: '{query}'")
                images = search_engine.search(query, top_k)
                print(f"📸 Search completed - Found {len(images)} images")
                
                # Log the first few images found
                for i, img in enumerate(images[:3]):
                    print(f"   {i+1}. {img.get('nasa_id', 'unknown')} - Score: {img.get('similarity_score', 0):.3f}")
                
                print("=" * 80)
                print("📡 SENDING IMAGES TO FRONTEND VIA SSE")
                print("=" * 80)
                
                sse_data = {
                    "type": "images",
                    "images": images,
                    "query": query,
                    "total": len(images),
                    "source": "tavus_tool_call",
                    "timestamp": time.time()
                }
                send_sse_event(sse_data)
                
                print(f"✅ Successfully sent {len(images)} images to frontend")
                print("=" * 100)
                
                return jsonify({
                    "tool_output": {
                        "status": "success", 
                        "message": f"Fetched {len(images)} images for '{query}'",
                        "images_found": len(images)
                    }
                }), 200
            else:
                print("❌ ERROR: No query provided for image search")
                return jsonify({"tool_output": {"status": "error", "message": "Query not provided for image search"}}), 400
        else:
            print(f"⚠️ Unknown tool: {tool_name}")
            return jsonify({"tool_output": {"status": "error", "message": f"Unknown tool: {tool_name}"}}), 400
            
    except Exception as e:
        print(f"❌ ERROR in tool call endpoint: {e}")
        logger.error(f"Error handling tool call: {e}")
        return jsonify({"error": str(e)}), 500


@sse_app.route('/api/search', methods=['POST'])
def search_images():
    """Direct image search endpoint"""
    try:
        payload = request.json
        query = payload.get('query', '')
        top_k = payload.get('top_k', 5)

        if not query:
            return jsonify({"error": "Query parameter is required"}), 400

        # Search for images
        images = search_engine.search(query, top_k)

        # Send to frontend via SSE
        sse_data = {
            "type": "images",
            "images": images,
            "query": query,
            "total": len(images),
            "source": "manual",
            "timestamp": time.time()
        }
        send_sse_event(sse_data)

        return jsonify({
            "success": True,
            "data": {
                "total": len(images),
                "images": images
            }
        }), 200

    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@sse_app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    stats = search_engine.get_stats()
    return jsonify({
        "status": "healthy" if stats['index_ready'] else "unhealthy",
        "index_ready": stats['index_ready'],
        "total_images": stats['total_images'],
        "categories": stats['categories'],
        "connected_clients": len(clients)
    }), 200 if stats['index_ready'] else 503

@sse_app.route('/api/tavus-test', methods=['GET', 'POST'])
def tavus_test():
    """Simple test endpoint to verify Tavus can reach our server"""
    print("🧪 TAVUS TEST ENDPOINT HIT!")
    return jsonify({
        'message': 'Tavus can reach our server!',
        'timestamp': time.time(),
        'method': request.method,
        'headers': dict(request.headers)
    }), 200

@sse_app.route('/api/test-sse', methods=['POST'])
def test_sse():
    """Test endpoint to send SSE events"""
    try:
        payload = request.json
        message = payload.get('message', 'Test message')
        
        sse_data = {
            "type": "test",
            "message": message,
            "timestamp": time.time()
        }
        send_sse_event(sse_data)
        
        return jsonify({"success": True, "message": "SSE event sent"}), 200
        
    except Exception as e:
        logger.error(f"Error in test SSE endpoint: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting SSE Server on port 5002...")
    sse_app.run(host='0.0.0.0', port=5002, debug=True)
