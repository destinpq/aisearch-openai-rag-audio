"""
Service-Based Authentication Middleware
Handles authentication and service access control for all endpoints
"""

from aiohttp import web
from functools import wraps
import json
import logging
from typing import Dict

# We'll import user_manager in functions to avoid circular imports
logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

def require_auth(func):
    """Decorator to require authentication"""
    @wraps(func)
    async def wrapper(request):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return web.json_response(
                {"error": "Authentication required", "code": "AUTH_REQUIRED"}, 
                status=401
            )
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Verify token
        from user_manager import user_manager
        user_data = user_manager.verify_jwt_token(token)
        if not user_data:
            return web.json_response(
                {"error": "Invalid or expired token", "code": "TOKEN_INVALID"}, 
                status=401
            )
        
        # Add user data to request
        request['user'] = user_data
        
        return await func(request)
    
    return wrapper

def require_service(service_name: str, usage_count: int = 1):
    """Decorator to require specific service access"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request):
            # Must be authenticated first
            if 'user' not in request:
                return web.json_response(
                    {"error": "Authentication required", "code": "AUTH_REQUIRED"}, 
                    status=401
                )
            
            user_id = request['user']['user_id']
            
            # Check service access
            from user_manager import user_manager
            access_check = user_manager.check_service_access(user_id, service_name)
            
            if not access_check["has_access"]:
                # Return specific error based on reason
                error_codes = {
                    "Service not found": "SERVICE_NOT_FOUND",
                    "Service disabled": "SERVICE_DISABLED", 
                    "Service expired": "SERVICE_EXPIRED",
                    "Usage limit exceeded": "USAGE_LIMIT_EXCEEDED",
                    "Insufficient credits": "INSUFFICIENT_CREDITS"
                }
                
                reason = access_check.get("reason", "Access denied")
                error_code = error_codes.get(reason, "ACCESS_DENIED")
                
                return web.json_response({
                    "error": reason,
                    "code": error_code,
                    "service": service_name,
                    "upgrade_required": reason in ["Usage limit exceeded", "Insufficient credits"]
                }, status=403)
            
            # Record service usage
            success = user_manager.use_service(user_id, service_name, usage_count)
            if not success:
                return web.json_response({
                    "error": "Failed to record service usage",
                    "code": "USAGE_RECORD_FAILED"
                }, status=500)
            
            # Add service info to request
            request['service_info'] = access_check
            
            return await func(request)
        
        return wrapper
    return decorator

def require_tier(minimum_tier: str):
    """Decorator to require minimum subscription tier"""
    tier_hierarchy = {"free": 0, "basic": 1, "pro": 2, "enterprise": 3}
    
    def decorator(func):
        @wraps(func)
        async def wrapper(request):
            if 'user' not in request:
                return web.json_response(
                    {"error": "Authentication required", "code": "AUTH_REQUIRED"}, 
                    status=401
                )
            
            user_tier = request['user'].get('subscription_tier', 'free')
            user_tier_level = tier_hierarchy.get(user_tier, 0)
            required_tier_level = tier_hierarchy.get(minimum_tier, 0)
            
            if user_tier_level < required_tier_level:
                return web.json_response({
                    "error": f"Subscription upgrade required to {minimum_tier} or higher",
                    "code": "TIER_UPGRADE_REQUIRED",
                    "current_tier": user_tier,
                    "required_tier": minimum_tier
                }, status=403)
            
            return await func(request)
        
        return wrapper
    return decorator

async def auth_middleware(app, handler):
    """Middleware to add user context to requests"""
    
    async def middleware_handler(request):
        # Skip auth for public endpoints
        public_endpoints = [
            '/api/register',
            '/api/login', 
            '/api/tiers',
            '/api/public/status',
            '/',
            '/static'
        ]
        
        skip_auth = any(request.path.startswith(endpoint) for endpoint in public_endpoints)
    
        if not skip_auth:
            # Try to get user from token
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                from user_manager import user_manager
                user_data = user_manager.verify_jwt_token(token)
                if user_data:
                    request['user'] = user_data
        
        return await handler(request)
    
    return middleware_handler

class ServiceAccessControl:
    """Class to handle service access control"""
    
    @staticmethod
    async def check_access_and_respond(request, service_name: str, usage_count: int = 1):
        """Check service access and return appropriate response"""
        if 'user' not in request:
            return web.json_response({
                "error": "Authentication required",
                "code": "AUTH_REQUIRED"
            }, status=401)
        
        user_id = request['user']['user_id']
        from user_manager import user_manager
        access_check = user_manager.check_service_access(user_id, service_name)
        
        if not access_check["has_access"]:
            reason = access_check.get("reason", "Access denied")
            
            # Provide upgrade suggestions
            upgrade_suggestions = {
                "Usage limit exceeded": "Consider upgrading to a higher tier for more usage",
                "Insufficient credits": "Please add credits or upgrade your subscription",
                "Service disabled": "This service is not available in your current plan"
            }
            
            return web.json_response({
                "error": reason,
                "code": "ACCESS_DENIED",
                "service": service_name,
                "suggestion": upgrade_suggestions.get(reason, "Contact support for assistance"),
                "current_usage": access_check.get("usage_count", 0),
                "usage_limit": access_check.get("usage_limit", -1)
            }, status=403)
        
        # Record usage
        from user_manager import user_manager
        user_manager.use_service(user_id, service_name, usage_count)
        
        return None  # Access granted
    
    @staticmethod
    def get_user_service_status(user_id: int) -> Dict:
        """Get comprehensive service status for user"""
        try:
            from user_manager import user_manager
            user = user_manager.get_user_by_id(user_id)
            if not user:
                return {"error": "User not found"}
            
            services = user.get("services", [])
            tier_info = user.get("tier_info", {})
            usage_stats = user_manager.get_user_usage_stats(user_id)
            
            # Categorize services
            service_categories = {}
            for service in services:
                category = service.get("category", "general")
                if category not in service_categories:
                    service_categories[category] = []
                
                service_categories[category].append({
                    "name": service["name"],
                    "display_name": service["display_name"],
                    "is_enabled": service["is_enabled"],
                    "usage_count": service["usage_count"],
                    "usage_limit": service["usage_limit"],
                    "remaining_uses": service["usage_limit"] - service["usage_count"] if service["usage_limit"] > 0 else -1,
                    "cost_per_use": service["per_use_cost"]
                })
            
            return {
                "user_info": {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                    "subscription_tier": user["subscription_tier"],
                    "credits_remaining": user["credits_remaining"]
                },
                "tier_info": tier_info,
                "services_by_category": service_categories,
                "usage_stats": usage_stats
            }
            
        except Exception as e:
            logger.error(f"Get user service status error: {e}")
            return {"error": "Failed to get service status"}

# Global instance
service_access = ServiceAccessControl()
