"""
Routes for document processing endpoints.
"""

import logging
import tempfile
import io
import os

from aiohttp import web

from .pdf_processor import extract_pdf_text, create_intelligent_chunks_with_ai

logger = logging.getLogger("voicerag.document_routes")

async def process_pdf(request):
    """
    Process uploaded PDF file, extract content, and create meaningful chunks using AI.
    Returns an array of objects with title and content.
    
    Endpoint: POST /process-pdf
    """
    logger.info("Processing PDF file")
    
    try:
        # Read the uploaded file
        reader = await request.multipart()
        field = await reader.next()
        
        if field is None:
            return web.json_response({"error": "No file uploaded"}, status=400)
            
        if field.name != 'file':
            return web.json_response({"error": "No file field found"}, status=400)
        
        # Check content type
        content_type = field.headers.get('Content-Type', '')
        if 'application/pdf' not in content_type.lower():
            return web.json_response({"error": "Uploaded file is not a PDF"}, status=400)
            
        # Get the file content - save to temp file for large PDFs
        file_data = await field.read()
        
        # Get document title from filename
        filename = field.filename or "Document"
        document_title = os.path.splitext(filename)[0]
        
        if len(file_data) > 10 * 1024 * 1024:  # 10MB
            logger.info(f"Large PDF detected ({len(file_data)/1024/1024:.2f} MB), using temp file")
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(file_data)
                temp_path = temp_file.name
                
            try:
                # Extract text from PDF using the temp file
                text = extract_pdf_text(temp_path, is_path=True)
                chunks = create_intelligent_chunks_with_ai(text, document_title)
                os.unlink(temp_path)  # Clean up temp file
                
                # Format the response to only include title and content
                response_chunks = [{"title": chunk["title"], "content": chunk["content"]} 
                                  for chunk in chunks]
                
                return web.json_response({"chunks": response_chunks})
            except Exception as e:
                # Clean up temp file in case of error
                try:
                    os.unlink(temp_path)
                except:
                    pass
                raise e
        else:
            # Process smaller PDFs in memory
            file_content = io.BytesIO(file_data)
            text = extract_pdf_text(file_content)
            chunks = create_intelligent_chunks_with_ai(text, document_title)
            
            # Format the response to only include title and content
            response_chunks = [{"title": chunk["title"], "content": chunk["content"]} 
                              for chunk in chunks]
            
            return web.json_response({"chunks": response_chunks})
        
    except web.HTTPClientError as e:
        logger.error(f"Client error processing PDF: {str(e)}")
        return web.json_response({"error": str(e)}, status=e.status_code)
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        return web.json_response({"error": "Failed to process PDF file"}, status=500)

def setup_routes(app):
    """
    Set up document processing routes on the app.
    
    Args:
        app: The aiohttp web application
    """
    app.router.add_post('/process-pdf', process_pdf) 