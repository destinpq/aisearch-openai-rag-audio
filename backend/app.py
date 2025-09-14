"""Main backend app moved from nested project."""
from aiohttp import web

async def hello(request):
    return web.Response(text="Hello from backend")

def create_app():
    app = web.Application()
    app.router.add_get('/', hello)
    return app

if __name__ == '__main__':
    web.run_app(create_app(), host='0.0.0.0', port=35532)
