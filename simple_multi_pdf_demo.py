#!/usr/bin/env python3
"""
Simple Multi-PDF Line Number Demo

This demonstrates the core functionality without requiring a full server setup.
Shows how multiple PDFs are indexed and searched with line numbers.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to the path
sys.path.append('/home/azureuser/aisearch-openai-rag-audio/app/backend')

# Set minimal environment to avoid Azure dependency issues
os.environ['RUNNING_IN_PRODUCTION'] = 'false'

async def simple_multi_pdf_demo():
    """Simple demo of multi-PDF indexing with line numbers"""
    
    print("🚀 Simple Multi-PDF Line Number Demo")
    print("=" * 60)
    
    try:
        from document_indexer import DocumentIndexer
        
        # Initialize indexer
        indexer = DocumentIndexer()
        print("✅ Document indexer initialized (using local storage fallback)")
        
        # Find PDF files
        pdf_files = [
            "/home/azureuser/aisearch-openai-rag-audio/data/employee_handbook.pdf",
            "/home/azureuser/aisearch-openai-rag-audio/data/Benefit_Options.pdf",
            "/home/azureuser/aisearch-openai-rag-audio/data/Northwind_Health_Plus_Benefits_Details.pdf"
        ]
        
        existing_files = [f for f in pdf_files if Path(f).exists()]
        
        if not existing_files:
            print("❌ No PDF files found! Looking for files in:")
            for f in pdf_files:
                print(f"   - {f}")
            return
        
        print(f"\n📄 Found {len(existing_files)} PDF files to process:")
        for f in existing_files:
            print(f"   - {Path(f).name}")
        
        # Step 1: Index all PDFs
        print(f"\n🔄 Indexing PDFs with line number tracking...")
        
        indexed_files = []
        for pdf_file in existing_files:
            filename = Path(pdf_file).name
            print(f"\n   📄 Processing: {filename}")
            
            try:
                success = await indexer.index_document(pdf_file, filename, "demo_user")
                if success:
                    print(f"   ✅ Successfully indexed {filename}")
                    indexed_files.append(filename)
                else:
                    print(f"   ❌ Failed to index {filename}")
            except Exception as e:
                print(f"   ❌ Error indexing {filename}: {e}")
        
        if not indexed_files:
            print("\n❌ No files were successfully indexed")
            return
        
        print(f"\n✅ Successfully indexed {len(indexed_files)} files")
        print(f"   Files: {', '.join(indexed_files)}")
        
        # Step 2: Search for content and show line numbers
        print(f"\n🔍 Searching across all indexed PDFs for line numbers...")
        
        search_queries = [
            "employee benefits",
            "health insurance", 
            "company policy",
            "vacation",
            "workplace"
        ]
        
        for query in search_queries:
            print(f"\n🔎 Query: '{query}'")
            print("-" * 50)
            
            try:
                results = await indexer.search_documents(query, top=5, user_id="demo_user")
                
                if results:
                    # Group results by file
                    files_found = {}
                    for result in results:
                        filename = result['filename']
                        if filename not in files_found:
                            files_found[filename] = []
                        files_found[filename].append(result)
                    
                    print(f"   📊 Found {len(results)} results in {len(files_found)} file(s)")
                    
                    for filename, file_results in files_found.items():
                        print(f"\n   📄 Results from '{filename}':")
                        for i, result in enumerate(file_results, 1):
                            lines_info = f"Lines {result['start_line']}-{result['end_line']}" if result['start_line'] > 0 else "Line info N/A"
                            print(f"      {i}. {lines_info}")
                            print(f"         📝 {result['title']}")
                            print(f"         🔢 Chunk {result['chunk_index']}/{result['total_chunks']}")
                            content_preview = result['content'][:120].replace('\n', ' ')
                            print(f"         📖 {content_preview}...")
                            print()
                    
                    # Summary
                    if len(files_found) > 1:
                        print(f"   🎯 '{query}' found in {len(files_found)} different PDFs!")
                
                else:
                    print(f"   ❌ No results found for '{query}'")
                    
            except Exception as e:
                print(f"   ❌ Search failed for '{query}': {e}")
        
        # Step 3: Demonstrate specific line extraction
        print(f"\n📍 Line Number Extraction Examples")
        print("=" * 50)
        
        specific_queries = [
            "What are the health benefits?",
            "Employee handbook policies",
            "Insurance coverage details"
        ]
        
        for question in specific_queries:
            print(f"\n❓ Question: {question}")
            print("-" * 30)
            
            try:
                results = await indexer.search_documents(question, top=3, user_id="demo_user")
                
                if results:
                    best_match = results[0]
                    print(f"   📄 Best match from: {best_match['filename']}")
                    if best_match['start_line'] > 0:
                        print(f"   📍 Located at: Lines {best_match['start_line']}-{best_match['end_line']}")
                    else:
                        print(f"   📍 Located in: Chunk {best_match['chunk_index']}")
                    print(f"   📝 Section: {best_match['title']}")
                    print(f"   📖 Content preview: {best_match['content'][:200]}...")
                else:
                    print(f"   ❌ No answer found")
                    
            except Exception as e:
                print(f"   ❌ Search failed: {e}")
        
        # Step 4: Show summary statistics
        print(f"\n📊 Summary")
        print("=" * 30)
        print(f"✅ Processed: {len(indexed_files)} PDF files")
        print(f"📄 Files indexed with line numbers:")
        for filename in indexed_files:
            print(f"   - {filename}")
        print(f"\n🎉 All PDFs are now searchable with line number references!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory and have the required dependencies")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("Simple Multi-PDF Line Number Extraction Demo")
    print("This demonstrates indexing multiple PDFs and extracting line numbers")
    print("\nThis demo will:")
    print("1. Index multiple PDF files with line tracking")
    print("2. Search across all PDFs")
    print("3. Return line numbers for each match")
    print("4. Show which PDF contains which information")
    
    input("\nPress Enter to start the demo...")
    
    try:
        asyncio.run(simple_multi_pdf_demo())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")

if __name__ == "__main__":
    main()
