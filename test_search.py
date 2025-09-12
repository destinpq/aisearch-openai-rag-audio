#!/usr/bin/env python3

import requests
import json
import os

# Get the auth token first
login_url = "http://localhost:8765/api/login"
login_data = {"username": "demo@example.com", "password": "Akanksha100991!"}

print("🔐 Getting authentication token...")
response = requests.post(login_url, json=login_data)
if response.status_code != 200:
    print(f"❌ Login failed: {response.status_code}")
    exit(1)

token = response.json()["token"]
headers = {"Authorization": f"Bearer {token}"}
print("✅ Authentication successful!")

# List uploaded files
print("\n📁 Checking uploaded files...")
files_response = requests.get("http://localhost:8765/api/files", headers=headers)
print(f"Files API Status: {files_response.status_code}")
if files_response.status_code == 200:
    files_data = files_response.json()
    files = files_data.get("files", [])
    print(f"📋 Found {len(files)} uploaded files:")
    for file in files:
        print(f"   - {file['filename']} ({file['size']} bytes)")
else:
    print(f"❌ Failed to get files: {files_response.text}")

# List indexed PDFs
print("\n🔍 Checking indexed PDFs...")
indexed_response = requests.get("http://localhost:8765/api/indexed-pdfs", headers=headers)
print(f"Indexed PDFs API Status: {indexed_response.status_code}")
if indexed_response.status_code == 200:
    indexed_data = indexed_response.json()
    indexed_pdfs = indexed_data.get("indexed_pdfs", [])
    print(f"📚 Found {len(indexed_pdfs)} indexed PDFs:")
    for pdf in indexed_pdfs:
        print(f"   - {pdf}")
else:
    print(f"❌ Failed to get indexed PDFs: {indexed_response.text}")

# Test a physics search
print("\n🔬 Testing physics search...")
search_data = {
    "query": "physics energy momentum force",
    "filename": "user_uploaded"  # Search only in user's uploaded documents
}
search_response = requests.post("http://localhost:8765/api/analyze", headers=headers, json=search_data)
print(f"Search API Status: {search_response.status_code}")
if search_response.status_code == 200:
    search_results = search_response.json()
    results = search_results.get("results", [])
    print(f"🎯 Found {len(results)} search results:")
    for i, result in enumerate(results[:3]):  # Show first 3 results
        print(f"   {i+1}. {result.get('title', 'No title')}")
        print(f"      File: {result.get('filename', 'Unknown')}")
        print(f"      Lines: {result.get('line_reference', 'N/A')}")
        print(f"      Content: {result.get('content', '')[:100]}...")
        print()
else:
    print(f"❌ Search failed: {search_response.text}")
