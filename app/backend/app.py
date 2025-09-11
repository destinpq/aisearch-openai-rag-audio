import logging
import os
from pathlib import Path
import json
from typing import Dict, Any
import datetime

from aiohttp import web
from aiohttp_cors import setup as setup_cors, ResourceOptions
from aiohttp_jwt import JWTMiddleware
from passlib.hash import bcrypt
import bcrypt as bcrypt_lib
import jwt
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential, DefaultAzureCredential
from dotenv import load_dotenv

from database import db
from rtmt import RTMiddleTier
from ragtools import attach_rag_tools
from document_indexer import get_document_indexer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voicerag")

try:
    from call_handler import CallHandler
    CALL_HANDLER_AVAILABLE = True
except ImportError:
    CALL_HANDLER_AVAILABLE = False
    logger.warning("CallHandler not available - Twilio functionality disabled")

# Simple in-memory user store for demo
users: Dict[str, Dict[str, Any]] = {
    "admin": {"password": bcrypt.hash("admin"), "role": "admin"},
    "demo@example.com": {"password": bcrypt.hash("Akanksha100991!"), "role": "user"},
    "test@example.com": {"password": bcrypt.hash("test123"), "role": "user"}
}

JWT_SECRET = os.environ.get("JWT_SECRET", "your-secret-key")
JWT_EXP_DELTA_SECONDS = 3600

async def register(request):
    try:
        data = await request.json()
        username = data.get('username')
        password = data.get('password')
        
        user = db.create_user(username, username, password)
        if not user:
            return web.json_response({'error': 'User already exists'}, status=400)
        
        return web.json_response({'message': 'User registered successfully'})
    except Exception as e:
        logger.error(f"Register error: {e}")
        return web.json_response({'error': 'Internal server error'}, status=500)

async def options_handler(request):
    """Handle CORS preflight requests"""
    origin = request.headers.get('Origin', '')
    allowed_origins = ['https://converse.destinpq.com']
    
    if os.environ.get("ALLOW_LOCALHOST", "true").lower() == "true":
        allowed_origins.extend([
            'http://localhost:3000',
            'http://localhost:5173',
            'http://localhost:8765'
        ])
    
    # Allow the origin if it's in our allowed list
    allow_origin = origin if origin in allowed_origins else 'https://converse.destinpq.com'
    
    return web.Response(
        status=200,
        headers={
            'Access-Control-Allow-Origin': allow_origin,
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Max-Age': '3600'
        }
    )

async def login(request):
    try:
        data = await request.json()
        username = data.get('username')
        password = data.get('password')
        
        # Try database authentication first
        user = db.authenticate_user(username, password)
        if user:
            token = db.generate_jwt_token(user)
            return web.json_response({
                'token': token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'role': 'user'  # Default role for now
                }
            })
        
        # Fallback to in-memory users for testing
        if username in users and bcrypt_lib.checkpw(password.encode('utf-8'), users[username]['password'].encode('utf-8')):
            # Create a mock user object for in-memory users
            from types import SimpleNamespace
            mock_user = SimpleNamespace()
            mock_user.id = 1
            mock_user.email = username
            mock_user.name = username.split('@')[0] if '@' in username else username
            
            # Generate JWT token manually for in-memory users
            import datetime
            payload = {
                'user_id': mock_user.id,
                'email': mock_user.email,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
            }
            token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
            
            return web.json_response({
                'token': token,
                'user': {
                    'id': mock_user.id,
                    'email': mock_user.email,
                    'name': mock_user.name,
                    'role': users[username]['role']
                }
            })
        
        return web.json_response({'error': 'Invalid credentials'}, status=401)
    except Exception as e:
        logger.error(f"Login error: {e}")
        return web.json_response({'error': 'Internal server error'}, status=500)

