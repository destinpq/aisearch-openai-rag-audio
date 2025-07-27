"""
Celery tasks for document processing.
"""

import logging
import os
import time

from celery import Celery

from .models import DocumentDatabase, ProcessingStatus
from .pdf_processor import extract_pdf_text, create_intelligent_chunks_with_ai
from .indexer import DocumentIndexer
from dotenv import load_dotenv

logger = logging.getLogger("voicerag.document_tasks")

load_dotenv()

# Configure Celery
celery_app = Celery('document_tasks')
celery_app.conf.broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
celery_app.conf.result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Initialize database
db = DocumentDatabase()

@celery_app.task(bind=True)
def process_pdf_task(self, file_path: str, document_id: str, filename: str, upload_to_index: bool = False):
    """
    Process PDF file and optionally upload to index.
    
    Args:
        file_path: Path to the PDF file
        document_id: Document ID
        filename: Original filename
        upload_to_index: Whether to upload to index
    """
    logger.info(f"Starting PDF processing task for document {document_id} (file: {filename})")
    logger.info(f"Task ID: {self.request.id}")
    logger.info(f"Upload to index: {upload_to_index}")
    
    try:
        # Update status to processing
        logger.info(f"Updating document status to processing")
        db.update_document_status(document_id, ProcessingStatus.PROCESSING)
        
        # Extract text from PDF
        logger.info(f"Extracting text from PDF: {filename}")
        text = extract_pdf_text(file_path, is_path=True)
        logger.info(f"Extracted {len(text)} characters from PDF")
        
        # Get document title from filename
        document_title = os.path.splitext(filename)[0]
        
        # Create intelligent chunks
        logger.info(f"Creating intelligent chunks for document: {document_title}")
        chunks = create_intelligent_chunks_with_ai(text, document_title)
        logger.info(f"Created {len(chunks)} chunks")
        
        # Update progress
        logger.info(f"Updating progress: {len(chunks)} chunks processed")
        db.update_document_progress(document_id, total_chunks=len(chunks), processed_chunks=len(chunks))
        
        # If upload to index is requested
        indexed_count = 0
        if upload_to_index:
            logger.info(f"Uploading chunks to index for document: {document_title}")
            # Create indexer
            indexer = DocumentIndexer()
            
            if not indexer.is_ready():
                error_msg = "Indexer not initialized properly"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Check if OpenAI embedding configuration is available
            if not os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"):
                # Set the environment variable if not already set
                logger.info("Setting AZURE_OPENAI_EMBEDDING_DEPLOYMENT to the same as AZURE_OPENAI_REALTIME_DEPLOYMENT")
                os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"] = os.environ.get("AZURE_OPENAI_REALTIME_DEPLOYMENT", "text-embedding-ada-002")
            
            # Process chunks in batches to avoid overwhelming the API
            batch_size = 10
            
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")
                
                try:
                    # Add created_at timestamp to each chunk
                    for chunk in batch:
                        chunk["created_at"] = time.time()
                    
                    # Index the batch with embeddings
                    result = indexer.index_chunks(batch, embedding_generator=indexer.generate_embeddings)
                    batch_indexed = result.get("indexed_count", 0)
                    indexed_count += batch_indexed
                    logger.info(f"Indexed {batch_indexed} chunks in this batch (total: {indexed_count})")
                    
                    # Update progress
                    db.update_document_progress(document_id, indexed_chunks=indexed_count)
                    
                    # Add small delay to avoid rate limiting
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error indexing batch: {e}", exc_info=True)
            
            logger.info(f"Indexed {indexed_count}/{len(chunks)} chunks for document: {document_title}")
        
        # Update status to completed
        logger.info(f"Updating document status to completed")
        db.update_document_status(document_id, ProcessingStatus.COMPLETED)
        
        # Clean up temp file
        try:
            os.unlink(file_path)
            logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to delete temporary file: {file_path} - {str(e)}")
        
        result = {
            "success": True,
            "document_id": document_id,
            "total_chunks": len(chunks),
            "indexed_chunks": indexed_count
        }
        logger.info(f"Task completed successfully: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing PDF: {e}", exc_info=True)
        db.update_document_status(document_id, ProcessingStatus.FAILED, str(e))
        
        # Clean up temp file in case of error
        try:
            os.unlink(file_path)
            logger.info(f"Cleaned up temporary file after error: {file_path}")
        except:
            pass
            
        result = {
            "success": False,
            "document_id": document_id,
            "error": str(e)
        }
        logger.info(f"Task failed: {result}")
        return result 