#!/bin/bash

# Production Deployment Script for Service-Based PDF RAG Platform
# This script sets up the platform with proper domain configuration

set -e

echo "🚀 Setting up Production Deployment for PDF RAG Platform"
echo "=================================================="

# Configuration
DOMAIN="${DOMAIN:-pdf-rag-platform.com}"
API_SUBDOMAIN="${API_SUBDOMAIN:-api}"
APP_SUBDOMAIN="${APP_SUBDOMAIN:-app}"
ADMIN_SUBDOMAIN="${ADMIN_SUBDOMAIN:-admin}"

echo "📋 Configuration:"
echo "   Domain: $DOMAIN"
echo "   API URL: https://$API_SUBDOMAIN.$DOMAIN"
echo "   App URL: https://$APP_SUBDOMAIN.$DOMAIN"
echo "   Admin URL: https://$ADMIN_SUBDOMAIN.$DOMAIN"
echo

# Step 1: Install dependencies
echo "📦 Installing system dependencies..."
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx supervisor redis-server postgresql postgresql-contrib

# Step 2: Create application user
echo "👤 Creating application user..."
sudo useradd -r -m -s /bin/bash pdfrag || echo "User already exists"
sudo usermod -aG www-data pdfrag

# Step 3: Setup directory structure
echo "📁 Setting up directory structure..."
sudo mkdir -p /var/lib/pdf-rag/{logs,uploads,static,ssl}
sudo mkdir -p /etc/pdf-rag
sudo chown -R pdfrag:www-data /var/lib/pdf-rag
sudo chmod -R 755 /var/lib/pdf-rag

