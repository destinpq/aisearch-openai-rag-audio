"""
Backend-Only Integration Guide
Configure service-based authentication to work with existing frontend
"""

class BackendIntegration:
    """Integration configuration for existing frontend"""
    
    # Existing frontend configuration
    EXISTING_FRONTEND = "https://converse.destinpq.com"
    
    # API-only endpoints (no frontend changes needed)
    API_ENDPOINTS = {
        # Authentication (works with existing frontend)
        "login": "/api/login",
        "register": "/api/register", 
        
        # Service management (new endpoints for existing frontend)
        "profile": "/api/profile",
        "tiers": "/api/tiers",
        "upgrade": "/api/upgrade",
        "usage_stats": "/api/usage-stats",
        "add_credits": "/api/add-credits",
        
        # Service-protected PDF operations
        "pdf_upload": "/api/pdf/upload",
        "pdf_search": "/api/pdf/search", 
        "pdf_ai_analysis": "/api/pdf/ai-analysis",
        "pdf_line_seek": "/api/pdf/line-seek",
        
        # Legacy endpoints (maintain compatibility)
        "legacy_upload": "/api/upload",
        "legacy_analyze": "/api/analyze",
        "legacy_files": "/api/files"
    }
    
    @classmethod
    def get_integration_instructions(cls):
        """Get instructions for integrating with existing frontend"""
        return f"""
        🔧 BACKEND-ONLY INTEGRATION COMPLETE
        ===================================
        
        ✅ Your existing frontend at {cls.EXISTING_FRONTEND} will continue to work
        ✅ No frontend changes required
        ✅ Service-based authentication added to backend
        ✅ All legacy endpoints maintained for compatibility
        
        📡 NEW API ENDPOINTS AVAILABLE:
        ------------------------------
        Authentication (Enhanced):
        - POST /api/login    - Now supports service tiers
        - POST /api/register - Now supports subscription selection
        
        User Management (New):
        - GET  /api/profile     - User profile with service status
        - GET  /api/tiers       - Available subscription tiers
        - POST /api/upgrade     - Upgrade subscription
        - GET  /api/usage-stats - Usage statistics
        - POST /api/add-credits - Add credits to account
        
        Service-Protected Features (New):
        - POST /api/pdf/upload      - Enhanced PDF upload with service control
        - POST /api/pdf/search      - Enhanced search with service control
        - POST /api/pdf/ai-analysis - AI analysis with service control
        - POST /api/pdf/line-seek   - Line seeking with service control
        
        Legacy Compatibility (Maintained):
        - POST /api/upload   - Original PDF upload (still works)
        - POST /api/analyze  - Original analysis (still works)
        - GET  /api/files    - File listing (still works)
        
        🔐 AUTHENTICATION TOKENS:
        ------------------------
        - Your existing frontend can use the same /api/login endpoint
        - JWT tokens now include subscription tier information
        - Token format remains compatible with existing code
        
        📊 SERVICE TIERS AVAILABLE:
        --------------------------
        - Free: $0/month (50 credits, basic features)
        - Basic: $9.99/month (500 credits, enhanced search)
        - Pro: $29.99/month (2000 credits, AI analysis)
        - Enterprise: $99.99/month (unlimited, all features)
        
        🚀 READY TO USE:
        ---------------
        Your existing frontend at {cls.EXISTING_FRONTEND} can immediately:
        1. Use enhanced authentication with service tiers
        2. Access new service-protected features
        3. Continue using all legacy endpoints
        4. Upgrade users to higher tiers
        5. Track usage and billing
        """

def print_backend_integration_status():
    """Print the current backend integration status"""
    return BackendIntegration.get_integration_instructions()

# Configuration for existing frontend integration
FRONTEND_INTEGRATION_CONFIG = {
    "existing_frontend_url": "https://converse.destinpq.com",
    "api_base_url": "http://localhost:52047",  # Development
    "production_api_url": "https://api.destinpq.com",  # Production
    "cors_enabled": True,
    "legacy_endpoints_maintained": True,
    "new_service_endpoints_added": True,
    "frontend_changes_required": False
}
