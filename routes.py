from aiohttp import web

import settings
from views import index, ws_handler, create_room, get_room


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/r', create_room)
    app.router.add_get(r'/r/{id:[0-9a-f]{32}\Z}', get_room)
    app.router.add_get('/ws', ws_handler)
    # static files
    if settings.SERVE_STATIC:
        app.add_routes([web.static('/static', 'static')])
