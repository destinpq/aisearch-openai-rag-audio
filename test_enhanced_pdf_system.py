#!/usr/bin/env python3
"""
Test script for Enhanced PDF Processing System
Tests token-based storage, vectorization, and live data enhancement
"""

import asyncio
import aiohttp
import json
import os
from pathlib import Path

# Test configuration  
API_BASE = "http://localhost:52047"
TEST_PDF = "test_sample.pdf"
AUTH_TOKEN = None

async def create_test_pdf():
    """Create a simple test PDF for testing"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(TEST_PDF, pagesize=letter)
        width, height = letter
        
        # Page 1
        c.drawString(100, height - 100, "Enhanced PDF Processing Test Document")
        c.drawString(100, height - 150, "This document contains sample content for testing token-based processing.")
        c.drawString(100, height - 200, "We will test vectorization and precise location tracking.")
        c.drawString(100, height - 250, "Each line should be tracked with accurate page and line numbers.")
        c.drawString(100, height - 300, "The system should extract tokens with character-level precision.")
        c.drawString(100, height - 350, "Live data enhancement will provide additional context from external sources.")
        c.showPage()
        
        # Page 2
        c.drawString(100, height - 100, "Page 2: Advanced Features")
        c.drawString(100, height - 150, "This page tests multi-page document processing.")
        c.drawString(100, height - 200, "Image analysis capabilities should detect and process visual elements.")
        c.drawString(100, height - 250, "The token search should provide precise location information.")
        c.drawString(100, height - 300, "Database storage ensures efficient retrieval and relationship mapping.")
        c.showPage()
        
        c.save()
        print(f"✓ Created test PDF: {TEST_PDF}")
        return True
        
    except ImportError:
        print("⚠ reportlab not available, creating simple text file instead")
        with open("test_sample.txt", "w") as f:
            f.write("""Enhanced PDF Processing Test Document

This document contains sample content for testing token-based processing.
We will test vectorization and precise location tracking.
Each line should be tracked with accurate page and line numbers.
The system should extract tokens with character-level precision.
Live data enhancement will provide additional context from external sources.

