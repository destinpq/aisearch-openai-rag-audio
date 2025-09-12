#!/usr/bin/env python3

import requests
import json

# Test the login endpoint
url = "http://localhost:8765/api/login"
headers = {"Content-Type": "application/json"}
data = {
    "username": "demo@example.com", 
    "password": "Akanksha100991!"
}

try:
    print("Testing login endpoint...")
    response = requests.post(url, headers=headers, json=data, timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Login successful!")
        print(f"Token: {result.get('token', 'No token')[:50]}...")
        print(f"User: {result.get('user', 'No user info')}")
    else:
        print(f"❌ Login failed: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test health endpoint
try:
    print("\nTesting health endpoint...")
    response = requests.get("http://localhost:8765/health", timeout=5)
    print(f"Health Status Code: {response.status_code}")
    print(f"Health Response: {response.text}")
except Exception as e:
    print(f"❌ Health check error: {e}")
