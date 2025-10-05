# 🚀 ISS Explorer with Tavus Integration - Complete Guide

## 📋 Overview

This guide shows you how to set up the complete ISS Explorer application with Tavus video chat, RAG-based image search, and real-time SSE updates.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                   │
│  ┌──────────────────┐           ┌────────────────────────┐  │
│  │  Tavus Video     │           │   Image Slideshow      │  │
│  │  Chat Component  │           │   (Real-time Updates)  │  │
│  └──────────────────┘           └────────────────────────┘  │
│           │                                  │               │
│           │                                  │               │
└───────────┼──────────────────────────────────┼───────────────┘
            │                                  │
            │ Tool Calls                       │ SSE Connection
            ▼                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    SSE Server (Port 5002)                    │
│  • Handles Tavus tool calls                                  │
│  • Manages SSE connections                                   │
│  • Sends real-time image updates                             │
└─────────────────────────────────────────────────────────────┘
            │
            │ Search Requests
            ▼
┌─────────────────────────────────────────────────────────────┐
│                  RAG API (Port 5001)                         │
│  • FAISS vector search                                       │
│  • Sentence transformers                                     │
│  • 40 curated ISS images                                     │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Setup Instructions

### Step 1: Backend Setup

#### 1.1 Install Python Dependencies

```bash
cd /Users/amit/github/nasa-space-apps-challenge-2025
pip install -r requirements.txt
```

#### 1.2 Start the RAG API (Port 5001)

```bash
python main.py
```

Verify it's running:
```bash
curl http://localhost:5001/health
```

Expected output:
```json
{
  "status": "healthy",
  "index_ready": true,
  "total_images": 40,
  "categories": ["Cupola Images", "NBL Training Images"]
}
```

#### 1.3 Start the SSE Server (Port 5002)

Open a new terminal:
```bash
python src/api/sse_server.py
```

Verify it's running:
```bash
curl http://localhost:5002/health
```

### Step 2: Frontend Setup

#### 2.1 Install Node Dependencies

```bash
cd frontend
npm install
```

#### 2.2 Configure Environment Variables

Create `.env.local` file:
```bash
cp env.example .env.local
```

Edit `.env.local` and add your Tavus credentials:
```env
NEXT_PUBLIC_TAVUS_API_KEY=your_tavus_api_key_here
NEXT_PUBLIC_TAVUS_PERSONA_ID=your_persona_id_here
NEXT_PUBLIC_TAVUS_REPLICA_ID=your_replica_id_here
NEXT_PUBLIC_SSE_URL=http://localhost:5002
NEXT_PUBLIC_RAG_API_URL=http://localhost:5001
```

#### 2.3 Start the Frontend

```bash
npm run dev
```

The app will be available at: http://localhost:3000

## 🎯 How It Works

### 1. **User Opens App**
- Frontend establishes SSE connection to backend
- Connection ID is generated and stored
- Status indicator shows "Connected"

### 2. **User Starts Conversation**
- Click "Start Conversation" button
- Tavus conversation is created with tools defined
- Daily.co video call is initialized
- AI guide greets the user

### 3. **User Asks for Images**
User says: *"Show me the Cupola"*

**Flow:**
```
User → Tavus AI → Tool Call → SSE Server → RAG API
                                    ↓
Frontend ← SSE Event ← SSE Server ← Search Results
```

**What happens:**
1. Tavus AI detects the request needs images
2. Tavus calls `fetch_relevant_image` tool with query: "Cupola"
3. Tool call is sent to SSE server
4. SSE server calls RAG API to search for images
5. RAG API returns relevant images
6. SSE server sends images via SSE to frontend
7. Frontend updates slideshow automatically
8. Tavus AI responds: "Here's what the Cupola looks like..."

### 4. **Images Display**
- Images appear in the slideshow panel
- Auto-advance every 5 seconds
- Shows image metadata (NASA ID, description, keywords)
- Similarity score displayed

## 🔨 Tavus Tool Configuration

### Tool Definition

The `fetch_relevant_image` tool is defined in `frontend/lib/tavus.ts`:

