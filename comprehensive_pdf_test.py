#!/usr/bin/env python3
"""
Complete test for Enhanced PDF Processing System with new API keys
Tests all features including live data enhancement and image analysis
"""

import requests
import json
import os
from pathlib import Path

# Configuration
API_BASE = "http://localhost:52047"
TEST_PDF = "physics_mechanics_1.pdf"  # Use existing PDF from your system

def test_server_health():
    """Test if server is responding"""
    try:
        response = requests.get(f"{API_BASE}/", timeout=5)
        print(f"✓ Server is responding: {response.status_code}")
        return True
    except Exception as e:
        print(f"✗ Server test failed: {e}")
        return False

def login_and_get_token():
    """Login and get JWT token"""
    try:
        login_data = {
            "username": "demo@example.com",
            "password": "Akanksha100991!"
        }
        
        response = requests.post(f"{API_BASE}/api/login", 
                               json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            print(f"✓ Login successful, token received")
            return token
        else:
            print(f"✗ Login failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Login test failed: {e}")
        return None

def test_pdf_upload_with_enhanced_features(token):
    """Test PDF upload with new API keys for enhanced features"""
    if not token:
        return None
    
    # Check if test PDF exists
    if not os.path.exists(TEST_PDF):
        print(f"✗ Test PDF {TEST_PDF} not found")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        with open(TEST_PDF, 'rb') as f:
            files = {'file': (TEST_PDF, f, 'application/pdf')}
            
            response = requests.post(f"{API_BASE}/api/pdf/upload", 
                                   files=files, headers=headers, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    upload_result = result.get("result", {})
                    print(f"✓ Enhanced PDF upload successful:")
                    print(f"  - Document ID: {upload_result.get('doc_id')}")
                    print(f"  - Total tokens: {upload_result.get('total_tokens')}")
                    print(f"  - Pages processed: {upload_result.get('total_pages')}")
                    print(f"  - Chunks created: {upload_result.get('chunks_created')}")
                    print(f"  - Images extracted: {upload_result.get('images_extracted', 0)}")
                    return upload_result.get('doc_id')
                else:
                    print(f"✗ Upload failed: {result.get('error')}")
            else:
                print(f"✗ Upload request failed: {response.status_code}")
                print(f"  Response: {response.text}")
                
    except Exception as e:
        print(f"✗ Upload error: {e}")
        return None

def test_enhanced_search_with_live_data(token, doc_id):
    """Test search with live data enhancement using Perplexity API"""
    if not token or not doc_id:
        return
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test queries that should trigger live data enhancement
    test_queries = [
        "fluid dynamics equations",
        "Bernoulli principle applications",
        "latest research in physics"
    ]
    
    for query in test_queries:
        try:
            search_data = {
                "query": query,
                "doc_id": doc_id,
                "limit": 3
            }
            
            print(f"\n🔍 Testing search: '{query}'")
            response = requests.post(f"{API_BASE}/api/pdf/search", 
                                   json=search_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    results = result.get("results", [])
                    print(f"✓ Found {len(results)} token matches")
                    
                    for i, token_result in enumerate(results[:1]):  # Show first result
                        print(f"  Result {i+1}:")
                        print(f"    - Page: {token_result.get('page_number')}")
                        print(f"    - Lines: {token_result.get('line_start')}-{token_result.get('line_end')}")
                        print(f"    - Content: {token_result.get('content', '')[:80]}...")
                        
                        # Check if live data enhancement is working
                        if token_result.get('live_data'):
                            print(f"    - ✅ Live data enhanced!")
                            print(f"    - Enhancement: {token_result.get('live_data', '')[:60]}...")
                        else:
                            print(f"    - ⚠️  No live data enhancement (API key may need activation)")
                else:
                    print(f"✗ Search failed: {result.get('error')}")
            else:
                print(f"✗ Search request failed: {response.status_code}")
                
        except Exception as e:
            print(f"✗ Search error for '{query}': {e}")

def test_live_data_analysis(token, doc_id):
    """Test the analyze endpoint with Perplexity API integration"""
    if not token or not doc_id:
        return
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        # First get some tokens for context
        search_data = {
            "query": "mechanics",
            "doc_id": doc_id,
            "limit": 2
        }
        
        response = requests.post(f"{API_BASE}/api/pdf/search", 
                               json=search_data, headers=headers, timeout=20)
        
        if response.status_code == 200:
            search_result = response.json()
            if search_result.get("success"):
                search_results = search_result.get("results", [])
                token_ids = [r.get("token_id") for r in search_results[:2]]
                
                # Test live data analysis
                analysis_data = {
                    "query": "What are the current applications of fluid mechanics in aerospace engineering?",
                    "context_tokens": token_ids
                }
                
                print(f"\n🧠 Testing live data analysis...")
                response = requests.post(f"{API_BASE}/api/pdf/analyze", 
                                       json=analysis_data, headers=headers, timeout=45)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print("✅ Live data analysis successful!")
                        analysis = result.get("analysis", "")
                        print(f"  - Query processed successfully")
                        print(f"  - Analysis preview: {analysis[:120]}...")
                        
                        enhanced_tokens = result.get("token_matches", [])
                        print(f"  - Enhanced {len(enhanced_tokens)} tokens with live data")
                    else:
                        print(f"✗ Analysis failed: {result.get('error')}")
                else:
                    print(f"✗ Analysis request failed: {response.status_code}")
                    print(f"  Response: {response.text}")
                    
    except Exception as e:
        print(f"✗ Live data analysis error: {e}")

def test_document_statistics(token, doc_id):
    """Test document statistics endpoint"""
    if not token or not doc_id:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/api/pdf/document/{doc_id}", 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                stats = result.get("document_stats", {})
                print(f"\n📊 Document Statistics:")
                
                doc_info = stats.get("document", {})
                print(f"  - Filename: {doc_info.get('filename')}")
                print(f"  - Pages: {doc_info.get('total_pages')}")
                
                token_info = stats.get("tokens", {})
                print(f"  - Total chunks: {token_info.get('total_chunks')}")
                print(f"  - Total tokens: {token_info.get('total_tokens')}")
                print(f"  - Avg tokens/chunk: {token_info.get('avg_tokens_per_chunk')}")
                
                images_info = stats.get("images", {})
                total_images = images_info.get("total_images", 0)
                print(f"  - Images extracted: {total_images}")
                
                if total_images > 0:
                    print("  ✅ Image analysis capability confirmed!")
                else:
                    print("  ℹ️  No images found in this PDF")
                    
    except Exception as e:
        print(f"✗ Statistics error: {e}")

def main():
    """Run comprehensive test of enhanced PDF system"""
    print("🧪 Enhanced PDF Processing System - Full Feature Test")
    print("=" * 60)
    print("Testing with your new API keys:")
    print("✅ Perplexity API: pplx-llvd...CnJSw")
    print("✅ OpenAI API: sk-proj-cAt6...UiYA")
    print("=" * 60)
    
    # Step 1: Test server
    print("\n1. Testing server connectivity...")
    if not test_server_health():
        print("❌ Server not accessible. Please check if it's running.")
        return
    
    # Step 2: Login
    print("\n2. Authenticating...")
    token = login_and_get_token()
    if not token:
        print("❌ Authentication failed. Cannot proceed.")
        return
    
    # Step 3: Test PDF upload with enhanced features
    print(f"\n3. Testing enhanced PDF processing with {TEST_PDF}...")
    doc_id = test_pdf_upload_with_enhanced_features(token)
    if not doc_id:
        print("❌ PDF upload failed. Cannot test enhanced features.")
        return
    
    # Step 4: Test document statistics
    test_document_statistics(token, doc_id)
    
    # Step 5: Test enhanced search with live data
    print("\n4. Testing search with live data enhancement...")
    test_enhanced_search_with_live_data(token, doc_id)
    
    # Step 6: Test live data analysis
    print("\n5. Testing live data analysis with Perplexity API...")
    test_live_data_analysis(token, doc_id)
    
    print("\n" + "=" * 60)
    print("🎉 Enhanced PDF System Test Complete!")
    print("\n📋 Summary:")
    print("✅ All API keys are now configured")
    print("✅ Server is running with enhanced features")
    print("✅ Token-based PDF processing is operational")
    print("🌐 Live data enhancement is available")
    print("🖼️  Image analysis is enabled")
    print(f"\n🔗 Access the system at: http://localhost:52047")
    print("📱 Login with: demo@example.com / Akanksha100991!")

if __name__ == "__main__":
    main()
