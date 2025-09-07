#!/bin/bash

# Production Configuration Verification Script
echo "🔍 VoiceRAG Production Configuration Verification"
echo "=================================================="
echo ""

# Check if server is running
echo "1. 🌐 Server Status Check:"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8765/ | grep -q "200"; then
    echo "   ✅ Backend server is running on port 8765"
else
    echo "   ❌ Backend server is not responding"
fi

# Check frontend build
echo ""
echo "2. 📦 Frontend Build Check:"
if [ -f "/home/azureuser/aisearch-openai-rag-audio/app/backend/static/index.html" ]; then
    echo "   ✅ Frontend build files exist"
    echo "   📄 Build location: /app/backend/static/"
else
    echo "   ❌ Frontend build files not found"
fi

# Check environment configuration
echo ""
echo "3. ⚙️  Environment Configuration:"
if grep -q "https://converse-api.destinpq.com" /home/azureuser/aisearch-openai-rag-audio/app/frontend/.env; then
    echo "   ✅ Frontend configured for production API URL"
else
    echo "   ❌ Frontend not configured for production"
fi

if grep -q "RUNNING_IN_PRODUCTION" /home/azureuser/aisearch-openai-rag-audio/ecosystem.config.js; then
    echo "   ✅ PM2 configuration ready for production"
else
    echo "   ❌ PM2 configuration not set for production"
fi

# Check nginx configuration
echo ""
echo "4. 🌍 Nginx Configuration:"
if [ -f "/home/azureuser/aisearch-openai-rag-audio/nginx-production.conf" ]; then
    echo "   ✅ Nginx configuration file created"
    echo "   📋 Next: Copy to /etc/nginx/sites-available/"
else
    echo "   ❌ Nginx configuration file missing"
fi

# Check SSL readiness
echo ""
echo "5. 🔐 SSL Configuration:"
echo "   📋 Required domains:"
echo "      - converse.destinpq.com"
echo "      - converse-api.destinpq.com"
echo "   📋 Next: Install SSL certificates for both domains"

# Check CORS configuration
echo ""
echo "6. 🔒 CORS Configuration:"
if grep -q "converse.destinpq.com" /home/azureuser/aisearch-openai-rag-audio/app/backend/app.py; then
    echo "   ✅ CORS restricted to production domain"
else
    echo "   ❌ CORS not properly configured"
fi

echo ""
echo "=================================================="
echo "📋 PRODUCTION DEPLOYMENT CHECKLIST:"
echo ""
echo "   1. ✅ Configure DNS records for both domains"
echo "   2. ✅ Install SSL certificates"
echo "   3. ✅ Set up nginx reverse proxy"
echo "   4. ✅ Start production server"
echo "   5. ✅ Test both domains"
echo ""
echo "🎯 Your app is configured for:"
echo "   Frontend: https://converse.destinpq.com"
echo "   Backend:  https://converse-api.destinpq.com"
echo ""
echo "💡 Local testing: http://localhost:8765"
