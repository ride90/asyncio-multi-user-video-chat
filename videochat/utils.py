from typing import Any, Dict, Union
from datetime import datetime, timedelta

from fastapi import WebSocket

import settings


def add_room(room_id: str, storage: Any) -> Dict:
    room = {
        'id': room_id,
        'expiry': datetime.now() + timedelta(hours=settings.ROOM_EXPIRATION_HOURS),
        'peers': {}
    }
    storage.setdefault('rooms', {})[room_id] = room
    return storage['rooms'][room_id]


def get_room(room_id: str, storage: Any) -> Union[Dict, None]:
    return storage.setdefault('rooms', {}).get(room_id)


def remove_room(room_id: str, storage: Any) -> None:
    try:
        del storage['rooms'][room_id]
    except KeyError:
        pass


def add_peer(room_id: str, peer: WebSocket, storage: Any) -> Union[Dict, None]:
    room = get_room(room_id, storage)
    if not room:
        return None
    peer_id = id(peer)
    room['peers'][peer_id] = {
        'ws': peer,
        'id': peer_id
    }
    return room['peers'][peer_id]


def get_peer(room_id: str, peer_id: int, storage: Any) -> Union[Dict, None]:
    try:
        return storage['rooms'][room_id]['peers'][peer_id]
    except KeyError:
        return None


def remove_peer(room_id: str, peer: WebSocket, storage: Any) -> None:
    try:
        del storage['rooms'][room_id]['peers'][id(peer)]
    except KeyError:
        pass
