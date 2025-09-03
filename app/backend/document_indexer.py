"""
Document indexing module for processing uploaded PDFs and indexing them in Azure Search.
"""

import logging
import os
import uuid
import json
from typing import List, Dict, Any
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery
from openai import AzureOpenAI

# Patch httpx to avoid proxy issues
import httpx
original_init = httpx.Client.__init__

def patched_init(self, *args, **kwargs):
    # Remove proxies from kwargs if it exists
    if 'proxies' in kwargs:
        del kwargs['proxies']
    # Call original init
    return original_init(self, *args, **kwargs)

httpx.Client.__init__ = patched_init

from document_processing.pdf_processor import extract_pdf_text, create_intelligent_chunks_with_ai

logger = logging.getLogger("voicerag.document_indexer")

class DocumentIndexer:
    def __init__(self):
        # Azure Search configuration
        self.search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
        self.search_index = os.environ.get("AZURE_SEARCH_INDEX")
        self.identifier_field = os.environ.get("AZURE_SEARCH_IDENTIFIER_FIELD", "chunk_id")
        self.content_field = os.environ.get("AZURE_SEARCH_CONTENT_FIELD", "chunk")
        self.title_field = os.environ.get("AZURE_SEARCH_TITLE_FIELD", "title")
        self.embedding_field = os.environ.get("AZURE_SEARCH_EMBEDDING_FIELD", "text_vector")

        # Azure OpenAI configuration for embeddings
        self.openai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        self.openai_key = os.environ.get("AZURE_OPENAI_API_KEY")
        self.embedding_deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")

        # Local storage fallback
        self.local_storage_file = os.path.join(os.path.dirname(__file__), "local_documents.json")
        self.local_documents = self._load_local_documents()

        # Initialize clients
        self.openai_client = None
        self.search_client = None
        
        try:
            if self.openai_key:
                self.openai_client = AzureOpenAI(
                    api_key=self.openai_key,
                    api_version="2023-05-15",
                    azure_endpoint=self.openai_endpoint
                )
            else:
                # Try to get access token from Azure Instance Metadata Service
                try:
                    import requests

                    # Get access token for Cognitive Services
                    token_response = requests.get(
                        "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://cognitiveservices.azure.com/",
                        headers={"Metadata": "true"},
                        timeout=5
                    )

                    if token_response.status_code == 200:
                        token_data = token_response.json()
                        access_token = token_data.get("access_token")

                        # Use azure_ad_token directly without custom http client
                        self.openai_client = AzureOpenAI(
                            api_version="2023-05-15",
                            azure_endpoint=self.openai_endpoint,
                            azure_ad_token=access_token
                        )
                    else:
                        raise Exception("Failed to get access token from IMDS")

                except Exception as e:
                    logger.error(f"Failed to get access token: {e}")
                    # Fallback: try with minimal configuration
                    try:
                        self.openai_client = AzureOpenAI(
                            api_version="2023-05-15",
                            azure_endpoint=self.openai_endpoint
                        )
                    except Exception as e2:
                        logger.error(f"Fallback also failed: {e2}")

        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")

        # Initialize search client
        try:
            search_key = os.environ.get("AZURE_SEARCH_API_KEY")
            if search_key:
                search_credential = AzureKeyCredential(search_key)
            else:
                search_credential = DefaultAzureCredential()

            self.search_client = SearchClient(
                endpoint=self.search_endpoint,
                index_name=self.search_index,
                credential=search_credential
            )
        except Exception as e:
            logger.error(f"Failed to initialize Search client: {e}")
            self.search_client = None

    def _load_local_documents(self) -> List[Dict[str, Any]]:
        """Load documents from local storage."""
        try:
            if os.path.exists(self.local_storage_file):
                with open(self.local_storage_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load local documents: {e}")
        return []

    def _save_local_documents(self):
        """Save documents to local storage."""
        try:
            with open(self.local_storage_file, 'w') as f:
                json.dump(self.local_documents, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save local documents: {e}")

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for text using Azure OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.embedding_deployment
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            # Fallback: generate a simple hash-based embedding
            import hashlib
            hash_obj = hashlib.md5(text.encode())
            hash_bytes = hash_obj.digest()
            # Convert to list of floats (simple approach for fallback)
            embedding = [float(b) / 255.0 for b in hash_bytes]
            # Pad to typical embedding dimension (1536 for ada-002)
            while len(embedding) < 1536:
                embedding.extend(embedding)
            embedding = embedding[:1536]
            logger.info(f"Using fallback embedding for text: {text[:50]}...")
            return embedding

    async def index_document(self, file_path: str, filename: str, user_id: str = None) -> bool:
        """
        Process and index a PDF document.

        Args:
            file_path: Path to the PDF file
            filename: Original filename

        Returns:
            bool: True if indexing was successful
        """
        try:
            logger.info(f"Processing document: {filename}")

            # Extract text from PDF
            text = extract_pdf_text(file_path, is_path=True)
            if not text or not text.strip():
                logger.error(f"No text extracted from {filename}")
                return False

            # Create intelligent chunks
            chunks = create_intelligent_chunks_with_ai(text, filename)
            if not chunks:
                logger.error(f"No chunks created for {filename}")
                return False

            logger.info(f"Created {len(chunks)} chunks for {filename}")

            # Prepare documents for indexing
            documents = []
            for i, chunk in enumerate(chunks):
                # Generate embedding for the chunk (now with fallback)
                embedding = await self.generate_embedding(chunk['content'])
                
                # Create document for Azure Search
                chunk_id = f"{Path(filename).stem}_{i+1}_{uuid.uuid4().hex[:8]}"
                document = {
                    self.identifier_field: chunk_id,
                    "parent_id": Path(filename).stem,
                    self.title_field: chunk['title'],
                    self.content_field: chunk['content'],
                    self.embedding_field: embedding,
                    "filename": filename,
                    "user_id": user_id or "anonymous",
                    "start_line": chunk.get('start_line', 0),
                    "end_line": chunk.get('end_line', 0),
                    "chunk_index": i + 1,
                    "total_chunks": len(chunks)
                }
                documents.append(document)

            if not documents:
                logger.error(f"No documents to index for {filename}")
                return False

            # Try Azure Search first
            if self.search_client:
                try:
                    result = self.search_client.upload_documents(documents)
                    successful_count = sum(1 for r in result if r.succeeded)
                    logger.info(f"Successfully indexed {successful_count}/{len(documents)} chunks in Azure Search")
                    return successful_count > 0
                except Exception as e:
                    logger.error(f"Azure Search failed: {e}")
            
            # Fallback to local storage
            logger.info("Using local storage as fallback")
            for doc in documents:
                # Remove embedding field for local storage (not needed for simple search)
                local_doc = {k: v for k, v in doc.items() if k != self.embedding_field}
                self.local_documents.append(local_doc)
            
            self._save_local_documents()
            logger.info(f"Successfully stored {len(documents)} chunks in local storage")
            return True

        except Exception as e:
            logger.error(f"Failed to index document {filename}: {e}")
            return False

    async def search_documents(self, query: str, top: int = 5, user_id: str = None, filename_filter: str = None) -> List[Dict[str, Any]]:
        """
        Search for documents in the index.

        Args:
            query: Search query
            top: Number of results to return
            user_id: Filter by user ID
            filename_filter: Filter by specific filename (optional)

        Returns:
            List of search results
        """
        try:
            # Try Azure Search first
            if self.search_client:
                # Create vector query for hybrid search
                vector_query = VectorizableTextQuery(
                    text=query,
                    k_nearest_neighbors=50,
                    fields=self.embedding_field
                )

                # Build filter for user-specific and filename-specific search
                filter_conditions = []
                if user_id:
                    filter_conditions.append(f"user_id eq '{user_id}'")
                if filename_filter:
                    filter_conditions.append(f"filename eq '{filename_filter}'")
                
                filter_str = " and ".join(filter_conditions) if filter_conditions else None

                results = self.search_client.search(
                    search_text=query,
                    vector_queries=[vector_query],
                    top=top,
                    filter=filter_str,
                    select=[self.identifier_field, self.title_field, self.content_field, "filename", "start_line", "end_line", "chunk_index", "total_chunks"]
                )

                search_results = []
                for result in results:
                    search_results.append({
                        'chunk_id': result[self.identifier_field],
                        'title': result[self.title_field],
                        'content': result[self.content_field],
                        'filename': getattr(result, 'filename', 'Unknown'),
                        'start_line': getattr(result, 'start_line', 0),
                        'end_line': getattr(result, 'end_line', 0),
                        'chunk_index': getattr(result, 'chunk_index', 0),
                        'total_chunks': getattr(result, 'total_chunks', 0)
                    })

                return search_results
            
        except Exception as e:
            logger.error(f"Azure Search failed: {e}")
        
        # Fallback to local storage
        logger.info("Using local storage for search")
        query_lower = query.lower()
        search_results = []
        
        for doc in self.local_documents:
            # Check user filter
            if user_id and doc.get('user_id') != user_id:
                continue
            
            # Check filename filter
            if filename_filter and doc.get('filename') != filename_filter:
                continue
                
            # Simple text matching
            content = doc.get(self.content_field, '').lower()
            title = doc.get(self.title_field, '').lower()
            
            if query_lower in content or query_lower in title:
                search_results.append({
                    'chunk_id': doc.get(self.identifier_field),
                    'title': doc.get(self.title_field),
                    'content': doc.get(self.content_field),
                    'filename': doc.get('filename', 'Unknown'),
                    'start_line': doc.get('start_line', 0),
                    'end_line': doc.get('end_line', 0),
                    'chunk_index': doc.get('chunk_index', 0),
                    'total_chunks': doc.get('total_chunks', 0)
                })
        
        # Return top results
        return search_results[:top]

    async def search_in_pdf(self, query: str, filename: str, top: int = 5, user_id: str = None) -> List[Dict[str, Any]]:
        """
        Search for content only within a specific PDF file.

        Args:
            query: Search query
            filename: Name of the PDF file to search in
            top: Number of results to return
            user_id: Filter by user ID

        Returns:
            List of search results from the specified PDF only
        """
        return await self.search_documents(query, top=top, user_id=user_id, filename_filter=filename)

    async def list_indexed_pdfs(self, user_id: str = None) -> List[Dict[str, Any]]:
        """
        List all indexed PDF files for a user.

        Args:
            user_id: Filter by user ID

        Returns:
            List of indexed PDF files with metadata
        """
        pdf_files = {}
        
        # Check local storage
        for doc in self.local_documents:
            if user_id and doc.get('user_id') != user_id:
                continue
                
            filename = doc.get('filename', 'Unknown')
            if filename not in pdf_files:
                pdf_files[filename] = {
                    'filename': filename,
                    'total_chunks': doc.get('total_chunks', 0),
                    'user_id': doc.get('user_id', 'unknown')
                }
        
        return list(pdf_files.values())

# Global indexer instance
document_indexer = None

def get_document_indexer() -> DocumentIndexer:
    """Get or create the global document indexer instance."""
    global document_indexer
    if document_indexer is None:
        document_indexer = DocumentIndexer()
    return document_indexer
