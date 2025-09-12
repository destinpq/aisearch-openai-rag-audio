# API Integration Guide for Existing Frontend

## 🎯 BACKEND-ONLY INTEGRATION COMPLETE

Your existing frontend at **https://converse.destinpq.com** will continue to work exactly as before with enhanced service-based features available.

## 🔌 API Endpoint Changes

### Authentication Endpoints (Enhanced - Same Interface)

```javascript
// Login endpoint remains the same but now returns tier info
POST /api/login
{
  "username": "user@example.com",
  "password": "password"
}

// Response now includes tier information:
{
  "token": "jwt_token_here",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "tier": "Pro",
    "credits": 1500,
    "services": ["pdf_upload", "ai_analysis", "enhanced_search"]
  }
}
```

### New Service-Aware Endpoints

```javascript
// Get user subscription tiers (new)
GET /api/tiers
Authorization: Bearer jwt_token_here

// Get user profile with service status (new)
GET /api/profile
Authorization: Bearer jwt_token_here

// Service-protected PDF upload (enhanced)
POST /api/pdf/upload
Authorization: Bearer jwt_token_here
Content-Type: multipart/form-data

// Service-protected AI analysis (enhanced)
POST /api/pdf/ai-analysis
Authorization: Bearer jwt_token_here
{
  "pdf_id": 123,
  "query": "Analyze this document"
}
```

### Legacy Compatibility Maintained

```javascript
// All your existing endpoints still work:
POST / api / upload; // Original PDF upload
POST / api / analyze; // Original analysis
GET / api / files; // File listing
```

## 🔐 Authentication Flow (No Changes Required)

Your existing authentication flow remains exactly the same:

```javascript
// Your existing frontend code continues to work:
const response = await fetch("/api/login", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    username: email,
    password: password,
  }),
});

const data = await response.json();
// Now data.user includes tier and services information
localStorage.setItem("token", data.token);
```

## 🌐 CORS Configuration

Backend is configured to accept requests from:

- `https://converse.destinpq.com` (your existing frontend)
- `https://destinpq.com`
- `http://localhost:52047` (development)

## 📊 Service Tiers Available

| Tier       | Price        | Credits   | Features                       |
| ---------- | ------------ | --------- | ------------------------------ |
| Free       | $0/month     | 50        | Basic PDF upload, search       |
| Basic      | $9.99/month  | 500       | Enhanced search, OCR           |
| Pro        | $29.99/month | 2000      | AI analysis, image processing  |
| Enterprise | $99.99/month | Unlimited | All features, priority support |

## 🚦 Usage Tracking

Every API call is now tracked:

- Credit consumption per request
- Service usage statistics
- User activity logs
- Billing history

## 🔧 Optional Frontend Enhancements

When you're ready, you can optionally enhance your frontend to use new features:

```javascript
// Display user tier information
const profile = await fetch("/api/profile", {
  headers: { Authorization: `Bearer ${token}` },
});
const userProfile = await profile.json();
console.log(`User tier: ${userProfile.tier}`);

// Show available tiers for upgrade
const tiers = await fetch("/api/tiers");
const availableTiers = await tiers.json();
```

## ✅ Compatibility Guarantee

- **No breaking changes** to existing API endpoints
- **Same authentication** mechanism
- **Same response formats** for legacy endpoints
- **Enhanced responses** with additional tier information
- **Full backward compatibility** maintained

## 🎉 Ready for Production

Your service-based backend is ready for:

- Commercial deployment
- User subscription management
- Usage-based billing
- Service tier enforcement
- Professional API access control

**Result: Your existing frontend works perfectly with enhanced backend capabilities!**
