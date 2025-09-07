#!/usr/bin/env python3
"""
Direct search for Bernoulli's equation in the physics book with line numbers
"""
import os
import sys
sys.path.insert(0, '/home/azureuser/aisearch-openai-rag-audio/app/backend')
sys.path.insert(0, '/home/azureuser/aisearch-openai-rag-audio/app/backend/document_processing')

from document_processing.pdf_processor import extract_pdf_text, _extract_with_ocr
import pdfplumber
import re

def find_bernoulli_in_physics_book():
    pdf_path = "/home/azureuser/aisearch-openai-rag-audio/app/backend/uploads/Concepts-of-Physics-By-H-C-Verma.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Physics book not found at: {pdf_path}")
        return
    
    print(f"🔍 Searching for Bernoulli's equation in: {pdf_path}")
    print("=" * 80)
    
    # Search patterns for Bernoulli
    patterns = [
        r'(?i)bernoulli.*equation',
        r'(?i)bernoulli.*principle',
        r'(?i)bernoulli.*theorem',
        r'(?i)p\s*\+\s*½\s*ρ\s*v²\s*\+\s*ρ\s*g\s*h',  # Bernoulli equation format
        r'(?i)p₁\s*\+\s*½\s*ρ\s*v₁².*p₂\s*\+\s*½\s*ρ\s*v₂²',  # Bernoulli comparison
        r'(?i)bernoulli',  # Just search for the name
    ]
    
    found_matches = []
    
    try:
        # First try to extract all text at once
        print("📄 Extracting text from entire PDF...")
        full_text = extract_pdf_text(pdf_path, is_path=True)
        
        if full_text and len(full_text.strip()) > 100:
            print(f"✅ Extracted {len(full_text)} characters from PDF")
            
            # Search in full text
            lines = full_text.split('\n')
            current_page = 1
            
            for line_num, line in enumerate(lines, 1):
                # Try to detect page boundaries (common in PDF extractions)
                if line.strip().startswith('Page ') or re.match(r'^\d+$', line.strip()):
                    try:
                        current_page = int(line.strip().split()[-1])
                    except:
                        pass
                
                for pattern in patterns:
                    if re.search(pattern, line):
                        found_matches.append({
                            'page': current_page,
                            'line': line_num,
                            'text': line.strip(),
                            'pattern': pattern
                        })
                        print(f"✅ FOUND on estimated Page {current_page}, Line {line_num}: {line.strip()}")
        
        else:
            print("❌ Could not extract text. PDF might be scanned. Trying OCR...")
            # Try OCR extraction
            ocr_text = _extract_with_ocr(pdf_path)
            
            if ocr_text:
                print(f"✅ OCR extracted {len(ocr_text)} characters")
                lines = ocr_text.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern in patterns:
                        if re.search(pattern, line):
                            found_matches.append({
                                'page': 'OCR',
                                'line': line_num,
                                'text': line.strip(),
                                'pattern': pattern
                            })
                            print(f"✅ FOUND via OCR at Line {line_num}: {line.strip()}")
            else:
                print("❌ OCR extraction also failed")
    
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        
        # Try manual page-by-page approach
        print("🔄 Trying page-by-page extraction...")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                print(f"📚 PDF has {total_pages} pages")
                
                # Search first 20 pages for Bernoulli
                for page_num in range(min(20, total_pages)):
                    try:
                        page = pdf.pages[page_num]
                        page_text = page.extract_text()
                        
                        if page_text:
                            lines = page_text.split('\n')
                            for line_num, line in enumerate(lines, 1):
                                for pattern in patterns:
                                    if re.search(pattern, line):
                                        found_matches.append({
                                            'page': page_num + 1,
                                            'line': line_num,
                                            'text': line.strip(),
                                            'pattern': pattern
                                        })
                                        print(f"✅ FOUND on Page {page_num + 1}, Line {line_num}: {line.strip()}")
                        
                        if page_num % 5 == 0:
                            print(f"   📄 Processed page {page_num + 1}")
                        
                    except Exception as pe:
                        print(f"   ❌ Error on page {page_num + 1}: {pe}")
                        continue
        
        except Exception as e2:
            print(f"❌ Manual extraction failed: {e2}")
    
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
        print("\n💡 The book might be a scanned PDF requiring full OCR processing")
        print("   or Bernoulli's equation might be in a different section")

if __name__ == "__main__":
    find_bernoulli_in_physics_book()
