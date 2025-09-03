#!/bin/bash

# Production deployment script for DestinPQ RAG Backend
# This script deploys the backend to converse-api.destinpq.com

echo "🚀 Starting DestinPQ RAG Backend Production Deployment"
echo "======================================================"

# Set production environment
export RUNNING_IN_PRODUCTION=true
export NODE_ENV=production
export PORT=80

# Load Python environment
echo "📦 Loading Python environment..."
. ./scripts/load_python_env.sh

# Install/update Python dependencies
echo "🔧 Installing Python dependencies..."
cd app/backend
pip install -r requirements.txt

# Build frontend for production
echo "🎨 Building frontend..."
cd ../frontend
npm install --legacy-peer-deps
npm run build

# Start backend with PM2 in production mode
echo "⚡ Starting backend in production mode..."
cd ../../
pm2 start ecosystem.config.js --env production

echo "✅ Production deployment complete!"
echo "🌐 Backend should now be available at: https://converse-api.destinpq.com"
echo "🎯 Frontend should be available at: https://converse.destinpq.com"
echo ""
echo "📋 Next steps:"
echo "   1. Make sure converse-api.destinpq.com points to this server"
echo "   2. Make sure converse.destinpq.com points to your frontend server"
echo "   3. Update AZURE_OPENAI_API_KEY and AZURE_SEARCH_API_KEY in app/backend/.env"
echo "   4. Test the /analyze endpoint with your JWT token"