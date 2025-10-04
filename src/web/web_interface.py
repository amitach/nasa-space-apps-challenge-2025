from flask import Flask, send_from_directory, render_template_string
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main search interface"""
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    print("🌐 Starting ISS Search Web Interface...")
    print("📱 Open your browser and go to: http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)
