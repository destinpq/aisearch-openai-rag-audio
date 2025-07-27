"""
Routes for document processing endpoints.
"""

import logging
import tempfile
import io
import os
import uuid
import json
import traceback

from aiohttp import web

from .pdf_processor import extract_pdf_text, create_intelligent_chunks_with_ai
from .models import DocumentDatabase, ProcessingStatus
from .tasks import process_pdf_task

logger = logging.getLogger("voicerag.document_routes")

# Initialize database
db = DocumentDatabase()

async def test_endpoint(request):
    """
    Test endpoint to verify server connectivity.
    
    Endpoint: GET /process-pdf/test
    """
    logger.info("Test endpoint called")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request path: {request.path}")
    logger.info(f"Request headers: {dict(request.headers)}")
    return web.json_response({"status": "ok", "message": "Server is running"})

async def process_pdf(request):
    """
    Process uploaded PDF file, extract content, and create meaningful chunks using AI.
    Optionally upload to index if upload_to_index=true is provided.
    
    Endpoint: POST /process-pdf
    Query Parameters:
        upload_to_index: Boolean flag to indicate if chunks should be uploaded to index
    """
    logger.info("Processing PDF file request received")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request path: {request.path}")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Request query: {dict(request.query)}")
    
    try:
        # Check for upload_to_index flag
        upload_to_index = request.query.get('upload_to_index', '').lower() == 'true'
        logger.info(f"Upload to index flag: {upload_to_index}")
        
        # Read the uploaded file
        reader = await request.multipart()
        field = await reader.next()
        
        if field is None:
            logger.error("No file uploaded - no multipart field found")
            return web.json_response({"error": "No file uploaded"}, status=400)
            
        if field.name != 'file':
            logger.error(f"No file field found - got field name: {field.name}")
            return web.json_response({"error": "No file field found"}, status=400)
        
        # Check content type
        content_type = field.headers.get('Content-Type', '')
        logger.info(f"Received file with content type: {content_type}")
        logger.info(f"Field headers: {dict(field.headers)}")
        
        if 'application/pdf' not in content_type.lower():
            logger.error(f"Invalid content type: {content_type}")
            return web.json_response({"error": "Uploaded file is not a PDF"}, status=400)
            
        # Get the file content
        try:
            file_data = await field.read()
            file_size = len(file_data)
            logger.info(f"Successfully read file data: {file_size} bytes")
        except Exception as e:
            logger.error(f"Error reading file data: {e}")
            logger.error(traceback.format_exc())
            return web.json_response({"error": "Failed to read uploaded file"}, status=400)
        
        # Get document title from filename
        filename = field.filename or "Document"
        document_title = os.path.splitext(filename)[0]
        logger.info(f"Processing document: {filename} (title: {document_title})")
        
        # Generate a unique document ID
        document_id = str(uuid.uuid4())
        logger.info(f"Generated document ID: {document_id}")
        
        # Create document record in database
        try:
            document = db.create_document(document_id, filename, {
                "title": document_title,
                "upload_to_index": upload_to_index,
                "size": len(file_data)
            })
            logger.info(f"Created document record in database: {document}")
        except Exception as e:
            logger.error(f"Error creating document record: {e}")
            logger.error(traceback.format_exc())
            return web.json_response({"error": "Failed to create document record"}, status=500)
        
        # For all PDFs, we'll use temp files and background processing
        logger.info(f"Saving PDF to temp file ({len(file_data)/1024/1024:.2f} MB)")
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(file_data)
                temp_path = temp_file.name
                logger.info(f"Saved to temp file: {temp_path}")
        except Exception as e:
            logger.error(f"Error saving temp file: {e}")
            logger.error(traceback.format_exc())
            return web.json_response({"error": "Failed to save temporary file"}, status=500)
        
        # Start background processing task
        try:
            logger.info("Starting Celery task for document processing")
            task = process_pdf_task.delay(temp_path, document_id, filename, upload_to_index)
            logger.info(f"Started Celery task with ID: {task.id}")
        except Exception as e:
            logger.error(f"Error starting Celery task: {e}")
            logger.error(traceback.format_exc())
            try:
                os.unlink(temp_path)
            except:
                pass
            return web.json_response({"error": "Failed to start processing task"}, status=500)
        
        # Return immediate response with document ID for status tracking
        response_data = {
            "document_id": document_id,
            "status": document["status"],
            "filename": filename,
            "upload_to_index": upload_to_index,
            "message": "PDF processing started in background",
            "task_id": task.id
        }
        logger.info(f"Returning response: {response_data}")
        return web.json_response(response_data)
        
    except web.HTTPClientError as e:
        logger.error(f"Client error processing PDF: {str(e)}")
        logger.error(traceback.format_exc())
        return web.json_response({"error": str(e)}, status=e.status_code)
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        logger.error(traceback.format_exc())
        return web.json_response({"error": "Failed to process PDF file"}, status=500)

async def get_document_status(request):
    """
    Get the status of a document processing task.
    
    Endpoint: GET /document/{document_id}
    """
    document_id = request.match_info.get('document_id')
    logger.info(f"Getting status for document: {document_id}")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request path: {request.path}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    if not document_id:
        logger.error("Document ID is required")
        return web.json_response({"error": "Document ID is required"}, status=400)
    
    try:
        document = db.get_document(document_id)
        if not document:
            logger.error(f"Document not found: {document_id}")
            return web.json_response({"error": "Document not found"}, status=404)
        
        logger.info(f"Retrieved document status: {document}")
        return web.json_response(document)
    except Exception as e:
        logger.error(f"Error getting document status: {e}")
        logger.error(traceback.format_exc())
        return web.json_response({"error": "Failed to get document status"}, status=500)

async def list_documents(request):
    """
    List all documents.
    
    Endpoint: GET /documents
    Query Parameters:
        limit: Maximum number of documents to return
        offset: Offset for pagination
    """
    limit = int(request.query.get('limit', 100))
    offset = int(request.query.get('offset', 0))
    logger.info(f"Listing documents with limit={limit}, offset={offset}")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request path: {request.path}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    try:
        documents = db.get_documents(limit, offset)
        logger.info(f"Found {len(documents)} documents")
        return web.json_response({"documents": documents})
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        logger.error(traceback.format_exc())
        return web.json_response({"error": "Failed to list documents"}, status=500)

async def get_pending_jobs(request):
    """
    Get all pending or processing jobs.
    
    Endpoint: GET /documents/pending
    """
    logger.info("Getting pending jobs")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request path: {request.path}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    try:
        documents = db.get_pending_jobs()
        logger.info(f"Found {len(documents)} pending jobs")
        return web.json_response({"documents": documents})
    except Exception as e:
        logger.error(f"Error getting pending jobs: {e}")
        logger.error(traceback.format_exc())
        return web.json_response({"error": "Failed to get pending jobs"}, status=500)

def setup_routes(app):
    """
    Set up document processing routes on the app.
    
    Args:
        app: The aiohttp web application
    """
    logger.info("Setting up document processing routes")
    app.router.add_get('/process-pdf/test', test_endpoint)
    app.router.add_post('/process-pdf', process_pdf)
    app.router.add_get('/document/{document_id}', get_document_status)
    app.router.add_get('/documents', list_documents)
    app.router.add_get('/documents/pending', get_pending_jobs)
    logger.info("Document processing routes set up successfully") 