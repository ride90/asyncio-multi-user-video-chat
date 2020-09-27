import json
from uuid import uuid4
from datetime import datetime, timedelta
from pprint import pprint

import aiohttp
from aiohttp import web
import aiohttp_jinja2

import settings


# TODO move to utils module
def setup_room(storage, room_id):
    room = {
        'id': room_id,
        'expiry': datetime.now() + timedelta(hours=settings.ROOM_EXPIRATION_HOURS),
        'peers': {}
    }
    storage.setdefault('rooms', {})[room_id] = room
    return storage['rooms'][room_id]


@aiohttp_jinja2.template('index.jinja2')
async def index(request):
    """
    Render index page
    """

    return {}


@aiohttp_jinja2.template('room.jinja2')
async def get_room(request):
    """
    Render room page html or 404
    """

    if request.match_info['id'] not in request.app.setdefault('rooms', {}):
        # use applicaiton "data store" to store rooms
        setup_room(storage=request.app, room_id=request.match_info['id'])

        # response = aiohttp_jinja2.render_template('404.jinja2', request, {})
        # response.set_status(404)
        # return response

    return {}


async def create_room(request):
    """
    Create new room
    """
    # use applicaiton "data store" to store rooms
    room = setup_room(storage=request.app, room_id=uuid4().hex)

    return web.json_response({'room_link': f'{settings.API_URL}/r/{room["id"]}'}, status=201)


async def ws_handler(request):
    """
    Handle web socket messages
    """

    ws = web.WebSocketResponse(
        autoping=True,
        heartbeat=10
    )
    await ws.prepare(request)
    request.app.setdefault('websockets', []).append(ws)

    room_id = None
    peer = {
        'ws': ws,
        'id': id(ws)
    }
    print(f'[WS] Connection opened {peer["id"]}')

    # wait for messages
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            # decode json
            try:
                data = json.loads(msg.data)
            except json.decoder.JSONDecodeError:
                await ws.close(code=1003)
                break
            # join room
            if data.get('action') == 'join' and data.get('room_id'):
                try:
                    room_id = data['room_id']
                    request.app['rooms'][room_id]['peers'][peer["id"]] = peer
                    print(f"Added new peer to room {room_id}")
                    pprint(request.app['rooms'][room_id]['peers'])
                    print('\n\n\n')
                except KeyError:
                    await ws.close()
                    print(f'[WS] Can not setup peer, no room with id: {room_id}')
                    break

                await ws.send_json({'status': 'joined'})
            else:
                await ws.close()
                break

        # binary video stream
        elif msg.type == aiohttp.WSMsgType.BINARY:
            # send binary to all peers in current rooms except the current one
            room = request.app['rooms'][room_id]
            for _peer in [p for p in room['peers'].values() if p['id'] != peer["id"]]:
                await _peer['ws'].send_bytes(msg.data)
            # await ws.send_bytes(msg.data)

        elif msg.type == aiohttp.WSMsgType.ERROR:
            print(f'[WS] Connection closed with exception {ws.exception()}')

    print(f'[WS] Connection closed {peer["id"]}')

    # remove peer
    if peer["id"]:
        try:
            del request.app['rooms'][room_id]['peers'][peer["id"]]
            print(f"Remove peer {peer['id']} from room: {room_id}")
            pprint(request.app['rooms'][room_id]['peers'])
        except KeyError:
            pass

    return ws


async def ws_shutdown_handler(app):
    for ws in app['websockets']:
        # 1012 is a server restart
        print('Server is stoped. Closing WS connection.')
        await ws.close(code=1012)
