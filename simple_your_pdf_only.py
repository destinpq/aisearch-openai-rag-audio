#!/usr/bin/env python3
"""
Simple Demo: Search Only Your PDF

This shows how to search ONLY within the PDF you upload,
not getting mixed results from other PDFs.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to the path
sys.path.append('/home/azureuser/aisearch-openai-rag-audio/app/backend')
os.environ['RUNNING_IN_PRODUCTION'] = 'false'

async def simple_demo():
    print("🎯 Simple Demo: Search Only Your PDF")
    print("=" * 50)
    
    try:
        from document_indexer import DocumentIndexer
        indexer = DocumentIndexer()
        
        # Step 1: Index a couple of PDFs
        pdf1 = "/home/azureuser/aisearch-openai-rag-audio/data/employee_handbook.pdf"
        pdf2 = "/home/azureuser/aisearch-openai-rag-audio/data/Benefit_Options.pdf"
        
        user_id = "your_user"
        
        print("📄 Indexing PDFs...")
        if Path(pdf1).exists():
            await indexer.index_document(pdf1, "employee_handbook.pdf", user_id)
            print("✅ Indexed: employee_handbook.pdf")
        
        if Path(pdf2).exists():
            await indexer.index_document(pdf2, "Benefit_Options.pdf", user_id)
            print("✅ Indexed: Benefit_Options.pdf")
        
        # Step 2: Show the difference
        query = "insurance"
        print(f"\n🔍 Searching for: '{query}'")
        print("-" * 30)
        
        # Search ALL PDFs
        print("1️⃣  Search across ALL PDFs:")
        all_results = await indexer.search_documents(query, top=5, user_id=user_id)
        if all_results:
            files_found = set(r['filename'] for r in all_results)
            print(f"   📊 Found results in: {', '.join(files_found)}")
            print(f"   📈 Total results: {len(all_results)}")
        
        # Search ONLY employee handbook
        print(f"\n2️⃣  Search ONLY in 'employee_handbook.pdf':")
        handbook_results = await indexer.search_in_pdf(query, "employee_handbook.pdf", top=5, user_id=user_id)
        if handbook_results:
            print(f"   📊 Found {len(handbook_results)} results in employee_handbook.pdf only")
            for i, result in enumerate(handbook_results[:2], 1):
                print(f"      {i}. Lines {result['start_line']}-{result['end_line']}")
        else:
            print(f"   ❌ No results in employee_handbook.pdf")
        
        # Search ONLY benefits document
        print(f"\n3️⃣  Search ONLY in 'Benefit_Options.pdf':")
        benefits_results = await indexer.search_in_pdf(query, "Benefit_Options.pdf", top=5, user_id=user_id)
        if benefits_results:
            print(f"   📊 Found {len(benefits_results)} results in Benefit_Options.pdf only")
            for i, result in enumerate(benefits_results[:2], 1):
                print(f"      {i}. Lines {result['start_line']}-{result['end_line']}")
        else:
            print(f"   ❌ No results in Benefit_Options.pdf")
        
        print(f"\n🎯 KEY POINT:")
        print(f"   ✅ You can now search ONLY within YOUR specific PDF!")
        print(f"   ✅ No more mixed results from other people's PDFs!")
        print(f"   ✅ Get line numbers from YOUR PDF only!")
        
        # Show available PDFs
        print(f"\n📋 Your available PDFs:")
        pdfs = await indexer.list_indexed_pdfs(user_id=user_id)
        for pdf in pdfs:
            print(f"   - {pdf['filename']} ({pdf['total_chunks']} chunks)")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("This demo shows how to search only within YOUR uploaded PDF")
    print("(not getting results from other PDFs)")
    
    asyncio.run(simple_demo())

if __name__ == "__main__":
    main()
