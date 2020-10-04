import json
from typing import List, Tuple, Type, Any, Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

import utils


router = APIRouter()


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self._connections.remove(ws)

    async def send_text(self, ws: WebSocket, data: str) -> None:
        await ws.send_text(data)

    async def send_json(self, ws: WebSocket, data: Dict) -> None:
        await ws.send_json(data, mode='text')

    async def send_bytes(self, ws: WebSocket, data: bytes) -> None:
        await ws.send_bytes(data)

    async def receive(self, ws: WebSocket) -> Tuple[Type, Any]:
        message = await ws.receive()
        ws._raise_on_disconnect(message)

        # binary message
        if message.get('bytes'):
            return (bytes, message['bytes'])

        try:
            # let's try to decode text as jsonTYPE
            return (dict, json.loads(message['text']))
        except json.JSONDecodeError:
            # nope it's just a text
            return (str, message['text'])


connection_manager: ConnectionManager = ConnectionManager()


@router.websocket("/ws")
async def ws_handler(websocket: WebSocket):
    storage = websocket.app._rooms
    print('STORAGE', storage)

    await connection_manager.connect(websocket)
    print('[WS] New connection is created')

    try:
        while True:
            _type, data = await connection_manager.receive(websocket)
            # join the room
            if _type is dict and data.get('room_id') and data.get('action') == 'join':
                room_id = data['room_id']
                peer = utils.add_peer(room_id, websocket, storage)
                if not peer:
                    print(f'[WS] Can not add a peer, no room with id: {room_id}')
                    await websocket.close()
                await connection_manager.send_json(websocket, {'status': 'joined'})

    except (WebSocketDisconnect, Exception) as e:
        connection_manager.disconnect(websocket)
        print(f'[WS] Connection is closed due to: {e}')
