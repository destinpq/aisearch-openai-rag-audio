"""
Production Configuration for Service-Based PDF RAG Platform
Configures domain, SSL, and production deployment settings
"""

import os
from pathlib import Path

class ProductionConfig:
    """Production configuration settings"""
    
    # Domain Configuration
    DOMAIN = os.environ.get("DOMAIN", "pdf-rag-platform.com")
    SUBDOMAIN = os.environ.get("SUBDOMAIN", "api")
    BASE_URL = f"https://{SUBDOMAIN}.{DOMAIN}" if SUBDOMAIN else f"https://{DOMAIN}"
    
    # Server Configuration
    HOST = "0.0.0.0"  # Bind to all interfaces for production
    PORT = int(os.environ.get("PORT", 443))  # HTTPS port
    
    # SSL Configuration
    SSL_CERT_PATH = os.environ.get("SSL_CERT_PATH", "/etc/letsencrypt/live/{DOMAIN}/fullchain.pem")
    SSL_KEY_PATH = os.environ.get("SSL_KEY_PATH", "/etc/letsencrypt/live/{DOMAIN}/privkey.pem")
    
    # Frontend Configuration
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://converse.destinpq.com")
    
    # CORS Configuration for Production
    CORS_ORIGINS = [
        "https://converse.destinpq.com",  # Existing frontend
        "https://destinpq.com",
        "https://www.destinpq.com",
        f"https://app.{DOMAIN}",  # Future frontend if needed
        f"https://{DOMAIN}",
        f"https://www.{DOMAIN}",
        "https://localhost:3000",  # Development fallback
        "http://localhost:52047",  # Development API
    ]
    
    # Database Configuration
    DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///var/lib/pdf-rag/production.db")
    
    # Security Configuration
    JWT_SECRET = os.environ.get("JWT_SECRET")  # Must be set in production
    CSRF_SECRET = os.environ.get("CSRF_SECRET")
    
    # Payment Integration
    STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
    
    # Email Configuration
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.sendgrid.net")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USER = os.environ.get("SMTP_USER")
    SMTP_PASS = os.environ.get("SMTP_PASS")
    FROM_EMAIL = os.environ.get("FROM_EMAIL", f"noreply@{DOMAIN}")
    
    # Monitoring & Analytics
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    GOOGLE_ANALYTICS_ID = os.environ.get("GOOGLE_ANALYTICS_ID")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", 100))
    
    @classmethod
    def validate_production_config(cls):
        """Validate required production configuration"""
        required_vars = [
            "DOMAIN",
            "JWT_SECRET", 
            "CSRF_SECRET",
            "STRIPE_SECRET_KEY",
            "SMTP_USER",
            "SMTP_PASS"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

class DomainConfig:
    """Domain-specific configuration"""
    
    # Suggested domain structure for the service
    DOMAIN_STRUCTURE = {
        "main": "pdf-rag-platform.com",  # Main landing page
        "app": "app.pdf-rag-platform.com",  # User dashboard/interface
        "api": "api.pdf-rag-platform.com",  # API endpoints
        "admin": "admin.pdf-rag-platform.com",  # Admin panel
        "docs": "docs.pdf-rag-platform.com",  # API documentation
        "status": "status.pdf-rag-platform.com",  # System status page
    }
    
    # CDN Configuration
    CDN_URL = os.environ.get("CDN_URL", "https://cdn.pdf-rag-platform.com")
    STATIC_URL = f"{CDN_URL}/static"
    
    # Service Endpoints
    ENDPOINTS = {
        "api_base": f"https://api.pdf-rag-platform.com",
        "websocket": f"wss://api.pdf-rag-platform.com/realtime",
        "uploads": f"https://uploads.pdf-rag-platform.com",
        "downloads": f"https://files.pdf-rag-platform.com"
    }

def get_production_cors_config():
    """Get CORS configuration for production"""
    return {
        "origins": ProductionConfig.CORS_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "headers": [
            "Content-Type",
            "Authorization", 
            "X-Requested-With",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers"
        ],
        "credentials": True
    }

def setup_ssl_context():
    """Setup SSL context for HTTPS"""
    import ssl
    
    if not os.path.exists(ProductionConfig.SSL_CERT_PATH):
        raise FileNotFoundError(f"SSL certificate not found: {ProductionConfig.SSL_CERT_PATH}")
    
    if not os.path.exists(ProductionConfig.SSL_KEY_PATH):
        raise FileNotFoundError(f"SSL private key not found: {ProductionConfig.SSL_KEY_PATH}")
    
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(ProductionConfig.SSL_CERT_PATH, ProductionConfig.SSL_KEY_PATH)
    
    return ssl_context
