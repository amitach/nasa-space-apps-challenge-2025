# 🚀 ISS Explorer - Complete System with Tavus Integration

## 🎯 What This Is

A complete AI-powered ISS (International Space Station) exploration app with:
- **🎥 Tavus Video Chat**: Talk to an AI guide about the ISS
- **🖼️ RAG Image Search**: AI searches 40+ curated NASA images
- **⚡ Real-time Updates**: Images appear automatically via Server-Sent Events (SSE)
- **🤖 Tool Calling**: AI guide can fetch and display images contextually

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Frontend (Next.js + TypeScript)                 │
│  ┌──────────────────┐         ┌──────────────────────────┐  │
│  │ Tavus Video Chat │◄────────┤  Image Slideshow         │  │
│  │ (Daily.co)       │         │  (Auto-updating via SSE) │  │
│  └────────┬─────────┘         └──────────▲───────────────┘  │
│           │                               │                  │
└───────────┼───────────────────────────────┼──────────────────┘
            │ Tool Calls                    │ SSE Events
            ▼                               │
┌─────────────────────────────────────────────────────────────┐
│          SSE Server (Flask + CORS) - Port 5002              │
│  • Handles Tavus tool calls                                  │
│  • Manages SSE connections                                   │
│  • Sends real-time image updates                             │
└────────────────────┬────────────────────────────────────────┘
                     │ Search Requests
                     ▼
┌─────────────────────────────────────────────────────────────┐
│       RAG API (Flask + FAISS + Transformers) - Port 5001    │
│  • Vector search with FAISS                                  │
│  • Sentence transformers (all-MiniLM-L6-v2)                  │
│  • 40 curated ISS images from NASA                           │
└─────────────────────────────────────────────────────────────┘
```

## 📦 What's Included

### Backend Services

1. **RAG API** (`main.py`, `src/api/app.py`, `src/search/engine.py`)
   - FAISS vector search
   - Sentence transformers for semantic search
   - 40 curated ISS images with metadata
   - REST API endpoints

2. **SSE Server** (`src/api/sse_server.py`)
   - Server-Sent Events for real-time updates
   - Tavus tool call handling
   - Connection management
   - CORS enabled for frontend

### Frontend Application

1. **Next.js App** (`frontend/`)
   - TypeScript + Tailwind CSS
   - Tavus video chat integration
   - Real-time image slideshow
   - SSE client hook

2. **Key Components**
   - `app/page.tsx` - Main application page
   - `lib/tavus.ts` - Tavus client and tool handling
   - `hooks/useSSE.ts` - SSE connection management

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn
- Tavus API key ([Get one here](https://tavus.io))

### Option 1: Automated Start (Recommended)

```bash
# Make scripts executable (first time only)
chmod +x start_all_services.sh stop_all_services.sh

# Start all services
./start_all_services.sh

# When done, stop all services
./stop_all_services.sh
```

### Option 2: Manual Start

#### Terminal 1: RAG API
```bash
pip install -r requirements.txt
python main.py
# Runs on http://localhost:5001
```

#### Terminal 2: SSE Server
```bash
python src/api/sse_server.py
# Runs on http://localhost:5002
```

#### Terminal 3: Frontend
```bash
cd frontend
npm install
cp env.example .env.local
# Edit .env.local with your Tavus credentials
npm run dev
# Runs on http://localhost:3000
```

## ⚙️ Configuration

### Backend Configuration

Edit `config.py`:
```python
API_PORT = 5001  # RAG API port
DATA_FILE = 'src/data/iss_images_organized.json'
MODEL_NAME = 'all-MiniLM-L6-v2'
```

### Frontend Configuration

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_TAVUS_API_KEY=your_tavus_api_key_here
NEXT_PUBLIC_TAVUS_PERSONA_ID=your_persona_id_here
NEXT_PUBLIC_TAVUS_REPLICA_ID=your_replica_id_here
NEXT_PUBLIC_SSE_URL=http://localhost:5002
NEXT_PUBLIC_RAG_API_URL=http://localhost:5001
```

## 🎮 How to Use

### 1. Open the App
Navigate to http://localhost:3000

### 2. Start Conversation
Click "Start Conversation" button

### 3. Talk to Your AI Guide
Try these example queries:
- "Show me the Cupola"
- "What does the ISS look like?"
- "Show me astronauts doing EVA training"
- "I want to see the space station modules"
- "Show me aurora from space"

### 4. Watch Images Appear
- Images automatically appear in the slideshow
- Auto-advance every 5 seconds
- Manual navigation with arrow buttons
- View image metadata and descriptions

## 🔧 Tavus Tool Configuration

### Tool Definition

The AI guide has access to the `fetch_relevant_image` tool:

