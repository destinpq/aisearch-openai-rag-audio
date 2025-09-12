#!/bin/bash

# Verify frontend configuration for production
echo "🔍 Verifying Frontend Production Configuration"
echo "=============================================="

# Check if .env file has correct API URL
if grep -q "VITE_API_URL=https://converse-api.destinpq.com" /home/azureuser/aisearch-openai-rag-audio/app/frontend/.env; then
    echo "✅ Frontend .env configured for production API"
else
    echo "❌ Frontend .env not configured correctly"
fi

# Check if frontend was built recently
if [ -f "/home/azureuser/aisearch-openai-rag-audio/app/backend/static/index.html" ]; then
    BUILD_TIME=$(stat -c %Y /home/azureuser/aisearch-openai-rag-audio/app/backend/static/index.html)
    CURRENT_TIME=$(date +%s)
    TIME_DIFF=$((CURRENT_TIME - BUILD_TIME))

    if [ $TIME_DIFF -lt 300 ]; then  # Less than 5 minutes ago
        echo "✅ Frontend built recently with production config"
    else
        echo "⚠️  Frontend build might be outdated"
    fi
else
    echo "❌ Frontend not built"
fi

echo ""
echo "🌐 Expected behavior:"
echo "   - Frontend: converse.destinpq.com"
echo "   - Backend API calls: converse-api.destinpq.com"
echo "   - No more localhost:8000 requests!"
