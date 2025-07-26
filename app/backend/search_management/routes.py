"""
Routes for Azure AI Search index operations.
"""

import logging
import os
import json
from typing import Optional

from aiohttp import web
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential, DefaultAzureCredential

from .search_client import SearchIndexClient

logger = logging.getLogger("voicerag.search_management")

class SearchManagementRoutes:
    """Routes for Azure AI Search index operations."""
    
    def __init__(self, app: web.Application):
        """
        Initialize the routes.
        
        Args:
            app: The aiohttp web application
        """
        self.app = app
        self._init_client()
        self._setup_routes()
    
    def _init_client(self):
        """Initialize the search client."""
        search_key = os.environ.get("AZURE_SEARCH_API_KEY")
        search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
        search_index = os.environ.get("AZURE_SEARCH_INDEX")
        
        credential = None
        if not search_key:
            if tenant_id := os.environ.get("AZURE_TENANT_ID"):
                logger.info("Using AzureDeveloperCliCredential with tenant_id %s", tenant_id)
                credential = AzureDeveloperCliCredential(tenant_id=tenant_id, process_timeout=60)
            else:
                logger.info("Using DefaultAzureCredential")
                credential = DefaultAzureCredential()
        
        search_credential = AzureKeyCredential(search_key) if search_key else credential
        
        self.client = SearchIndexClient(
            credentials=search_credential,
            search_endpoint=search_endpoint,
            search_index=search_index
        )
    
    def _setup_routes(self):
        """Set up the routes."""
        self.app.router.add_get('/api/documents', self.get_documents)
        self.app.router.add_get('/api/documents/{document_id}', self.get_document)
        self.app.router.add_post('/api/documents', self.create_document)
        self.app.router.add_delete('/api/documents/{document_id}', self.delete_document)
    
    async def get_documents(self, request: web.Request) -> web.Response:
        """
        Get the latest documents from the search index.
        
        Endpoint: GET /api/documents
        Query parameters:
            limit: Maximum number of documents to retrieve (default: 15)
        """
        try:
            limit = int(request.query.get('limit', '15'))
            limit = min(max(1, limit), 100)  # Limit between 1 and 100
            
            documents = await self.client.get_documents(limit=limit)
            return web.json_response({"documents": documents})
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_document(self, request: web.Request) -> web.Response:
        """
        Get a document by its ID.
        
        Endpoint: GET /api/documents/{document_id}
        """
        try:
            document_id = request.match_info['document_id']
            document = await self.client.get_document_by_id(document_id)
            
            if document:
                return web.json_response(document)
            else:
                return web.json_response({"error": "Document not found"}, status=404)
        except Exception as e:
            logger.error(f"Error retrieving document: {str(e)}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def create_document(self, request: web.Request) -> web.Response:
        """
        Create a new document in the search index.
        
        Endpoint: POST /api/documents
        Request body:
            {
                "fact": "The fact content",
                "title": "The document title",
                "factVector": [optional vector embedding]
            }
        """
        try:
            body = await request.json()
            
            if 'fact' not in body or not body['fact']:
                return web.json_response({"error": "Missing required field: fact"}, status=400)
            
            if 'title' not in body or not body['title']:
                return web.json_response({"error": "Missing required field: title"}, status=400)
            
            vector = body.get('factVector')
            
            document = await self.client.create_document(
                fact=body['fact'],
                title=body['title'],
                vector=vector
            )
            
            return web.json_response(document, status=201)
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON in request body"}, status=400)
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def delete_document(self, request: web.Request) -> web.Response:
        """
        Delete a document by its ID.
        
        Endpoint: DELETE /api/documents/{document_id}
        """
        try:
            document_id = request.match_info['document_id']
            success = await self.client.delete_document(document_id)
            
            if success:
                return web.json_response({"message": f"Document {document_id} deleted successfully"})
            else:
                return web.json_response({"error": f"Failed to delete document {document_id}"}, status=500)
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return web.json_response({"error": str(e)}, status=500)


def setup_routes(app: web.Application) -> None:
    """
    Set up search management routes on the app.
    
    Args:
        app: The aiohttp web application
    """
    SearchManagementRoutes(app) 