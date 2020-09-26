import ssl

from aiohttp import web
import jinja2
import aiohttp_jinja2

import settings
from routes import setup_routes
from views import ws_shutdown_handler


app = web.Application(debug=settings.DEBUG)
# routes
setup_routes(app)
# jinja
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(settings.JINJA2_TEMPLATES_DIR))
jinja_env = aiohttp_jinja2.get_env(app)
jinja_env.globals.update({
    'API_URL': settings.API_URL,
    'WS_URL': settings.WS_URL
})
# shut down handlers
app.on_shutdown.append(ws_shutdown_handler)

if __name__ == '__main__':
    if settings.SSL:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.check_hostname = False
        ssl_context.load_cert_chain(settings.SSL_CRT_PATH, settings.SSL_KEY_PATH)
        web.run_app(app, host=settings.HOST, port=settings.PORT, ssl_context=ssl_context)
    else:
        web.run_app(app, host=settings.HOST, port=settings.PORT)
