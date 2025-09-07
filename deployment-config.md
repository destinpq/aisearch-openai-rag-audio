# Production Deployment Configuration

## Domain Setup

- **Frontend**: `converse.destinpq.com`
- **Backend API**: `converse-api.destinpq.com`

## Configuration Changes Made

### 1. Frontend Configuration

- Updated `/app/frontend/.env` to point to production API URL: `https://converse-api.destinpq.com`
- Frontend now configured for production domains only
- Frontend builds to `/app/backend/static` for serving
- WebSocket connections automatically use `wss://converse-api.destinpq.com/realtime`

### 2. Backend Configuration

- Updated CORS settings in `app.py` to allow only `https://converse.destinpq.com` and localhost for development
- Backend configured to run on port 8765 (reverse proxy to port 80/443)
- Production mode enabled with `RUNNING_IN_PRODUCTION=true`

## Deployment Steps

### For the Backend (converse-api.destinpq.com):

1. **Set up the server** (port 8765):

   ```bash
   cd /home/azureuser/aisearch-openai-rag-audio
   python3 app/backend/app.py
   # OR using PM2:
   pm2 start ecosystem.config.js --env production
   ```

2. **Environment Variables** (ensure these are set):

   ```bash
   export RUNNING_IN_PRODUCTION=true
   export PORT=8765
   export AZURE_OPENAI_API_KEY=your_api_key
   export AZURE_SEARCH_API_KEY=your_search_key
   # ... other Azure configs (already in .env file)
   ```

3. **Reverse Proxy Setup** (nginx):
   ```nginx
   server {
       server_name converse-api.destinpq.com;
       location / {
           proxy_pass http://localhost:8765;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;

           # WebSocket support
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```

### For the Frontend (converse.destinpq.com):

**Option 1: Serve via Backend** (Recommended)

- The built frontend files are in `/app/backend/static`
- Backend serves the frontend at the root path `/`
- Point `converse.destinpq.com` to the same server as the backend

**Option 2: Separate Frontend Server**

- Copy contents of `/app/backend/static` to a separate web server
- Configure web server to serve static files for `converse.destinpq.com`

## SSL/TLS Configuration

Ensure both domains have SSL certificates configured:

- `converse.destinpq.com` → HTTPS
- `converse-api.destinpq.com` → HTTPS

## Testing

1. **Test Backend API**:

   ```bash
   curl https://converse-api.destinpq.com/health
   ```

2. **Test Frontend**:
   - Visit `https://converse.destinpq.com`
   - Check browser console for any CORS or API connection errors

## Security Configuration

- CORS restricted to production domains only
- Backend only accepts requests from `https://converse.destinpq.com`
- All communication over HTTPS
- JWT authentication enabled

## Current Status

✅ Frontend configured for production API URL  
✅ Backend CORS restricted to production domains  
✅ Production mode enabled  
✅ Port 8765 configured for backend  
⏳ Ready for domain deployment

The application is now configured to work exclusively with your production domains!
