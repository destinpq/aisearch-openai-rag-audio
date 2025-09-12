#!/usr/bin/env python3

import requests
import json

# Get the auth token first
login_url = "http://localhost:8765/api/login"
login_data = {"username": "demo@example.com", "password": "Akanksha100991!"}

print("🔐 Getting authentication token...")
response = requests.post(login_url, json=login_data)
token = response.json()["token"]
headers = {"Authorization": f"Bearer {token}"}
print("✅ Authentication successful!")

# Manually trigger indexing of existing files
print("\n📚 Indexing existing files...")
index_response = requests.post("http://localhost:8765/api/index-existing", headers=headers)
print(f"Indexing API Status: {index_response.status_code}")
if index_response.status_code == 200:
    index_data = index_response.json()
    results = index_data.get("results", [])
    print(f"📋 Indexing results:")
    for result in results:
        filename = result['filename']
        indexed = result['indexed']
        status = "✅" if indexed else "❌"
        print(f"   {status} {filename}")
else:
    print(f"❌ Failed to trigger indexing: {index_response.text}")

# Test physics search
print("\n🔬 Testing physics search...")
search_queries = [
    "energy momentum force",
    "Newton laws of motion", 
    "kinetic energy",
    "physics concepts"
]

for query in search_queries:
    print(f"\n🔍 Searching for: '{query}'")
    search_data = {"query": query}
    search_response = requests.post("http://localhost:8765/api/analyze", headers=headers, json=search_data)
    
    if search_response.status_code == 200:
        search_results = search_response.json()
        results = search_results.get("results", [])
        print(f"   📊 Found {len(results)} results")
        
        for i, result in enumerate(results[:2]):  # Show first 2 results
            print(f"   {i+1}. {result.get('title', 'No title')}")
            print(f"      File: {result.get('filename', 'Unknown')}")
            print(f"      Content: {result.get('content', '')[:150]}...")
    else:
        print(f"   ❌ Search failed: {search_response.status_code}")
    
    if len(search_queries) > 1 and query != search_queries[-1]:
        print("   " + "-"*50)