# Step 4: Copy application files
echo "📋 Copying application files..."
sudo cp -r /home/azureuser/aisearch-openai-rag-audio/app/backend/* /var/lib/pdf-rag/
sudo chown -R pdfrag:www-data /var/lib/pdf-rag
sudo chmod +x /var/lib/pdf-rag/*.py

# Step 5: Setup Python virtual environment
echo "🐍 Setting up Python environment..."
sudo -u pdfrag python3 -m venv /var/lib/pdf-rag/venv
sudo -u pdfrag /var/lib/pdf-rag/venv/bin/pip install -r /var/lib/pdf-rag/requirements.txt || echo "Creating requirements.txt..."

# Create requirements.txt if it doesn't exist
cat > /tmp/requirements.txt << EOF
aiohttp>=3.8.0
aiohttp-cors>=0.7.0
aiohttp-jwt>=0.8.0
aiofiles>=23.0.0
passlib>=1.7.4
bcrypt>=4.0.0
PyJWT>=2.8.0
python-dotenv>=1.0.0
pymupdf>=1.23.0
tiktoken>=0.5.0
numpy>=1.24.0
PyPDF2>=3.0.0
sqlite3
redis>=4.0.0
psycopg2-binary>=2.9.0
stripe>=7.0.0
sendgrid>=6.10.0
sentry-sdk>=1.40.0
EOF

sudo cp /tmp/requirements.txt /var/lib/pdf-rag/
sudo -u pdfrag /var/lib/pdf-rag/venv/bin/pip install -r /var/lib/pdf-rag/requirements.txt

# Step 6: Setup environment variables
echo "🔐 Setting up environment variables..."
cat > /tmp/production.env << EOF
# Domain Configuration
DOMAIN=$DOMAIN
SUBDOMAIN=$API_SUBDOMAIN
BASE_URL=https://$API_SUBDOMAIN.$DOMAIN
FRONTEND_URL=https://$APP_SUBDOMAIN.$DOMAIN

# Server Configuration
PORT=8000
HOST=127.0.0.1

# Database Configuration
DATABASE_URL=postgresql://pdfrag:$(openssl rand -base64 32)@localhost/pdfrag_prod

# Security Configuration (CHANGE THESE IN PRODUCTION!)
JWT_SECRET=$(openssl rand -base64 64)
CSRF_SECRET=$(openssl rand -base64 32)

# SSL Configuration
SSL_CERT_PATH=/etc/letsencrypt/live/$DOMAIN/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/$DOMAIN/privkey.pem

# AI API Keys (SET THESE!)
PERPLEXITY_API_KEY=your_perplexity_key_here
OPENAI_API_KEY=your_openai_key_here

# Payment Configuration (SET THESE!)
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_key
STRIPE_SECRET_KEY=sk_live_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Email Configuration (SET THESE!)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=your_sendgrid_api_key
FROM_EMAIL=noreply@$DOMAIN

# Monitoring (OPTIONAL)
SENTRY_DSN=your_sentry_dsn_here
GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX
EOF

sudo cp /tmp/production.env /etc/pdf-rag/production.env
sudo chown pdfrag:www-data /etc/pdf-rag/production.env
sudo chmod 600 /etc/pdf-rag/production.env

# Step 7: Setup PostgreSQL database
echo "🗄️ Setting up PostgreSQL database..."
sudo -u postgres createuser pdfrag || echo "User exists"
sudo -u postgres createdb pdfrag_prod -O pdfrag || echo "Database exists"

# Step 8: Setup Nginx configuration
echo "🌐 Setting up Nginx configuration..."
cat > /tmp/nginx-pdfrag.conf << EOF
# API Server Configuration
server {
    listen 80;
    server_name $API_SUBDOMAIN.$DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name $API_SUBDOMAIN.$DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    
    # Security Headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
    
    # API Proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files
    location /static/ {
        alias /var/lib/pdf-rag/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # File uploads
    location /uploads/ {
        alias /var/lib/pdf-rag/uploads/;
        expires 1d;
    }
}

# Frontend App Configuration
server {
    listen 80;
    server_name $APP_SUBDOMAIN.$DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name $APP_SUBDOMAIN.$DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL Configuration (same as API)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    
    # Security Headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
    
    # Frontend App (serve from API server for now)
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}

# Main Domain Redirect
server {
    listen 80;
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    return 301 https://$APP_SUBDOMAIN.$DOMAIN\$request_uri;
}
EOF

sudo cp /tmp/nginx-pdfrag.conf /etc/nginx/sites-available/pdfrag
sudo ln -sf /etc/nginx/sites-available/pdfrag /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Step 9: Setup SSL certificates
echo "🔒 Setting up SSL certificates..."
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN -d $API_SUBDOMAIN.$DOMAIN -d $APP_SUBDOMAIN.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Step 10: Setup Supervisor for process management
echo "👨‍💼 Setting up Supervisor..."
cat > /tmp/pdfrag-supervisor.conf << EOF
[program:pdfrag-api]
directory=/var/lib/pdf-rag
command=/var/lib/pdf-rag/venv/bin/python app.py
user=pdfrag
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/lib/pdf-rag/logs/api.log
environment=ENV_FILE="/etc/pdf-rag/production.env"

[program:pdfrag-worker]
directory=/var/lib/pdf-rag
command=/var/lib/pdf-rag/venv/bin/python worker.py
user=pdfrag
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/lib/pdf-rag/logs/worker.log
environment=ENV_FILE="/etc/pdf-rag/production.env"
EOF

sudo cp /tmp/pdfrag-supervisor.conf /etc/supervisor/conf.d/pdfrag.conf
sudo supervisorctl reread
sudo supervisorctl update

# Step 11: Setup log rotation
echo "📋 Setting up log rotation..."
cat > /tmp/pdfrag-logrotate << EOF
/var/lib/pdf-rag/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    sharedscripts
    postrotate
        supervisorctl restart pdfrag-api pdfrag-worker
    endscript
}
EOF

sudo cp /tmp/pdfrag-logrotate /etc/logrotate.d/pdfrag

# Step 12: Setup firewall
echo "🔥 Setting up firewall..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Step 13: Start services
echo "🚀 Starting services..."
sudo systemctl enable nginx postgresql redis-server supervisor
sudo systemctl start nginx postgresql redis-server supervisor
sudo supervisorctl start pdfrag-api pdfrag-worker

# Step 14: Initialize database
echo "🗄️ Initializing database..."
sudo -u pdfrag /var/lib/pdf-rag/venv/bin/python /var/lib/pdf-rag/database_init.py

echo
echo "✅ Production deployment complete!"
echo "=================================================="
echo "🌐 Your PDF RAG Platform is now available at:"
echo "   Main App: https://$APP_SUBDOMAIN.$DOMAIN"
echo "   API: https://$API_SUBDOMAIN.$DOMAIN"
echo "   Login: https://$APP_SUBDOMAIN.$DOMAIN/login"
echo
echo "🔧 Next steps:"
echo "1. Update API keys in /etc/pdf-rag/production.env"
echo "2. Configure Stripe payment processing"
echo "3. Setup email notifications"
echo "4. Configure monitoring and backups"
echo "5. Test the complete user registration flow"
echo
echo "📋 Management commands:"
echo "   sudo supervisorctl status"
echo "   sudo supervisorctl restart pdfrag-api"
echo "   sudo tail -f /var/lib/pdf-rag/logs/api.log"
echo "   sudo nginx -t && sudo systemctl reload nginx"
echo
