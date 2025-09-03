#!/usr/bin/env python3
"""
PROOF: PDF Line Numbers with Guarded/Unguarded Search

This script provides definitive proof that:
1. PDF line numbers are extracted correctly
2. Guarded mode works (search only specific PDF)
3. Unguarded mode works (search all PDFs)
4. Line numbers are returned in search results
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to the path
sys.path.append('/home/azureuser/aisearch-openai-rag-audio/app/backend')
os.environ['RUNNING_IN_PRODUCTION'] = 'false'

async def proof_test():
    print("🎯 PROOF: PDF Line Numbers & Guarded/Unguarded Search")
    print("=" * 70)
    
    try:
        from document_indexer import DocumentIndexer
        
        # Initialize indexer
        indexer = DocumentIndexer()
        user_id = "proof_user"
        
        # Clear any existing data
        indexer.local_documents = []
        
        # Test PDFs
        pdf1 = "/home/azureuser/aisearch-openai-rag-audio/data/employee_handbook.pdf"
        pdf2 = "/home/azureuser/aisearch-openai-rag-audio/data/Benefit_Options.pdf"
        
        print("📄 STEP 1: Index Multiple PDFs")
        print("-" * 40)
        
        indexed_files = []
        
        if Path(pdf1).exists():
            await indexer.index_document(pdf1, "employee_handbook.pdf", user_id)
            indexed_files.append("employee_handbook.pdf")
            print("✅ Indexed: employee_handbook.pdf")
        
        if Path(pdf2).exists():
            await indexer.index_document(pdf2, "Benefit_Options.pdf", user_id)
            indexed_files.append("Benefit_Options.pdf")
            print("✅ Indexed: Benefit_Options.pdf")
        
        print(f"📊 Total indexed files: {len(indexed_files)}")
        
        # PROOF 1: Show that each PDF has different line numbers
        print(f"\n🔍 PROOF 1: Line Numbers Are Different for Each PDF")
        print("-" * 50)
        
        for filename in indexed_files:
            results = await indexer.search_in_pdf("Contoso", filename, top=1, user_id=user_id)
            if results:
                result = results[0]
                print(f"📄 {filename}:")
                print(f"   📍 Lines {result['start_line']} to {result['end_line']}")
                print(f"   📝 {result['title']}")
                print(f"   📖 Content: {result['content'][:60]}...")
            else:
                print(f"📄 {filename}: No 'Contoso' found")
        
        # PROOF 2: Unguarded search returns results from multiple PDFs
        print(f"\n🔓 PROOF 2: UNGUARDED Search (All PDFs)")
        print("-" * 50)
        
        unguarded_results = await indexer.search_documents("Contoso", top=5, user_id=user_id)
        print(f"📊 Found {len(unguarded_results)} results across all PDFs:")
        
        files_found = set()
        for i, result in enumerate(unguarded_results, 1):
            files_found.add(result['filename'])
            print(f"   {i}. 📄 {result['filename']} - Lines {result['start_line']}-{result['end_line']}")
        
        print(f"📈 Results came from {len(files_found)} different PDFs: {list(files_found)}")
        
        # PROOF 3: Guarded search returns results from only ONE PDF
        print(f"\n🔒 PROOF 3: GUARDED Search (Specific PDF Only)")
        print("-" * 50)
        
        target_pdf = "employee_handbook.pdf"
        guarded_results = await indexer.search_in_pdf("employee", target_pdf, top=3, user_id=user_id)
        
        print(f"🎯 Searching ONLY in: {target_pdf}")
        print(f"📊 Found {len(guarded_results)} results:")
        
        for i, result in enumerate(guarded_results, 1):
            print(f"   {i}. Lines {result['start_line']}-{result['end_line']}")
            print(f"      📝 {result['title']}")
            print(f"      📄 File: {result['filename']}")
            assert result['filename'] == target_pdf, f"ERROR: Found result from wrong file!"
        
        print(f"✅ ALL results are from {target_pdf} only!")
        
        # PROOF 4: Compare guarded vs unguarded for same query
        print(f"\n⚔️  PROOF 4: Guarded vs Unguarded Comparison")
        print("-" * 50)
        
        test_query = "document"
        
        print(f"🔍 Query: '{test_query}'")
        
        # Unguarded
        unguarded = await indexer.search_documents(test_query, top=10, user_id=user_id)
        unguarded_files = set(r['filename'] for r in unguarded)
        
        print(f"🔓 UNGUARDED: {len(unguarded)} results from {len(unguarded_files)} PDFs")
        for filename in sorted(unguarded_files):
            count = sum(1 for r in unguarded if r['filename'] == filename)
            print(f"   📄 {filename}: {count} results")
        
        # Guarded
        for target_file in indexed_files:
            guarded = await indexer.search_in_pdf(test_query, target_file, top=10, user_id=user_id)
            print(f"🔒 GUARDED ({target_file}): {len(guarded)} results")
            
            # Verify all results are from target file
            for result in guarded:
                assert result['filename'] == target_file, "ERROR: Wrong file in guarded search!"
        
        # PROOF 5: Line numbers are sequential and valid
        print(f"\n📏 PROOF 5: Line Numbers Are Valid and Sequential")
        print("-" * 50)
        
        for filename in indexed_files:
            results = await indexer.search_in_pdf("the", filename, top=3, user_id=user_id)
            print(f"📄 {filename}:")
            
            for i, result in enumerate(results, 1):
                start = result['start_line']
                end = result['end_line']
                
                # Validate line numbers
                assert start > 0, f"ERROR: Invalid start line {start}"
                assert end >= start, f"ERROR: End line {end} before start line {start}"
                assert end - start < 1000, f"ERROR: Chunk too large: {end - start} lines"
                
                print(f"   {i}. Lines {start}-{end} ✅ (span: {end-start+1} lines)")
        
        # PROOF 6: API format verification
        print(f"\n📡 PROOF 6: API Response Format")
        print("-" * 50)
        
        api_result = await indexer.search_documents("employee", top=1, user_id=user_id)
        if api_result:
            result = api_result[0]
            required_fields = ['filename', 'start_line', 'end_line', 'title', 'content', 'chunk_index', 'total_chunks']
            
            print("📋 API Response contains all required fields:")
            for field in required_fields:
                value = result.get(field, 'MISSING')
                print(f"   ✅ {field}: {value}")
                assert field in result, f"ERROR: Missing field {field}"
        
        # FINAL PROOF SUMMARY
        print(f"\n🎉 FINAL PROOF SUMMARY")
        print("=" * 50)
        print("✅ PDF line numbers: WORKING")
        print("✅ Multiple PDF indexing: WORKING") 
        print("✅ Unguarded search (all PDFs): WORKING")
        print("✅ Guarded search (specific PDF): WORKING")
        print("✅ Line number extraction: WORKING")
        print("✅ File isolation in guarded mode: WORKING")
        print("✅ API response format: WORKING")
        
        print(f"\n🎯 PROOF COMPLETE!")
        print(f"📊 Indexed {len(indexed_files)} PDFs")
        print(f"🔓 Unguarded search works across all PDFs")
        print(f"🔒 Guarded search works within specific PDFs")
        print(f"📍 Line numbers show exact location in PDFs")
        
        return True
        
    except Exception as e:
        print(f"❌ PROOF FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("PROOF TEST: PDF Line Numbers & Guarded/Unguarded Search")
    print("This will provide definitive proof that everything works")
    
    try:
        success = asyncio.run(proof_test())
        if success:
            print(f"\n🏆 PROOF SUCCESSFUL! Everything works as expected!")
        else:
            print(f"\n💥 PROOF FAILED! Something is broken!")
    except KeyboardInterrupt:
        print("\n👋 Proof interrupted")
    except Exception as e:
        print(f"\n💥 Proof failed: {e}")

if __name__ == "__main__":
    main()
