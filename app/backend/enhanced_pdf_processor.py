"""
Enhanced PDF Processor with Token-based Storage and Precise Location Tracking
"""
import logging
import os
import io
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import hashlib
import base64
from datetime import datetime

import PyPDF2
import fitz  # PyMuPDF for better text extraction and image handling
import tiktoken
from PIL import Image
import numpy as np
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
import openai
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("enhanced_pdf_processor")

class TokenizedPDFProcessor:
    def __init__(self, azure_search_client=None, openai_client=None):
        self.azure_search_client = azure_search_client
        self.openai_client = openai_client
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.enable_image_analysis = os.getenv("ENABLE_IMAGE_ANALYSIS", "true").lower() == "true"
        self.enable_live_data = os.getenv("ENABLE_LIVE_DATA_ANALYSIS", "true").lower() == "true"
        
        # Token configuration
        self.token_chunk_size = int(os.getenv("TOKEN_CHUNK_SIZE", "500"))
        self.token_overlap = int(os.getenv("TOKEN_OVERLAP", "50"))
        self.max_tokens_per_chunk = int(os.getenv("MAX_TOKENS_PER_CHUNK", "512"))
        
        # Initialize tokenizer
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Initialize database
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for token storage"""
        self.db_path = "enhanced_pdf_tokens.db"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables for enhanced token storage
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pdf_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_hash TEXT UNIQUE NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_pages INTEGER,
                total_tokens INTEGER,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pdf_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id INTEGER,
                token_id TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                token_count INTEGER,
                page_number INTEGER,
                line_start INTEGER,
                line_end INTEGER,
                char_start INTEGER,
                char_end INTEGER,
                bbox_x REAL,
                bbox_y REAL,
                bbox_width REAL,
                bbox_height REAL,
                embedding BLOB,
                chunk_index INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doc_id) REFERENCES pdf_documents (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pdf_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id INTEGER,
                page_number INTEGER,
                image_hash TEXT,
                image_data BLOB,
                bbox_x REAL,
                bbox_y REAL,
                bbox_width REAL,
                bbox_height REAL,
                analysis_result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doc_id) REFERENCES pdf_documents (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS token_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_token_id TEXT,
                target_token_id TEXT,
                relationship_type TEXT,
                confidence_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for efficient querying
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_doc_id ON pdf_tokens(doc_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_page ON pdf_tokens(page_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_lines ON pdf_tokens(line_start, line_end)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_hash ON pdf_documents(file_hash)")
        
        conn.commit()
        conn.close()
    
    async def process_pdf(self, pdf_path: str, filename: str) -> Dict[str, Any]:
        """Process PDF with enhanced token-based extraction"""
        try:
            # Calculate file hash
            file_hash = self._calculate_file_hash(pdf_path)
            
            # Check if already processed
            existing_doc = self._get_document_by_hash(file_hash)
            if existing_doc:
                logger.info(f"Document {filename} already processed")
                return {"status": "exists", "doc_id": existing_doc["id"]}
            
            # Open PDF with PyMuPDF for better text and image extraction
            doc = fitz.open(pdf_path)
            
            # Store document metadata
            doc_id = self._store_document_metadata(filename, file_hash, len(doc))
            
            total_tokens = 0
            all_chunks = []
            
            # Process each page
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Extract text with position information
                text_data = self._extract_text_with_positions(page, page_num + 1)
                
                # Extract images if enabled
                if self.enable_image_analysis:
                    await self._extract_and_analyze_images(page, page_num + 1, doc_id)
                
                # Tokenize and chunk text
                page_chunks = self._create_token_chunks(text_data, page_num + 1)
                
                # Store chunks in database
                for chunk in page_chunks:
                    chunk_id = await self._store_token_chunk(doc_id, chunk)
                    all_chunks.append(chunk)
                    total_tokens += chunk["token_count"]
            
            # Update document with total token count
            self._update_document_token_count(doc_id, total_tokens)
            
            # Generate embeddings and store in vector database
            if self.azure_search_client:
                await self._vectorize_and_store(doc_id, all_chunks)
            
            doc.close()
            
            logger.info(f"Successfully processed {filename}: {total_tokens} tokens across {len(doc)} pages")
            
            return {
                "status": "success",
                "doc_id": doc_id,
                "total_tokens": total_tokens,
                "total_pages": len(doc),
                "chunks_created": len(all_chunks)
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _extract_text_with_positions(self, page, page_num: int) -> Dict[str, Any]:
        """Extract text with precise position information"""
        # Get text blocks with position data
        blocks = page.get_text("dict")
        
        text_data = {
            "page_number": page_num,
            "lines": [],
            "full_text": "",
            "char_positions": []
        }
        
        char_offset = 0
        line_number = 0
        
        for block in blocks["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    line_text = ""
                    line_bbox = None
                    
                    for span in line["spans"]:
                        span_text = span["text"]
                        line_text += span_text
                        
                        # Track character positions
                        for char in span_text:
                            text_data["char_positions"].append({
                                "char": char,
                                "offset": char_offset,
                                "line": line_number,
                                "bbox": span["bbox"]
                            })
                            char_offset += 1
                        
                        if not line_bbox:
                            line_bbox = span["bbox"]
                        else:
                            # Expand bounding box
                            line_bbox = [
                                min(line_bbox[0], span["bbox"][0]),  # x0
                                min(line_bbox[1], span["bbox"][1]),  # y0
                                max(line_bbox[2], span["bbox"][2]),  # x1
                                max(line_bbox[3], span["bbox"][3])   # y1
                            ]
                    
                    if line_text.strip():
                        text_data["lines"].append({
                            "line_number": line_number,
                            "text": line_text.strip(),
                            "bbox": line_bbox,
                            "char_start": char_offset - len(line_text.strip()),
                            "char_end": char_offset
                        })
                        text_data["full_text"] += line_text.strip() + "\n"
                        line_number += 1
        
        return text_data
    
    def _create_token_chunks(self, text_data: Dict[str, Any], page_num: int) -> List[Dict[str, Any]]:
        """Create token-based chunks with precise location tracking"""
        full_text = text_data["full_text"]
        tokens = self.tokenizer.encode(full_text)
        
        chunks = []
        chunk_index = 0
        
        for i in range(0, len(tokens), self.token_chunk_size - self.token_overlap):
            chunk_tokens = tokens[i:i + self.token_chunk_size]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            
            # Find corresponding lines and positions
            chunk_lines = self._find_chunk_lines(chunk_text, text_data["lines"])
            
            # Generate unique token ID
            token_id = self._generate_token_id(page_num, chunk_index, chunk_text)
            
            chunk_data = {
                "token_id": token_id,
                "content": chunk_text,
                "token_count": len(chunk_tokens),
                "page_number": page_num,
                "chunk_index": chunk_index,
                "lines": chunk_lines,
                "line_start": chunk_lines[0]["line_number"] if chunk_lines else 0,
                "line_end": chunk_lines[-1]["line_number"] if chunk_lines else 0,
                "char_start": chunk_lines[0]["char_start"] if chunk_lines else 0,
                "char_end": chunk_lines[-1]["char_end"] if chunk_lines else 0,
                "bbox": self._calculate_chunk_bbox(chunk_lines)
            }
            
            chunks.append(chunk_data)
            chunk_index += 1
        
        return chunks
    
    def _find_chunk_lines(self, chunk_text: str, lines: List[Dict]) -> List[Dict]:
        """Find which lines correspond to a text chunk"""
        chunk_lines = []
        chunk_words = chunk_text.lower().split()
        
        if not chunk_words:
            return chunk_lines
        
        for line in lines:
            line_words = line["text"].lower().split()
            
            # Check for word overlap
            overlap = len(set(chunk_words) & set(line_words))
            if overlap > 0:
                chunk_lines.append(line)
        
        return chunk_lines
    
    def _calculate_chunk_bbox(self, lines: List[Dict]) -> Dict[str, float]:
        """Calculate bounding box for a chunk based on its lines"""
        if not lines:
            return {"x": 0, "y": 0, "width": 0, "height": 0}
        
        x_coords = []
        y_coords = []
        
        for line in lines:
            if line.get("bbox"):
                bbox = line["bbox"]
                x_coords.extend([bbox[0], bbox[2]])
                y_coords.extend([bbox[1], bbox[3]])
        
        if not x_coords:
            return {"x": 0, "y": 0, "width": 0, "height": 0}
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        return {
            "x": x_min,
            "y": y_min,
            "width": x_max - x_min,
            "height": y_max - y_min
        }
    
    async def _extract_and_analyze_images(self, page, page_num: int, doc_id: int):
        """Extract and analyze images from PDF page"""
        try:
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                # Extract image
                xref = img[0]
                pix = fitz.Pixmap(page.parent, xref)
                
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    img_data = pix.tobytes("png")
                    
                    # Calculate image hash
                    img_hash = hashlib.md5(img_data).hexdigest()
                    
                    # Get image position
                    img_bbox = page.get_image_bbox(img)
                    
                    # Analyze image if OpenAI vision is available
                    analysis_result = None
                    if self.enable_image_analysis and self.openai_api_key:
                        analysis_result = await self._analyze_image_with_openai(img_data)
                    
                    # Store image in database
                    self._store_image_data(
                        doc_id, page_num, img_hash, img_data, 
                        img_bbox, analysis_result
                    )
                
                pix = None  # Clean up
                
        except Exception as e:
            logger.error(f"Error extracting images from page {page_num}: {str(e)}")
    
    async def _analyze_image_with_openai(self, image_data: bytes) -> str:
        """Analyze image using OpenAI Vision API"""
        try:
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this image and describe what you see. Include any text, charts, diagrams, or important visual elements."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 500
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"OpenAI Vision API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return None
    
    async def search_tokens(self, query: str, doc_id: Optional[int] = None, 
                          limit: int = 10) -> List[Dict[str, Any]]:
        """Search tokens with precise location information"""
        try:
            # First, get embedding for the query
            query_embedding = await self._get_query_embedding(query)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Base SQL query
            sql = """
                SELECT t.*, d.filename, d.total_pages
                FROM pdf_tokens t
                JOIN pdf_documents d ON t.doc_id = d.id
                WHERE t.content LIKE ?
            """
            params = [f"%{query}%"]
            
            if doc_id:
                sql += " AND t.doc_id = ?"
                params.append(doc_id)
            
            sql += " ORDER BY t.page_number, t.line_start LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            # Convert to dictionaries with enhanced information
            token_results = []
            for row in results:
                token_data = {
                    "token_id": row[2],
                    "content": row[3],
                    "token_count": row[4],
                    "page_number": row[5],
                    "line_start": row[6],
                    "line_end": row[7],
                    "char_start": row[8],
                    "char_end": row[9],
                    "bbox": {
                        "x": row[10],
                        "y": row[11],
                        "width": row[12],
                        "height": row[13]
                    },
                    "filename": row[16],
                    "total_pages": row[17],
                    "highlight_info": {
                        "highlightLine": row[6],
                        "highlightText": query
                    }
                }
                token_results.append(token_data)
            
            conn.close()
            
            # Enhance with live data if enabled
            if self.enable_live_data and self.perplexity_api_key:
                enhanced_results = await self._enhance_with_live_data(query, token_results)
                return enhanced_results
            
            return token_results
            
        except Exception as e:
            logger.error(f"Error searching tokens: {str(e)}")
            return []
    
    async def _enhance_with_live_data(self, query: str, token_results: List[Dict]) -> List[Dict]:
        """Enhance results with live data from Perplexity"""
        try:
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that provides current, accurate information to enhance document search results."
                    },
                    {
                        "role": "user",
                        "content": f"Provide current, relevant information about: {query}. Keep it concise and factual."
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.2
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                live_data = result['choices'][0]['message']['content']
                
                # Add live data to each result
                for token_result in token_results:
                    token_result["live_data"] = live_data
                    token_result["enhanced_at"] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Error enhancing with live data: {str(e)}")
        
        return token_results
    
    async def get_document_stats(self, doc_id: int) -> Dict[str, Any]:
        """Get comprehensive statistics for a document"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get document info
        cursor.execute("SELECT * FROM pdf_documents WHERE id = ?", (doc_id,))
        doc_info = cursor.fetchone()
        
        if not doc_info:
            return {"error": "Document not found"}
        
        # Get token statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as token_chunks,
                SUM(token_count) as total_tokens,
                AVG(token_count) as avg_tokens_per_chunk,
                MIN(page_number) as first_page,
                MAX(page_number) as last_page
            FROM pdf_tokens WHERE doc_id = ?
        """, (doc_id,))
        token_stats = cursor.fetchone()
        
        # Get page distribution
        cursor.execute("""
            SELECT page_number, COUNT(*) as chunks_per_page
            FROM pdf_tokens WHERE doc_id = ?
            GROUP BY page_number ORDER BY page_number
        """, (doc_id,))
        page_distribution = cursor.fetchall()
        
        # Get image count
        cursor.execute("SELECT COUNT(*) FROM pdf_images WHERE doc_id = ?", (doc_id,))
        image_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "document": {
                "id": doc_info[0],
                "filename": doc_info[1],
                "file_hash": doc_info[2],
                "upload_date": doc_info[3],
                "total_pages": doc_info[4]
            },
            "tokens": {
                "total_chunks": token_stats[0],
                "total_tokens": token_stats[1],
                "avg_tokens_per_chunk": round(token_stats[2], 2) if token_stats[2] else 0,
                "page_range": f"{token_stats[3]}-{token_stats[4]}"
            },
            "page_distribution": [
                {"page": row[0], "chunks": row[1]} for row in page_distribution
            ],
            "images": {
                "total_images": image_count
            }
        }
    
    # Helper methods for database operations
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _generate_token_id(self, page_num: int, chunk_index: int, content: str) -> str:
        """Generate unique token ID"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"p{page_num}_c{chunk_index}_{content_hash}"
    
    def _get_document_by_hash(self, file_hash: str) -> Optional[Dict]:
        """Check if document already exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pdf_documents WHERE file_hash = ?", (file_hash,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "filename": result[1],
                "file_hash": result[2],
                "upload_date": result[3],
                "total_pages": result[4],
                "total_tokens": result[5]
            }
        return None
    
    def _store_document_metadata(self, filename: str, file_hash: str, total_pages: int) -> int:
        """Store document metadata and return doc_id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pdf_documents (filename, file_hash, total_pages, total_tokens)
            VALUES (?, ?, ?, 0)
        """, (filename, file_hash, total_pages))
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return doc_id
    
    async def _store_token_chunk(self, doc_id: int, chunk_data: Dict) -> str:
        """Store token chunk in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        bbox = chunk_data["bbox"]
        cursor.execute("""
            INSERT INTO pdf_tokens (
                doc_id, token_id, content, token_count, page_number,
                line_start, line_end, char_start, char_end,
                bbox_x, bbox_y, bbox_width, bbox_height, chunk_index
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id, chunk_data["token_id"], chunk_data["content"],
            chunk_data["token_count"], chunk_data["page_number"],
            chunk_data["line_start"], chunk_data["line_end"],
            chunk_data["char_start"], chunk_data["char_end"],
            bbox["x"], bbox["y"], bbox["width"], bbox["height"],
            chunk_data["chunk_index"]
        ))
        
        conn.commit()
        conn.close()
        return chunk_data["token_id"]
    
    def _store_image_data(self, doc_id: int, page_num: int, img_hash: str, 
                         img_data: bytes, bbox: tuple, analysis: str):
        """Store image data in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pdf_images (
                doc_id, page_number, image_hash, image_data,
                bbox_x, bbox_y, bbox_width, bbox_height, analysis_result
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id, page_num, img_hash, img_data,
            bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1],
            analysis
        ))
        conn.commit()
        conn.close()
    
    def _update_document_token_count(self, doc_id: int, total_tokens: int):
        """Update total token count for document"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pdf_documents SET total_tokens = ? WHERE id = ?
        """, (total_tokens, doc_id))
        conn.commit()
        conn.close()
    
    async def _get_query_embedding(self, query: str) -> List[float]:
        """Get embedding for search query"""
        # This would use your Azure OpenAI embedding service
        # Placeholder for now
        return []
    
    async def _vectorize_and_store(self, doc_id: int, chunks: List[Dict]):
        """Create embeddings and store in vector database"""
        # This would create embeddings for each chunk and store in Azure Search
        # Implementation depends on your Azure Search setup
        pass
