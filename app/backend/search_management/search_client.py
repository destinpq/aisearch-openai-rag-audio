"""
Azure AI Search client service for index operations.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizedQuery

logger = logging.getLogger("voicerag.search_management")

class SearchIndexClient:
    """Client for Azure AI Search index operations."""
    
    def __init__(
        self,
        credentials: AzureKeyCredential | DefaultAzureCredential,
        search_endpoint: str,
        search_index: str,
    ):
        """
        Initialize the search client.
        
        Args:
            credentials: Azure credentials for authentication
            search_endpoint: Azure AI Search endpoint URL
            search_index: Name of the search index
        """
        self.search_client = SearchClient(
            search_endpoint, 
            search_index, 
            credentials, 
            user_agent="SearchManagement"
        )
        self.index_name = search_index
    
    async def create_document(self, fact: str, title: str, vector: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        Create a new document in the search index.
        
        Args:
            fact: The fact content
            title: The document title
            vector: Optional vector embedding for the fact
            
        Returns:
            The created document
        """
        document_id = str(uuid.uuid4())
        # Format datetime in the format expected by Edm.DateTimeOffset
        # Format: YYYY-MM-DDThh:mm:ss.fffffffZ (Azure AI Search expects Z for UTC)
        document = {
            "id": document_id,
            "fact": fact,
            "title": title,
            "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        if vector:
            document["factVector"] = vector
            
        try:
            result = await self.search_client.upload_documents(documents=[document])
            if result[0].succeeded:
                logger.info(f"Document created with ID: {document_id}")
                return document
            else:
                logger.error(f"Failed to create document: {result[0].error_message}")
                raise Exception(f"Failed to create document: {result[0].error_message}")
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            raise
    
    async def get_documents(self, limit: int = 15) -> List[Dict[str, Any]]:
        """
        Get the latest documents from the search index.
        
        Args:
            limit: Maximum number of documents to retrieve (default: 15)
            
        Returns:
            List of documents ordered by created_at in descending order
        """
        try:
            results = await self.search_client.search(
                search_text="*",
                select=["id", "fact", "title", "created_at"],
                order_by=["created_at desc"],
                top=limit
            )
            
            documents = []
            async for document in results:
                documents.append({
                    "id": document["id"],
                    "fact": document["fact"],
                    "title": document["title"],
                    "created_at": document["created_at"]
                })
            
            return documents
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise
    
    async def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by its ID.
        
        Args:
            document_id: The document ID
            
        Returns:
            The document if found, None otherwise
        """
        try:
            results = await self.search_client.search(
                search_text=f"id:{document_id}",
                select=["id", "fact", "title", "created_at"]
            )
            
            async for document in results:
                return {
                    "id": document["id"],
                    "fact": document["fact"],
                    "title": document["title"],
                    "created_at": document["created_at"]
                }
            
            return None
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {str(e)}")
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document by its ID.
        
        Args:
            document_id: The document ID
            
        Returns:
            True if the document was deleted successfully, False otherwise
        """
        try:
            result = await self.search_client.delete_documents(
                documents=[{"id": document_id}]
            )
            
            if result[0].succeeded:
                logger.info(f"Document deleted: {document_id}")
                return True
            else:
                logger.error(f"Failed to delete document {document_id}: {result[0].error_message}")
                return False
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            raise 
            
    async def search_documents(self, query: str, limit: int = 50, vector: Optional[List[float]] = None) -> List[Dict[str, Any]]:
        """
        Search documents using text and/or vector queries.
        
        Args:
            query: The search query text
            limit: Maximum number of documents to retrieve (default: 50)
            vector: Optional vector embedding for semantic search
            
        Returns:
            List of matching documents
        """
        try:
            # Log the search parameters for debugging
            logger.info(f"Performing search with query: '{query}', limit: {limit}, vector provided: {vector is not None}")
            
            # Prepare vector query if vector is available
            vector_queries = []
            if vector:
                vector_queries.append(VectorizedQuery(
                    vector=vector,
                    k_nearest_neighbors=limit,
                    fields="factVector"
                ))
                logger.info("Using vector search")
                
                # When using vector search, we can use an empty string as the search text
                # This ensures that only vector similarity is used for ranking
                search_text = "*"
                search_params = {
                    "search_text": search_text,
                    "top": limit,
                    "vector_queries": vector_queries,
                    "select": ["*"],
                    "include_total_count": True
                }
            else:
                # Fallback to text search if no vector is available
                search_text = query
                logger.info("Using text search")
                search_params = {
                    "search_text": search_text,
                    "top": limit,
                    "query_type": "full",  # Use full Lucene query syntax for text search
                    "search_mode": "all",  # Match all terms (AND operation) for text search
                    "select": ["*"],
                    "include_total_count": True
                }
            
            # Execute the search
            results = await self.search_client.search(**search_params)
            
            # Get count for logging
            try:
                count = await results.get_count()
                logger.info(f"Search found {count} results")
            except:
                logger.info("Could not get result count")
            
            documents = []
            async for document in results:
                # Log each document for debugging
                logger.debug(f"Found document: {document}")
                
                # Create a standardized document with flexible field mapping
                doc = {
                    "id": document.get("id", document.get("ID", "")),
                    "title": document.get("title", document.get("Title", document.get("name", ""))),
                    "fact": document.get("fact", document.get("Fact", document.get("content", document.get("text", ""))))
                }
                
                # Add created_at if available
                if "created_at" in document:
                    doc["created_at"] = document["created_at"]
                elif "createdAt" in document:
                    doc["created_at"] = document["createdAt"]
                elif "timestamp" in document:
                    doc["created_at"] = document["timestamp"]
                else:
                    doc["created_at"] = ""
                
                documents.append(doc)
            
            return documents
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise
            
    async def clear_index(self) -> Dict[str, Any]:
        """
        Clear all documents from the search index.
        
        Returns:
            A dictionary with the operation results
        """
        try:
            # Get all document IDs
            logger.info(f"Retrieving all document IDs from index '{self.index_name}'")
            
            results = await self.search_client.search(
                search_text="*",
                select=["id"],
                top=1000,  # Adjust based on your index size
                include_total_count=True
            )
            
            # Get total count for reporting
            total_count = await results.get_count()
            logger.info(f"Found {total_count} documents in index '{self.index_name}'")
            
            if total_count == 0:
                return {"success": True, "message": "Index is already empty", "deleted_count": 0, "total_count": 0}
            
            # Collect all document IDs
            document_ids = []
            async for document in results:
                if "id" in document:
                    document_ids.append(document["id"])
            
            if not document_ids:
                return {"success": True, "message": "No documents found with ID field", "deleted_count": 0, "total_count": total_count}
            
            # Delete documents in batches
            MAX_BATCH_SIZE = 100
            total_deleted = 0
            
            for i in range(0, len(document_ids), MAX_BATCH_SIZE):
                batch_ids = document_ids[i:i + MAX_BATCH_SIZE]
                
                # Create batch of documents to delete (only need the key field)
                batch_docs = [{"id": doc_id} for doc_id in batch_ids]
                
                logger.info(f"Deleting batch {i//MAX_BATCH_SIZE + 1}: {len(batch_docs)} documents")
                
                result = await self.search_client.delete_documents(documents=batch_docs)
                
                # Check for failures
                failures = [r for r in result if not r.succeeded]
                successes = len(batch_docs) - len(failures)
                
                if failures:
                    logger.warning(f"Failed to delete {len(failures)} documents in batch {i//MAX_BATCH_SIZE + 1}")
                    for failure in failures:
                        logger.warning(f"Failed to delete {failure.key}: {failure.error_message}")
                
                total_deleted += successes
                
                logger.info(f"Successfully deleted {successes} documents from batch {i//MAX_BATCH_SIZE + 1}")
            
            return {
                "success": True,
                "message": f"Successfully deleted {total_deleted} documents from index '{self.index_name}'",
                "deleted_count": total_deleted,
                "total_count": total_count
            }
            
        except Exception as e:
            error_msg = f"Error clearing index: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg, "deleted_count": 0} 