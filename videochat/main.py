import asyncio

import hypercorn
from hypercorn.asyncio import serve
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

import settings
import exceptions
from routers import rooms, ws


app = FastAPI()
# routers
app.include_router(ws.router)
app.include_router(rooms.router)
# custom exception handlers
app.add_exception_handler(StarletteHTTPException, exceptions.http_exception_handler)
# static
if settings.SERVE_STATIC:
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name='static')
    # jinja2
app.templates = Jinja2Templates(directory=settings.JINJA2_TEMPLATES_DIR)
app.templates.env.globals.update({
    'API_URL': settings.API_URL,
    'WS_URL': settings.WS_URL
})
# rooms
# this one should be something else (redis, zeromq)
app._rooms = {}

if __name__ == '__main__':
    config = hypercorn.config.Config()
    config.bind = f"{settings.HOST}:{settings.PORT}"
    config.debug = settings.DEBUG
    config.use_reloader = settings.DEBUG
    if settings.SSL:
        config.keyfile = settings.SSL_KEY_PATH
        config.certfile = settings.SSL_CRT_PATH

    asyncio.run(serve(app, config))
