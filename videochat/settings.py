import os
from distutils.util import strtobool


# debug
DEBUG = strtobool(os.environ.get('DEBUG', 'True'))

# static
SERVE_STATIC = strtobool(os.environ.get('SERVE_STATIC', 'True'))
STATIC_DIR = 'static'

# server
HOST = os.environ.get('HOST', '127.0.0.1')
PORT = int(os.environ.get('PORT', 8088))

# ssl
SSL = strtobool(os.environ.get('SSL', 'True'))
SSL_CRT_PATH = os.environ.get('SSL_CRT_PATH', '../certificate/sslcert.crt')
SSL_KEY_PATH = os.environ.get('SSL_KEY_PATH', '../certificate/sslcert.key')

# jinja
JINJA2_TEMPLATES_DIR = 'templates'

# client config
WS_URL = os.environ.get('WS_URL', f'wss://{HOST}:{PORT}/ws')
API_URL = os.environ.get('API_URL', f'https://{HOST}:{PORT}')

# app
ROOM_EXPIRATION_HOURS = int(os.environ.get('ROOM_EXPIRATION_HOURS', 1))
