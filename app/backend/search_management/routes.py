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
from azure.search.documents.models import VectorizedQuery

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
        self.app.router.add_get('/api/search', self.search_documents)
        self.app.router.add_get('/api/search/debug', self.debug_search)
        self.app.router.add_post('/api/index/clear', self.clear_index)
        
    async def debug_search(self, request: web.Request) -> web.Response:
        """
        Debug search functionality by returning raw search results.
        
        Endpoint: GET /api/search/debug
        Query parameters:
            query: The search query
            limit: Maximum number of documents to retrieve (default: 10)
            vector_only: Whether to use only vector search (default: false)
        """
        try:
            query = request.query.get('query', '').strip()
            if not query:
                return web.json_response({"results": []})
                
            limit = int(request.query.get('limit', '10'))
            limit = min(max(1, limit), 50)  # Limit between 1 and 50
            
            # Force vector search if specified in query params
            vector_only = request.query.get('vector_only', '').lower() == 'true'
            
            logger.info(f"Debug search for query: '{query}' with limit: {limit}, vector_only: {vector_only}")
            
            # For vector search, we need to generate an embedding
            vector = None
            if vector_only:
                try:
                    from azure.ai.openai import AzureOpenAI
                    
                    # Get environment variables
                    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
                    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
                    deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
                    
                    if api_key and endpoint and deployment:
                        client = AzureOpenAI(
                            api_key=api_key,
                            api_version="2023-12-01-preview",
                            azure_endpoint=endpoint
                        )
                        
                        # Generate embedding for the query
                        response = client.embeddings.create(
                            input=query,
                            deployment_id=deployment
                        )
                        
                        vector = response.data[0].embedding
                        logger.info(f"Generated embedding vector for query: '{query}'")
                    else:
                        logger.warning("Missing OpenAI configuration for embedding generation")
                except Exception as e:
                    logger.error(f"Error generating embedding: {str(e)}")
                    return web.json_response({"error": f"Failed to generate embedding: {str(e)}"}, status=500)
            
            # Prepare search parameters
            if vector_only and vector:
                # Vector search
                vector_queries = [VectorizedQuery(
                    vector=vector,
                    k_nearest_neighbors=limit,
                    fields="factVector"
                )]
                
                search_params = {
                    "search_text": "*",  # Use * to match all documents, ranking will be by vector similarity
                    "top": limit,
                    "vector_queries": vector_queries,
                    "select": ["*"],
                    "include_total_count": True
                }
                search_type = "vector"
            else:
                # Text search
                search_params = {
                    "search_text": query,
                    "top": limit,
                    "query_type": "full",
                    "search_mode": "all",
                    "select": ["*"],
                    "include_total_count": True
                }
                search_type = "text"
            
            # Perform raw search using the search client directly
            results = await self.client.search_client.search(**search_params)
            
            # Get count
            count = await results.get_count()
            
            # Get raw results
            raw_results = []
            async for document in results:
                raw_results.append(dict(document))
            
            logger.info(f"Debug search found {count} results using {search_type} search")
            
            return web.json_response({
                "query": query,
                "count": count,
                "results": raw_results,
                "index_name": self.client.index_name,
                "search_type": search_type,
                "vector_used": vector_only and vector is not None
            })
        except Exception as e:
            logger.error(f"Error in debug search: {str(e)}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_documents(self, request: web.Request) -> web.Response:
        """
        Get the latest documents from the search index.
        
        Endpoint: GET /api/documents
        Query parameters:
            limit: Maximum number of documents to retrieve (default: 15)
        """
        try:
            limit = int(request.query.get('limit', '50'))
            limit = min(max(1, limit), 100)  # Limit between 1 and 100
            
            documents = await self.client.get_documents(limit=limit)
            return web.json_response({"documents": documents})
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def search_documents(self, request: web.Request) -> web.Response:
        """
        Search documents in Azure AI Search.
        
        Endpoint: GET /api/search
        Query parameters:
            query: The search query
            limit: Maximum number of documents to retrieve (default: 10)
            vector_only: Whether to use only vector search (default: false)
        """
        try:
            query = request.query.get('query', '').strip()
            if not query:
                return web.json_response({"results": []})
                
            limit = int(request.query.get('limit', '10'))
            limit = min(max(1, limit), 50)  # Limit between 1 and 50
            
            # Force vector search if specified in query params or environment
            vector_only = request.query.get('vector_only', '').lower() == 'true'
            use_vector_query = os.environ.get("AZURE_SEARCH_USE_VECTOR_QUERY", "true").lower() == "true"
            
            # Always use vector search if either vector_only is true or use_vector_query is true
            use_vector = vector_only or use_vector_query
            
            logger.info(f"Searching for query: '{query}' with limit: {limit}, vector search: {use_vector}")
            
            # For vector search, we need to generate an embedding
            vector = None
            if use_vector:
                try:
                    from azure.ai.openai import AzureOpenAI
                    
                    # Get environment variables
                    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
                    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
                    deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
                    
                    if api_key and endpoint and deployment:
                        client = AzureOpenAI(
                            api_key=api_key,
                            api_version="2023-12-01-preview",
                            azure_endpoint=endpoint
                        )
                        
                        # Generate embedding for the query
                        response = client.embeddings.create(
                            input=query,
                            deployment_id=deployment
                        )
                        
                        vector = response.data[0].embedding
                        logger.info(f"Generated embedding vector for query: '{query}'")
                    else:
                        logger.warning("Missing OpenAI configuration for embedding generation")
                except Exception as e:
                    logger.error(f"Error generating embedding: {str(e)}")
                    # Continue with text search if embedding generation fails
            
            # Perform search using our client method
            results = await self.client.search_documents(query=query, limit=limit, vector=vector)
            
            logger.info(f"Search results count: {len(results)}")
            
            return web.json_response({"results": results})
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
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

    async def clear_index(self, request: web.Request) -> web.Response:
        """
        Clear all documents from the search index.
        
        Endpoint: POST /api/index/clear
        
        Request body:
            {
                "confirm": true  # Must be true to proceed with deletion
            }
        """
        try:
            # Require confirmation in the request body
            body = await request.json()
            
            if not body.get('confirm'):
                return web.json_response({
                    "success": False, 
                    "message": "Confirmation required. Set 'confirm' to true in request body."
                }, status=400)
            
            logger.warning(f"Clearing all documents from index '{self.client.index_name}'")
            
            # Call the clear_index method
            result = await self.client.clear_index()
            
            if result["success"]:
                return web.json_response(result)
            else:
                return web.json_response(result, status=500)
                
        except json.JSONDecodeError:
            return web.json_response({
                "success": False, 
                "message": "Invalid JSON in request body"
            }, status=400)
        except Exception as e:
            logger.error(f"Error clearing index: {str(e)}")
            return web.json_response({
                "success": False, 
                "message": f"Error clearing index: {str(e)}"
            }, status=500)


def setup_routes(app: web.Application) -> None:
    """
    Set up search management routes on the app.
    
    Args:
        app: The aiohttp web application
    """
    SearchManagementRoutes(app) 