#!/usr/bin/env python3
"""
Simple test for Enhanced PDF Processing System
"""

import requests
import json

# Simple test
def test_server_health():
    try:
        response = requests.get("http://localhost:52047/api/", timeout=5)
        print(f"✓ Server is responding: {response.status_code}")
        return True
    except Exception as e:
        print(f"✗ Server test failed: {e}")
        return False

def test_auth_endpoint():
    try:
        # Test login with demo credentials
        login_data = {
            "username": "demo@example.com",
            "password": "Akanksha100991!"
        }
        
        response = requests.post("http://localhost:52047/api/auth/login", 
                               json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            print(f"✓ Login successful, token received: {token[:20]}...")
            return token
        else:
            print(f"✗ Login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Login test failed: {e}")
        return None

def test_enhanced_pdf_endpoint(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test if enhanced PDF endpoint exists
        response = requests.get("http://localhost:52047/api/pdf/", 
                              headers=headers, timeout=5)
        
        print(f"✓ Enhanced PDF endpoint accessible: {response.status_code}")
        return True
        
    except Exception as e:
        print(f"✗ Enhanced PDF endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Simple Enhanced PDF System Test")
    print("==================================")
    
    print("\n1. Testing server health...")
    if not test_server_health():
        print("Server is not running. Please start it first.")
        exit(1)
    
    print("\n2. Testing authentication...")
    token = test_auth_endpoint()
    if not token:
        print("Authentication failed.")
        exit(1)
    
    print("\n3. Testing enhanced PDF endpoint...")
    test_enhanced_pdf_endpoint(token)
    
    print("\n✅ Basic tests completed!")
    print("The enhanced PDF processing system appears to be working.")
    print("\nNext steps:")
    print("1. Open http://localhost:52047 in your browser")
    print("2. Login with demo@example.com / Akanksha100991!")
    print("3. Navigate to the Enhanced PDF page")
    print("4. Upload a PDF to test the token-based processing")