```typescript
{
  type: 'function',
  function: {
    name: 'fetch_relevant_image',
    description: 'Fetches relevant ISS images based on a search query. Use this when the user asks about specific parts of the ISS, astronauts, space activities, or wants to see images.',
    parameters: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Natural language search query for ISS images'
        },
        top_k: {
          type: 'number',
          description: 'Number of images to return (1-10)',
          default: 5
        }
      },
      required: ['query']
    }
  }
}
```

### Tool Call Handling

When Tavus makes a tool call:

1. **Frontend receives tool call** via Daily.co app-message event
2. **Frontend calls SSE server** at `/api/tavus-tool-call`
3. **SSE server searches images** via RAG API
4. **SSE server sends results** via SSE to frontend
5. **Frontend submits result** back to Tavus
6. **Tavus continues conversation** with context

## 📝 Example Queries

Try these queries with your AI guide:

- "Show me the Cupola"
- "What does the ISS look like from space?"
- "Show me astronauts doing EVA training"
- "I want to see the space station modules"
- "Show me aurora from space"
- "What do astronauts see from the Cupola?"

## 🔍 API Endpoints

### RAG API (Port 5001)

- `GET /health` - Health check
- `POST /search` - Search for images
- `GET /images/{nasa_id}` - Get specific image
- `GET /categories` - Get image categories
- `GET /stats` - Get statistics

### SSE Server (Port 5002)

- `GET /sse/connect?connection_id={id}` - Establish SSE connection
- `POST /api/search-images` - Search and send via SSE
- `POST /api/tavus-tool-call` - Handle Tavus tool calls
- `GET /health` - Health check

## 🎨 Frontend Components

### Key Files

- `app/page.tsx` - Main application page
- `lib/tavus.ts` - Tavus client and tool handling
- `hooks/useSSE.ts` - SSE connection hook
- `env.example` - Environment variables template

### State Management

- **SSE Connection**: Managed by `useSSE` hook
- **Tavus Client**: Initialized when SSE connects
- **Images**: Updated via SSE events
- **Video Call**: Managed by Daily.co iframe

## 🚀 Deployment

### Backend Deployment

```bash
# Use gunicorn for production
gunicorn -w 4 -b 0.0.0.0:5001 main:app
gunicorn -w 4 -b 0.0.0.0:5002 src.api.sse_server:app
```

### Frontend Deployment

```bash
cd frontend
npm run build
npm start
```

Or deploy to Vercel:
```bash
vercel deploy
```

## 🐛 Troubleshooting

### Issue: SSE not connecting

**Solution:**
- Check if SSE server is running on port 5002
- Check browser console for CORS errors
- Verify `NEXT_PUBLIC_SSE_URL` in `.env.local`

### Issue: Images not appearing

**Solution:**
- Check if RAG API is running on port 5001
- Verify SSE connection is established
- Check browser console for errors
- Test RAG API directly: `curl -X POST http://localhost:5001/search -H "Content-Type: application/json" -d '{"query": "cupola", "top_k": 5}'`

### Issue: Tavus tool calls not working

**Solution:**
- Verify Tavus API key and replica ID
- Check that tools are properly defined in conversation creation
- Check SSE server logs for tool call events
- Ensure `connection_id` is passed to Tavus client

### Issue: Video not loading

**Solution:**
- Check Daily.co script is loaded
- Verify Tavus conversation was created successfully
- Check browser console for Daily.co errors
- Ensure HTTPS is used in production

## 📚 Additional Resources

- [Tavus API Documentation](https://docs.tavus.io)
- [Daily.co Documentation](https://docs.daily.co)
- [Server-Sent Events (SSE) Guide](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [FAISS Documentation](https://faiss.ai)

## 🎉 Success Checklist

- [ ] RAG API running on port 5001
- [ ] SSE server running on port 5002
- [ ] Frontend running on port 3000
- [ ] SSE connection established (green indicator)
- [ ] Tavus API key configured
- [ ] Video call starts successfully
- [ ] Tool calls trigger image searches
- [ ] Images display in slideshow
- [ ] Images update in real-time

## 🔐 Security Notes

- Never commit `.env.local` file
- Keep Tavus API keys secure
- Use HTTPS in production
- Implement rate limiting for API endpoints
- Validate all user inputs
- Sanitize tool call parameters

---

**Built for NASA Space Apps Challenge 2025 - ISS 25th Anniversary** 🚀
