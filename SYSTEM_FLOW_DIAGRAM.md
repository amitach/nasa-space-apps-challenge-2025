# 🚀 ISS Explorer - Complete System Flow

## 📋 System Overview
A real-time AI-powered video chat system that displays contextual ISS images based on conversation topics using Tavus AI, Daily.co, and NASA Image API.

---

## 🏗️ Architecture Components

### 1. **Frontend (Next.js)**
- **Port**: 3001
- **Location**: `frontend/`
- **Key Files**:
  - `app/page.tsx` - Main UI component
  - `lib/tavus-corrected.ts` - Tavus API client
  - `hooks/useSSE.ts` - Server-Sent Events hook

### 2. **RAG API (Flask)**
- **Port**: 5001
- **Location**: `src/api/app.py`
- **Purpose**: Vector search for ISS images using FAISS + SentenceTransformer

### 3. **SSE Server (Flask)**
- **Port**: 5002
- **Location**: `src/api/sse_server.py`
- **Purpose**: Real-time communication and Tavus webhook handling

### 4. **Search Engine**
- **Location**: `src/search/engine.py`
- **Purpose**: FAISS vector search with 40 curated ISS images

---

## 🔄 Complete Data Flow

### **Phase 1: System Initialization**

```
1. User opens browser → http://localhost:3001
2. Frontend loads → Initializes Tavus client
3. SSE connection established → http://localhost:5002/events
4. RAG API starts → Loads 40 ISS images + FAISS index
5. SSE Server starts → Ready for webhooks
```

### **Phase 2: Conversation Start**

```
User clicks "Start Conversation"
    ↓
Frontend calls Tavus API:
    - POST https://tavusapi.com/v2/conversations
    - Body: {persona_id, replica_id, callback_url}
    ↓
Tavus creates conversation → Returns conversation_url
    ↓
Frontend initializes Daily.co iframe:
    - Joins Daily.co room using conversation_url
    - Sets up custom tray button
    ↓
Frontend calls configureTools():
    - POST https://tavusapi.com/v2/conversations/{id}/tools
    - Body: {tools: [fetch_relevant_image]}
    ↓
Conversation ready → tavusConnected = true
```

### **Phase 3: User Interaction & Tool Calls**

```
User asks: "Show me the Cupola module"
    ↓
Tavus AI processes request → Decides to use fetch_relevant_image tool
    ↓
Tavus calls webhook:
    - POST http://localhost:5002/api/tavus-webhook
    - Body: {type: "tool_call", tool_call: {name: "fetch_relevant_image", parameters: {query: "Cupola module"}}}
    ↓
SSE Server processes webhook:
    - Validates tool call
    - Calls search_engine.search("Cupola module", 5)
    - FAISS returns top 5 similar images
    ↓
SSE Server sends images via SSE:
    - Event: "images"
    - Data: {images: [...], query: "Cupola module", total: 5}
    ↓
Frontend receives SSE event:
    - Checks if tavusConnected = true
    - Updates currentImages state
    - Displays images in slideshow
```

### **Phase 4: Real-time Image Display**

```
Images displayed in frontend:
    - Current image with navigation arrows
    - Image description and keywords
    - Similarity score
    - Auto-advance every 5 seconds
    ↓
User can:
    - Navigate images manually
    - Ask for different topics
    - End conversation
```

### **Phase 5: Conversation End**

```
User clicks "End Conversation"
    ↓
Frontend calls:
    - dailyCallFrame.destroy()
    - tavusClient.endConversation(conversation_id)
    ↓
State cleanup:
    - tavusConnected = false
    - currentImages = []
    - currentImageIndex = 0
    ↓
Images cleared from display
```

---

## 🔧 Key Technical Details

### **SSE Event Types**
```javascript
// Connection established
event: connected
data: {connection_id, status: "connected"}

// Images received
event: images  
data: {images: [...], query: "...", total: 5}

// Test events
event: test
data: {message: "Test message"}
```

### **Tavus Tool Definition**
```javascript
{
  type: 'function',
  function: {
    name: 'fetch_relevant_image',
    description: 'Fetches relevant ISS images based on search query',
    parameters: {
      type: 'object',
      properties: {
        query: {type: 'string', description: 'Search query'},
        top_k: {type: 'number', description: 'Number of images (default: 5)'}
      },
      required: ['query']
    }
  }
}
```

### **Image Data Structure**
```javascript
{
  nasa_id: "iss043e122274",
  description: "ISS043E122274 (04/17/2015) --- ESA astronaut...",
  image_url: "https://images-assets.nasa.gov/image/iss043e122274/iss043e122274~orig.jpg",
  similarity_score: 0.85,
  keywords: ["iss", "canadarm", "experiment"],
  category: "Cupola Images"
}
```

---

## 🚦 Status Indicators

### **Frontend Status**
- **SSE**: Connected/Disconnected (green/red)
- **Tavus**: Connected/Disconnected (green/gray)  
- **Images**: Count of current images (blue/gray)

### **Backend Health**
- **RAG API**: `/health` → `{status: "healthy", total_images: 40}`
- **SSE Server**: `/api/health` → `{status: "healthy", connected_clients: 5}`

---

## 🔍 Debugging Points

### **Common Issues**
1. **SSE Disconnected**: Check if SSE server is running on port 5002
2. **No Tool Calls**: Verify Tavus webhook URL and tool configuration
3. **Images Not Showing**: Check if tavusConnected = true
4. **API Errors**: Check RAG API health endpoint

### **Log Locations**
- **Frontend**: Browser console (F12)
- **RAG API**: Terminal running `python main.py`
- **SSE Server**: Terminal running `python src/api/sse_server.py`
- **Frontend**: Terminal running `npm run dev`

---

## 🎯 Success Criteria

✅ **System Working When**:
1. All 3 services running (RAG API, SSE Server, Frontend)
2. SSE shows "Connected" status
3. Can start Tavus conversation
4. Tavus shows "Connected" status  
5. Asking for images triggers tool calls
6. Images appear in real-time
7. Images clear when conversation ends

---

## 🚀 Quick Start Commands

```bash
# Start all services
./start_all_services.sh

# Stop all services  
./stop_all_services.sh

# Manual start
python main.py &                    # RAG API (port 5001)
python src/api/sse_server.py &      # SSE Server (port 5002)
cd frontend && npm run dev &        # Frontend (port 3001)
```

---

## 📊 Data Sources

- **40 Curated ISS Images**: `src/data/iss_images_organized.json`
  - 30 Cupola module images
  - 10 NBL training images
- **Vector Search**: FAISS index with SentenceTransformer embeddings
- **Real-time Updates**: Server-Sent Events (SSE)
- **AI Integration**: Tavus API with tool calling
