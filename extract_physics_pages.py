#!/usr/bin/env python3
"""
Extract specific pages from physics book to find Bernoulli's equation faster
"""
import PyPDF2
import sys
from pathlib import Path

def extract_pages(input_pdf, output_pdf, start_page, end_page):
    """Extract pages from start_page to end_page (1-indexed)"""
    try:
        with open(input_pdf, 'rb') as infile:
            reader = PyPDF2.PdfReader(infile)
            writer = PyPDF2.PdfWriter()
            
            total_pages = len(reader.pages)
            print(f"Total pages in source: {total_pages}")
            
            # Convert to 0-indexed
            start_idx = start_page - 1
            end_idx = min(end_page - 1, total_pages - 1)
            
            print(f"Extracting pages {start_page}-{end_page} (indices {start_idx}-{end_idx})")
            
            for page_num in range(start_idx, end_idx + 1):
                page = reader.pages[page_num]
                writer.add_page(page)
                print(f"Added page {page_num + 1}")
            
            with open(output_pdf, 'wb') as outfile:
                writer.write(outfile)
            
            print(f"✅ Created {output_pdf} with pages {start_page}-{end_page}")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    input_pdf = "/home/azureuser/aisearch-openai-rag-audio/app/backend/uploads/Concepts-of-Physics-By-H-C-Verma.pdf"
    
    # Create multiple small sections to search for Bernoulli
    sections = [
        ("physics_fluid_dynamics_1.pdf", 15, 25),  # Pages 15-25 (likely fluid mechanics)
        ("physics_fluid_dynamics_2.pdf", 30, 40),  # Pages 30-40
        ("physics_mechanics_1.pdf", 45, 55),       # Pages 45-55
        ("physics_mechanics_2.pdf", 60, 70),       # Pages 60-70
    ]
    
    for output_name, start, end in sections:
        output_path = f"/home/azureuser/aisearch-openai-rag-audio/{output_name}"
        print(f"\n📄 Creating {output_name}...")
        extract_pages(input_pdf, output_path, start, end)
