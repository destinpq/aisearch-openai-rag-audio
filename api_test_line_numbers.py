#!/usr/bin/env python3
"""
API Test Script for Multi-PDF Line Number Extraction

This script tests the existing API endpoints to:
1. Login to the system
2. Upload multiple PDFs
3. Search and get line numbers from all PDFs

Usage: python api_test_line_numbers.py
"""

import requests
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8765"
USERNAME = "demo@example.com"
PASSWORD = "Akanksha100991!"

class APITester:
    def __init__(self):
        self.token = None
        self.session = requests.Session()
    
    def login(self):
        """Login and get JWT token"""
        response = self.session.post(f"{BASE_URL}/login", json={
            "username": USERNAME,
            "password": PASSWORD
        })
        
        if response.status_code == 200:
            self.token = response.json()["token"]
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            print("✅ Logged in successfully")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    
    def upload_pdf(self, pdf_path):
        """Upload a PDF file"""
        if not Path(pdf_path).exists():
            print(f"❌ File not found: {pdf_path}")
            return False
        
        with open(pdf_path, 'rb') as f:
            files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
            response = self.session.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Uploaded: {result['filename']} (Indexed: {result['indexed']})")
            return True
        else:
            print(f"❌ Upload failed for {pdf_path}: {response.text}")
            return False
    
    def search_documents(self, query):
        """Search across all uploaded documents and return line numbers"""
        response = self.session.post(f"{BASE_URL}/analyze", json={"query": query})
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Search failed: {response.text}")
            return None
    
    def list_files(self):
        """List all uploaded files"""
        response = self.session.get(f"{BASE_URL}/files")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to list files: {response.text}")
            return None
    
    def demo_api_line_extraction(self):
        """Complete API demo for line extraction from multiple PDFs"""
        print("🚀 API Multi-PDF Line Number Demo")
        print("=" * 50)
        
        # Step 1: Login
        if not self.login():
            return
        
        # Step 2: List existing files first
        print(f"\n📋 Current files in system:")
        files_result = self.list_files()
        if files_result and files_result.get('files'):
            for file_info in files_result['files']:
                print(f"   - {file_info['filename']}")
        else:
            print("   No files currently uploaded")
        
        # Step 3: Upload new PDFs (if they exist)
        pdf_files = [
            "/home/azureuser/aisearch-openai-rag-audio/data/employee_handbook.pdf",
            "/home/azureuser/aisearch-openai-rag-audio/data/Benefit_Options.pdf", 
            "/home/azureuser/aisearch-openai-rag-audio/data/Northwind_Health_Plus_Benefits_Details.pdf"
        ]
        
        existing_files = [f for f in pdf_files if Path(f).exists()]
        
        if existing_files:
            print(f"\n📄 Uploading {len(existing_files)} PDF files...")
            for pdf_file in existing_files:
                self.upload_pdf(pdf_file)
        
        # Step 4: Search for terms and show line numbers from multiple PDFs
        search_queries = [
            "employee benefits",
            "health insurance",
            "vacation policy", 
            "salary information",
            "company policy"
        ]
        
        print(f"\n🔍 Searching for line numbers across all PDFs...")
        
        for query in search_queries:
            print(f"\n🔎 Query: '{query}'")
            print("-" * 40)
            
            results = self.search_documents(query)
            if results and results.get('results'):
                print(f"   📊 Found {results['total_results']} results:")
                
                # Group by filename to show results from multiple PDFs
                by_file = {}
                for result in results['results']:
                    filename = result['filename']
                    if filename not in by_file:
                        by_file[filename] = []
                    by_file[filename].append(result)
                
                # Display results grouped by file
                for filename, file_results in by_file.items():
                    print(f"\n   📄 From '{filename}':")
                    for i, result in enumerate(file_results, 1):
                        print(f"      {i}. {result['line_reference']}")
                        print(f"         Title: {result['title']}")
                        print(f"         Chunk: {result['chunk_index']}/{result['total_chunks']}")
                        content = result['content'][:100].replace('\n', ' ')
                        print(f"         Preview: {content}...")
                        print()
                
                if len(by_file) > 1:
                    print(f"   🎯 Results found in {len(by_file)} different PDFs!")
            else:
                print(f"   ❌ No results found for '{query}'")
        
        # Step 5: Demonstrate specific line number queries
        print(f"\n📍 Line Number Extraction Examples")
        print("=" * 40)
        
        line_queries = [
            "What are the vacation benefits?",
            "How much is the health insurance coverage?",
            "What is the employee handbook policy on remote work?"
        ]
        
        for query in line_queries:
            print(f"\n❓ Question: {query}")
            print("-" * 30)
            
            results = self.search_documents(query)
            if results and results.get('results'):
                best_result = results['results'][0]  # Get the top result
                print(f"   📄 Best match from: {best_result['filename']}")
                print(f"   📍 Found at: {best_result['line_reference']}")
                print(f"   📝 Section: {best_result['title']}")
                print(f"   📖 Content: {best_result['content'][:200]}...")
            else:
                print(f"   ❌ No answer found")

def main():
    print("API Multi-PDF Line Number Extraction Test")
    print("This will test the API endpoints for uploading and searching PDFs")
    print("\n⚠️  Make sure your server is running on http://localhost:8765")
    print("   You can start it with: python app/backend/app.py")
    
    input("\nPress Enter to continue...")
    
    tester = APITester()
    try:
        tester.demo_api_line_extraction()
        print(f"\n🎉 API test completed successfully!")
    except Exception as e:
        print(f"\n❌ API test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
