#!/usr/bin/env python3

import sys
import os
sys.path.append('/home/azureuser/aisearch-openai-rag-audio/app/backend')

import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import json
import uuid
from pathlib import Path

def extract_text_with_ocr(pdf_path):
    """Extract text from your scanned physics book using OCR"""
    print(f"📖 Starting OCR extraction from: {pdf_path}")
    
    try:
        # Convert PDF pages to images
        print("🖼️  Converting PDF pages to images...")
        images = convert_from_path(pdf_path, dpi=200, first_page=1, last_page=5)  # Process first 5 pages for testing
        print(f"✅ Converted {len(images)} pages to images")
        
        all_text = ""
        for i, image in enumerate(images):
            print(f"🔍 Processing page {i+1}/{len(images)} with OCR...")
            
            # Use OCR to extract text
            page_text = pytesseract.image_to_string(image, lang='eng')
            
            if page_text.strip():
                all_text += f"\n--- Page {i+1} ---\n{page_text}\n"
                print(f"✅ Extracted {len(page_text)} characters from page {i+1}")
            else:
                print(f"⚠️  No text found on page {i+1}")
                
        if all_text.strip():
            print(f"🎉 Successfully extracted {len(all_text)} total characters!")
            return all_text
        else:
            print("❌ No text could be extracted with OCR")
            return None
            
    except Exception as e:
        print(f"❌ OCR extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_simple_chunks(text, chunk_size=2000):
    """Create simple text chunks from the extracted text"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        if current_size + len(word) > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_size = len(word)
        else:
            current_chunk.append(word)
            current_size += len(word) + 1
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def index_physics_book_with_ocr():
    """Index your physics book using OCR"""
    pdf_path = "/home/azureuser/aisearch-openai-rag-audio/app/backend/uploads/Concepts-of-Physics-By-H-C-Verma.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Physics book not found at: {pdf_path}")
        return False
    
    # Extract text using OCR
    text = extract_text_with_ocr(pdf_path)
    if not text:
        return False
    
    print(f"📝 Creating chunks from extracted text...")
    chunks = create_simple_chunks(text, chunk_size=1500)
    print(f"✅ Created {len(chunks)} chunks")
    
    # Load existing local storage
    local_storage_file = "/home/azureuser/aisearch-openai-rag-audio/app/backend/local_documents.json"
    
    if os.path.exists(local_storage_file):
        with open(local_storage_file, 'r') as f:
            existing_docs = json.load(f)
    else:
        existing_docs = []
    
    # Create documents for local storage
    filename = "Concepts-of-Physics-By-H-C-Verma.pdf"
    new_documents = []
    
    for i, chunk in enumerate(chunks):
        chunk_id = f"{Path(filename).stem}_{i+1}_{uuid.uuid4().hex[:8]}"
        
        document = {
            "chunk_id": chunk_id,
            "parent_id": Path(filename).stem,
            "title": f"{filename} - Part {i+1}/{len(chunks)} (OCR)",
            "chunk": chunk,
            "filename": filename,
            "user_id": "demo@example.com",
            "start_line": i * 50 + 1,
            "end_line": (i + 1) * 50,
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
    
    print(f"✅ Successfully indexed {len(new_documents)} chunks from YOUR physics book!")
    print(f"📊 Total documents in storage: {len(all_documents)}")
    
    # Show sample physics content
    if new_documents:
        sample = new_documents[0]
        print(f"\n📄 Sample physics content:")
        print(f"   Title: {sample['title']}")
        print(f"   Content: {sample['chunk'][:300]}...")
    
    return True

if __name__ == "__main__":
    print("🔬 Processing YOUR Concepts of Physics book with OCR...")
    success = index_physics_book_with_ocr()
    
    if success:
        print("\n🎉 YOUR PHYSICS BOOK IS NOW INDEXED!")
        print("💡 You can now search for physics concepts, laws, equations, etc.")
        print("🔍 Try searching for: 'Newton', 'energy', 'momentum', 'force', 'motion'")
    else:
        print("\n💥 Failed to index your physics book.")
