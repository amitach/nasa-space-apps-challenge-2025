#!/bin/bash

# ISS Explorer - Restore Local URLs
# This script restores the original localhost URLs from backup files

echo "🔄 Restoring original localhost URLs..."
echo "===================================="

# Restore .env.local
if [ -f ".env.local.backup" ]; then
    cp .env.local.backup .env.local
    echo "  ✅ Restored .env.local from backup"
else
    echo "  ⚠️  No .env.local.backup found"
fi

# Restore frontend/app/page.tsx
if [ -f "frontend/app/page.tsx.backup" ]; then
    cp frontend/app/page.tsx.backup frontend/app/page.tsx
    echo "  ✅ Restored frontend/app/page.tsx from backup"
else
    echo "  ⚠️  No frontend/app/page.tsx.backup found"
fi

echo ""
echo "✅ Restore complete!"
echo ""
echo "📝 Original localhost URLs have been restored:"
echo "  • RAG API:      http://localhost:5001"
echo "  • SSE Server:   http://localhost:5002"
echo "  • Frontend:     http://localhost:3000"
echo ""