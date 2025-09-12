"""
Service-Based User Management Endpoints
"""

import datetime
from aiohttp import web
from auth_middleware import require_auth, require_service, service_access
from user_manager import user_manager
from enhanced_pdf_processor import TokenizedPDFProcessor as EnhancedPDFProcessor
# from ai_enhancer import AIEnhancer  # Will implement AI enhancer later
import logging

logger = logging.getLogger(__name__)

# Service-Based User Management Endpoints

@require_auth
async def get_user_profile(request):
    """Get user profile with service status"""
    try:
        user_id = request['user']['user_id']
        profile = service_access.get_user_service_status(user_id)
        
        if "error" in profile:
            return web.json_response({
                'error': profile["error"],
                'code': 'PROFILE_ERROR'
            }, status=400)
        
        return web.json_response(profile)
        
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return web.json_response({
            'error': 'Failed to get profile',
            'code': 'SERVER_ERROR'
        }, status=500)

@require_auth
async def upgrade_subscription(request):
    """Upgrade user subscription tier"""
    try:
        data = await request.json()
        user_id = request['user']['user_id']
        new_tier = data.get('tier')
        
        if not new_tier:
            return web.json_response({
                'error': 'Subscription tier required',
                'code': 'MISSING_TIER'
            }, status=400)
        
        result = user_manager.upgrade_subscription(user_id, new_tier)
        
        if not result['success']:
            return web.json_response({
                'error': result['error'],
                'code': 'UPGRADE_FAILED'
            }, status=400)
        
        return web.json_response({
            'message': f'Upgraded to {new_tier} tier',
            'user': result['user']
        })
        
    except Exception as e:
        logger.error(f"Upgrade subscription error: {e}")
        return web.json_response({
            'error': 'Upgrade failed',
            'code': 'SERVER_ERROR'
        }, status=500)

async def get_subscription_tiers(request):
    """Get available subscription tiers (public endpoint)"""
    try:
        tiers = user_manager.get_subscription_tiers()
        return web.json_response({'tiers': tiers})
        
    except Exception as e:
        logger.error(f"Get tiers error: {e}")
        return web.json_response({
            'error': 'Failed to get tiers',
            'code': 'SERVER_ERROR'
        }, status=500)

@require_auth
async def get_user_usage_stats(request):
    """Get user usage statistics"""
    try:
        user_id = request['user']['user_id']
        stats = user_manager.get_user_usage_stats(user_id)
        
        return web.json_response({
            'usage_stats': stats,
            'billing_summary': user_manager.get_user_billing_summary(user_id)
        })
        
    except Exception as e:
        logger.error(f"Get usage stats error: {e}")
        return web.json_response({
            'error': 'Failed to get usage stats',
            'code': 'SERVER_ERROR'
        }, status=500)

@require_auth 
async def add_user_credits(request):
    """Add credits to user account"""
    try:
        data = await request.json()
        user_id = request['user']['user_id']
        credits = data.get('credits', 0)
        
        if credits <= 0:
            return web.json_response({
                'error': 'Invalid credit amount',
                'code': 'INVALID_CREDITS'
            }, status=400)
        
        success = user_manager.add_user_credits(user_id, credits)
        
        if not success:
            return web.json_response({
                'error': 'Failed to add credits',
                'code': 'CREDIT_ADD_FAILED'
            }, status=500)
        
        user = user_manager.get_user_by_id(user_id)
        
        return web.json_response({
            'message': f'Added {credits} credits',
            'credits_remaining': user.get('credits_remaining', 0)
        })
        
    except Exception as e:
        logger.error(f"Add credits error: {e}")
        return web.json_response({
            'error': 'Failed to add credits',
            'code': 'SERVER_ERROR'
        }, status=500)

# Service-protected PDF endpoints