async def upload_pdf(request):
    # Check JWT
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return web.json_response({'error': 'Unauthorized'}, status=401)
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
    except:
        return web.json_response({'error': 'Invalid token'}, status=401)
    
    reader = await request.multipart()
    field = await reader.next()
    if field.name != 'file':
        return web.json_response({'error': 'No file provided'}, status=400)
    
    filename = field.filename
    allowed_extensions = ['.pdf', '.ppt', '.pptx']
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        return web.json_response({'error': 'Only PDF, PPT, and PPTX files allowed'}, status=400)
    
    # Create user-specific upload directory
    upload_dir = Path(__file__).parent / 'uploads' / str(user_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    filepath = upload_dir / filename
    
    # Check if file already exists
    if filepath.exists():
        return web.json_response({'error': 'File already exists'}, status=409)
    
    # Save file
    with open(filepath, 'wb') as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            f.write(chunk)
    
    # Index the document in Azure Search with user context
    try:
        indexer = get_document_indexer()
        indexing_success = await indexer.index_document(str(filepath), filename, user_id)
        if indexing_success:
            logger.info(f"Successfully indexed document: {filename} for user: {user_id}")
        else:
            logger.warning(f"Failed to index document: {filename} for user: {user_id}")
    except Exception as e:
        logger.error(f"Error during document indexing: {e}")
        # Don't fail the upload if indexing fails
        pass
    
    return web.json_response({
        'message': 'File uploaded successfully', 
        'filename': filename, 
        'indexed': indexing_success,
        'user_id': user_id
    })

async def list_files(request):
    # Check JWT
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return web.json_response({'error': 'Unauthorized'}, status=401)
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
    except:
        return web.json_response({'error': 'Invalid token'}, status=401)
    
    files = []
    
    # First, try to get files from user-specific directory
    user_upload_dir = Path(__file__).parent / 'uploads' / str(user_id)
    if user_upload_dir.exists():
        for file_path in user_upload_dir.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    'filename': file_path.name,
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                    'user_id': user_id
                })
    
    # If no user-specific files, also include files from root uploads directory
    # (for backward compatibility with existing files)
    root_upload_dir = Path(__file__).parent / 'uploads'
    if root_upload_dir.exists():
        for file_path in root_upload_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.ppt', '.pptx']:
                stat = file_path.stat()
                # Check if this file is already in the user-specific list
                if not any(f['filename'] == file_path.name for f in files):
                    files.append({
                        'filename': file_path.name,
                        'size': stat.st_size,
                        'modified': stat.st_mtime,
                        'user_id': user_id  # Assign to current user for display
                    })
    
    return web.json_response({'files': files})

async def index_existing_files(request):
    """Manually trigger indexing of all files in the uploads directory."""
    # Check JWT
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return web.json_response({'error': 'Unauthorized'}, status=401)
    token = auth_header.split(' ')[1]
    try:
        jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except:
        return web.json_response({'error': 'Invalid token'}, status=401)
    
    upload_dir = Path(__file__).parent / 'uploads'
    if not upload_dir.exists():
        return web.json_response({'error': 'No uploads directory found'}, status=404)
    
    indexer = get_document_indexer()
    results = []
    
    for file_path in upload_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.ppt', '.pptx']:
            try:
                success = await indexer.index_document(str(file_path), file_path.name)
                results.append({
                    'filename': file_path.name,
                    'indexed': success
                })
                logger.info(f"Indexed {file_path.name}: {success}")
            except Exception as e:
                logger.error(f"Failed to index {file_path.name}: {e}")
                results.append({
                    'filename': file_path.name,
                    'indexed': False,
                    'error': str(e)
                })
    
    return web.json_response({'results': results})

async def analyze_pdf(request):
    # Check JWT
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return web.json_response({'error': 'Unauthorized'}, status=401)
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
    except:
        return web.json_response({'error': 'Invalid token'}, status=401)
    
    data = await request.json()
    query = data.get('query')
    filename = data.get('filename')  # Optional: search only in specific PDF
    
    if not query:
        return web.json_response({'error': 'Query is required'}, status=400)
    
    # Search the indexed documents
    try:
        indexer = get_document_indexer()
        
        # Handle special "user_uploaded" flag for guarded search
        if filename == "user_uploaded":
            # Search only in user's uploaded documents (guarded mode)
            search_results = await indexer.search_documents(query, top=10, user_id=user_id)
        elif filename:
            # Search in specific PDF (original functionality)
            search_results = await indexer.search_in_pdf(query, filename, top=10, user_id=user_id)
        else:
            # Search in all documents (unguarded mode)
            search_results = await indexer.search_documents(query, top=10, user_id=None)
        
        if not search_results:
            return web.json_response({
                'query': query,
                'results': [],
                'message': 'No matching documents found'
            })
        
        # Format results with line number information
        results = []
        for result in search_results:
            results.append({
                'title': result['title'],
                'content': result['content'][:500] + '...' if len(result['content']) > 500 else result['content'],
                'chunk_id': result['chunk_id'],
                'filename': result['filename'],
                'start_line': result['start_line'],
                'end_line': result['end_line'],
                'chunk_index': result['chunk_index'],
                'total_chunks': result['total_chunks'],
                'line_reference': f"Lines {result['start_line']}-{result['end_line']}" if result['start_line'] > 0 else "Line information not available"
            })
        
        return web.json_response({
            'query': query,
            'filename': filename,  # Show which PDF was searched
            'search_mode': 'guarded' if filename == "user_uploaded" else ('specific' if filename else 'unguarded'),
            'results': results,
            'total_results': len(results)
        })
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return web.json_response({'error': 'Search failed', 'details': str(e)}, status=500)

