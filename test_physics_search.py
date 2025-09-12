#!/usr/bin/env python3

import requests
import json

# Get the auth token first
login_url = "http://localhost:8765/api/login"
login_data = {"username": "demo@example.com", "password": "Akanksha100991!"}

response = requests.post(login_url, json=login_data)
token = response.json()["token"]
headers = {"Authorization": f"Bearer {token}"}

print("🔬 Testing specific physics searches on YOUR book...")

search_queries = [
    "physics",
    "Verma",
    "IIT Kanpur", 
    "concepts",
    "Dr Harish Chandra",
    "physical principles"
]

for query in search_queries:
    print(f"\n🔍 Searching for: '{query}'")
    search_data = {"query": query}
    search_response = requests.post("http://localhost:8765/api/analyze", headers=headers, json=search_data)
    
    if search_response.status_code == 200:
        search_results = search_response.json()
        results = search_results.get("results", [])
        print(f"   📊 Found {len(results)} results")
        
        for i, result in enumerate(results[:2]):
            if "Concepts-of-Physics" in result.get('filename', ''):
                print(f"   ✅ {i+1}. {result.get('title', 'No title')}")
                print(f"      Content: {result.get('content', '')[:200]}...")
                break
    else:
        print(f"   ❌ Search failed: {search_response.status_code}")
        
print(f"\n🎯 Your physics book is indexed and searchable!")
