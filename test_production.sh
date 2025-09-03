#!/bin/bash

# Test script for DestinPQ production deployment
echo "🧪 Testing DestinPQ Production Setup"
echo "===================================="

# Test backend health
echo "🔍 Testing backend connectivity..."
curl -s -o /dev/null -w "%{http_code}" https://converse-api.destinpq.com/ | grep -q "200" && echo "✅ Backend is responding" || echo "❌ Backend not responding"

# Test CORS headers
echo "🔒 Testing CORS configuration..."
curl -s -H "Origin: https://converse.destinpq.com" -H "Access-Control-Request-Method: POST" -X OPTIONS https://converse-api.destinpq.com/analyze | grep -q "Access-Control-Allow-Origin" && echo "✅ CORS configured correctly" || echo "❌ CORS not configured"

# Test login endpoint
echo "🔐 Testing authentication..."
LOGIN_RESPONSE=$(curl -s -X POST https://converse-api.destinpq.com/login -H "Content-Type: application/json" -d '{"username":"demo@example.com","password":"Akanksha100991!"}')
if echo "$LOGIN_RESPONSE" | grep -q "token"; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token')
    echo "✅ Authentication working, got JWT token"

    # Test search with token
    echo "🔍 Testing search functionality..."
    SEARCH_RESPONSE=$(curl -s -X POST https://converse-api.destinpq.com/analyze -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"query": "What is DestinPQ?"}')
    if echo "$SEARCH_RESPONSE" | grep -q "results"; then
        echo "✅ Search working correctly"
    else
        echo "❌ Search not working"
    fi
else
    echo "❌ Authentication failed"
fi

echo ""
echo "📋 If tests fail, check:"
echo "   1. DNS configuration for converse-api.destinpq.com"
echo "   2. PM2 process status: pm2 status"
echo "   3. Backend logs: pm2 logs aisearch-rag-backend"
echo "   4. Environment variables in app/backend/.env"
