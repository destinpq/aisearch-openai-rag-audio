#!/usr/bin/env python3

import sys
import os
sys.path.append('/home/azureuser/aisearch-openai-rag-audio/app/backend')

from document_processing.pdf_processor import extract_pdf_text, create_intelligent_chunks_with_ai
import json
import uuid
from pathlib import Path

def manually_index_physics_book():
    pdf_path = "/home/azureuser/aisearch-openai-rag-audio/app/backend/uploads/Concepts-of-Physics-By-H-C-Verma.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Physics book not found at: {pdf_path}")
        return False
        
    print(f"📖 Processing physics book: {pdf_path}")
    
    try:
        # Extract text from PDF
        print("🔍 Extracting text from PDF...")
        text = extract_pdf_text(pdf_path)
        
        if not text:
            print("❌ No text extracted from PDF")
            return False
            
        print(f"✅ Extracted {len(text)} characters of text")
        
        # Create chunks
        print("📝 Creating intelligent chunks...")
        filename = "Concepts-of-Physics-By-H-C-Verma.pdf"
        chunks = create_intelligent_chunks_with_ai(text, filename)
        
        if not chunks:
            print("❌ No chunks created")
            return False
            
        print(f"✅ Created {len(chunks)} chunks")
        
        # Load existing local storage
        local_storage_file = "/home/azureuser/aisearch-openai-rag-audio/app/backend/local_documents.json"
        
        if os.path.exists(local_storage_file):
            with open(local_storage_file, 'r') as f:
                existing_docs = json.load(f)
        else:
            existing_docs = []
            
        print(f"📚 Found {len(existing_docs)} existing documents in local storage")
        
        # Create documents for local storage
        new_documents = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{Path(filename).stem}_{i+1}_{uuid.uuid4().hex[:8]}"
            
            document = {
                "chunk_id": chunk_id,
                "parent_id": Path(filename).stem,
                "title": f"{filename} - Part {i+1}/{len(chunks)}",
                "chunk": chunk.get('content', ''),
                "filename": filename,
                "user_id": "demo@example.com",  # Your user ID
                "start_line": chunk.get('start_line', i * 50 + 1),
                "end_line": chunk.get('end_line', (i + 1) * 50),
                "chunk_index": i + 1,
                "total_chunks": len(chunks)
            }
            new_documents.append(document)
            
        # Remove any existing documents for this file
        existing_docs = [doc for doc in existing_docs if doc.get('filename') != filename]
        
        # Add new documents
        all_documents = existing_docs + new_documents
        
        # Save to local storage
        with open(local_storage_file, 'w') as f:
            json.dump(all_documents, f, indent=2)
            
        print(f"✅ Successfully indexed {len(new_documents)} chunks from physics book!")
        print(f"📊 Total documents in storage: {len(all_documents)}")
        
        # Show sample content
        if new_documents:
            sample = new_documents[0]
            print(f"\n📄 Sample chunk:")
            print(f"   Title: {sample['title']}")
            print(f"   Content: {sample['chunk'][:200]}...")
            
        return True
        
    except Exception as e:
        print(f"❌ Error processing physics book: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = manually_index_physics_book()
    if success:
        print("\n🎉 Physics book successfully indexed! You can now search for physics concepts.")
    else:
        print("\n💥 Failed to index physics book.")
