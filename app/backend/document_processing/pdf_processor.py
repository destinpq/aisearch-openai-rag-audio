"""
PDF processing module for extracting and processing content from PDF documents using AI.
"""

import logging
import os
from typing import List, Dict, Any

import pdfplumber

# OCR imports for scanned PDFs
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

logger = logging.getLogger("voicerag.pdf_processor")

# GPT-4.1 Configuration for intelligent chunking
GPT_ENDPOINT = os.environ.get("GPT_ENDPOINT")
GPT_API_KEY = os.environ.get("GPT_API_KEY")

# Function schema for GPT-4.1 to create intelligent chunks
CHUNK_ANALYSIS_FUNCTION = {
    "type": "function",
    "function": {
        "name": "create_intelligent_chunks",
        "description": "Analyze text content and create meaningful, intelligent chunks with titles. Filter out irrelevant information and organize content logically.",
        "parameters": {
            "type": "object",
            "properties": {
                "chunks": {
                    "type": "array",
                    "description": "Array of intelligent chunks created from the text",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Short, descriptive title for this chunk (max 100 characters)"
                            },
                            "content": {
                                "type": "string",
                                "description": "The meaningful content for this chunk, filtered and organized"
                            },
                            "relevance_score": {
                                "type": "number",
                                "description": "Relevance score from 0.0 to 1.0 (1.0 being most relevant)"
                            },
                            "category": {
                                "type": "string",
                                "description": "Category or topic this chunk belongs to"
                            }
                        },
                        "required": ["title", "content", "relevance_score", "category"]
                    }
                },
                "analysis_summary": {
                    "type": "string",
                    "description": "Brief summary of what was analyzed and how chunks were created"
                }
            },
            "required": ["chunks", "analysis_summary"]
        }
    }
}

def _extract_with_ocr(pdf_path):
    """Extract text using OCR for scanned PDFs - process ALL pages concurrently"""
    if not OCR_AVAILABLE:
        raise ValueError("OCR libraries not available - cannot extract from scanned PDF")
    
    try:
        import concurrent.futures
        import threading
        
        logger.info("Starting concurrent OCR extraction for ALL pages...")
        
        # Convert ALL pages to images first
        images = convert_from_path(pdf_path, dpi=150)
        total_pages = len(images)
        logger.info(f"Converting ALL {total_pages} pages to images for OCR (batch mode, 1 worker)")

        def process_page(page_num, image):
            try:
                page_text = pytesseract.image_to_string(image, lang='eng', config='--psm 6')
                if page_text.strip():
                    return f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                return f"\n--- Page {page_num + 1} ---\n[No text detected]\n"
            except Exception as e:
                logger.error(f"OCR failed for page {page_num + 1}: {e}")
                return f"\n--- Page {page_num + 1} ---\n[OCR Error: {e}]\n"

        # Batch processing: 10 pages at a time, 1 worker
        all_text = ""
        batch_size = 10
        for batch_start in range(0, total_pages, batch_size):
            batch_end = min(batch_start + batch_size, total_pages)
            logger.info(f"Processing pages {batch_start+1} to {batch_end} with 1 worker...")
            page_results = {}
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future_to_page = {
                    executor.submit(process_page, i, images[i]): i
                    for i in range(batch_start, batch_end)
                }
                try:
                    for future in concurrent.futures.as_completed(future_to_page, timeout=600):
                        page_num = future_to_page[future]
                        try:
                            page_text = future.result(timeout=180)  # 3 min per page timeout
                            page_results[page_num] = page_text
                            logger.info(f"Completed OCR for page {page_num + 1}/{total_pages}")
                        except concurrent.futures.TimeoutError:
                            logger.error(f"Timeout processing page {page_num + 1}")
                            page_results[page_num] = f"\n--- Page {page_num + 1} ---\n[Timeout Error]\n"
                except concurrent.futures.TimeoutError:
                    logger.error(f"Timeout processing batch {batch_start+1}-{batch_end}")
                # Append results in order
                for i in range(batch_start, batch_end):
                    all_text += page_results.get(i, f"\n--- Page {i + 1} ---\n[No OCR result]\n")
            
            # Combine results in page order
            for i in range(total_pages):
                if i in page_results:
                    all_text += page_results[i]
        
        if all_text.strip():
            logger.info(f"Concurrent OCR extracted {len(all_text)} characters from {total_pages} pages!")
            return all_text
        else:
            raise ValueError("OCR could not extract any text from PDF")
            
    except Exception as e:
        logger.error(f"Concurrent OCR extraction failed: {e}")
        raise ValueError(f"Concurrent OCR extraction failed: {e}")

