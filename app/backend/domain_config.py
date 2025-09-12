"""
Domain Configuration and URL Management
Handles dynamic domain configuration for different environments
"""

from dataclasses import dataclass
from typing import Dict, List
import os

@dataclass 
class DomainEndpoints:
    """Domain-specific endpoint configuration"""
    main: str
    api: str
    app: str
    admin: str
    docs: str
    status: str
    cdn: str
    uploads: str
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins for this domain configuration"""
        return [
            self.main,
            self.api,
            self.app,
            self.admin,
            f"https://www.{self.main}",
            "http://localhost:3000",  # Development
            "http://localhost:52047",  # Development API
        ]

class DomainManager:
    """Manages domain configuration for different environments"""
    
    PRODUCTION_DOMAINS = {
        "pdf-rag-platform.com": DomainEndpoints(
            main="https://pdf-rag-platform.com",
            api="https://api.pdf-rag-platform.com", 
            app="https://app.pdf-rag-platform.com",
            admin="https://admin.pdf-rag-platform.com",
            docs="https://docs.pdf-rag-platform.com",
            status="https://status.pdf-rag-platform.com",
            cdn="https://cdn.pdf-rag-platform.com",
            uploads="https://files.pdf-rag-platform.com"
        ),
        "pdfrag.ai": DomainEndpoints(
            main="https://pdfrag.ai",
            api="https://api.pdfrag.ai",
            app="https://app.pdfrag.ai", 
            admin="https://admin.pdfrag.ai",
            docs="https://docs.pdfrag.ai",
            status="https://status.pdfrag.ai",
            cdn="https://cdn.pdfrag.ai",
            uploads="https://files.pdfrag.ai"
        ),
        "docrag.com": DomainEndpoints(
            main="https://docrag.com",
            api="https://api.docrag.com",
            app="https://app.docrag.com",
            admin="https://admin.docrag.com", 
            docs="https://docs.docrag.com",
            status="https://status.docrag.com",
            cdn="https://cdn.docrag.com",
            uploads="https://files.docrag.com"
        )
    }
    
    @classmethod
    def get_domain_config(cls, domain: str = None) -> DomainEndpoints:
        """Get domain configuration"""
        if not domain:
            domain = os.environ.get("DOMAIN", "pdf-rag-platform.com")
        
        # Remove protocol if present
        domain = domain.replace("https://", "").replace("http://", "")
        
        if domain in cls.PRODUCTION_DOMAINS:
            return cls.PRODUCTION_DOMAINS[domain]
        
        # Default/development configuration
        return DomainEndpoints(
            main=f"https://{domain}",
            api=f"https://api.{domain}",
            app=f"https://app.{domain}",
            admin=f"https://admin.{domain}",
            docs=f"https://docs.{domain}",
            status=f"https://status.{domain}",
            cdn=f"https://cdn.{domain}",
            uploads=f"https://files.{domain}"
        )
    
    @classmethod
    def update_frontend_urls(cls, domain_config: DomainEndpoints) -> Dict[str, str]:
        """Update frontend URL references for the domain"""
        return {
            "LOGIN_REDIRECT": f"{domain_config.app}/dashboard",
            "LOGOUT_REDIRECT": f"{domain_config.app}/login",
            "API_BASE_URL": domain_config.api,
            "WEBSOCKET_URL": f"{domain_config.api.replace('https:', 'wss:')}/realtime",
            "UPLOAD_URL": f"{domain_config.uploads}/upload",
            "STATIC_URL": f"{domain_config.cdn}/static",
            "SUPPORT_EMAIL": f"support@{domain_config.main.replace('https://', '')}",
            "PRIVACY_POLICY": f"{domain_config.main}/privacy",
            "TERMS_OF_SERVICE": f"{domain_config.main}/terms"
        }

def get_domain_specific_config():
    """Get complete domain-specific configuration"""
    domain = os.environ.get("DOMAIN", "pdf-rag-platform.com")
    endpoints = DomainManager.get_domain_config(domain)
    frontend_urls = DomainManager.update_frontend_urls(endpoints)
    
    return {
        "domain": domain,
        "endpoints": endpoints,
        "frontend_urls": frontend_urls,
        "cors_origins": endpoints.get_cors_origins(),
        "is_production": os.environ.get("PRODUCTION", "false").lower() == "true"
    }

# Suggested domain names for the service
DOMAIN_SUGGESTIONS = [
    # Primary suggestions
    "pdf-rag-platform.com",
    "pdfrag.ai", 
    "docrag.com",
    "aipdfreader.com",
    "smartpdfrag.com",
    
    # Alternative suggestions
    "pdfanalyzer.ai",
    "ragpdf.com", 
    "pdfdocs.ai",
    "intelligentpdf.com",
    "pdfinsights.ai",
    "documentrag.com",
    "pdfchat.ai",
    "ragdocs.com",
    "pdfbrain.ai",
    "docanalytics.ai"
]

def check_domain_availability():
    """
    Instructions for checking domain availability
    This is a placeholder - in production you'd integrate with domain registrars
    """
    instructions = """
    🌐 Domain Setup Instructions:
    
    1. Choose a domain from suggestions:
       {domains}
    
    2. Purchase domain from registrar:
       - Namecheap, GoDaddy, Cloudflare, etc.
    
    3. Configure DNS records:
       A     @                  -> Your server IP
       A     www               -> Your server IP  
       A     api               -> Your server IP
       A     app               -> Your server IP
       A     admin             -> Your server IP
       CNAME docs              -> Your server IP
       CNAME status            -> Your server IP
    
    4. Update environment variables:
       export DOMAIN=your-chosen-domain.com
       export PRODUCTION=true
    
    5. Run deployment script:
       ./deploy_production.sh
    
    6. SSL certificates will be automatically configured via Let's Encrypt
    """.format(domains="\n       ".join(f"- {domain}" for domain in DOMAIN_SUGGESTIONS[:10]))
    
    return instructions
