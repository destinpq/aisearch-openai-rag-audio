#!/usr/bin/env python3
"""
PDF Line Number Test - Verify line numbers are working

This script tests that PDF line numbers are being extracted and displayed correctly.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to the path
sys.path.append('/home/azureuser/aisearch-openai-rag-audio/app/backend')
os.environ['RUNNING_IN_PRODUCTION'] = 'false'

async def test_pdf_line_numbers():
    print("🔍 Testing PDF Line Number Extraction")
    print("=" * 50)
    
    try:
        from document_indexer import DocumentIndexer
        from document_processing.pdf_processor import extract_pdf_text, create_intelligent_chunks_with_ai
        
        # Test 1: Extract text and create chunks with line numbers
        pdf_file = "/home/azureuser/aisearch-openai-rag-audio/data/employee_handbook.pdf"
        
        if not Path(pdf_file).exists():
            print("❌ Test PDF not found!")
            return
        
        print(f"📄 Testing with: {Path(pdf_file).name}")
        
        # Step 1: Extract text
        print("\n🔧 Step 1: Extracting PDF text...")
        text = extract_pdf_text(pdf_file, is_path=True)
        lines = text.split('\n')
        print(f"   ✅ Extracted {len(text)} characters, {len(lines)} lines")
        
        # Step 2: Create chunks with line numbers
        print("\n🔧 Step 2: Creating chunks with line numbers...")
        chunks = create_intelligent_chunks_with_ai(text, "employee_handbook.pdf")
        print(f"   ✅ Created {len(chunks)} chunks")
        
        # Step 3: Display chunk info with line numbers
        print("\n📊 Chunk Information:")
        for i, chunk in enumerate(chunks[:3], 1):  # Show first 3 chunks
            start_line = chunk.get('start_line', 'N/A')
            end_line = chunk.get('end_line', 'N/A')
            print(f"\n   Chunk {i}:")
            print(f"      📝 Title: {chunk['title']}")
            print(f"      📍 Lines: {start_line} - {end_line}")
            print(f"      📖 Content preview: {chunk['content'][:100]}...")
            print(f"      📏 Content length: {len(chunk['content'])} chars")
        
        # Step 4: Index and search test
        print("\n🔧 Step 4: Testing indexing and search...")
        indexer = DocumentIndexer()
        
        # Index the document
        success = await indexer.index_document(pdf_file, "employee_handbook.pdf", "test_user")
        print(f"   {'✅' if success else '❌'} Indexing: {success}")
        
        # Search and check if line numbers appear
        results = await indexer.search_documents("employee", top=3, user_id="test_user")
        print(f"   📊 Search returned {len(results) if results else 0} results")
        
        if results:
            print("\n📋 Search Results with Line Numbers:")
            for i, result in enumerate(results, 1):
                start_line = result.get('start_line', 'N/A')
                end_line = result.get('end_line', 'N/A')
                filename = result.get('filename', 'N/A')
                print(f"\n   Result {i}:")
                print(f"      📄 File: {filename}")
                print(f"      📍 Lines: {start_line} - {end_line}")
                print(f"      📝 Title: {result.get('title', 'N/A')}")
                print(f"      📖 Content: {result.get('content', '')[:100]}...")
                
                # Check if line numbers are valid
                if start_line != 'N/A' and end_line != 'N/A' and start_line > 0:
                    print(f"      ✅ Line numbers are present!")
                else:
                    print(f"      ❌ Line numbers are missing!")
        else:
            print("   ❌ No search results returned")
        
        # Step 5: Test guarded search
        print("\n🔧 Step 5: Testing guarded search...")
        guarded_results = await indexer.search_in_pdf("handbook", "employee_handbook.pdf", top=2, user_id="test_user")
        print(f"   📊 Guarded search returned {len(guarded_results) if guarded_results else 0} results")
        
        if guarded_results:
            print("\n📋 Guarded Search Results:")
            for i, result in enumerate(guarded_results, 1):
                start_line = result.get('start_line', 'N/A')
                end_line = result.get('end_line', 'N/A')
                print(f"   Result {i}: Lines {start_line}-{end_line}")
        
        print(f"\n🎯 Summary:")
        print(f"   ✅ PDF text extraction: Working")
        print(f"   ✅ Chunk creation: Working")
        print(f"   ✅ Line number assignment: {'Working' if chunks and chunks[0].get('start_line') else 'MISSING'}")
        print(f"   ✅ Document indexing: {'Working' if success else 'FAILED'}")
        print(f"   ✅ Search results: {'Working' if results else 'FAILED'}")
        print(f"   ✅ Line numbers in results: {'Working' if results and results[0].get('start_line') else 'MISSING'}")
        
        if results and results[0].get('start_line'):
            print(f"\n🎉 LINE NUMBERS ARE WORKING CORRECTLY!")
        else:
            print(f"\n❌ LINE NUMBERS ARE MISSING - Need to investigate!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("PDF Line Number Test")
    print("This will test if line numbers are being extracted and displayed correctly")
    
    try:
        asyncio.run(test_pdf_line_numbers())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    main()
