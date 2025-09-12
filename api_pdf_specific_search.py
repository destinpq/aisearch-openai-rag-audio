#!/usr/bin/env python3
"""
API Demo: PDF-Specific Search

This demonstrates the API endpoints for searching within specific PDFs only.

Usage: python api_pdf_specific_search.py
"""

import requests
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8765"
USERNAME = "demo@example.com"
PASSWORD = "Akanksha100991!"

class PDFSpecificSearchAPI:
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
    
    def list_indexed_pdfs(self):
        """List all indexed PDFs"""
        response = self.session.get(f"{BASE_URL}/indexed-pdfs")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to list indexed PDFs: {response.text}")
            return None
    
    def search_all_pdfs(self, query):
        """Search across all PDFs"""
        response = self.session.post(f"{BASE_URL}/analyze", json={"query": query})
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Search failed: {response.text}")
            return None
    
    def search_specific_pdf(self, query, filename):
        """Search within a specific PDF only"""
        response = self.session.post(f"{BASE_URL}/analyze", json={
            "query": query,
            "filename": filename
        })
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Search failed: {response.text}")
            return None
    
    def demo_pdf_specific_search(self):
        """Complete demo of PDF-specific search functionality"""
        print("🎯 API Demo: PDF-Specific Search")
        print("=" * 60)
        
        # Step 1: Login
        if not self.login():
            return
        
        # Step 2: Upload some PDFs (if they exist)
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
        
        # Step 3: List indexed PDFs
        print(f"\n📋 Listing indexed PDFs...")
        indexed_pdfs_result = self.list_indexed_pdfs()
        if indexed_pdfs_result:
            indexed_pdfs = indexed_pdfs_result.get('indexed_pdfs', [])
            print(f"   📊 Found {len(indexed_pdfs)} indexed PDFs:")
            for i, pdf_info in enumerate(indexed_pdfs, 1):
                print(f"      {i}. {pdf_info['filename']} ({pdf_info['total_chunks']} chunks)")
        else:
            print("   ❌ No indexed PDFs found")
            return
        
        # Step 4: Demonstrate PDF-specific searches
        print(f"\n🎯 PDF-Specific Search Examples")
        print("=" * 50)
        
        # Test queries for specific PDFs
        search_tests = [
            {
                'pdf': 'employee_handbook.pdf',
                'query': 'workplace policy',
                'description': 'Employee handbook policies'
            },
            {
                'pdf': 'Benefit_Options.pdf',
                'query': 'health insurance',
                'description': 'Health insurance in benefits document'
            },
            {
                'pdf': 'Northwind_Health_Plus_Benefits_Details.pdf',
                'query': 'coverage details',
                'description': 'Coverage details in health plan'
            }
        ]
        
        for test in search_tests:
            pdf_name = test['pdf']
            query = test['query']
            description = test['description']
            
            print(f"\n📄 Test: {description}")
            print(f"   🔍 Query: '{query}'")
            print(f"   📋 Searching ONLY in: {pdf_name}")
            print("-" * 40)
            
            # Check if PDF exists in indexed list
            pdf_exists = any(p['filename'] == pdf_name for p in indexed_pdfs)
            if not pdf_exists:
                print(f"   ⚠️  PDF '{pdf_name}' not found in indexed PDFs, skipping...")
                continue
            
            # Search in specific PDF
            result = self.search_specific_pdf(query, pdf_name)
            if result and result.get('results'):
                results = result['results']
                print(f"   📊 Found {len(results)} results in '{pdf_name}' only:")
                
                for i, r in enumerate(results[:3], 1):  # Show top 3
                    print(f"      {i}. {r['line_reference']}")
                    print(f"         📝 {r['title']}")
                    content = r['content'][:100].replace('\n', ' ')
                    print(f"         📖 {content}...")
                    print()
            else:
                print(f"   ❌ No results found for '{query}' in '{pdf_name}'")
        
        # Step 5: Compare cross-PDF vs specific PDF search
        print(f"\n🔄 Comparison Demo")
        print("=" * 40)
        
        comparison_query = "employee benefits"
        print(f"🔍 Query: '{comparison_query}'")
        
        # Search across ALL PDFs
        print(f"\n1️⃣  Search across ALL PDFs:")
        all_results = self.search_all_pdfs(comparison_query)
        if all_results and all_results.get('results'):
            results = all_results['results']
            files_found = set(r['filename'] for r in results)
            print(f"   📊 Found {len(results)} results across {len(files_found)} PDFs:")
            for filename in sorted(files_found):
                count = sum(1 for r in results if r['filename'] == filename)
                print(f"      - {filename}: {count} results")
        else:
            print(f"   ❌ No results found across all PDFs")
        
        # Search in ONE specific PDF
        specific_pdf = "employee_handbook.pdf"
        print(f"\n2️⃣  Search ONLY in '{specific_pdf}':")
        specific_results = self.search_specific_pdf(comparison_query, specific_pdf)
        if specific_results and specific_results.get('results'):
            results = specific_results['results']
            print(f"   📊 Found {len(results)} results in '{specific_pdf}' only:")
            for i, r in enumerate(results[:2], 1):  # Show top 2
                print(f"      {i}. {r['line_reference']} - {r['title']}")
        else:
            print(f"   ❌ No results found in '{specific_pdf}'")
        
        # Step 6: Summary
        print(f"\n📊 API Usage Summary")
        print("=" * 30)
        print(f"✅ API Endpoints available:")
        print(f"   GET  /indexed-pdfs - List available PDFs")
        print(f"   POST /analyze - Search with optional 'filename' parameter")
        print(f"        • Without 'filename': Search ALL PDFs")
        print(f"        • With 'filename': Search SPECIFIC PDF only")
        print(f"\n🎯 You now have precise control over which PDF to search!")
        
        print(f"\n📝 Example API calls:")
        print(f'   # Search all PDFs:')
        print(f'   POST /analyze {{"query": "benefits"}}')
        print(f'   # Search specific PDF:')
        print(f'   POST /analyze {{"query": "benefits", "filename": "employee_handbook.pdf"}}')

def main():
    print("API Demo: PDF-Specific Search")
    print("This demonstrates searching within specific PDFs via API")
    print("\n⚠️  Make sure your server is running on http://localhost:8765")
    
    input("\nPress Enter to continue...")
    
    api = PDFSpecificSearchAPI()
    try:
        api.demo_pdf_specific_search()
        print(f"\n🎉 API demo completed successfully!")
    except Exception as e:
        print(f"\n❌ API demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
