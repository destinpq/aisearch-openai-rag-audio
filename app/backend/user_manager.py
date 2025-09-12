"""
User Management System with Service-Based Features
Handles authentication, subscription tiers, and feature access control
"""

import sqlite3
import bcrypt
import jwt
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self, db_path: str = "app_data.db", jwt_secret: str = "your-secret-key"):
        self.db_path = db_path
        self.jwt_secret = jwt_secret
        self.init_database()
    
    def init_database(self):
        """Initialize database with schema"""
        try:
            with open("database_schema.sql", "r") as f:
                schema = f.read()
            
            conn = sqlite3.connect(self.db_path)
            conn.executescript(schema)
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def create_user(self, email: str, name: str, password: str, subscription_tier: str = "free") -> Optional[Dict]:
        """Create a new user account"""
        try:
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert user
            cursor.execute("""
                INSERT INTO users (email, name, password_hash, subscription_tier, 
                                 billing_cycle_start, billing_cycle_end)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                email, name, password_hash, subscription_tier,
                datetime.now().date(),
                (datetime.now() + timedelta(days=30)).date()
            ))
            
            user_id = cursor.lastrowid
            
            # Initialize user services based on subscription tier
            self._initialize_user_services(cursor, user_id, subscription_tier)
            
            conn.commit()
            conn.close()
            
            return self.get_user_by_id(user_id)
            
        except sqlite3.IntegrityError:
            return None  # Email already exists
        except Exception as e:
            logger.error(f"User creation error: {e}")
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, email, name, password_hash, role, subscription_tier, 
                       is_active, credits_remaining, monthly_usage
                FROM users WHERE email = ? AND is_active = 1
            """, (email,))
            
            user_data = cursor.fetchone()
            
            if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data[3].encode('utf-8')):
                # Update last login
                cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", 
                             (datetime.now(), user_data[0]))
                conn.commit()
                
                user = {
                    "id": user_data[0],
                    "email": user_data[1],
                    "name": user_data[2],
                    "role": user_data[4],
                    "subscription_tier": user_data[5],
                    "is_active": user_data[6],
                    "credits_remaining": user_data[7],
                    "monthly_usage": user_data[8]
                }
                
                # Add user services
                user["services"] = self.get_user_services(user_data[0])
                
                conn.close()
                return user
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def generate_jwt_token(self, user: Dict) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            "user_id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "subscription_tier": user["subscription_tier"],
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return user data"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, email, name, role, subscription_tier, is_active,
                       credits_remaining, monthly_usage, created_at, last_login
                FROM users WHERE id = ?
            """, (user_id,))
            
            user_data = cursor.fetchone()
            
            if user_data:
                user = {
                    "id": user_data[0],
                    "email": user_data[1],
                    "name": user_data[2],
                    "role": user_data[3],
                    "subscription_tier": user_data[4],
                    "is_active": user_data[5],
                    "credits_remaining": user_data[6],
                    "monthly_usage": user_data[7],
                    "created_at": user_data[8],
                    "last_login": user_data[9]
                }
                
                # Add services and tier info
                user["services"] = self.get_user_services(user_id)
                user["tier_info"] = self.get_subscription_tier_info(user_data[4])
                
                conn.close()
                return user
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Get user error: {e}")
            return None
    
    def get_subscription_tier_info(self, tier_name: str) -> Optional[Dict]:
        """Get subscription tier information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name, display_name, price_monthly, price_yearly,
                       features, limits, description
                FROM subscription_tiers WHERE name = ? AND is_active = 1
            """, (tier_name,))
            
            tier_data = cursor.fetchone()
            
            if tier_data:
                tier_info = {
                    "name": tier_data[0],
                    "display_name": tier_data[1],
                    "price_monthly": float(tier_data[2]),
                    "price_yearly": float(tier_data[3]),
                    "features": json.loads(tier_data[4]) if tier_data[4] else {},
                    "limits": json.loads(tier_data[5]) if tier_data[5] else {},
                    "description": tier_data[6]
                }
                
                conn.close()
                return tier_info
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Get tier info error: {e}")
            return None
    
    def get_user_services(self, user_id: int) -> List[Dict]:
        """Get all services for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT us.service_name, us.is_enabled, us.usage_count, 
                       us.usage_limit, us.last_used, us.expires_at,
                       s.display_name, s.description, s.category, s.per_use_cost
                FROM user_services us
                JOIN services s ON us.service_name = s.name
                WHERE us.user_id = ?
            """, (user_id,))
            
            services = []
            for row in cursor.fetchall():
                service = {
                    "name": row[0],
                    "is_enabled": bool(row[1]),
                    "usage_count": row[2],
                    "usage_limit": row[3],
                    "last_used": row[4],
                    "expires_at": row[5],
                    "display_name": row[6],
                    "description": row[7],
                    "category": row[8],
                    "per_use_cost": float(row[9]) if row[9] else 0.0
                }
                services.append(service)
            
            conn.close()
            return services
            
        except Exception as e:
            logger.error(f"Get user services error: {e}")
            return []
    
    def check_service_access(self, user_id: int, service_name: str) -> Dict[str, Any]:
        """Check if user has access to a service"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user service info
            cursor.execute("""
                SELECT us.is_enabled, us.usage_count, us.usage_limit, us.expires_at,
                       u.subscription_tier, u.credits_remaining
                FROM user_services us
                JOIN users u ON us.user_id = u.id
                WHERE us.user_id = ? AND us.service_name = ?
            """, (user_id, service_name))
            
            service_data = cursor.fetchone()
            
            if not service_data:
                return {"has_access": False, "reason": "Service not found"}
            
            is_enabled, usage_count, usage_limit, expires_at, tier, credits = service_data
            
            # Check if service is enabled
            if not is_enabled:
                return {"has_access": False, "reason": "Service disabled"}
            
            # Check expiration
            if expires_at and datetime.fromisoformat(expires_at) < datetime.now():
                return {"has_access": False, "reason": "Service expired"}
            
            # Check usage limit
            if usage_limit > 0 and usage_count >= usage_limit:
                return {"has_access": False, "reason": "Usage limit exceeded"}
            
            # Check credits for paid services
            cursor.execute("SELECT per_use_cost FROM services WHERE name = ?", (service_name,))
            cost_data = cursor.fetchone()
            per_use_cost = float(cost_data[0]) if cost_data and cost_data[0] else 0.0
            
            if per_use_cost > 0 and credits < per_use_cost:
                return {"has_access": False, "reason": "Insufficient credits"}
            
            conn.close()
            return {
                "has_access": True,
                "usage_count": usage_count,
                "usage_limit": usage_limit,
                "remaining_uses": usage_limit - usage_count if usage_limit > 0 else -1,
                "cost": per_use_cost
            }
            
        except Exception as e:
            logger.error(f"Check service access error: {e}")
            return {"has_access": False, "reason": "System error"}
    
    def use_service(self, user_id: int, service_name: str, usage_count: int = 1, metadata: Dict = None) -> bool:
        """Record service usage and deduct credits/usage"""
        try:
            # Check access first
            access_check = self.check_service_access(user_id, service_name)
            if not access_check["has_access"]:
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get service cost
            cursor.execute("SELECT per_use_cost FROM services WHERE name = ?", (service_name,))
            cost_data = cursor.fetchone()
            per_use_cost = float(cost_data[0]) if cost_data and cost_data[0] else 0.0
            
            total_cost = per_use_cost * usage_count
            
            # Update user service usage
            cursor.execute("""
                UPDATE user_services 
                SET usage_count = usage_count + ?, last_used = ?
                WHERE user_id = ? AND service_name = ?
            """, (usage_count, datetime.now(), user_id, service_name))
            
            # Deduct credits if applicable
            if total_cost > 0:
                cursor.execute("""
                    UPDATE users 
                    SET credits_remaining = credits_remaining - ?,
                        monthly_usage = monthly_usage + ?
                    WHERE id = ?
                """, (total_cost, total_cost, user_id))
            
            # Log usage
            cursor.execute("""
                INSERT INTO usage_logs (user_id, service_name, usage_type, 
                                      usage_count, cost, metadata)
                VALUES (?, ?, 'service_use', ?, ?, ?)
            """, (user_id, service_name, usage_count, total_cost, 
                  json.dumps(metadata) if metadata else None))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Use service error: {e}")
            return False
    
    def _initialize_user_services(self, cursor, user_id: int, subscription_tier: str):
        """Initialize services for a new user based on their tier"""
        # Get tier features
        cursor.execute("""
            SELECT features FROM subscription_tiers WHERE name = ?
        """, (subscription_tier,))
        
        tier_data = cursor.fetchone()
        if not tier_data:
            return
        
        features = json.loads(tier_data[0]) if tier_data[0] else {}
        
        # Get all services
        cursor.execute("SELECT name, required_tier FROM services WHERE is_active = 1")
        all_services = cursor.fetchall()
        
        tier_hierarchy = {"free": 0, "basic": 1, "pro": 2, "enterprise": 3}
        user_tier_level = tier_hierarchy.get(subscription_tier, 0)
        
        for service_name, required_tier in all_services:
            required_tier_level = tier_hierarchy.get(required_tier, 0)
            
            # Enable service if user's tier is high enough
            is_enabled = user_tier_level >= required_tier_level
            
            # Set usage limits based on tier
            usage_limit = -1  # Unlimited by default
            if subscription_tier == "free":
                usage_limit = 50 if "basic" in service_name else 10
            elif subscription_tier == "basic":
                usage_limit = 500 if "enhanced" in service_name else 100
            
            cursor.execute("""
                INSERT INTO user_services (user_id, service_name, is_enabled, usage_limit)
                VALUES (?, ?, ?, ?)
            """, (user_id, service_name, is_enabled, usage_limit))
    
    def upgrade_user_subscription(self, user_id: int, new_tier: str) -> bool:
        """Upgrade user subscription tier"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update user tier
            cursor.execute("""
                UPDATE users 
                SET subscription_tier = ?, 
                    billing_cycle_start = ?,
                    billing_cycle_end = ?
                WHERE id = ?
            """, (new_tier, datetime.now().date(), 
                  (datetime.now() + timedelta(days=30)).date(), user_id))
            
            # Remove old services
            cursor.execute("DELETE FROM user_services WHERE user_id = ?", (user_id,))
            
            # Initialize new services
            self._initialize_user_services(cursor, user_id, new_tier)
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Upgrade subscription error: {e}")
            return False
    
    def get_all_tiers(self) -> List[Dict]:
        """Get all available subscription tiers"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name, display_name, price_monthly, price_yearly,
                       features, limits, description
                FROM subscription_tiers WHERE is_active = 1
                ORDER BY price_monthly ASC
            """)
            
            tiers = []
            for row in cursor.fetchall():
                tier = {
                    "name": row[0],
                    "display_name": row[1],
                    "price_monthly": float(row[2]),
                    "price_yearly": float(row[3]),
                    "features": json.loads(row[4]) if row[4] else {},
                    "limits": json.loads(row[5]) if row[5] else {},
                    "description": row[6]
                }
                tiers.append(tier)
            
            conn.close()
            return tiers
            
        except Exception as e:
            logger.error(f"Get all tiers error: {e}")
            return []
    
    def get_user_usage_stats(self, user_id: int) -> Dict:
        """Get user usage statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current month usage
            current_month = datetime.now().strftime("%Y-%m")
            
            cursor.execute("""
                SELECT service_name, SUM(usage_count), SUM(cost)
                FROM usage_logs 
                WHERE user_id = ? AND strftime('%Y-%m', timestamp) = ?
                GROUP BY service_name
            """, (user_id, current_month))
            
            monthly_usage = {}
            total_cost = 0
            
            for row in cursor.fetchall():
                service_name, usage_count, cost = row
                monthly_usage[service_name] = {
                    "usage_count": usage_count,
                    "cost": float(cost) if cost else 0.0
                }
                total_cost += float(cost) if cost else 0.0
            
            # Get user limits
            user = self.get_user_by_id(user_id)
            tier_limits = user["tier_info"]["limits"] if user and user["tier_info"] else {}
            
            conn.close()
            
            return {
                "monthly_usage": monthly_usage,
                "total_monthly_cost": total_cost,
                "tier_limits": tier_limits,
                "credits_remaining": user["credits_remaining"] if user else 0
            }
            
        except Exception as e:
            logger.error(f"Get usage stats error: {e}")
            return {}

# Global instance
user_manager = UserManager()
