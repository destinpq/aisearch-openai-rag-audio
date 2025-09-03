#!/usr/bin/env python3
"""
PDF-Specific Search Demo

This demonstrates how to search only within specific PDFs you upload,
not getting mixed results from all PDFs.

Usage: python pdf_specific_search_demo.py
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to the path
sys.path.append('/home/azureuser/aisearch-openai-rag-audio/app/backend')

# Set minimal environment to avoid Azure dependency issues
os.environ['RUNNING_IN_PRODUCTION'] = 'false'

async def pdf_specific_search_demo():
    """Demo of searching within specific PDFs only"""
    
    print("🎯 PDF-Specific Search Demo")
    print("=" * 60)
    print("This demo shows how to search ONLY within specific PDFs")
    print("(not getting mixed results from all uploaded PDFs)")
    
    try:
        from document_indexer import DocumentIndexer
        
        # Initialize indexer
        indexer = DocumentIndexer()
        print("\n✅ Document indexer initialized (using local storage)")
        
        # Find PDF files
        pdf_files = [
            "/home/azureuser/aisearch-openai-rag-audio/data/employee_handbook.pdf",
            "/home/azureuser/aisearch-openai-rag-audio/data/Benefit_Options.pdf",
            "/home/azureuser/aisearch-openai-rag-audio/data/Northwind_Health_Plus_Benefits_Details.pdf"
        ]
        
        existing_files = [f for f in pdf_files if Path(f).exists()]
        
        if not existing_files:
            print("❌ No PDF files found!")
            return
        
        print(f"\n📄 Found {len(existing_files)} PDF files:")
        for f in existing_files:
            print(f"   - {Path(f).name}")
        
        # Step 1: Index all PDFs
        print(f"\n🔄 Indexing PDFs...")
        
        indexed_files = []
        for pdf_file in existing_files:
            filename = Path(pdf_file).name
            print(f"   📄 Indexing: {filename}")
            
            try:
                success = await indexer.index_document(pdf_file, filename, "demo_user")
                if success:
                    indexed_files.append(filename)
                    print(f"   ✅ Indexed: {filename}")
                else:
                    print(f"   ❌ Failed: {filename}")
            except Exception as e:
                print(f"   ❌ Error: {filename} - {e}")
        
        print(f"\n✅ Successfully indexed {len(indexed_files)} files")
        
        # Step 2: List indexed PDFs
        print(f"\n📋 Available PDFs for search:")
        indexed_pdfs = await indexer.list_indexed_pdfs(user_id="demo_user")
        for i, pdf_info in enumerate(indexed_pdfs, 1):
            print(f"   {i}. {pdf_info['filename']} ({pdf_info['total_chunks']} chunks)")
        
        # Step 3: Search within SPECIFIC PDFs only
        print(f"\n🎯 PDF-Specific Searches")
        print("=" * 50)
        
        search_tests = [
            {
                'pdf': 'employee_handbook.pdf',
                'queries': ['employee policy', 'workplace', 'handbook']
            },
            {
                'pdf': 'Benefit_Options.pdf', 
                'queries': ['benefits', 'insurance', 'plan']
            },
            {
                'pdf': 'Northwind_Health_Plus_Benefits_Details.pdf',
                'queries': ['health coverage', 'provider', 'network']
            }
        ]
        
        for test in search_tests:
            pdf_name = test['pdf']
            print(f"\n📄 Searching ONLY in '{pdf_name}':")
            print("-" * 40)
            
            # Check if this PDF was indexed
            if pdf_name not in indexed_files:
                print(f"   ⚠️  PDF '{pdf_name}' was not indexed, skipping...")
                continue
            
            for query in test['queries']:
                print(f"\n   🔍 Query: '{query}'")
                
                try:
                    # Search ONLY in this specific PDF
                    results = await indexer.search_in_pdf(query, pdf_name, top=3, user_id="demo_user")
                    
                    if results:
                        print(f"      📊 Found {len(results)} results in '{pdf_name}':")
                        for i, result in enumerate(results, 1):
                            lines_info = f"Lines {result['start_line']}-{result['end_line']}" if result['start_line'] > 0 else "Line info N/A"
                            print(f"         {i}. {lines_info}")
                            print(f"            📝 {result['title']}")
                            content_preview = result['content'][:100].replace('\n', ' ')
                            print(f"            📖 {content_preview}...")
                    else:
                        print(f"      ❌ No results found for '{query}' in '{pdf_name}'")
                        
                except Exception as e:
                    print(f"      ❌ Search failed: {e}")
        
        # Step 4: Compare with cross-PDF search
        print(f"\n🔄 Comparison: Cross-PDF vs PDF-Specific Search")
        print("=" * 60)
        
        comparison_query = "health insurance"
        print(f"🔍 Query: '{comparison_query}'")
        
        # Search across ALL PDFs
        print(f"\n1️⃣  Search across ALL PDFs:")
        try:
            all_results = await indexer.search_documents(comparison_query, top=10, user_id="demo_user")
            if all_results:
                files_found = set(result['filename'] for result in all_results)
                print(f"   📊 Found {len(all_results)} results across {len(files_found)} PDFs:")
                for filename in sorted(files_found):
                    file_count = sum(1 for r in all_results if r['filename'] == filename)
                    print(f"      - {filename}: {file_count} results")
            else:
                print(f"   ❌ No results found")
        except Exception as e:
            print(f"   ❌ Search failed: {e}")
        
        # Search in specific PDF only
        specific_pdf = "Benefit_Options.pdf"
        print(f"\n2️⃣  Search ONLY in '{specific_pdf}':")
        try:
            specific_results = await indexer.search_in_pdf(comparison_query, specific_pdf, top=10, user_id="demo_user")
            if specific_results:
                print(f"   📊 Found {len(specific_results)} results in '{specific_pdf}' only:")
                for i, result in enumerate(specific_results, 1):
                    lines_info = f"Lines {result['start_line']}-{result['end_line']}" if result['start_line'] > 0 else "Line info N/A"
                    print(f"      {i}. {lines_info} - {result['title']}")
            else:
                print(f"   ❌ No results found in '{specific_pdf}'")
        except Exception as e:
            print(f"   ❌ Search failed: {e}")
        
        # Step 5: Summary
        print(f"\n📊 Summary")
        print("=" * 30)
        print(f"✅ You can now search within specific PDFs!")
        print(f"📄 Available methods:")
        print(f"   - search_documents() - Search across ALL PDFs")
        print(f"   - search_in_pdf() - Search within ONE specific PDF")
        print(f"   - list_indexed_pdfs() - List available PDFs to search")
        print(f"\n🎯 This ensures you get data ONLY from the PDF you want!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("PDF-Specific Search Demo")
    print("This shows how to search within specific PDFs only")
    print("(avoiding mixed results from all uploaded PDFs)")
    
    input("\nPress Enter to start the demo...")
    
    try:
        asyncio.run(pdf_specific_search_demo())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")

if __name__ == "__main__":
    main()