```typescript
{
  name: 'fetch_relevant_image',
  description: 'Fetches relevant ISS images based on a search query',
  parameters: {
    query: 'Natural language search query',
    top_k: 'Number of images to return (1-10)'
  }
}
```

### Tool Call Flow

```
1. User: "Show me the Cupola"
2. Tavus AI: Recognizes need for images
3. Tavus AI: Calls fetch_relevant_image("Cupola windows Earth view")
4. Frontend: Receives tool call
5. Frontend: Sends to SSE server
6. SSE Server: Calls RAG API
7. RAG API: Searches with FAISS
8. RAG API: Returns 5 relevant images
9. SSE Server: Sends images via SSE
10. Frontend: Updates slideshow
11. Tavus AI: "Here's what the Cupola looks like..."
```

## 📊 API Endpoints

### RAG API (Port 5001)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/search` | POST | Search images |
| `/images/{id}` | GET | Get specific image |
| `/categories` | GET | Get categories |
| `/stats` | GET | Get statistics |

### SSE Server (Port 5002)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sse/connect` | GET | Establish SSE connection |
| `/api/search-images` | POST | Search and send via SSE |
| `/api/tavus-tool-call` | POST | Handle Tavus tool calls |
| `/health` | GET | Health check |

## 🧪 Testing

### Test RAG API
```bash
curl -X POST http://localhost:5001/search \
  -H "Content-Type: application/json" \
  -d '{"query": "cupola", "top_k": 5}'
```

### Test SSE Server
```bash
curl http://localhost:5002/health
```

### Test Frontend
Open http://localhost:3000 in your browser

## 📁 Project Structure

```
nasa-space-apps-challenge-2025/
├── main.py                          # RAG API entry point
├── config.py                        # Configuration
├── requirements.txt                 # Python dependencies
├── start_all_services.sh           # Start all services
├── stop_all_services.sh            # Stop all services
│
├── src/
│   ├── api/
│   │   ├── app.py                  # Main RAG API
│   │   └── sse_server.py           # SSE server
│   ├── search/
│   │   └── engine.py               # FAISS search engine
│   └── data/
│       └── iss_images_organized.json
│
├── frontend/
│   ├── app/
│   │   └── page.tsx                # Main page
│   ├── lib/
│   │   └── tavus.ts                # Tavus client
│   ├── hooks/
│   │   └── useSSE.ts               # SSE hook
│   └── env.example                 # Environment template
│
└── logs/                            # Service logs
```

## 🐛 Troubleshooting

### Issue: "SSE not connecting"
**Solution:**
```bash
# Check if SSE server is running
curl http://localhost:5002/health

# Check logs
tail -f logs/sse_server.log
```

### Issue: "Images not appearing"
**Solution:**
```bash
# Test RAG API
curl -X POST http://localhost:5001/search \
  -H "Content-Type: application/json" \
  -d '{"query": "cupola", "top_k": 5}'

# Check logs
tail -f logs/rag_api.log
```

### Issue: "Tavus tool calls not working"
**Solution:**
1. Verify Tavus API key in `.env.local`
2. Check browser console for errors
3. Verify SSE connection is established
4. Check `logs/sse_server.log` for tool call events

### Issue: "Port already in use"
**Solution:**
```bash
# Stop all services
./stop_all_services.sh

# Or manually kill processes
lsof -ti:5001 | xargs kill -9
lsof -ti:5002 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

## 📚 Documentation

- [Tavus Integration Guide](TAVUS_INTEGRATION_GUIDE.md)
- [API Documentation](README_API.md)
- [Structure Summary](STRUCTURE_SUMMARY.md)

## 🔐 Security Notes

- Never commit `.env.local` file
- Keep Tavus API keys secure
- Use HTTPS in production
- Implement rate limiting
- Validate all inputs
- Sanitize tool call parameters

## 🚀 Deployment

### Backend (Heroku/Railway/Fly.io)
```bash
# Use gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 main:app
gunicorn -w 4 -b 0.0.0.0:5002 src.api.sse_server:app
```

### Frontend (Vercel/Netlify)
```bash
cd frontend
npm run build
# Deploy to Vercel
vercel deploy
```

## 🎉 Success Checklist

- [ ] All Python dependencies installed
- [ ] All Node dependencies installed
- [ ] Tavus API key configured
- [ ] RAG API running on port 5001
- [ ] SSE server running on port 5002
- [ ] Frontend running on port 3000
- [ ] SSE connection established (green indicator)
- [ ] Video call starts successfully
- [ ] Tool calls trigger image searches
- [ ] Images display in slideshow
- [ ] Images update in real-time

## 🤝 Contributing

This project was built for the NASA Space Apps Challenge 2025 - ISS 25th Anniversary Apps.

## 📄 License

Built for NASA Space Apps Challenge 2025

---

**🚀 Ready to explore the ISS! Open http://localhost:3000 and start your journey!**