async def list_indexed_pdfs(request):
    """List all indexed PDFs for the user"""
    # Check JWT
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return web.json_response({'error': 'Unauthorized'}, status=401)
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
    except:
        return web.json_response({'error': 'Invalid token'}, status=401)
    
    try:
        indexer = get_document_indexer()
        indexed_pdfs = await indexer.list_indexed_pdfs(user_id=user_id)
        
        return web.json_response({
            'indexed_pdfs': indexed_pdfs,
            'total_count': len(indexed_pdfs)
        })
        
    except Exception as e:
        logger.error(f"Failed to list indexed PDFs: {e}")
        return web.json_response({'error': 'Failed to list PDFs', 'details': str(e)}, status=500)

async def get_chat_history(request):
    """Get chat history for the user"""
    # Check JWT
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return web.json_response({'error': 'Unauthorized'}, status=401)
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
    except:
        return web.json_response({'error': 'Invalid token'}, status=401)
    
    session_id = request.query.get('session_id')
    limit = int(request.query.get('limit', 50))
    
    try:
        chats = db.get_chat_history(user_id, session_id, limit)
        
        # Convert to dict format for JSON response
        chat_history = []
        for chat in chats:
            chat_dict = {
                'id': chat.id,
                'session_id': chat.session_id,
                'message_type': chat.message_type,
                'content': chat.content,
                'timestamp': chat.timestamp.isoformat(),
                'search_mode': chat.search_mode
            }
            if chat.grounding_sources:
                chat_dict['grounding_sources'] = json.loads(chat.grounding_sources)
            chat_history.append(chat_dict)
        
        return web.json_response({
            'chat_history': chat_history,
            'total_count': len(chat_history)
        })
        
    except Exception as e:
        logger.error(f"Failed to get chat history: {e}")
        return web.json_response({'error': 'Failed to get chat history', 'details': str(e)}, status=500)

async def get_chat_sessions(request):
    """Get chat sessions for the user"""
    # Check JWT
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return web.json_response({'error': 'Unauthorized'}, status=401)
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
    except:
        return web.json_response({'error': 'Invalid token'}, status=401)
    
    try:
        sessions = db.get_chat_sessions(user_id)
        
        # Convert to dict format for JSON response
        session_list = []
        for session in sessions:
            session_list.append({
                'session_id': session['session_id'],
                'last_message': session['last_message'].isoformat(),
                'message_count': session['message_count']
            })
        
        return web.json_response({
            'sessions': session_list,
            'total_count': len(session_list)
        })
        
    except Exception as e:
        logger.error(f"Failed to get chat sessions: {e}")
        return web.json_response({'error': 'Failed to get chat sessions', 'details': str(e)}, status=500)

def jwt_request_processor(request):
    if request.path in ['/api/register', '/api/login', '/']:
        return None
    return request

# Calling handlers
async def initiate_call_handler(request, call_handler):
    """Handle call initiation requests"""
    if not call_handler:
        return web.json_response({'error': 'Calling functionality not available'}, status=503)
    
    try:
        data = await request.json()
        to_number = data.get('to_number')

        if not to_number:
            return web.json_response({'error': 'Phone number is required'}, status=400)

        result = call_handler.initiate_call(to_number)
        return web.json_response(result)
    except Exception as e:
        logger.error(f"Error in initiate_call_handler: {e}")
        return web.json_response({'error': 'Internal server error'}, status=500)

async def get_call_status_handler(request, call_handler):
    """Handle call status requests"""
    if not call_handler:
        return web.json_response({'error': 'Calling functionality not available'}, status=503)
    
    try:
        call_sid = request.match_info['call_sid']
        result = call_handler.get_call_status(call_sid)
        return web.json_response(result)
    except Exception as e:
        logger.error(f"Error in get_call_status_handler: {e}")
        return web.json_response({'error': 'Internal server error'}, status=500)

async def end_call_handler(request, call_handler):
    """Handle call ending requests"""
    if not call_handler:
        return web.json_response({'error': 'Calling functionality not available'}, status=503)
    
    try:
        call_sid = request.match_info['call_sid']
        result = call_handler.end_call(call_sid)
        return web.json_response(result)
    except Exception as e:
        logger.error(f"Error in end_call_handler: {e}")
        return web.json_response({'error': 'Internal server error'}, status=500)

