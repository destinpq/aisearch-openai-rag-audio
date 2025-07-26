"""
Azure AI Search client service for index operations.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

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