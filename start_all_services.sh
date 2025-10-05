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

# Check if ngrok is available
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not found. Please install ngrok."
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

# Start ngrok tunnels
echo -e "\n${BLUE}3. Starting ngrok tunnels...${NC}"
ngrok http 5001 > logs/ngrok_5001.log 2>&1 &
NGROK_5001_PID=$!
ngrok http 5002 > logs/ngrok_5002.log 2>&1 &
NGROK_5002_PID=$!
echo "  ✅ ngrok tunnels started (PIDs: $NGROK_5001_PID, $NGROK_5002_PID)"
sleep 5 # Wait for ngrok to start and tunnels to be established

# Get ngrok URLs (need to check which tunnel points to which port)
echo "  ⏳ Fetching ngrok URLs..."

# Check port 4040 tunnel
NGROK_4040_TARGET=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].config.addr')
NGROK_4040_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')

# Check port 4041 tunnel
NGROK_4041_TARGET=$(curl -s http://localhost:4041/api/tunnels | jq -r '.tunnels[0].config.addr')
NGROK_4041_URL=$(curl -s http://localhost:4041/api/tunnels | jq -r '.tunnels[0].public_url')

# Map URLs to correct services based on target ports
if [[ "$NGROK_4040_TARGET" == "http://localhost:5001" ]]; then
    NGROK_API_URL_5001="$NGROK_4040_URL"
else
    NGROK_API_URL_5001="$NGROK_4041_URL"
fi

if [[ "$NGROK_4040_TARGET" == "http://localhost:5002" ]]; then
    NGROK_API_URL_5002="$NGROK_4040_URL"
else
    NGROK_API_URL_5002="$NGROK_4041_URL"
fi

if [ -z "$NGROK_API_URL_5001" ] || [ -z "$NGROK_API_URL_5002" ]; then
    echo "  ❌ Failed to get ngrok URLs. Please check logs/ngrok_5001.log and logs/ngrok_5002.log"
    exit 1
fi

echo "  ✅ ngrok URLs fetched successfully!"

# Update configuration files with ngrok URLs
echo "  🔄 Updating configuration files with ngrok URLs..."

# Update frontend/.env.local (this is where Next.js looks for env vars)
if [ -f "frontend/.env.local" ]; then
    # Backup original file
    cp frontend/.env.local frontend/.env.local.backup
    
    # Update the URLs - SSE must use localhost (ngrok blocks EventSource)
    sed -i '' "s|NEXT_PUBLIC_SSE_URL=.*|NEXT_PUBLIC_SSE_URL=http://localhost:5002/events|g" frontend/.env.local
    sed -i '' "s|NEXT_PUBLIC_RAG_API_URL=.*|NEXT_PUBLIC_RAG_API_URL=http://localhost:5001|g" frontend/.env.local
    sed -i '' "s|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=http://localhost:5002|g" frontend/.env.local
    sed -i '' "s|NEXT_PUBLIC_TAVUS_CALLBACK_URL=.*|NEXT_PUBLIC_TAVUS_CALLBACK_URL=$NGROK_API_URL_5002/api/tavus-webhook|g" frontend/.env.local
    sed -i '' "s|NEXT_PUBLIC_WEBHOOK_URL=.*|NEXT_PUBLIC_WEBHOOK_URL=$NGROK_API_URL_5002/api/tavus-webhook|g" frontend/.env.local
    
    echo "    ✅ Updated frontend/.env.local"
    echo "      • RAG API: http://localhost:5001"
    echo "      • SSE Server: http://localhost:5002/events (localhost - ngrok blocks SSE)"
    echo "      • Webhook URL: $NGROK_API_URL_5002/api/tavus-webhook (ngrok - for Tavus callbacks)"
else
    echo "    ⚠️  frontend/.env.local not found - creating it..."
    cat > frontend/.env.local << EOF
NEXT_PUBLIC_SSE_URL=$NGROK_API_URL_5002/events
NEXT_PUBLIC_RAG_API_URL=$NGROK_API_URL_5001
NEXT_PUBLIC_API_URL=$NGROK_API_URL_5002
NEXT_PUBLIC_TAVUS_API_KEY=eb513dc5bc324cba8fe2210653b512ce
NEXT_PUBLIC_TAVUS_REPLICA_ID=r92debe21318
NEXT_PUBLIC_TAVUS_PERSONA_ID=p8ea2e6b8a04
NEXT_PUBLIC_TAVUS_CALLBACK_URL=$NGROK_API_URL_5002/api/tavus-webhook
NEXT_PUBLIC_WEBHOOK_URL=$NGROK_API_URL_5002/api/tavus-webhook
EOF
    echo "    ✅ Created frontend/.env.local with ngrok URLs"
fi

# Also update project root .env.local for Python scripts
if [ -f ".env.local" ]; then
    cp .env.local .env.local.backup
    sed -i '' "s|NEXT_PUBLIC_SSE_URL=.*|NEXT_PUBLIC_SSE_URL=$NGROK_API_URL_5002/events|g" .env.local
    sed -i '' "s|NEXT_PUBLIC_RAG_API_URL=.*|NEXT_PUBLIC_RAG_API_URL=$NGROK_API_URL_5001|g" .env.local
    sed -i '' "s|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=$NGROK_API_URL_5002|g" .env.local
    sed -i '' "s|NEXT_PUBLIC_WEBHOOK_URL=.*|NEXT_PUBLIC_WEBHOOK_URL=$NGROK_API_URL_5002/api/tavus-webhook|g" .env.local
    echo "    ✅ Updated project root .env.local for Python scripts"
else
    cat > .env.local << EOF
NEXT_PUBLIC_SSE_URL=$NGROK_API_URL_5002/events
NEXT_PUBLIC_RAG_API_URL=$NGROK_API_URL_5001
NEXT_PUBLIC_API_URL=$NGROK_API_URL_5002
NEXT_PUBLIC_TAVUS_API_KEY=eb513dc5bc324cba8fe2210653b512ce
NEXT_PUBLIC_TAVUS_REPLICA_ID=r92debe21318
NEXT_PUBLIC_TAVUS_PERSONA_ID=p8ea2e6b8a04
NEXT_PUBLIC_WEBHOOK_URL=$NGROK_API_URL_5002/api/tavus-webhook
EOF
    echo "    ✅ Created project root .env.local"
fi

# Start Frontend
echo -e "\n${BLUE}4. Starting Frontend (Port 3000)...${NC}"
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
echo -e "\n${GREEN}====================================\n"
echo "✅ All Services Started Successfully!"
echo -e "\n====================================${NC}"
echo ""
echo "📍 Services:"
echo "  • RAG API:      http://localhost:5001 -> $NGROK_API_URL_5001"
echo "  • SSE Server:   http://localhost:5002 -> $NGROK_API_URL_5002"
echo "  • Frontend:     http://localhost:3000"
echo ""
echo "🔄 Configuration Files Updated:"
echo "  • frontend/.env.local - Updated with ngrok URLs (Next.js uses this)"
echo "  • .env.local - Updated for Python scripts"
echo "  • Webhook URL: $NGROK_API_URL_5002/api/tavus-webhook"
echo "  • Backup files created with .backup extension"
echo ""
echo "📊 Process IDs:"
echo "  • RAG API:      $RAG_PID"
echo "  • SSE Server:   $SSE_PID"
echo "  • Frontend:     $FRONTEND_PID"
echo "  • ngrok (5001): $NGROK_5001_PID"
echo "  • ngrok (5002): $NGROK_5002_PID"
echo ""
echo "📝 Logs:"
echo "  • RAG API:      logs/rag_api.log"
echo "  • SSE Server:   logs/sse_server.log"
echo "  • Frontend:     logs/frontend.log"
echo "  • ngrok (5001): logs/ngrok_5001.log"
echo "  • ngrok (5002): logs/ngrok_5002.log"
echo ""
echo "🛑 To stop all services:"
echo "  ./stop_all_services.sh"
echo ""
echo "🌐 Open your browser to: http://localhost:3000"
echo ""
