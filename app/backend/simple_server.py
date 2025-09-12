#!/usr/bin/env python3
"""
Simple server to serve the React frontend
"""
import os
from aiohttp import web
from aiohttp_cors import setup as setup_cors, ResourceOptions

async def health(request):
    return web.json_response({
        'status': 'healthy', 
        'message': 'Frontend deployed successfully!',
        'ui': 'React with Ant Design ready'
    })

async def serve_index(request):
    """Serve the React app index.html for all routes"""
    return web.FileResponse('static/index.html')

def create_app():
    app = web.Application()
    
    # Configure CORS
    cors = setup_cors(app, defaults={
        'https://converse.destinpq.com': ResourceOptions(
            allow_credentials=True,
            expose_headers='*',
            allow_headers='*',
            allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        ),
        'http://localhost:3000': ResourceOptions(
            allow_credentials=True,
            expose_headers='*',
            allow_headers='*',
            allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        )
    })
    
    # Add health check first
    health_resource = cors.add(app.router.add_resource('/api/health'))
    health_resource.add_route('GET', health)
    
    # Serve static files (React app) - this should be last
    app.router.add_get('/', serve_index)
    app.router.add_static('/', 'static/', name='static')
    
    return app

if __name__ == '__main__':
    print('🚀 Starting React frontend server...')
    print('📱 Frontend available at: http://localhost:52047')
    print('🌐 API health check: http://localhost:52047/api/health')
    print('✨ React UI with Ant Design components ready!')
    
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=52047)
