# 🔍 Enhanced Logging for Tavus Tool Call Tracking

## 📋 Overview
We've added comprehensive logging to track the complete flow when a user asks about ISS topics and Tavus decides to use the `fetch_relevant_image` tool.

---

## 🎯 What We Track

### **Step 1: User Question → Tavus Processing**
When a user asks a question in the Tavus conversation, we can now see:

```
🔔 TAVUS WEBHOOK RECEIVED - USER QUESTION PROCESSING
================================================================================
📨 Webhook payload: {
  "type": "tool_call",
  "tool_call": {
    "name": "fetch_relevant_image",
    "parameters": {
      "query": "International Space Station Cupola module",
      "top_k": 3
    }
  }
}
================================================================================
```

### **Step 2: Tavus Decision to Use Tool**
```
✅ TAVUS DECIDED TO USE TOOL - Processing tool_call from webhook
🔧 Tool name: fetch_relevant_image
🔧 Tool parameters: {"query": "International Space Station Cupola module", "top_k": 3}
```

### **Step 3: Image Search Execution**
```
================================================================================
🔍 EXECUTING IMAGE SEARCH
================================================================================
📝 User query: 'International Space Station Cupola module'
📊 Requested images: 3
================================================================================
🚀 Starting vector search for: 'International Space Station Cupola module'
📸 Search completed - Found 3 images
   1. iss043e122274 - Score: 0.852
   2. iss043e122275 - Score: 0.798
   3. iss043e122276 - Score: 0.745
```

### **Step 4: SSE Event Sending**
```
================================================================================
📡 SENDING IMAGES TO FRONTEND VIA SSE
================================================================================
✅ Successfully sent 3 images to frontend
================================================================================
```

### **Step 5: Frontend Reception**
```
================================================================================
📸 FRONTEND RECEIVED IMAGES VIA SSE
================================================================================
🔍 Query: "International Space Station Cupola module"
📊 Total images: 3
📡 Source: tavus_webhook
🕐 Timestamp: 10:25:30 PM
📋 Images received:
   1. iss043e122274 - Score: 0.852 - ISS043E122274 (04/17/2015) --- ESA astronaut...
   2. iss043e122275 - Score: 0.798 - ISS043E122275 (04/17/2015) --- ESA astronaut...
   3. iss043e122276 - Score: 0.745 - ISS043E122276 (04/17/2015) --- ESA astronaut...
================================================================================
```

### **Step 6: Frontend Processing**
```
================================================================================
🎯 FRONTEND PROCESSING IMAGES FOR DISPLAY
================================================================================
✅ Tavus connected: true
📸 Images received: 3
🔍 Query: "International Space Station Cupola module"
🖼️ Setting images for display...
✅ Successfully updated UI with 3 images
================================================================================
```

---

## 🧪 Testing the Logging

### **Test 1: Tavus Webhook Simulation**
Click the **"Test Tavus Webhook"** button in the frontend to simulate a real Tavus tool call.

### **Test 2: Manual Webhook Test**
```bash
curl -X POST http://localhost:5002/api/tavus-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "type": "tool_call",
    "tool_call": {
      "name": "fetch_relevant_image",
      "parameters": {
        "query": "International Space Station Cupola module",
        "top_k": 3
      }
    }
  }'
```

### **Test 3: Real Tavus Conversation**
1. Start a conversation with Tavus
2. Ask: "Show me images of the Cupola module"
3. Watch the logs in the SSE server terminal

---

## 📊 Log Locations

### **SSE Server Logs** (Terminal running `python src/api/sse_server.py`)
- Webhook reception
- Tool call processing
- Image search execution
- SSE event sending

### **Frontend Logs** (Browser Console - F12)
- SSE connection status
- Image reception
- Frontend processing
- UI updates

### **RAG API Logs** (Terminal running `python main.py`)
- Search engine initialization
- Vector search execution

---

## 🔍 Debugging with Logs

### **If No Tool Calls Are Received:**
1. Check if Tavus webhook URL is correct: `http://localhost:5002/api/tavus-webhook`
2. Verify tools are configured: Look for `configureTools` success message
3. Check Tavus conversation status

### **If Images Don't Appear:**
1. Check frontend logs for "FRONTEND PROCESSING IMAGES"
2. Verify `tavusConnected` is `true`
3. Check SSE connection status

### **If Search Fails:**
1. Check RAG API health: `curl http://localhost:5001/health`
2. Verify search engine is initialized
3. Check image data is loaded

---

## 🎯 Success Indicators

✅ **Complete Flow Working When You See:**
1. `🔔 TAVUS WEBHOOK RECEIVED` in SSE server logs
2. `✅ TAVUS DECIDED TO USE TOOL` in SSE server logs
3. `🔍 EXECUTING IMAGE SEARCH` in SSE server logs
4. `📸 FRONTEND RECEIVED IMAGES VIA SSE` in browser console
5. `🎯 FRONTEND PROCESSING IMAGES FOR DISPLAY` in browser console
6. Images appear in the UI

---

## 🚀 Quick Test Commands

```bash
# Test webhook directly
curl -X POST http://localhost:5002/api/tavus-webhook \
  -H "Content-Type: application/json" \
  -d '{"type": "tool_call", "tool_call": {"name": "fetch_relevant_image", "parameters": {"query": "Cupola module", "top_k": 5}}}'

# Test SSE connection
curl -X POST http://localhost:5002/api/test-sse \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message"}'

# Check system health
curl http://localhost:5001/health | jq .
curl http://localhost:5002/api/health | jq .
```

Now you can easily track the complete flow from user question to image display! 🎉
