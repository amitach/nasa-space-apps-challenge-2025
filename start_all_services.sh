#!/bin/bash

# ISS Explorer - Start All Services
# This script starts the RAG API, SSE Server, and Frontend

echo "🚀 Starting ISS Explorer Services..."
echo "===================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+."
    exit 1
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Kill existing processes on our ports
echo -e "${YELLOW}Checking for existing processes...${NC}"
if check_port 5001; then
    echo "  Stopping process on port 5001..."
    lsof -ti:5001 | xargs kill -9 2>/dev/null
fi
if check_port 5002; then
    echo "  Stopping process on port 5002..."
    lsof -ti:5002 | xargs kill -9 2>/dev/null
fi
if check_port 3000; then
    echo "  Stopping process on port 3000..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null
fi

sleep 2

# Start RAG API
echo -e "\n${BLUE}1. Starting RAG API (Port 5001)...${NC}"
python main.py > logs/rag_api.log 2>&1 &
RAG_PID=$!
echo "  ✅ RAG API started (PID: $RAG_PID)"

# Wait for RAG API to be ready
echo "  ⏳ Waiting for RAG API to initialize..."
for i in {1..30}; do
    if curl -s http://localhost:5001/health > /dev/null 2>&1; then
        echo "  ✅ RAG API is ready!"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo "  ❌ RAG API failed to start. Check logs/rag_api.log"
        exit 1
    fi
done

# Start SSE Server
echo -e "\n${BLUE}2. Starting SSE Server (Port 5002)...${NC}"
python src/api/sse_server.py > logs/sse_server.log 2>&1 &
SSE_PID=$!
echo "  ✅ SSE Server started (PID: $SSE_PID)"

# Wait for SSE Server to be ready
echo "  ⏳ Waiting for SSE Server to initialize..."
for i in {1..15}; do
    if curl -s http://localhost:5002/health > /dev/null 2>&1; then
        echo "  ✅ SSE Server is ready!"
        break
    fi
    sleep 1
    if [ $i -eq 15 ]; then
        echo "  ❌ SSE Server failed to start. Check logs/sse_server.log"
        exit 1
    fi
done

# Start Frontend
echo -e "\n${BLUE}3. Starting Frontend (Port 3000)...${NC}"
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "  ✅ Frontend started (PID: $FRONTEND_PID)"

# Wait for Frontend to be ready
echo "  ⏳ Waiting for Frontend to initialize..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "  ✅ Frontend is ready!"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo "  ⚠️  Frontend may still be starting. Check logs/frontend.log"
    fi
done

# Summary
echo -e "\n${GREEN}===================================="
echo "✅ All Services Started Successfully!"
echo "====================================${NC}"
echo ""
echo "📍 Services:"
echo "  • RAG API:      http://localhost:5001"
echo "  • SSE Server:   http://localhost:5002"
echo "  • Frontend:     http://localhost:3000"
echo ""
echo "📊 Process IDs:"
echo "  • RAG API:      $RAG_PID"
echo "  • SSE Server:   $SSE_PID"
echo "  • Frontend:     $FRONTEND_PID"
echo ""
echo "📝 Logs:"
echo "  • RAG API:      logs/rag_api.log"
echo "  • SSE Server:   logs/sse_server.log"
echo "  • Frontend:     logs/frontend.log"
echo ""
echo "🛑 To stop all services:"
echo "  ./stop_all_services.sh"
echo ""
echo "🌐 Open your browser to: http://localhost:3000"
echo ""
