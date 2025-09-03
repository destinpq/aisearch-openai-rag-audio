#!/usr/bin/env python3
"""
Show PDF Line Numbers - Simple Demo

This script clearly shows the line numbers from your PDF uploads.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to the path
sys.path.append('/home/azureuser/aisearch-openai-rag-audio/app/backend')
os.environ['RUNNING_IN_PRODUCTION'] = 'false'

async def show_pdf_line_numbers():
    print("📍 PDF Line Numbers Demo")
    print("=" * 50)
    
    try:
        from document_indexer import DocumentIndexer
        
        # Initialize indexer
        indexer = DocumentIndexer()
        
        # Test with available PDFs
        pdf_files = [
            "/home/azureuser/aisearch-openai-rag-audio/data/employee_handbook.pdf",
            "/home/azureuser/aisearch-openai-rag-audio/data/Benefit_Options.pdf",
        ]
        
        user_id = "line_test_user"
        
        # Index PDFs
        print("📄 Indexing PDFs...")
        for pdf_file in pdf_files:
            if Path(pdf_file).exists():
                filename = Path(pdf_file).name
                await indexer.index_document(pdf_file, filename, user_id)
                print(f"   ✅ {filename}")
        
        # Test searches with clear line number display
        search_terms = ["employee", "handbook", "benefits", "insurance"]
        
        for term in search_terms:
            print(f"\n🔍 Searching for: '{term}'")
            print("-" * 40)
            
            # UNGUARDED: Search all PDFs
            print("🔓 UNGUARDED (search all PDFs):")
            results = await indexer.search_documents(term, top=3, user_id=user_id)
            
            if results:
                for i, result in enumerate(results, 1):
                    filename = result['filename']
                    start_line = result['start_line']
                    end_line = result['end_line']
                    
                    print(f"   {i}. 📄 {filename}")
                    print(f"      📍 LINES {start_line} to {end_line}")
                    print(f"      📝 {result['title']}")
                    print(f"      📖 {result['content'][:80]}...")
                    print()
            else:
                print("   ❌ No results found\n")
            
            # GUARDED: Search specific PDF
            for pdf_file in pdf_files:
                if Path(pdf_file).exists():
                    filename = Path(pdf_file).name
                    print(f"🔒 GUARDED (search only {filename}):")
                    
                    guarded_results = await indexer.search_in_pdf(term, filename, top=2, user_id=user_id)
                    
                    if guarded_results:
                        for i, result in enumerate(guarded_results, 1):
                            start_line = result['start_line']
                            end_line = result['end_line']
                            
                            print(f"   {i}. 📍 LINES {start_line} to {end_line}")
                            print(f"      📝 {result['title']}")
                            print(f"      📖 {result['content'][:60]}...")
                    else:
                        print(f"   ❌ No results in {filename}")
                    print()
        
        # Show available PDFs
        print(f"\n📋 Your Indexed PDFs:")
        pdfs = await indexer.list_indexed_pdfs(user_id=user_id)
        for pdf in pdfs:
            print(f"   📄 {pdf['filename']} - {pdf['total_chunks']} chunks")
        
        print(f"\n🎯 KEY POINTS:")
        print(f"   ✅ Line numbers show EXACT location in your PDF")
        print(f"   🔓 UNGUARDED = Search across ALL your PDFs")
        print(f"   🔒 GUARDED = Search within ONE specific PDF")
        print(f"   📍 Each result shows: Lines X to Y")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("This demo shows PDF line numbers clearly")
    
    try:
        asyncio.run(show_pdf_line_numbers())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted")
    except Exception as e:
        print(f"\n❌ Failed: {e}")

if __name__ == "__main__":
    main()
