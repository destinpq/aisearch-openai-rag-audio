"""
Document indexing module for saving processed documents to Azure AI Search.
"""

import logging
import os
import uuid
import numpy as np
from typing import List, Dict, Any, Optional

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai import AzureOpenAI

logger = logging.getLogger("voicerag.document_indexer")

# Constants
EMBEDDING_DIM = 3072  # text-embedding-3-large dimension

class DocumentIndexer:
    """
    Class for indexing documents in Azure AI Search.
    """
    
    def __init__(self, 
                 search_endpoint: Optional[str] = None,
                 search_key: Optional[str] = None,
                 index_name: Optional[str] = None):
        """
        Initialize the document indexer.
        
        Args:
            search_endpoint: Azure AI Search endpoint
            search_key: Azure AI Search API key
            index_name: Azure AI Search index name
        """
        self.search_endpoint = search_endpoint or os.environ.get("AZURE_SEARCH_ENDPOINT")
        self.search_key = search_key or os.environ.get("AZURE_SEARCH_API_KEY")
        self.index_name = index_name or os.environ.get("AZURE_SEARCH_INDEX") or "sop-index"
        
        # Initialize OpenAI client for embeddings
        self.openai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        self.openai_key = os.environ.get("AZURE_OPENAI_API_KEY")
        self.embedding_deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        
        if self.openai_endpoint and self.openai_key and self.embedding_deployment:
            try:
                self.openai_client = AzureOpenAI(
                    api_key=self.openai_key,
                    api_version="2023-05-15",
                    azure_endpoint=self.openai_endpoint
                )
                logger.info(f"OpenAI client initialized for embeddings with deployment: {self.embedding_deployment}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        else:
            logger.warning("OpenAI endpoint, key, or deployment not provided. Embeddings will not be functional.")
            self.openai_client = None
        
        if not self.search_endpoint or not self.search_key:
            logger.warning("Search endpoint or key not provided. Indexer will not be functional.")
            self._client = None
        else:
            try:
                self._client = SearchClient(
                    endpoint=self.search_endpoint,
                    index_name=self.index_name,
                    credential=AzureKeyCredential(self.search_key)
                )
                logger.info(f"Document indexer initialized for index: {self.index_name}")
            except Exception as e:
                logger.error(f"Failed to initialize search client: {e}")
                self._client = None

    def is_ready(self) -> bool:
        """
        Check if the indexer is ready to use.
        
        Returns:
            bool: True if the indexer is ready
        """
        return self._client is not None
        
    def index_chunks(self, chunks: List[Dict[str, Any]], 
                    embedding_generator=None) -> Dict[str, Any]:
        """
        Index chunks in Azure AI Search.
        
        Args:
            chunks: List of chunks to index
            embedding_generator: Function to generate embeddings for chunks
            
        Returns:
            dict: Result of the indexing operation
        """
        if not self.is_ready():
            return {"success": False, "error": "Indexer not initialized", "indexed_count": 0}
            
        if not chunks:
            return {"success": True, "message": "No chunks to index", "indexed_count": 0}
        
        try:
            # Prepare documents for indexing
            documents = []
            
            for chunk in chunks:
                # Generate a unique ID for each chunk
                chunk_id = str(uuid.uuid4())
                
                # Create document with required fields
                document = {
                    "id": chunk_id,
                    "title": chunk.get("title", "Untitled"),
                    "fact": chunk.get("content", "")
                }
                
                # Add vector embedding if available
                if embedding_generator:
                    try:
                        # Get embedding and convert to list
                        embedding = embedding_generator(chunk["content"])
                        if isinstance(embedding, (list, np.ndarray)):
                            # Convert numpy array to list if needed
                            embedding = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
                            # Ensure it's a flat list of floats
                            if all(isinstance(x, (int, float)) for x in embedding):
                                # Pad or truncate to match expected dimension
                                if len(embedding) < EMBEDDING_DIM:
                                    embedding.extend([0.0] * (EMBEDDING_DIM - len(embedding)))
                                elif len(embedding) > EMBEDDING_DIM:
                                    embedding = embedding[:EMBEDDING_DIM]
                                document["factVector"] = embedding
                            else:
                                logger.error(f"Invalid embedding format for chunk {chunk_id}: not all elements are numbers")
                                continue
                        else:
                            logger.error(f"Invalid embedding format for chunk {chunk_id}: not a list or numpy array")
                            continue
                    except Exception as e:
                        logger.error(f"Failed to generate embedding: {e}")
                        # Skip this document if embedding fails
                        continue
                        
                documents.append(document)
            
            # Upload documents in batches
            batch_size = 50
            total_indexed = 0
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                try:
                    # Log the first document structure (without content) for debugging
                    if i == 0 and batch:
                        debug_doc = batch[0].copy()
                        debug_doc['fact'] = f"[{len(debug_doc['fact'])} chars]"
                        if 'factVector' in debug_doc:
                            debug_doc['factVector'] = f"[{len(debug_doc['factVector'])} dims]"
                        logger.info(f"Document structure example: {debug_doc}")
                    
                    results = self._client.upload_documents(documents=batch)
                    succeeded = sum(1 for r in results if r.succeeded)
                    failed = len(batch) - succeeded
                    
                    if failed > 0:
                        logger.warning(f"Failed to index {failed} documents in batch")
                        
                    total_indexed += succeeded
                except Exception as e:
                    logger.error(f"Error indexing batch: {e}")
            
            return {
                "success": True,
                "indexed_count": total_indexed,
                "total_chunks": len(chunks)
            }
                
        except Exception as e:
            logger.error(f"Failed to index chunks: {e}")
            return {"success": False, "error": str(e), "indexed_count": 0}
            
    def generate_embeddings(self, texts: List[str]) -> List[float]:
        """
        Generate embeddings using Azure OpenAI.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            list: List of embeddings
        """
        if not self.openai_client or not self.embedding_deployment:
            # Fallback to placeholder if OpenAI client is not available
            logger.warning("Using placeholder embeddings - not suitable for production!")
            return [0.1] * EMBEDDING_DIM
        
        try:
            # Use the first text in the list (assuming single text input)
            text = texts[0] if texts else ""
            
            # Call Azure OpenAI to get embeddings
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.embedding_deployment
            )
            
            # Extract embedding from response
            embedding = response.data[0].embedding
            
            logger.info(f"Successfully generated embedding with {len(embedding)} dimensions")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Fallback to placeholder on error
            logger.warning("Using placeholder embeddings due to error - not suitable for production!")
            return [0.1] * EMBEDDING_DIM 