#!/bin/bash

# ISS Explorer - Stop All Services

echo "🛑 Stopping ISS Explorer Services..."
echo "===================================="

# Kill processes on our ports
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    echo "  Stopping RAG API (Port 5001)..."
    lsof -ti:5001 | xargs kill -9 2>/dev/null
    echo "  ✅ RAG API stopped"
fi

if lsof -Pi :5002 -sTCP:LISTEN -t >/dev/null ; then
    echo "  Stopping SSE Server (Port 5002)..."
    lsof -ti:5002 | xargs kill -9 2>/dev/null
    echo "  ✅ SSE Server stopped"
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "  Stopping Frontend (Port 3000)..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    echo "  ✅ Frontend stopped"
fi

echo ""
echo "✅ All services stopped successfully!"
echo ""
