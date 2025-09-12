"""
Enhanced PDF API endpoints with token-based processing
"""
import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, Any
import json

from aiohttp import web, multipart
from aiohttp_cors import ResourceOptions
import aiofiles

from enhanced_pdf_processor import TokenizedPDFProcessor

logger = logging.getLogger("enhanced_pdf_api")

class EnhancedPDFAPI:
    def __init__(self, azure_search_client=None, openai_client=None):
        self.processor = TokenizedPDFProcessor(azure_search_client, openai_client)
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
    
    async def upload_and_process_pdf(self, request):
        """Enhanced PDF upload with token-based processing"""
        try:
            # Check authentication
            user = getattr(request, 'user', None)
            if not user:
                return web.json_response({'error': 'Authentication required'}, status=401)
            
            reader = await request.multipart()
            field = await reader.next()
            
            if field.name != 'file':
                return web.json_response({'error': 'File field required'}, status=400)
            
            filename = field.filename
            if not filename.lower().endswith('.pdf'):
                return web.json_response({'error': 'Only PDF files allowed'}, status=400)
            
            # Save uploaded file
            file_path = self.upload_dir / filename
            async with aiofiles.open(file_path, 'wb') as f:
                while True:
                    chunk = await field.read_chunk()
                    if not chunk:
                        break
                    await f.write(chunk)
            
            # Process PDF with enhanced tokenization
            result = await self.processor.process_pdf(str(file_path), filename)
            
            # Return processing results
            return web.json_response({
                'success': True,
                'message': 'PDF processed successfully',
                'result': result
            })
            
        except Exception as e:
            logger.error(f"Error in PDF upload/processing: {str(e)}")
            return web.json_response({
                'error': 'Failed to process PDF',
                'details': str(e)
            }, status=500)
    
    async def search_tokens(self, request):
        """Search tokens with precise location information"""
        try:
            user = getattr(request, 'user', None)
            if not user:
                return web.json_response({'error': 'Authentication required'}, status=401)
            
            data = await request.json()
            query = data.get('query', '')
            doc_id = data.get('doc_id')
            limit = data.get('limit', 10)
            
            if not query:
                return web.json_response({'error': 'Query required'}, status=400)
            
            # Search tokens
            results = await self.processor.search_tokens(query, doc_id, limit)
            
            return web.json_response({
                'success': True,
                'query': query,
                'results': results,
                'total_found': len(results)
            })
            
        except Exception as e:
            logger.error(f"Error in token search: {str(e)}")
            return web.json_response({
                'error': 'Search failed',
                'details': str(e)
            }, status=500)
    
    async def get_document_info(self, request):
        """Get comprehensive document information"""
        try:
            user = getattr(request, 'user', None)
            if not user:
                return web.json_response({'error': 'Authentication required'}, status=401)
            
            doc_id = request.match_info.get('doc_id')
            if not doc_id:
                return web.json_response({'error': 'Document ID required'}, status=400)
            
            try:
                doc_id = int(doc_id)
            except ValueError:
                return web.json_response({'error': 'Invalid document ID'}, status=400)
            
            # Get document statistics
            stats = await self.processor.get_document_stats(doc_id)
            
            return web.json_response({
                'success': True,
                'document_stats': stats
            })
            
        except Exception as e:
            logger.error(f"Error getting document info: {str(e)}")
            return web.json_response({
                'error': 'Failed to get document info',
                'details': str(e)
            }, status=500)
    
    async def get_token_details(self, request):
        """Get detailed information about a specific token"""
        try:
            user = getattr(request, 'user', None)
            if not user:
                return web.json_response({'error': 'Authentication required'}, status=401)
            
            token_id = request.match_info.get('token_id')
            if not token_id:
                return web.json_response({'error': 'Token ID required'}, status=400)
            
            # Get token details from database
            import sqlite3
            conn = sqlite3.connect(self.processor.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT t.*, d.filename, d.total_pages
                FROM pdf_tokens t
                JOIN pdf_documents d ON t.doc_id = d.id
                WHERE t.token_id = ?
            """, (token_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return web.json_response({'error': 'Token not found'}, status=404)
            
            token_details = {
                "token_id": result[2],
                "content": result[3],
                "token_count": result[4],
                "page_number": result[5],
                "line_start": result[6],
                "line_end": result[7],
                "char_start": result[8],
                "char_end": result[9],
                "bbox": {
                    "x": result[10],
                    "y": result[11],
                    "width": result[12],
                    "height": result[13]
                },
                "chunk_index": result[15],
                "filename": result[17],
                "total_pages": result[18],
                "created_at": result[16]
            }
            
            return web.json_response({
                'success': True,
                'token_details': token_details
            })
            
        except Exception as e:
            logger.error(f"Error getting token details: {str(e)}")
            return web.json_response({
                'error': 'Failed to get token details',
                'details': str(e)
            }, status=500)
    
    async def analyze_with_live_data(self, request):
        """Analyze query with live data enhancement"""
        try:
            user = getattr(request, 'user', None)
            if not user:
                return web.json_response({'error': 'Authentication required'}, status=401)
            
            data = await request.json()
            query = data.get('query', '')
            context_tokens = data.get('context_tokens', [])
            
            if not query:
                return web.json_response({'error': 'Query required'}, status=400)
            
            # Search relevant tokens first
            token_results = await self.processor.search_tokens(query, limit=5)
            
            # Enhance with live data
            if self.processor.enable_live_data and self.processor.perplexity_api_key:
                enhanced_results = await self.processor._enhance_with_live_data(query, token_results)
            else:
                enhanced_results = token_results
            
            # Additional analysis with OpenAI if available
            analysis_result = None
            if self.processor.openai_api_key:
                analysis_result = await self._analyze_with_openai(query, enhanced_results)
            
            return web.json_response({
                'success': True,
                'query': query,
                'token_matches': enhanced_results,
                'analysis': analysis_result,
                'enhanced_at': self.processor.datetime.now().isoformat() if hasattr(self.processor, 'datetime') else None
            })
            
        except Exception as e:
            logger.error(f"Error in live data analysis: {str(e)}")
            return web.json_response({
                'error': 'Analysis failed',
                'details': str(e)
            }, status=500)
    
    async def get_image_analysis(self, request):
        """Get image analysis results for a document"""
        try:
            user = getattr(request, 'user', None)
            if not user:
                return web.json_response({'error': 'Authentication required'}, status=401)
            
            doc_id = request.match_info.get('doc_id')
            if not doc_id:
                return web.json_response({'error': 'Document ID required'}, status=400)
            
            try:
                doc_id = int(doc_id)
            except ValueError:
                return web.json_response({'error': 'Invalid document ID'}, status=400)
            
            # Get image analysis from database
            import sqlite3
            conn = sqlite3.connect(self.processor.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT page_number, bbox_x, bbox_y, bbox_width, bbox_height, 
                       analysis_result, created_at
                FROM pdf_images 
                WHERE doc_id = ? AND analysis_result IS NOT NULL
                ORDER BY page_number
            """, (doc_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            image_analyses = []
            for row in results:
                image_analyses.append({
                    "page_number": row[0],
                    "bbox": {
                        "x": row[1],
                        "y": row[2],
                        "width": row[3],
                        "height": row[4]
                    },
                    "analysis": row[5],
                    "analyzed_at": row[6]
                })
            
            return web.json_response({
                'success': True,
                'doc_id': doc_id,
                'image_analyses': image_analyses,
                'total_images': len(image_analyses)
            })
            
        except Exception as e:
            logger.error(f"Error getting image analysis: {str(e)}")
            return web.json_response({
                'error': 'Failed to get image analysis',
                'details': str(e)
            }, status=500)
    
    async def _analyze_with_openai(self, query: str, token_results: list) -> str:
        """Perform additional analysis using OpenAI"""
        try:
            import requests
            
            # Prepare context from token results
            context = "\n".join([result["content"] for result in token_results[:3]])
            
            headers = {
                "Authorization": f"Bearer {self.processor.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert document analyst. Provide insightful analysis based on the given context and query."
                    },
                    {
                        "role": "user",
                        "content": f"Query: {query}\n\nContext from document:\n{context}\n\nProvide a comprehensive analysis including key insights, relationships, and implications."
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.3
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
                logger.error(f"OpenAI API error: {response.status_code}")
                return "Analysis unavailable"
                
        except Exception as e:
            logger.error(f"Error in OpenAI analysis: {str(e)}")
            return "Analysis failed"
    
    def setup_routes(self, app):
        """Setup API routes"""
        app.router.add_post('/api/pdf/upload', self.upload_and_process_pdf)
        app.router.add_post('/api/pdf/search', self.search_tokens)
        app.router.add_get('/api/pdf/document/{doc_id}', self.get_document_info)
        app.router.add_get('/api/pdf/token/{token_id}', self.get_token_details)
        app.router.add_post('/api/pdf/analyze', self.analyze_with_live_data)
        app.router.add_get('/api/pdf/images/{doc_id}', self.get_image_analysis)
        
        # Add CORS support
        cors_options = ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        )
        
        for route in app.router.routes():
            if hasattr(route, 'resource'):
                app['cors'].add(route.resource, cors_options)
