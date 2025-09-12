"""
Frontend Registration Component for Service-Based Authentication
"""

import datetime
from typing import Dict, List

class FrontendServiceDashboard:
    """Generate HTML dashboard for user services"""
    
    @staticmethod
    def generate_login_page() -> str:
        """Generate modern login page with service features"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced PDF RAG - Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .auth-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            width: 100%;
            max-width: 500px;
            margin: 20px;
        }
        
        .auth-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .auth-header h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .auth-header p {
            color: #666;
            font-size: 1.1em;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        
        .form-group input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e1e1;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus {
            border-color: #667eea;
            outline: none;
        }
        
        .auth-button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .auth-button:hover {
            transform: translateY(-2px);
        }
        
        .auth-switch {
            text-align: center;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e1e1e1;
        }
        
        .auth-switch a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        
        .error-message {
            background: #fee;
            color: #c33;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .tier-selection {
            margin: 20px 0;
        }
        
        .tier-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }
        
        .tier-option {
            padding: 10px;
            border: 2px solid #e1e1e1;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .tier-option:hover, .tier-option.selected {
            border-color: #667eea;
            background: #f8f9ff;
        }
        
        .tier-name {
            font-weight: 600;
            color: #333;
        }
        
        .tier-price {
            font-size: 0.9em;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="auth-container">
        <div class="auth-header">
            <h1>Enhanced PDF RAG</h1>
            <p>AI-Powered Document Analysis Platform</p>
        </div>
        
        <div id="error-message" class="error-message" style="display: none;"></div>
        
        <form id="auth-form">
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <div id="register-fields" style="display: none;">
                <div class="form-group">
                    <label for="name">Full Name</label>
                    <input type="text" id="name" name="name">
                </div>
                
                <div class="tier-selection">
                    <label>Choose Your Plan</label>
                    <div class="tier-grid">
                        <div class="tier-option selected" data-tier="free">
                            <div class="tier-name">Free</div>
                            <div class="tier-price">$0/month</div>
                        </div>
                        <div class="tier-option" data-tier="basic">
                            <div class="tier-name">Basic</div>
                            <div class="tier-price">$9.99/month</div>
                        </div>
                        <div class="tier-option" data-tier="pro">
                            <div class="tier-name">Pro</div>
                            <div class="tier-price">$29.99/month</div>
                        </div>
                        <div class="tier-option" data-tier="enterprise">
                            <div class="tier-name">Enterprise</div>
                            <div class="tier-price">$99.99/month</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <button type="submit" class="auth-button" id="auth-submit">Login</button>
        </form>
        
        <div class="auth-switch">
            <a href="#" id="auth-switch-link">Don't have an account? Register here</a>
        </div>
    </div>

    <script>
        let isLoginMode = true;
        let selectedTier = 'free';
        
        const authForm = document.getElementById('auth-form');
        const authSubmit = document.getElementById('auth-submit');
        const authSwitchLink = document.getElementById('auth-switch-link');
        const registerFields = document.getElementById('register-fields');
        const errorMessage = document.getElementById('error-message');
        const tierOptions = document.querySelectorAll('.tier-option');
        
        // Tier selection
        tierOptions.forEach(option => {
            option.addEventListener('click', () => {
                tierOptions.forEach(opt => opt.classList.remove('selected'));
                option.classList.add('selected');
                selectedTier = option.dataset.tier;
            });
        });
        
        // Switch between login and register
        authSwitchLink.addEventListener('click', (e) => {
            e.preventDefault();
            isLoginMode = !isLoginMode;
            
            if (isLoginMode) {
                authSubmit.textContent = 'Login';
                authSwitchLink.textContent = "Don't have an account? Register here";
                registerFields.style.display = 'none';
            } else {
                authSubmit.textContent = 'Register';
                authSwitchLink.textContent = 'Already have an account? Login here';
                registerFields.style.display = 'block';
            }
        });
        
        // Get API base URL from environment or default
        const API_BASE_URL = window.location.hostname === 'localhost' 
            ? `${window.location.protocol}//${window.location.host}`
            : `${window.location.protocol}//api.${window.location.hostname.replace('app.', '')}`;
        
        const APP_BASE_URL = window.location.hostname === 'localhost'
            ? `${window.location.protocol}//${window.location.host}`
            : `${window.location.protocol}//app.${window.location.hostname.replace('api.', '')}`;

        // Form submission
        authForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(authForm);
            const email = formData.get('email');
            const password = formData.get('password');
            const name = formData.get('name');
            
            const endpoint = isLoginMode ? '/api/login' : '/api/register';
            const data = isLoginMode 
                ? { email, password }
                : { email, password, name, subscription_tier: selectedTier };
            
            try {
                authSubmit.disabled = true;
                authSubmit.textContent = isLoginMode ? 'Logging in...' : 'Registering...';
                
                const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    // Store token and redirect to dashboard
                    localStorage.setItem('token', result.token);
                    localStorage.setItem('user', JSON.stringify(result.user));
                    window.location.href = `${APP_BASE_URL}/dashboard`;
                } else {
                    showError(result.error || 'Authentication failed');
                }
            } catch (error) {
                showError('Network error. Please try again.');
            } finally {
                authSubmit.disabled = false;
                authSubmit.textContent = isLoginMode ? 'Login' : 'Register';
            }
        });
        
        function showError(message) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 5000);
        }
        
        // Auto-redirect if already logged in
        if (localStorage.getItem('token')) {
            window.location.href = `${APP_BASE_URL}/dashboard`;
        }
    </script>
</body>
</html>
        """
        
    @staticmethod
    def generate_dashboard_page() -> str:
        """Generate service dashboard page"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced PDF RAG - Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
        }
        
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.8em;
            font-weight: 600;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .user-details {
            text-align: right;
        }
        
        .user-name {
            font-weight: 600;
        }
        
        .user-tier {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .logout-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .logout-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .dashboard-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-title {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: 600;
            color: #333;
        }
        
        .services-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }
        
        .section-title {
            font-size: 1.5em;
            color: #333;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .service-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .service-card {
            border: 2px solid #e1e1e1;
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s;
        }
        
        .service-card.enabled {
            border-color: #4CAF50;
            background: #f8fff8;
        }
        
        .service-card.disabled {
            border-color: #f44336;
            background: #fff8f8;
            opacity: 0.7;
        }
        
        .service-card.limited {
            border-color: #ff9800;
            background: #fff8f0;
        }
        
        .service-header {
            display: flex;
            justify-content: between;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        
        .service-name {
            font-weight: 600;
            color: #333;
            font-size: 1.1em;
        }
        
        .service-status {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 500;
            text-transform: uppercase;
        }
        
        .status-enabled {
            background: #4CAF50;
            color: white;
        }
        
        .status-disabled {
            background: #f44336;
            color: white;
        }
        
        .status-limited {
            background: #ff9800;
            color: white;
        }
        
        .usage-info {
            display: flex;
            justify-content: space-between;
            margin-top: 10px;
            font-size: 0.9em;
            color: #666;
        }
        
        .usage-bar {
            width: 100%;
            height: 6px;
            background: #e1e1e1;
            border-radius: 3px;
            margin: 10px 0;
            overflow: hidden;
        }
        
        .usage-fill {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #45a049);
            transition: width 0.3s;
        }
        
        .upgrade-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            margin-bottom: 30px;
        }
        
        .upgrade-title {
            font-size: 1.8em;
            margin-bottom: 15px;
        }
        
        .upgrade-description {
            font-size: 1.1em;
            margin-bottom: 25px;
            opacity: 0.9;
        }
        
        .tier-comparison {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .tier-card {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s;
            cursor: pointer;
        }
        
        .tier-card:hover {
            transform: scale(1.05);
        }
        
        .tier-card.current {
            background: rgba(255,255,255,0.2);
            border: 2px solid rgba(255,255,255,0.5);
        }
        
        .tier-name {
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .tier-price {
            font-size: 1.5em;
            font-weight: 700;
            margin-bottom: 15px;
        }
        
        .tier-features {
            list-style: none;
            font-size: 0.9em;
        }
        
        .tier-features li {
            margin: 5px 0;
            opacity: 0.9;
        }
        
        .action-button {
            background: white;
            color: #667eea;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin: 10px;
        }
        
        .action-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .pdf-tools {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }
        
        .tool-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .tool-card {
            border: 2px solid #e1e1e1;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .tool-card:hover {
            border-color: #667eea;
            transform: translateY(-5px);
        }
        
        .tool-icon {
            font-size: 3em;
            margin-bottom: 15px;
        }
        
        .tool-name {
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 10px;
            color: #333;
        }
        
        .tool-description {
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="dashboard-header">
        <div class="header-content">
            <div class="logo">Enhanced PDF RAG</div>
            <div class="user-info">
                <div class="user-details">
                    <div class="user-name" id="user-name">Loading...</div>
                    <div class="user-tier" id="user-tier">Loading...</div>
                </div>
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>
        </div>
    </div>
    
    <div class="dashboard-container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-title">Credits Remaining</div>
                <div class="stat-value" id="credits-remaining">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Services Active</div>
                <div class="stat-value" id="services-active">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">This Month Usage</div>
                <div class="stat-value" id="monthly-usage">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Documents Processed</div>
                <div class="stat-value" id="docs-processed">-</div>
            </div>
        </div>
        
        <div class="services-section">
            <h2 class="section-title">
                🛠️ Your Services
            </h2>
            <div id="services-grid" class="service-grid">
                <!-- Services will be loaded here -->
            </div>
        </div>
        
        <div id="upgrade-section" class="upgrade-section" style="display: none;">
            <h2 class="upgrade-title">Upgrade Your Plan</h2>
            <p class="upgrade-description">Unlock more features and higher usage limits</p>
            <div class="tier-comparison" id="tier-comparison">
                <!-- Tier cards will be loaded here -->
            </div>
        </div>
        
        <div class="pdf-tools">
            <h2 class="section-title">
                📄 PDF Tools
            </h2>
            <div class="tool-grid">
                <div class="tool-card" onclick="openTool('upload')">
                    <div class="tool-icon">📤</div>
                    <div class="tool-name">Upload PDF</div>
                    <div class="tool-description">Upload and process your PDF documents</div>
                </div>
                <div class="tool-card" onclick="openTool('search')">
                    <div class="tool-icon">🔍</div>
                    <div class="tool-name">Search Documents</div>
                    <div class="tool-description">Search through your processed PDFs</div>
                </div>
                <div class="tool-card" onclick="openTool('ai-analysis')">
                    <div class="tool-icon">🤖</div>
                    <div class="tool-name">AI Analysis</div>
                    <div class="tool-description">Get AI-powered insights from your documents</div>
                </div>
                <div class="tool-card" onclick="openTool('line-seek')">
                    <div class="tool-icon">🎯</div>
                    <div class="tool-name">Line Seeking</div>
                    <div class="tool-description">Find specific lines and references</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let userProfile = null;
        let availableTiers = null;
        
        // Get API and APP URLs
        const API_BASE_URL = window.location.hostname === 'localhost' 
            ? `${window.location.protocol}//${window.location.host}`
            : `${window.location.protocol}//api.${window.location.hostname.replace('app.', '')}`;
        
        const APP_BASE_URL = window.location.hostname === 'localhost'
            ? `${window.location.protocol}//${window.location.host}`
            : `${window.location.protocol}//app.${window.location.hostname.replace('api.', '')}`;

        // Load user profile and services
        async function loadDashboard() {
            const token = localStorage.getItem('token');
            if (!token) {
                window.location.href = `${APP_BASE_URL}/login`;
                return;
            }
            
            try {
                // Load user profile
                const profileResponse = await fetch(`${API_BASE_URL}/api/profile`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (profileResponse.ok) {
                    userProfile = await profileResponse.json();
                    updateUserInterface();
                } else {
                    throw new Error('Failed to load profile');
                }
                
                // Load available tiers
                const tiersResponse = await fetch(`${API_BASE_URL}/api/tiers`);
                if (tiersResponse.ok) {
                    const tiersData = await tiersResponse.json();
                    availableTiers = tiersData.tiers;
                    updateTierComparison();
                }
                
            } catch (error) {
                console.error('Dashboard load error:', error);
                if (error.message.includes('401')) {
                    localStorage.removeItem('token');
                    window.location.href = `${APP_BASE_URL}/login`;
                }
            }
        }
        
        function updateUserInterface() {
            const userInfo = userProfile.user_info;
            
            // Update header
            document.getElementById('user-name').textContent = userInfo.name;
            document.getElementById('user-tier').textContent = `${userInfo.subscription_tier.toUpperCase()} Plan`;
            
            // Update stats
            document.getElementById('credits-remaining').textContent = userInfo.credits_remaining;
            
            const servicesActive = Object.values(userProfile.services_by_category || {})
                .flat()
                .filter(service => service.is_enabled).length;
            document.getElementById('services-active').textContent = servicesActive;
            
            // Update usage stats
            const stats = userProfile.usage_stats || {};
            document.getElementById('monthly-usage').textContent = stats.total_usage || 0;
            document.getElementById('docs-processed').textContent = stats.documents_processed || 0;
            
            // Update services grid
            updateServicesGrid();
            
            // Show upgrade section if not on highest tier
            if (userInfo.subscription_tier !== 'enterprise') {
                document.getElementById('upgrade-section').style.display = 'block';
            }
        }
        
        function updateServicesGrid() {
            const servicesGrid = document.getElementById('services-grid');
            servicesGrid.innerHTML = '';
            
            const servicesByCategory = userProfile.services_by_category || {};
            
            Object.entries(servicesByCategory).forEach(([category, services]) => {
                services.forEach(service => {
                    const serviceCard = createServiceCard(service);
                    servicesGrid.appendChild(serviceCard);
                });
            });
        }
        
        function createServiceCard(service) {
            const card = document.createElement('div');
            card.className = `service-card ${service.is_enabled ? 'enabled' : 'disabled'}`;
            
            const usagePercentage = service.usage_limit > 0 
                ? (service.usage_count / service.usage_limit) * 100 
                : 0;
            
            const statusClass = service.is_enabled 
                ? (usagePercentage > 80 ? 'limited' : 'enabled')
                : 'disabled';
            
            card.innerHTML = `
                <div class="service-header">
                    <div class="service-name">${service.display_name}</div>
                    <div class="service-status status-${statusClass}">
                        ${service.is_enabled ? (usagePercentage > 80 ? 'Limited' : 'Active') : 'Disabled'}
                    </div>
                </div>
                <div class="usage-info">
                    <span>Used: ${service.usage_count}</span>
                    <span>Limit: ${service.usage_limit > 0 ? service.usage_limit : '∞'}</span>
                </div>
                ${service.usage_limit > 0 ? `
                    <div class="usage-bar">
                        <div class="usage-fill" style="width: ${Math.min(usagePercentage, 100)}%"></div>
                    </div>
                ` : ''}
                <div style="margin-top: 10px; font-size: 0.9em; color: #666;">
                    Cost per use: $${service.cost_per_use}
                </div>
            `;
            
            return card;
        }
        
        function updateTierComparison() {
            if (!availableTiers) return;
            
            const tierComparison = document.getElementById('tier-comparison');
            tierComparison.innerHTML = '';
            
            availableTiers.forEach(tier => {
                const tierCard = createTierCard(tier);
                tierComparison.appendChild(tierCard);
            });
        }
        
        function createTierCard(tier) {
            const card = document.createElement('div');
            const isCurrent = userProfile?.user_info?.subscription_tier === tier.name;
            card.className = `tier-card ${isCurrent ? 'current' : ''}`;
            
            card.innerHTML = `
                <div class="tier-name">${tier.display_name}</div>
                <div class="tier-price">$${tier.price}/month</div>
                <ul class="tier-features">
                    <li>${tier.monthly_credits} credits/month</li>
                    <li>${tier.description}</li>
                </ul>
                ${!isCurrent ? `
                    <button class="action-button" onclick="upgradeTier('${tier.name}')">
                        Upgrade
                    </button>
                ` : '<div style="padding: 12px; color: rgba(255,255,255,0.8);">Current Plan</div>'}
            `;
            
            return card;
        }
        
        async function upgradeTier(tierName) {
            const token = localStorage.getItem('token');
            
            try {
                const response = await fetch(`${API_BASE_URL}/api/upgrade`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ tier: tierName })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    alert(`Successfully upgraded to ${tierName} plan!`);
                    loadDashboard(); // Reload dashboard
                } else {
                    alert(`Upgrade failed: ${result.error}`);
                }
            } catch (error) {
                alert('Network error during upgrade');
            }
        }
        
        function openTool(tool) {
            // Implement tool navigation
            switch (tool) {
                case 'upload':
                    window.location.href = '/upload';
                    break;
                case 'search':
                    window.location.href = '/search';
                    break;
                case 'ai-analysis':
                    window.location.href = '/analysis';
                    break;
                case 'line-seek':
                    window.location.href = '/line-seek';
                    break;
            }
        }
        
        function logout() {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = `${APP_BASE_URL}/login`;
        }
        
        // Load dashboard on page load
        document.addEventListener('DOMContentLoaded', loadDashboard);
    </script>
</body>
</html>
        """

# Static endpoints for serving the frontend
async def serve_login_page(request):
    """Serve the login page"""
    return web.Response(
        text=FrontendServiceDashboard.generate_login_page(),
        content_type='text/html'
    )

async def serve_dashboard_page(request):
    """Serve the dashboard page"""
    return web.Response(
        text=FrontendServiceDashboard.generate_dashboard_page(),
        content_type='text/html'
    )
