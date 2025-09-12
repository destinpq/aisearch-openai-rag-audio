#!/usr/bin/env python3
"""
Multi-PDF Upload and Line Number Extraction Demo

This script demonstrates how to:
1. Upload multiple PDF files
2. Index them with line number tracking
3. Search across all PDFs and get line numbers from both

Usage: python multi_pdf_line_demo.py
"""

import asyncio
import aiohttp
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8765"  # Change to your server URL
USERNAME = "demo@example.com"
PASSWORD = "Akanksha100991!"

class MultiPDFDemo:
    def __init__(self):
        self.session = None
        self.token = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def login(self):
        """Login and get JWT token"""
        async with self.session.post(f"{BASE_URL}/login", json={
            "username": USERNAME,
            "password": PASSWORD
        }) as resp:
            if resp.status == 200:
                data = await resp.json()
                self.token = data["token"]
                print(f"✅ Logged in successfully")
                return True
            else:
                error = await resp.text()
                print(f"❌ Login failed: {error}")
                return False
    
    async def upload_pdf(self, pdf_path: str):
        """Upload a PDF file"""
        if not Path(pdf_path).exists():
            print(f"❌ File not found: {pdf_path}")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        with open(pdf_path, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('file', f, filename=Path(pdf_path).name, content_type='application/pdf')
            
            async with self.session.post(f"{BASE_URL}/upload", data=data, headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✅ Uploaded: {result['filename']} (Indexed: {result['indexed']})")
                    return True
                else:
                    error = await resp.text()
                    print(f"❌ Upload failed for {pdf_path}: {error}")
                    return False
    
    async def search_documents(self, query: str, mode: str = "unguarded", filename: str = None):
        """
        Search documents in guarded or unguarded mode.
        - guarded: search only within the specified PDF (filename required)
        - unguarded: search across all PDFs
        """
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {"query": query}
        if mode == "guarded" and filename:
            payload["filename"] = filename
        async with self.session.post(f"{BASE_URL}/analyze", json=payload, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                error = await resp.text()
                print(f"❌ Search failed: {error}")
                return None
    
    async def list_files(self):
        """List all uploaded files"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with self.session.get(f"{BASE_URL}/files", headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                error = await resp.text()
                print(f"❌ Failed to list files: {error}")
                return None
    
    async def demo_multiple_pdfs(self, pdf_files: list, mode: str = "unguarded"):
        """Demo: upload multiple PDFs and search in guarded/unguarded mode"""
        print(f"🚀 Starting Multi-PDF Demo ({mode.upper()} mode)")
        print("=" * 50)
        
        # Step 1: Login
        if not await self.login():
            return
        
        # Step 2: Upload all PDFs
        print(f"\n📄 Uploading {len(pdf_files)} PDF files...")
        uploaded_count = 0
        for pdf_file in pdf_files:
            if await self.upload_pdf(pdf_file):
                uploaded_count += 1
            await asyncio.sleep(1)  # Small delay between uploads
        
        print(f"\n✅ Successfully uploaded {uploaded_count}/{len(pdf_files)} files")
        
        # Step 3: List uploaded files
        print(f"\n📋 Listing all files...")
        files_result = await self.list_files()
        uploaded_filenames = [Path(f).name for f in pdf_files]
        if files_result:
            for file_info in files_result.get('files', []):
                print(f"   - {file_info['filename']} ({file_info['size']} bytes)")
        
        # Step 4: Search for specific terms
        search_queries = [
            "benefits",
            "employee handbook", 
            "vacation",
            "health insurance",
            "salary"
        ]
        
        print(f"\n🔍 Searching {'ONLY within each PDF (guarded)' if mode=='guarded' else 'across all PDFs (unguarded)'}...")
        for query in search_queries:
            print(f"\n🔎 Query: '{query}'")
            print("-" * 30)
            if mode == "guarded":
                for filename in uploaded_filenames:
                    print(f"   [GUARDED] Searching only in: {filename}")
                    results = await self.search_documents(query, mode="guarded", filename=filename)
                    if results and results.get('results'):
                        for i, result in enumerate(results['results'][:3], 1):
                            print(f"\n      Result {i}:")
                            print(f"      📄 File: {result['filename']}")
                            print(f"      📍 {result['line_reference']}")
                            print(f"      📝 Title: {result['title']}")
                            print(f"      📖 Content: {result['content'][:200]}...")
                            print(f"      🔢 Chunk {result['chunk_index']}/{result['total_chunks']}")
                    else:
                        print(f"      ❌ No results found for '{query}' in {filename}")
                    await asyncio.sleep(0.5)
            else:
                results = await self.search_documents(query, mode="unguarded")
                if results and results.get('results'):
                    for i, result in enumerate(results['results'][:3], 1):
                        print(f"\n   Result {i}:")
                        print(f"   📄 File: {result['filename']}")
                        print(f"   📍 {result['line_reference']}")
                        print(f"   📝 Title: {result['title']}")
                        print(f"   📖 Content: {result['content'][:200]}...")
                        print(f"   🔢 Chunk {result['chunk_index']}/{result['total_chunks']}")
                else:
                    print(f"   ❌ No results found for '{query}'")
                await asyncio.sleep(1)

async def main():
    # Example PDF files to upload (you can modify these paths)
    pdf_files = [
        "/home/azureuser/aisearch-openai-rag-audio/data/employee_handbook.pdf",
        "/home/azureuser/aisearch-openai-rag-audio/data/Benefit_Options.pdf",
        "/home/azureuser/aisearch-openai-rag-audio/data/Northwind_Health_Plus_Benefits_Details.pdf"
    ]
    
    # Filter to only existing files
    existing_files = [f for f in pdf_files if Path(f).exists()]
    
    if not existing_files:
        print("❌ No PDF files found in the data directory!")
        print("Please ensure you have PDF files in the following locations:")
        for f in pdf_files:
            print(f"   - {f}")
        return
    
    print(f"Found {len(existing_files)} PDF files to upload:")
    for f in existing_files:
        print(f"   - {f}")
    
    # Choose mode: "guarded" or "unguarded"
    mode = os.environ.get("SEARCH_MODE", "unguarded")  # or set manually
    async with MultiPDFDemo() as demo:
        await demo.demo_multiple_pdfs(existing_files, mode=mode)

if __name__ == "__main__":
    print("Multi-PDF Line Number Demo")
    print("This demo will upload multiple PDFs and search across them to get line numbers")
    print("\n⚠️  Make sure your server is running on http://localhost:8765")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