def extract_pdf_text(file_source, is_path=False):
    """
    Extract text from a PDF file. Falls back to OCR for scanned PDFs.
    
    Args:
        file_source: Either a file-like object or a path string
        is_path: Boolean indicating if file_source is a path
    
    Returns:
        str: The extracted text from the PDF
    """
    try:
        # First try regular text extraction
        with pdfplumber.open(file_source) as pdf:
            if not pdf.pages:
                raise ValueError("PDF contains no pages")
            
            total_pages = len(pdf.pages)
            logger.info(f"Extracting text from PDF with {total_pages} pages")
            
            pages = []
            for i, page in enumerate(pdf.pages):
                try:
                    if i % 10 == 0 and i > 0:
                        logger.info(f"Processed {i}/{total_pages} pages")
                        
                    text = page.extract_text() or ""
                    pages.append(text)
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {i+1}: {e}")
                    pages.append("")
            
            combined_text = "\n".join(pages)
            text_length = len(combined_text)
            
            # If we got good text, return it
            if combined_text.strip() and text_length > 100:
                logger.info(f"Successfully extracted {text_length} characters from PDF")
                return combined_text
            
            # If no text or very little text, try OCR
            logger.info("Little to no text found, attempting OCR extraction...")
            return _extract_with_ocr(file_source)
            
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        raise

def create_intelligent_chunks_with_ai(text: str, document_title: str = "Document") -> List[Dict[str, Any]]:
    """
    Create chunks from text using direct chunking method.
    
    Args:
        text: The text to analyze
        document_title: Optional title of the document
        
    Returns:
        list: A list of dictionaries with title and content keys
    """
    if not text or not text.strip():
        return []
    
    logger.info("Creating chunks using direct chunking method...")
    
    # Always use direct chunking
    return direct_chunk(text, document_title)

def direct_chunk(text: str, document_title: str = "Document", chunk_size: int = 3000) -> List[Dict[str, Any]]:
    """
    Create direct chunks from text without AI processing.
    This is a simple chunking method that splits text into fixed-size chunks with overlap.
    
    Args:
        text: The text to chunk
        document_title: Optional title of the document
        chunk_size: Size of each chunk in characters
        
    Returns:
        list: A list of dictionaries with title and content keys
    """
    if not text or not text.strip():
        return []
    
    # Split text into lines
    lines = text.split('\n')
    total_lines = len(lines)
    
    if total_lines == 0:
        return []
    
    # Approximate lines per chunk (assuming ~50 chars per line)
    lines_per_chunk = chunk_size // 50
    
    # Add 10% overlap between chunks
    overlap_lines = lines_per_chunk // 10
    
    chunks = []
    chunk_count = (total_lines + lines_per_chunk - overlap_lines - 1) // (lines_per_chunk - overlap_lines)
    
    for i in range(chunk_count):
        start_idx = i * (lines_per_chunk - overlap_lines)
        end_idx = min(start_idx + lines_per_chunk, total_lines)
        
        # Don't process beyond the text length
        if start_idx >= total_lines:
            break
            
        chunk_lines = lines[start_idx:end_idx]
        chunk_text = "\n".join(chunk_lines)
        chunk_number = i + 1
        
        chunk = {
            "title": f"{document_title} - Part {chunk_number}/{chunk_count}",
            "content": chunk_text,
            "category": "Document Section",
            "relevance_score": 0.8,
            "start_line": start_idx + 1,
            "end_line": end_idx
        }
        
        chunks.append(chunk)
    
    return chunks

def process_large_text(text: str, document_title: str = "Document") -> List[Dict[str, Any]]:
    """
    Process large text by breaking it into manageable sections and directly creating chunks.
    This avoids recursion by not calling create_intelligent_chunks_with_ai again.
    
    Args:
        text: The text to process
        document_title: Optional title of the document
        
    Returns:
        list: The processed chunks
    """
    # Maximum text size to process at once
    MAX_TEXT_SIZE = 15000
    
    # Maximum number of sections to process to avoid excessive processing
    MAX_SECTIONS = 20
    
    logger.info(f"Breaking large text ({len(text)} chars) into direct chunks")
    
    # Use the direct chunking method with a smaller chunk size
    return direct_chunk(text, document_title, chunk_size=MAX_TEXT_SIZE // 2)