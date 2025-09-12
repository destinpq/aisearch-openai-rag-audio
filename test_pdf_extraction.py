#!/usr/bin/env python3

import sys
import os
sys.path.append('/home/azureuser/aisearch-openai-rag-audio/app/backend')

from document_processing.pdf_processor import extract_pdf_text

def test_pdf_extraction():
    pdf_path = "/home/azureuser/aisearch-openai-rag-audio/app/backend/uploads/Concepts-of-Physics-By-H-C-Verma.pdf"
    
    print(f"🔍 Testing PDF extraction on: {pdf_path}")
    print(f"📏 File size: {os.path.getsize(pdf_path)} bytes")
    
    try:
        # Try the original method
        text = extract_pdf_text(pdf_path, is_path=True)
        print(f"✅ Extracted {len(text)} characters")
        print(f"📄 First 500 characters:\n{text[:500]}")
        return True
        
    except Exception as e:
        print(f"❌ Original extraction failed: {e}")
        
        # Try alternative method with PyPDF2
        try:
            import PyPDF2
            print("🔄 Trying PyPDF2...")
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                    
                if text.strip():
                    print(f"✅ PyPDF2 extracted {len(text)} characters")
                    print(f"📄 First 500 characters:\n{text[:500]}")
                    return True
                else:
                    print("❌ PyPDF2 also returned empty text")
                    
        except ImportError:
            print("❌ PyPDF2 not available")
        except Exception as e2:
            print(f"❌ PyPDF2 failed: {e2}")
            
        # Check if it's a scanned PDF
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                print(f"📋 PDF has {len(pdf.pages)} pages")
                
                # Check first page for images
                if pdf.pages:
                    first_page = pdf.pages[0]
                    images = first_page.images
                    text_content = first_page.extract_text()
                    
                    print(f"📷 First page has {len(images)} images")
                    print(f"📝 First page text length: {len(text_content or '')}")
                    
                    if len(images) > 0 and len(text_content or '') < 50:
                        print("🤔 This appears to be a scanned PDF (image-based)")
                        print("💡 You need OCR (Optical Character Recognition) to extract text")
                        return False
                        
        except Exception as e3:
            print(f"❌ PDF analysis failed: {e3}")
            
        return False

if __name__ == "__main__":
    test_pdf_extraction()
