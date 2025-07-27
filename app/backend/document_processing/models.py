"""
Database models for document processing.
"""

import sqlite3
import os
import json
import datetime
from enum import Enum
from typing import List, Dict, Any, Optional

class ProcessingStatus(Enum):
    """Enum for document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentDatabase:
    """SQLite database for tracking document processing."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize the document database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), "documents.db")
        self._initialize_db()
    
    def _initialize_db(self):
        """Create the database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create documents table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            total_chunks INTEGER DEFAULT 0,
            processed_chunks INTEGER DEFAULT 0,
            indexed_chunks INTEGER DEFAULT 0,
            error_message TEXT,
            metadata TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _ensure_db_exists(self):
        """Ensure the database exists before performing operations."""
        if not os.path.exists(self.db_path):
            self._initialize_db()
    
    def create_document(self, document_id: str, filename: str, metadata: Dict = None) -> Dict:
        """
        Create a new document entry.
        
        Args:
            document_id: Unique ID for the document
            filename: Original filename
            metadata: Additional metadata
            
        Returns:
            dict: The created document record
        """
        self._ensure_db_exists()
        
        now = datetime.datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            INSERT INTO documents 
            (id, filename, status, created_at, updated_at, metadata) 
            VALUES (?, ?, ?, ?, ?, ?)
            ''', 
            (document_id, filename, ProcessingStatus.PENDING.value, now, now, 
             json.dumps(metadata) if metadata else None)
        )
        
        conn.commit()
        conn.close()
        
        return self.get_document(document_id)
    
    def update_document_status(self, document_id: str, status: ProcessingStatus, 
                              error_message: str = None) -> Dict:
        """
        Update document processing status.
        
        Args:
            document_id: Document ID
            status: New status
            error_message: Optional error message
            
        Returns:
            dict: The updated document record
        """
        self._ensure_db_exists()
        
        now = datetime.datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            UPDATE documents 
            SET status = ?, updated_at = ?, error_message = ?
            WHERE id = ?
            ''', 
            (status.value, now, error_message, document_id)
        )
        
        conn.commit()
        conn.close()
        
        return self.get_document(document_id)
    
    def update_document_progress(self, document_id: str, total_chunks: int = None,
                               processed_chunks: int = None, indexed_chunks: int = None) -> Dict:
        """
        Update document processing progress.
        
        Args:
            document_id: Document ID
            total_chunks: Total number of chunks
            processed_chunks: Number of processed chunks
            indexed_chunks: Number of indexed chunks
            
        Returns:
            dict: The updated document record
        """
        self._ensure_db_exists()
        
        now = datetime.datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        update_parts = ["updated_at = ?"]
        params = [now]
        
        if total_chunks is not None:
            update_parts.append("total_chunks = ?")
            params.append(total_chunks)
            
        if processed_chunks is not None:
            update_parts.append("processed_chunks = ?")
            params.append(processed_chunks)
            
        if indexed_chunks is not None:
            update_parts.append("indexed_chunks = ?")
            params.append(indexed_chunks)
            
        params.append(document_id)
        
        query = f"UPDATE documents SET {', '.join(update_parts)} WHERE id = ?"
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        
        return self.get_document(document_id)
    
    def get_document(self, document_id: str) -> Dict:
        """
        Get document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            dict: The document record or None if not found
        """
        self._ensure_db_exists()
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if not row:
            return None
            
        document = dict(row)
        if document.get("metadata"):
            document["metadata"] = json.loads(document["metadata"])
            
        return document
    
    def get_documents(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get list of documents.
        
        Args:
            limit: Maximum number of documents to return
            offset: Offset for pagination
            
        Returns:
            list: List of document records
        """
        self._ensure_db_exists()
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM documents ORDER BY created_at DESC LIMIT ? OFFSET ?", 
            (limit, offset)
        )
        rows = cursor.fetchall()
        
        conn.close()
        
        documents = []
        for row in rows:
            document = dict(row)
            if document.get("metadata"):
                document["metadata"] = json.loads(document["metadata"])
            documents.append(document)
            
        return documents 

    def get_pending_jobs(self) -> List[Dict]:
        """
        Get all pending or processing jobs.
        
        Returns:
            list: List of document records with status pending or processing
        """
        self._ensure_db_exists()
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM documents WHERE status = ? OR status = ? ORDER BY created_at DESC", 
            (ProcessingStatus.PENDING.value, ProcessingStatus.PROCESSING.value)
        )
        rows = cursor.fetchall()
        
        conn.close()
        
        documents = []
        for row in rows:
            document = dict(row)
            if document.get("metadata"):
                document["metadata"] = json.loads(document["metadata"])
            documents.append(document)
            
        return documents 