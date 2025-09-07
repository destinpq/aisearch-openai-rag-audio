#!/usr/bin/env python3
"""
Direct search for Bernoulli's equation in the physics book with line numbers
"""
import os
import sys
sys.path.insert(0, '/home/azureuser/aisearch-openai-rag-audio/app/backend')
sys.path.insert(0, '/home/azureuser/aisearch-openai-rag-audio/app/backend/document_processing')

from document_processing.pdf_processor import PDFProcessor
import re

def find_bernoulli_in_physics_book():
    pdf_path = "/home/azureuser/aisearch-openai-rag-audio/app/backend/uploads/Concepts-of-Physics-By-H-C-Verma.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Physics book not found at: {pdf_path}")
        return
    
    print(f"🔍 Searching for Bernoulli's equation in: {pdf_path}")
    print("=" * 80)
    
    processor = PDFProcessor()
    
    # Search patterns for Bernoulli
    patterns = [
        r'(?i)bernoulli.*equation',
        r'(?i)bernoulli.*principle',
        r'(?i)bernoulli.*theorem',
        r'(?i)p\s*\+\s*½\s*ρ\s*v²\s*\+\s*ρ\s*g\s*h',  # Bernoulli equation format
        r'(?i)p₁\s*\+\s*½\s*ρ\s*v₁².*p₂\s*\+\s*½\s*ρ\s*v₂²',  # Bernoulli comparison
    ]
    
    found_matches = []
    
    try:
        # Process pages 1-80 (physics book)
        for page_num in range(1, 81):
            print(f"📄 Processing page {page_num}...")
            
            try:
                # Extract text from page
                page_text = processor._extract_text_from_page(pdf_path, page_num - 1)  # 0-indexed
                
                if not page_text or len(page_text.strip()) < 10:
                    # Try OCR if text extraction failed
                    print(f"   🔍 Trying OCR for page {page_num}")
                    page_text = processor._extract_with_ocr(pdf_path, page_num - 1)
                
                if page_text:
                    lines = page_text.split('\n')
                    
                    # Search each line for Bernoulli patterns
                    for line_num, line in enumerate(lines, 1):
                        for pattern in patterns:
                            if re.search(pattern, line):
                                found_matches.append({
                                    'page': page_num,
                                    'line': line_num,
                                    'text': line.strip(),
                                    'pattern': pattern
                                })
                                print(f"✅ FOUND on Page {page_num}, Line {line_num}: {line.strip()}")
                
            except Exception as e:
                print(f"   ❌ Error processing page {page_num}: {e}")
                continue
    
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        return
    
    print("\n" + "=" * 80)
    print(f"📊 SEARCH RESULTS: Found {len(found_matches)} matches")
    print("=" * 80)
    
    if found_matches:
        for i, match in enumerate(found_matches, 1):
            print(f"\n{i}. PAGE {match['page']}, LINE {match['line']}:")
            print(f"   {match['text']}")
            print(f"   (Pattern: {match['pattern']})")
    else:
        print("❌ No Bernoulli equation found in the physics book")
        print("\n🔍 Let me try broader search terms...")
        
        # Try broader search
        broader_patterns = [
            r'(?i)bernoulli',
            r'(?i)fluid.*dynamics',
            r'(?i)pressure.*velocity',
            r'(?i)conservation.*energy.*fluid'
        ]
        
        # Just check first few pages for broader terms
        for page_num in range(1, 11):
            try:
                page_text = processor._extract_text_from_page(pdf_path, page_num - 1)
                if not page_text:
                    page_text = processor._extract_with_ocr(pdf_path, page_num - 1)
                
                if page_text:
                    for pattern in broader_patterns:
                        if re.search(pattern, page_text):
                            print(f"📍 Found '{pattern}' on page {page_num}")
                            # Show some context
                            lines = page_text.split('\n')
                            for line_num, line in enumerate(lines, 1):
                                if re.search(pattern, line):
                                    print(f"   Line {line_num}: {line.strip()}")
                                    break
                            break
            except:
                continue

if __name__ == "__main__":
    find_bernoulli_in_physics_book()