Page 2: Advanced Features
This page tests multi-page document processing.
Image analysis capabilities should detect and process visual elements.
The token search should provide precise location information.
Database storage ensures efficient retrieval and relationship mapping.
""")
        return False

async def login_user():
    """Login and get authentication token"""
    global AUTH_TOKEN
    
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{API_BASE}/api/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    AUTH_TOKEN = data.get("token")
                    print("✓ Successfully logged in")
                    return True
                else:
                    print(f"✗ Login failed: {response.status}")
                    return False
        except Exception as e:
            print(f"✗ Login error: {e}")
            return False

async def test_pdf_upload():
    """Test PDF upload and processing"""
    if not AUTH_TOKEN:
        print("✗ No authentication token available")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    async with aiohttp.ClientSession() as session:
        try:
            # Upload PDF file
            with open(TEST_PDF, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename=TEST_PDF, content_type='application/pdf')
                
                async with session.post(f"{API_BASE}/api/pdf/upload", 
                                      data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("success"):
                            upload_result = result.get("result", {})
                            print(f"✓ PDF uploaded successfully:")
                            print(f"  - Document ID: {upload_result.get('doc_id')}")
                            print(f"  - Total tokens: {upload_result.get('total_tokens')}")
                            print(f"  - Total pages: {upload_result.get('total_pages')}")
                            print(f"  - Chunks created: {upload_result.get('chunks_created')}")
                            print(f"  - Images extracted: {upload_result.get('images_extracted', 0)}")
                            return upload_result.get('doc_id')
                        else:
                            print(f"✗ Upload failed: {result.get('error')}")
                            return None
                    else:
                        print(f"✗ Upload request failed: {response.status}")
                        error_text = await response.text()
                        print(f"  Error: {error_text}")
                        return None
                        
        except Exception as e:
            print(f"✗ Upload error: {e}")
            return None

async def test_document_stats(doc_id):
    """Test document statistics retrieval"""
    if not AUTH_TOKEN or not doc_id:
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_BASE}/api/pdf/document/{doc_id}", 
                                 headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        stats = result.get("document_stats", {})
                        print(f"✓ Document statistics retrieved:")
                        
                        doc_info = stats.get("document", {})
                        print(f"  - Filename: {doc_info.get('filename')}")
                        print(f"  - Upload date: {doc_info.get('upload_date')}")
                        print(f"  - Total pages: {doc_info.get('total_pages')}")
                        
                        token_info = stats.get("tokens", {})
                        print(f"  - Total chunks: {token_info.get('total_chunks')}")
                        print(f"  - Total tokens: {token_info.get('total_tokens')}")
                        print(f"  - Avg tokens per chunk: {token_info.get('avg_tokens_per_chunk')}")
                        
                        page_dist = stats.get("page_distribution", [])
                        print(f"  - Page distribution: {len(page_dist)} pages with chunks")
                        
                        return True
                    else:
                        print(f"✗ Stats retrieval failed: {result.get('error')}")
                        return False
                else:
                    print(f"✗ Stats request failed: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"✗ Stats error: {e}")
            return False

async def test_token_search(doc_id):
    """Test token-based search functionality"""
    if not AUTH_TOKEN or not doc_id:
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}", "Content-Type": "application/json"}
    
    search_queries = [
        "token processing",
        "vectorization",
        "line numbers",
        "advanced features"
    ]
    
    async with aiohttp.ClientSession() as session:
        for query in search_queries:
            try:
                search_data = {
                    "query": query,
                    "doc_id": doc_id,
                    "limit": 5
                }
                
                async with session.post(f"{API_BASE}/api/pdf/search", 
                                      json=search_data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("success"):
                            results = result.get("results", [])
                            print(f"✓ Search for '{query}' found {len(results)} results:")
                            
                            for i, token_result in enumerate(results[:2]):  # Show first 2 results
                                print(f"  Result {i+1}:")
                                print(f"    - Token ID: {token_result.get('token_id')}")
                                print(f"    - Page: {token_result.get('page_number')}")
                                print(f"    - Lines: {token_result.get('line_start')}-{token_result.get('line_end')}")
                                print(f"    - Token count: {token_result.get('token_count')}")
                                print(f"    - Content preview: {token_result.get('content', '')[:50]}...")
                                if token_result.get('bbox'):
                                    bbox = token_result['bbox']
                                    print(f"    - Position: x={bbox['x']:.1f}, y={bbox['y']:.1f}")
                                print()
                        else:
                            print(f"✗ Search for '{query}' failed: {result.get('error')}")
                    else:
                        print(f"✗ Search request for '{query}' failed: {response.status}")
                        
            except Exception as e:
                print(f"✗ Search error for '{query}': {e}")

async def test_live_data_analysis(doc_id):
    """Test live data enhancement with Perplexity API"""
    if not AUTH_TOKEN or not doc_id:
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}", "Content-Type": "application/json"}
    
    async with aiohttp.ClientSession() as session:
        try:
            # First, search for some tokens to use as context
            search_data = {
                "query": "processing",
                "doc_id": doc_id,
                "limit": 3
            }
            
            async with session.post(f"{API_BASE}/api/pdf/search", 
                                  json=search_data, headers=headers) as response:
                if response.status == 200:
                    search_result = await response.json()
                    if search_result.get("success"):
                        search_results = search_result.get("results", [])
                        token_ids = [r.get("token_id") for r in search_results[:2]]
                        
                        # Now test live data analysis
                        analysis_data = {
                            "query": "What are the latest developments in PDF processing technology?",
                            "context_tokens": token_ids
                        }
                        
                        async with session.post(f"{API_BASE}/api/pdf/analyze", 
                                              json=analysis_data, headers=headers) as analyze_response:
                            if analyze_response.status == 200:
                                result = await analyze_response.json()
                                if result.get("success"):
                                    print("✓ Live data analysis completed:")
                                    print(f"  - Query: {analysis_data['query']}")
                                    print(f"  - Context tokens: {len(token_ids)}")
                                    
                                    analysis = result.get("analysis", "")
                                    print(f"  - Analysis preview: {analysis[:100]}...")
                                    
                                    enhanced_tokens = result.get("token_matches", [])
                                    print(f"  - Enhanced token matches: {len(enhanced_tokens)}")
                                    
                                    return True
                                else:
                                    print(f"✗ Analysis failed: {result.get('error')}")
                            else:
                                print(f"✗ Analysis request failed: {analyze_response.status}")
                                error_text = await analyze_response.text()
                                print(f"  Error: {error_text}")
                    else:
                        print("✗ Could not get tokens for analysis context")
                else:
                    print("✗ Could not search for context tokens")
                    
        except Exception as e:
            print(f"✗ Live data analysis error: {e}")
            return False

async def cleanup():
    """Clean up test files"""
    try:
        if os.path.exists(TEST_PDF):
            os.remove(TEST_PDF)
            print(f"✓ Cleaned up {TEST_PDF}")
        if os.path.exists("test_sample.txt"):
            os.remove("test_sample.txt")
            print("✓ Cleaned up test_sample.txt")
    except Exception as e:
        print(f"⚠ Cleanup error: {e}")

async def main():
    """Run all tests"""
    print("🧪 Enhanced PDF Processing System Test")
    print("=" * 50)
    
    # Step 1: Create test PDF
    print("\n1. Creating test PDF...")
    pdf_created = await create_test_pdf()
    if not pdf_created and not os.path.exists("test_sample.txt"):
        print("✗ Could not create test file")
        return
    
    # Step 2: Login
    print("\n2. Authenticating...")
    login_success = await login_user()
    if not login_success:
        print("✗ Authentication failed - cannot proceed with API tests")
        await cleanup()
        return
    
    # Step 3: Upload PDF
    print("\n3. Testing PDF upload and processing...")
    doc_id = await test_pdf_upload()
    if not doc_id:
        print("✗ PDF upload failed - cannot proceed with other tests")
        await cleanup()
        return
    
    # Step 4: Test document statistics
    print("\n4. Testing document statistics...")
    await test_document_stats(doc_id)
    
    # Step 5: Test token search
    print("\n5. Testing token-based search...")
    await test_token_search(doc_id)
    
    # Step 6: Test live data analysis (optional - requires API keys)
    print("\n6. Testing live data analysis...")
    await test_live_data_analysis(doc_id)
    
    # Cleanup
    print("\n7. Cleaning up...")
    await cleanup()
    
    print("\n" + "=" * 50)
    print("🎉 Enhanced PDF Processing System Test Complete!")
    print("\nNext steps:")
    print("1. Configure Perplexity and OpenAI API keys in .env file")
    print("2. Test with real PDF documents")
    print("3. Verify frontend integration at /enhanced-pdf route")

if __name__ == "__main__":
    asyncio.run(main())
