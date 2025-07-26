"""
Document indexing module for saving processed documents to Azure AI Search.
"""

import logging
import os
import uuid
from typing import List, Dict, Any, Optional

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

logger = logging.getLogger("voicerag.document_indexer")

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
        
    async def index_chunks(self, chunks: List[Dict[str, Any]], 
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
                        embedding = await embedding_generator(chunk["content"])
                        document["factVector"] = embedding
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
            
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Placeholder for generating embeddings.
        In a real implementation, this would call Azure OpenAI to generate embeddings.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            list: List of embeddings
        """
        # This is a placeholder - in a real implementation, this would call Azure OpenAI
        logger.warning("Using placeholder embeddings - not suitable for production!")
        return [[0.0] * 1536 for _ in texts] 