async def twiml_handler(request, call_handler):
    """Handle Twilio TwiML requests"""
    if not call_handler:
        return web.Response(text='<Response><Say>Calling functionality not available</Say></Response>', content_type='text/xml')
    
    try:
        data = await request.post()
        call_sid = data.get('CallSid')
        speech_result = data.get('SpeechResult')

        twiml_response = call_handler.generate_twiml_response(call_sid, speech_result)

        return web.Response(text=twiml_response, content_type='text/xml')
    except Exception as e:
        logger.error(f"Error in twiml_handler: {e}")
        # Return a basic error TwiML response
        from twilio.twiml.voice_response import VoiceResponse
        response = VoiceResponse()
        response.say("I'm sorry, an error occurred. Goodbye.", voice='alice')
        return web.Response(text=str(response), content_type='text/xml')

async def create_app():
    # Always load .env file for development and ensure environment variables are available
    logger.info("Loading environment variables from .env file")
    load_dotenv()
    
    # Reload JWT_SECRET after dotenv is loaded
    global JWT_SECRET
    JWT_SECRET = os.environ.get("JWT_SECRET", "your-secret-key")

    llm_key = os.environ.get("AZURE_OPENAI_API_KEY")
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")

    credential = None
    if not llm_key or not search_key:
        if tenant_id := os.environ.get("AZURE_TENANT_ID"):
            logger.info("Using AzureDeveloperCliCredential with tenant_id %s", tenant_id)
            credential = AzureDeveloperCliCredential(tenant_id=tenant_id, process_timeout=60)
        else:
            logger.info("Using DefaultAzureCredential")
            credential = DefaultAzureCredential()
    llm_credential = AzureKeyCredential(llm_key) if llm_key else credential
    search_credential = AzureKeyCredential(search_key) if search_key else credential
    
    app = web.Application()

    # Initialize call handler for phone calling functionality (if available)
    call_handler = None
    if CALL_HANDLER_AVAILABLE:
        call_handler = CallHandler()

    rtmt = RTMiddleTier(
        credentials=llm_credential,
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment=os.environ["AZURE_OPENAI_REALTIME_DEPLOYMENT"],
        voice_choice=os.environ.get("AZURE_OPENAI_REALTIME_VOICE_CHOICE") or "alloy"
        )
    rtmt.system_message = """
        You are a helpful assistant. Only answer questions based on information you searched in the knowledge base, accessible with the 'search' tool. 
        The user is listening to answers with audio, so it's *super* important that answers are as short as possible, a single sentence if at all possible. 
        Never read file names or source names or keys out loud. 
        Always use the following step-by-step instructions to respond: 
        1. Always use the 'search' tool to check the knowledge base before answering a question. 
        2. Always use the 'report_grounding' tool to report the source of information from the knowledge base. 
        3. Produce an answer that's as short as possible. If the answer isn't in the knowledge base, say you don't know.
    """.strip()

    attach_rag_tools(rtmt,
        credentials=search_credential,
        search_endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT"),
        search_index=os.environ.get("AZURE_SEARCH_INDEX"),
        semantic_configuration=os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION") or None,
        identifier_field=os.environ.get("AZURE_SEARCH_IDENTIFIER_FIELD") or "chunk_id",
        content_field=os.environ.get("AZURE_SEARCH_CONTENT_FIELD") or "chunk",
        embedding_field=os.environ.get("AZURE_SEARCH_EMBEDDING_FIELD") or "text_vector",
        title_field=os.environ.get("AZURE_SEARCH_TITLE_FIELD") or "title",
        use_vector_query=(os.getenv("AZURE_SEARCH_USE_VECTOR_QUERY", "true") == "true")
        )

    # Setup CORS - allow production domains and localhost for testing
    cors_origins = {
        "https://converse.destinpq.com": ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            max_age=3600
        )
    }
    
    # Add localhost for development/testing if production domains aren't accessible
    if os.environ.get("ALLOW_LOCALHOST", "true").lower() == "true":
        cors_origins.update({
            "http://localhost:3000": ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                max_age=3600
            ),
            "http://localhost:5173": ResourceOptions(  # Vite dev server
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                max_age=3600
            )
        })
    
    cors = setup_cors(app, defaults=cors_origins)

    # Health check endpoint
    async def health_check(request):
        return web.json_response({'status': 'healthy', 'service': 'voicerag-api'})
    
    cors.add(app.router.add_get('/health', health_check))
    cors.add(app.router.add_get('/api/health', health_check))

    # Auth routes with CORS
    cors.add(app.router.add_post('/api/login', login))
    cors.add(app.router.add_post('/api/register', register))
    cors.add(app.router.add_post('/api/upload', upload_pdf))
    cors.add(app.router.add_post('/api/analyze', analyze_pdf))
    cors.add(app.router.add_get('/api/files', list_files))
    cors.add(app.router.add_get('/api/indexed-pdfs', list_indexed_pdfs))
    cors.add(app.router.add_post('/api/index-existing', index_existing_files))
    
    # Chat routes
    cors.add(app.router.add_get('/api/chat-history', get_chat_history))
    cors.add(app.router.add_get('/api/chat-sessions', get_chat_sessions))

    # Calling routes (only if available)
    if call_handler:
        app.router.add_post('/call/initiate', lambda req: initiate_call_handler(req, call_handler))
        app.router.add_get('/call/status/{call_sid}', lambda req: get_call_status_handler(req, call_handler))
        app.router.add_post('/call/end/{call_sid}', lambda req: end_call_handler(req, call_handler))
        app.router.add_post('/call/twiml', lambda req: twiml_handler(req, call_handler))

    rtmt.attach_to_app(app, "/realtime")

    current_directory = Path(__file__).parent
    
    # Serve uploaded files with user-specific paths
    uploads_dir = current_directory / 'uploads'
    app.router.add_static('/uploads/', path=uploads_dir, name='uploads')
    
    # Serve static assets (CSS, JS, images) directly
    static_dir = current_directory / 'static'
    app.router.add_static('/assets/', path=static_dir / 'assets', name='assets')
    app.router.add_static('/static/', path=static_dir, name='static_files')
    
    # Test route for assets
    async def test_assets(request):
        static_dir = current_directory / 'static'
        asset_path = static_dir / 'assets' / 'index-BaqNhHWx.js'
        print(f"Static dir: {static_dir}")
        print(f"Asset path: {asset_path}")
        print(f"Asset exists: {asset_path.exists()}")
        if asset_path.exists():
            return web.FileResponse(asset_path)
        else:
            return web.Response(text=f"File not found at {asset_path}", status=404)
    app.router.add_get('/test-asset', test_assets)
    
    # Serve audio worklet files from root path
    async def audio_processor_worklet_handler(request):
        return web.FileResponse(current_directory / 'static/audio-processor-worklet.js', headers={'Content-Type': 'application/javascript'})
    app.router.add_get('/audio-processor-worklet.js', audio_processor_worklet_handler)
    
    async def audio_playback_worklet_handler(request):
        return web.FileResponse(current_directory / 'static/audio-playback-worklet.js', headers={'Content-Type': 'application/javascript'})
    app.router.add_get('/audio-playback-worklet.js', audio_playback_worklet_handler)
    
    # Serve favicon.ico
    async def favicon_handler(request):
        return web.FileResponse(current_directory / 'static/favicon.ico')
    app.router.add_get('/favicon.ico', favicon_handler)
    
    # Catch-all route for React Router - serve index.html for any non-API route
    async def spa_handler(request):
        # Don't serve index.html for API routes or static assets
        path = request.path
        if (path.startswith('/api/') or 
            path.startswith('/uploads/') or 
            path.startswith('/assets/') or
            path.startswith('/static/') or
            path.startswith('/realtime') or
            path == '/favicon.ico' or
            path == '/audio-processor-worklet.js' or
            path == '/audio-playback-worklet.js' or
            path.endswith('.js') or path.endswith('.css') or path.endswith('.png') or 
            path.endswith('.jpg') or path.endswith('.jpeg') or path.endswith('.gif') or
            path.endswith('.ico') or path.endswith('.svg') or path.endswith('.woff') or
            path.endswith('.woff2') or path.endswith('.ttf') or path.endswith('.eot')):
            # Let the specific routes handle these
            return web.Response(status=404, text="Not found")
        
        # Serve index.html for all other routes (React Router handles them)
        index_path = current_directory / 'static/index.html'
        if index_path.exists():
            return web.FileResponse(index_path)
        else:
            return web.Response(text=f"index.html not found at {index_path}", status=404)
    
    # Add the catch-all route LAST (so it doesn't override other routes)
    app.router.add_get('/{path:.*}', spa_handler)
    
    return app

if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 52047))
    web.run_app(create_app(), host=host, port=port)
