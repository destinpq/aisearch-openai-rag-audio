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
import jwt
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential, DefaultAzureCredential
from dotenv import load_dotenv

from ragtools import attach_rag_tools
from rtmt import RTMiddleTier
from call_handler import CallHandler
from document_indexer import get_document_indexer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voicerag")

# Simple in-memory user store for demo
users: Dict[str, Dict[str, Any]] = {
    "admin": {"password": bcrypt.hash("admin"), "role": "admin"},
    "demo@example.com": {"password": bcrypt.hash("Akanksha100991!"), "role": "user"}
}

JWT_SECRET = os.environ.get("JWT_SECRET", "your-secret-key")
JWT_EXP_DELTA_SECONDS = 3600

async def register(request):
    try:
        data = await request.json()
        username = data.get('username')
        password = data.get('password')
        
        if username in users:
            return web.json_response({'error': 'User already exists'}, status=400)
        
        users[username] = {"password": bcrypt.hash(password), "role": "user"}
        return web.json_response({'message': 'User registered successfully'})
    except Exception as e:
        logger.error(f"Register error: {e}")
        return web.json_response({'error': 'Internal server error'}, status=500)

async def login(request):
    try:
        data = await request.json()
        username = data.get('username')
        password = data.get('password')
        
        user = users.get(username)
        if not user or not bcrypt.verify(password, user['password']):
            return web.json_response({'error': 'Invalid credentials'}, status=401)
        
        payload = {
            'user_id': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        return web.json_response({'token': token})
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
    upload_dir = Path(__file__).parent / 'uploads' / user_id
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
    user_upload_dir = Path(__file__).parent / 'uploads' / user_id
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

def jwt_request_processor(request):
    if request.path in ['/register', '/login', '/']:
        return None
    return request

# Calling handlers
async def initiate_call_handler(request, call_handler: CallHandler):
    """Handle call initiation requests"""
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

async def get_call_status_handler(request, call_handler: CallHandler):
    """Handle call status requests"""
    try:
        call_sid = request.match_info['call_sid']
        result = call_handler.get_call_status(call_sid)
        return web.json_response(result)
    except Exception as e:
        logger.error(f"Error in get_call_status_handler: {e}")
        return web.json_response({'error': 'Internal server error'}, status=500)

async def end_call_handler(request, call_handler: CallHandler):
    """Handle call ending requests"""
    try:
        call_sid = request.match_info['call_sid']
        result = call_handler.end_call(call_sid)
        return web.json_response(result)
    except Exception as e:
        logger.error(f"Error in end_call_handler: {e}")
        return web.json_response({'error': 'Internal server error'}, status=500)

async def twiml_handler(request, call_handler: CallHandler):
    """Handle Twilio TwiML requests"""
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
    if not os.environ.get("RUNNING_IN_PRODUCTION"):
        logger.info("Running in development mode, loading from .env file")
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

    # Initialize call handler for phone calling functionality
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

    # Auth routes
    app.router.add_post('/register', register)
    app.router.add_post('/login', login)
    app.router.add_post('/upload', upload_pdf)
    app.router.add_post('/analyze', analyze_pdf)
    app.router.add_get('/files', list_files)
    app.router.add_get('/indexed-pdfs', list_indexed_pdfs)
    app.router.add_post('/index-existing', index_existing_files)

    # Calling routes
    app.router.add_post('/call/initiate', lambda req: initiate_call_handler(req, call_handler))
    app.router.add_get('/call/status/{call_sid}', lambda req: get_call_status_handler(req, call_handler))
    app.router.add_post('/call/end/{call_sid}', lambda req: end_call_handler(req, call_handler))
    app.router.add_post('/call/twiml', lambda req: twiml_handler(req, call_handler))

    rtmt.attach_to_app(app, "/realtime")

    current_directory = Path(__file__).parent
    app.add_routes([web.get('/', lambda _: web.FileResponse(current_directory / 'static/index.html'))])
    
    # Serve uploaded files with user-specific paths
    uploads_dir = current_directory / 'uploads'
    app.router.add_static('/uploads/', path=uploads_dir, name='uploads')
    
    app.router.add_static('/', path=current_directory / 'static', name='static')
    
    # Setup CORS
    allowed_origins = [
        "https://converse.destinpq.com",
        "https://converse-api.destinpq.com"
    ]
    
    # Add current host if running in production
    if os.environ.get("RUNNING_IN_PRODUCTION"):
        # Allow the Azure Container App domain
        current_host = os.environ.get("WEBSITE_HOSTNAME", "")
        if current_host:
            allowed_origins.append(f"https://{current_host}")
    
    cors_config = {}
    for origin in allowed_origins:
        cors_config[origin] = ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        )
    
    cors = setup_cors(app, defaults=cors_config)
    
    return app

if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 8765))
    web.run_app(create_app(), host=host, port=port)
