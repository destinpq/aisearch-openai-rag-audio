#!/bin/bash

# Production startup script for VoiceRAG
# This script starts the backend server configured for production domains

echo "🚀 Starting VoiceRAG for Production Deployment"
echo "Frontend Domain: converse.destinpq.com"
echo "Backend API Domain: converse-api.destinpq.com"
echo ""

# Set production environment
export RUNNING_IN_PRODUCTION=true
export PORT=8765

# Navigate to project directory
cd /home/azureuser/aisearch-openai-rag-audio

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "🐍 Using virtual environment"
fi

# Kill any existing processes on port 8765
echo "🔄 Stopping any existing processes on port 8765..."
lsof -ti :8765 | xargs -r kill -9

# Start the backend server
echo "🌐 Starting backend server on port 8765..."
echo "API will be available at: http://localhost:8765"
echo "Configure your reverse proxy to forward:"
echo "  converse-api.destinpq.com → localhost:8765"
echo "  converse.destinpq.com → localhost:8765"
echo ""

# Start server in background with logging
nohup python app/backend/app.py > production.log 2>&1 &
SERVER_PID=$!

echo "✅ Server started with PID: $SERVER_PID"
echo "📋 Logs available in: production.log"
echo ""
echo "🔍 To monitor logs: tail -f production.log"
echo "🛑 To stop server: kill $SERVER_PID"
echo ""

# Wait a moment and check if server started successfully
sleep 3
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Server is running successfully!"
    echo "🌍 Test locally: curl http://localhost:8765/"
else
    echo "❌ Server failed to start. Check production.log for errors."
    exit 1
fi
