#!/usr/bin/env python3
"""
Direct API test for Enhanced PDF Processing System
"""

import requests
import json

def test_all_endpoints():
    """Test various endpoints to see what's available"""
    base_url = "http://localhost:52047"
    
    endpoints = [
        "/api/",
        "/api/auth/",
        "/api/auth/login",
        "/api/pdf/",
        "/",
    ]
    
    print("Testing available endpoints:")
    for endpoint in endpoints:
        try:
            # Try GET first
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"GET {endpoint}: {response.status_code}")
            
            # Try POST for login
            if "login" in endpoint:
                login_data = {
                    "username": "demo@example.com",
                    "password": "Akanksha100991!"
                }
                response = requests.post(f"{base_url}{endpoint}", json=login_data, timeout=5)
                print(f"POST {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"  Response: {data}")
                    
        except Exception as e:
            print(f"{endpoint}: ERROR - {e}")
    
    print("\nTesting simple endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"Root endpoint: {response.status_code}")
        if response.status_code == 200:
            print("Frontend is accessible!")
    except Exception as e:
        print(f"Root endpoint error: {e}")

if __name__ == "__main__":
    test_all_endpoints()
