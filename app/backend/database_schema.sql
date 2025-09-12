-- Enhanced User Management Schema with Service Tiers
-- This creates a complete user system with feature-based services

-- Users table with subscription tiers
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    subscription_tier TEXT DEFAULT 'free',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    email_verified BOOLEAN DEFAULT 0,
    credits_remaining INTEGER DEFAULT 0,
    monthly_usage INTEGER DEFAULT 0,
    billing_cycle_start DATE,
    billing_cycle_end DATE
);

-- Subscription tiers with limits
CREATE TABLE IF NOT EXISTS subscription_tiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    price_monthly DECIMAL(10,2) DEFAULT 0.00,
    price_yearly DECIMAL(10,2) DEFAULT 0.00,
    features TEXT, -- JSON string of features
    limits TEXT, -- JSON string of limits
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User services/features
CREATE TABLE IF NOT EXISTS user_services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    service_name TEXT NOT NULL,
    is_enabled BOOLEAN DEFAULT 1,
    usage_count INTEGER DEFAULT 0,
    usage_limit INTEGER DEFAULT -1, -- -1 means unlimited
    last_used TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE(user_id, service_name)
);

-- Available services
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    base_cost DECIMAL(10,2) DEFAULT 0.00,
    per_use_cost DECIMAL(10,2) DEFAULT 0.00,
    category TEXT DEFAULT 'general',
    is_active BOOLEAN DEFAULT 1,
    required_tier TEXT DEFAULT 'free',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usage tracking
CREATE TABLE IF NOT EXISTS usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    service_name TEXT NOT NULL,
    usage_type TEXT NOT NULL,
    usage_count INTEGER DEFAULT 1,
    cost DECIMAL(10,2) DEFAULT 0.00,
    metadata TEXT, -- JSON for additional data
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Billing and payments
CREATE TABLE IF NOT EXISTS billing_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    status TEXT DEFAULT 'pending',
    payment_method TEXT,
    transaction_id TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Insert default subscription tiers
INSERT OR REPLACE INTO subscription_tiers (name, display_name, price_monthly, price_yearly, features, limits, description) VALUES 
('free', 'Free Tier', 0.00, 0.00, 
 '{"basic_pdf_upload": true, "basic_search": true, "document_limit": 5, "search_limit": 50}',
 '{"pdf_uploads_per_month": 5, "searches_per_month": 50, "storage_mb": 100, "api_calls_per_day": 20}',
 'Perfect for trying out the system with basic features'),
 
('basic', 'Basic Plan', 9.99, 99.00,
 '{"pdf_upload": true, "enhanced_search": true, "line_numbers": true, "basic_analytics": true}',
 '{"pdf_uploads_per_month": 50, "searches_per_month": 500, "storage_mb": 1000, "api_calls_per_day": 200}',
 'Great for individual users with regular PDF processing needs'),
 
('pro', 'Professional', 29.99, 299.00,
 '{"pdf_upload": true, "enhanced_search": true, "line_numbers": true, "live_data": true, "image_analysis": true, "api_access": true}',
 '{"pdf_uploads_per_month": 200, "searches_per_month": 2000, "storage_mb": 5000, "api_calls_per_day": 1000}',
 'Perfect for professionals with advanced AI enhancement needs'),
 
('enterprise', 'Enterprise', 99.99, 999.00,
 '{"pdf_upload": true, "enhanced_search": true, "line_numbers": true, "live_data": true, "image_analysis": true, "api_access": true, "priority_support": true, "custom_integrations": true}',
 '{"pdf_uploads_per_month": -1, "searches_per_month": -1, "storage_mb": -1, "api_calls_per_day": -1}',
 'Unlimited access with priority support and custom features');

-- Insert default services
INSERT OR REPLACE INTO services (name, display_name, description, base_cost, per_use_cost, category, required_tier) VALUES 
('basic_pdf_upload', 'Basic PDF Upload', 'Upload and process PDF files with basic text extraction', 0.00, 0.00, 'core', 'free'),
('enhanced_pdf_upload', 'Enhanced PDF Upload', 'Advanced PDF processing with token-based analysis', 0.00, 0.05, 'advanced', 'basic'),
('basic_search', 'Basic Search', 'Search through your uploaded documents', 0.00, 0.00, 'core', 'free'),
('enhanced_search', 'Enhanced Search', 'Advanced search with precise line number tracking', 0.00, 0.01, 'advanced', 'basic'),
('line_number_tracking', 'Line Number Tracking', 'Precise line number and position tracking', 0.00, 0.02, 'advanced', 'basic'),
('live_data_enhancement', 'Live Data Enhancement', 'Real-time information enhancement using Perplexity API', 0.00, 0.10, 'ai', 'pro'),
('image_analysis', 'Image Analysis', 'AI-powered image analysis in PDFs using OpenAI Vision', 0.00, 0.15, 'ai', 'pro'),
('api_access', 'API Access', 'Programmatic access to all features', 0.00, 0.00, 'developer', 'pro'),
('priority_support', 'Priority Support', '24/7 priority customer support', 0.00, 0.00, 'support', 'enterprise'),
('custom_integrations', 'Custom Integrations', 'Custom API integrations and webhooks', 0.00, 0.00, 'enterprise', 'enterprise');

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_subscription_tier ON users(subscription_tier);
CREATE INDEX IF NOT EXISTS idx_user_services_user_id ON user_services(user_id);
CREATE INDEX IF NOT EXISTS idx_user_services_service_name ON user_services(service_name);
CREATE INDEX IF NOT EXISTS idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_timestamp ON usage_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_billing_history_user_id ON billing_history(user_id);