@require_auth
@require_service("pdf_upload")
async def enhanced_pdf_upload(request):
    """Upload PDF with service access control"""
    try:
        # Check if we have a file
        reader = await request.multipart()
        field = await reader.next()
        
        if not field:
            return web.json_response({
                'error': 'No file provided',
                'code': 'NO_FILE'
            }, status=400)
        
        if field.name != 'file':
            return web.json_response({
                'error': 'File field required',
                'code': 'INVALID_FIELD'
            }, status=400)
        
        # Read file content
        content = await field.read()
        filename = field.filename or 'uploaded.pdf'
        
        if not filename.lower().endswith('.pdf'):
            return web.json_response({
                'error': 'Only PDF files allowed',
                'code': 'INVALID_FILE_TYPE'
            }, status=400)
        
        # Initialize processor if needed
        if not hasattr(request.app, 'pdf_processor'):
            request.app['pdf_processor'] = EnhancedPDFProcessor()
        
        processor = request.app['pdf_processor']
        
        # Process the PDF
        result = await processor.process_pdf_from_bytes(content, filename)
        
        if not result['success']:
            return web.json_response({
                'error': result['error'],
                'code': 'PROCESSING_FAILED'
            }, status=500)
        
        # Store document info for user
        doc_info = {
            'filename': filename,
            'document_id': result['document_id'],
            'total_tokens': result['stats']['total_tokens'],
            'total_chunks': result['stats']['total_chunks'],
            'pages': result['stats']['pages'],
            'upload_time': datetime.datetime.utcnow().isoformat()
        }
        
        return web.json_response({
            'message': 'PDF processed successfully',
            'document': doc_info,
            'processing_stats': result['stats']
        })
        
    except Exception as e:
        logger.error(f"Enhanced PDF upload error: {e}")
        return web.json_response({
            'error': 'PDF upload failed',
            'code': 'SERVER_ERROR'
        }, status=500)

@require_auth
@require_service("pdf_search")
async def enhanced_pdf_search(request):
    """Search PDF content with service access control"""
    try:
        data = await request.json()
        query = data.get('query', '')
        document_id = data.get('document_id')
        include_line_numbers = data.get('include_line_numbers', True)
        max_results = data.get('max_results', 10)
        
        if not query:
            return web.json_response({
                'error': 'Search query required',
                'code': 'NO_QUERY'
            }, status=400)
        
        # Initialize processor if needed
        if not hasattr(request.app, 'pdf_processor'):
            request.app['pdf_processor'] = EnhancedPDFProcessor()
        
        processor = request.app['pdf_processor']
        
        # Perform search
        results = await processor.search_documents(
            query=query,
            document_id=document_id,
            include_line_numbers=include_line_numbers,
            max_results=max_results
        )
        
        return web.json_response({
            'query': query,
            'results': results,
            'total_found': len(results)
        })
        
    except Exception as e:
        logger.error(f"Enhanced PDF search error: {e}")
        return web.json_response({
            'error': 'PDF search failed',
            'code': 'SERVER_ERROR'
        }, status=500)

@require_auth
@require_service("ai_analysis", usage_count=2)  # AI features cost more
async def ai_enhanced_analysis(request):
    """AI-enhanced analysis with service access control"""
    try:
        data = await request.json()
        query = data.get('query', '')
        document_id = data.get('document_id')
        analysis_type = data.get('analysis_type', 'comprehensive')
        
        if not query:
            return web.json_response({
                'error': 'Analysis query required',
                'code': 'NO_QUERY'
            }, status=400)
        
        # AI analysis placeholder - will implement proper AI enhancer
        result = {
            'analysis': f'AI analysis for query: {query}',
            'type': analysis_type,
            'status': 'AI enhancer module will be implemented',
            'suggestions': [
                'Implement proper AI enhancer module',
                'Add Perplexity API integration',
                'Add OpenAI Vision API integration'
            ]
        }
        
        return web.json_response({
            'query': query,
            'analysis_type': analysis_type,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"AI analysis error: {e}")
        return web.json_response({
            'error': 'AI analysis failed',
            'code': 'SERVER_ERROR'
        }, status=500)

@require_auth
@require_service("line_seeking")
async def pdf_line_seeking(request):
    """PDF line seeking with service access control"""
    try:
        data = await request.json()
        document_id = data.get('document_id')
        line_number = data.get('line_number')
        context_lines = data.get('context_lines', 5)
        
        if not document_id or line_number is None:
            return web.json_response({
                'error': 'Document ID and line number required',
                'code': 'MISSING_PARAMS'
            }, status=400)
        
        # Initialize processor if needed
        if not hasattr(request.app, 'pdf_processor'):
            request.app['pdf_processor'] = EnhancedPDFProcessor()
        
        processor = request.app['pdf_processor']
        
        # Get line content
        result = await processor.get_line_context(
            document_id=document_id,
            line_number=line_number,
            context_lines=context_lines
        )
        
        return web.json_response(result)
        
    except Exception as e:
        logger.error(f"Line seeking error: {e}")
        return web.json_response({
            'error': 'Line seeking failed',
            'code': 'SERVER_ERROR'
        }, status=500)
