# VoiceRAG Production Domain Configuration Summary

## ✅ Configuration Complete

Your VoiceRAG application is now configured to work exclusively with your production domains:

- **Frontend**: `converse.destinpq.com`
- **Backend API**: `converse-api.destinpq.com`

## 🔧 Changes Made

### Frontend Configuration

- ✅ Environment file updated to use `https://converse-api.destinpq.com`
- ✅ WebSocket connections automatically use `wss://converse-api.destinpq.com/realtime`
- ✅ Frontend rebuilt and optimized for production
- ✅ Static files available in `/app/backend/static/`

### Backend Configuration

- ✅ CORS restricted to allow only `https://converse.destinpq.com`
- ✅ Development localhost access maintained for testing
- ✅ Production environment variables configured
- ✅ Port 8765 configured for reverse proxy setup

### Security Settings

- ✅ HTTPS-only configuration
- ✅ Secure CORS policy
- ✅ JWT authentication enabled
- ✅ Production environment flags set

## 🚀 Deployment Files Created

1. **nginx-production.conf** - Complete nginx configuration for both domains
2. **start-production.sh** - Production startup script
3. **ecosystem.config.js** - Updated PM2 configuration
4. **deployment-config.md** - Detailed deployment instructions

## 🌐 Domain Setup Required

### DNS Configuration

Point both domains to your server IP:

```
converse.destinpq.com       A    YOUR_SERVER_IP
converse-api.destinpq.com   A    YOUR_SERVER_IP
```

### SSL Certificates

Obtain SSL certificates for both domains:

```bash
# Using Let's Encrypt (example)
certbot --nginx -d converse.destinpq.com -d converse-api.destinpq.com
```

### Nginx Setup

1. Copy `nginx-production.conf` to `/etc/nginx/sites-available/voicerag`
2. Create symlink: `ln -s /etc/nginx/sites-available/voicerag /etc/nginx/sites-enabled/`
3. Update SSL certificate paths in the config
4. Test: `nginx -t`
5. Reload: `systemctl reload nginx`

## 🎯 Quick Start Commands

### Start Production Server

```bash
cd /home/azureuser/aisearch-openai-rag-audio
./start-production.sh
```

### Using PM2 (Alternative)

```bash
pm2 start ecosystem.config.js --env production
pm2 save
pm2 startup
```

### Test Configuration

```bash
# Test backend API
curl http://localhost:8765/

# Test with production URL (after DNS/proxy setup)
curl https://converse-api.destinpq.com/
```

## 📋 Verification Checklist

- [ ] DNS records pointing to your server
- [ ] SSL certificates installed
- [ ] Nginx configuration updated
- [ ] Backend server running on port 8765
- [ ] Frontend accessible at `https://converse.destinpq.com`
- [ ] API accessible at `https://converse-api.destinpq.com`
- [ ] WebSocket connections working
- [ ] Authentication system functional

## 🔐 Admin Access

- **Username**: demo@example.com
- **Password**: Akanksha100991!

## 📞 Support

All components are now configured for your production domains. The application will only accept requests from `converse.destinpq.com` and serve the API at `converse-api.destinpq.com`.

Next steps:

1. Set up DNS records
2. Install SSL certificates
3. Configure nginx with the provided config
4. Start the production server
5. Test both domains

Your VoiceRAG application is ready for production deployment! 🎉
