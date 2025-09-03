#!/usr/bin/env python3
"""
Direct Line Number Extraction from Multiple PDFs

This script demonstrates direct usage of the DocumentIndexer to:
1. Index multiple PDFs with line tracking
2. Search and get line numbers from all PDFs

Usage: python direct_line_extraction.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the path
sys.path.append('/home/azureuser/aisearch-openai-rag-audio/app/backend')

from document_indexer import DocumentIndexer

async def demo_line_extraction():
    """Demonstrate line number extraction from multiple PDFs"""
    
    print("🚀 Direct Line Number Extraction Demo")
    print("=" * 50)
    
    # Initialize the document indexer
    indexer = DocumentIndexer()
    
    # PDF files to process
    pdf_files = [
        "/home/azureuser/aisearch-openai-rag-audio/data/employee_handbook.pdf",
        "/home/azureuser/aisearch-openai-rag-audio/data/Benefit_Options.pdf",
        "/home/azureuser/aisearch-openai-rag-audio/data/Northwind_Health_Plus_Benefits_Details.pdf"
    ]
    
    # Filter to existing files
    existing_files = [f for f in pdf_files if Path(f).exists()]
    
    if not existing_files:
        print("❌ No PDF files found!")
        return
    
    print(f"📄 Found {len(existing_files)} PDF files:")
    for f in existing_files:
        print(f"   - {Path(f).name}")
    
    # Step 1: Index all PDFs
    print(f"\n🔄 Indexing PDFs...")
    indexed_count = 0
    
    for pdf_file in existing_files:
        filename = Path(pdf_file).name
        print(f"   📄 Processing {filename}...")
        
        try:
            success = await indexer.index_document(pdf_file, filename, "demo_user")
            if success:
                print(f"   ✅ Successfully indexed {filename}")
                indexed_count += 1
            else:
                print(f"   ❌ Failed to index {filename}")
        except Exception as e:
            print(f"   ❌ Error indexing {filename}: {e}")
    
    print(f"\n✅ Successfully indexed {indexed_count}/{len(existing_files)} files")
    
    if indexed_count == 0:
        print("❌ No files were indexed. Cannot proceed with search.")
        return
    
    # Step 2: Search across all PDFs for different terms
    search_terms = [
        "benefits",
        "vacation",
        "health insurance", 
        "employee",
        "salary",
        "policy"
    ]
    
    print(f"\n🔍 Searching across all indexed PDFs...")
    
    for term in search_terms:
        print(f"\n🔎 Searching for: '{term}'")
        print("-" * 40)
        
        try:
            results = await indexer.search_documents(term, top=5, user_id="demo_user")
            
            if results:
                print(f"   📊 Found {len(results)} results:")
                
                # Group results by filename for better display
                by_file = {}
                for result in results:
                    filename = result['filename']
                    if filename not in by_file:
                        by_file[filename] = []
                    by_file[filename].append(result)
                
                for filename, file_results in by_file.items():
                    print(f"\n   📄 From {filename}:")
                    for i, result in enumerate(file_results, 1):
                        print(f"      {i}. Lines {result['start_line']}-{result['end_line']}")
                        print(f"         Title: {result['title']}")
                        print(f"         Chunk: {result['chunk_index']}/{result['total_chunks']}")
                        content_preview = result['content'][:150].replace('\n', ' ')
                        print(f"         Content: {content_preview}...")
                        print()
            else:
                print(f"   ❌ No results found for '{term}'")
                
        except Exception as e:
            print(f"   ❌ Search failed for '{term}': {e}")
    
    # Step 3: Demonstrate cross-document search
    print(f"\n🔄 Cross-Document Search Examples")
    print("=" * 40)
    
    cross_searches = [
        "employee benefits policy",
        "health insurance coverage",
        "vacation time policy"
    ]
    
    for query in cross_searches:
        print(f"\n🔎 Multi-PDF Query: '{query}'")
        print("-" * 30)
        
        try:
            results = await indexer.search_documents(query, top=10, user_id="demo_user")
            
            if results:
                # Show which PDFs contain relevant information
                files_with_results = set()
                total_line_references = []
                
                for result in results:
                    files_with_results.add(result['filename'])
                    total_line_references.append({
                        'file': result['filename'],
                        'lines': f"{result['start_line']}-{result['end_line']}",
                        'title': result['title']
                    })
                
                print(f"   📊 Found in {len(files_with_results)} different PDFs:")
                for filename in sorted(files_with_results):
                    file_refs = [ref for ref in total_line_references if ref['file'] == filename]
                    print(f"      📄 {filename}: {len(file_refs)} references")
                    for ref in file_refs[:3]:  # Show first 3 references
                        print(f"         - Lines {ref['lines']}: {ref['title']}")
                
            else:
                print(f"   ❌ No results found")
                
        except Exception as e:
            print(f"   ❌ Search failed: {e}")

if __name__ == "__main__":
    print("Direct Line Number Extraction Demo")
    print("This will directly index PDFs and extract line numbers")
    
    try:
        asyncio.run(demo_line_extraction())
        print(f"\n🎉 Demo completed successfully!")
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
