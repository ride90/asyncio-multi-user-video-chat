from datetime import datetime, timedelta

import settings


def add_room(room_id, storage):
    room = {
        'id': room_id,
        'expiry': datetime.now() + timedelta(hours=settings.ROOM_EXPIRATION_HOURS),
        'peers': {}
    }
    storage.setdefault('rooms', {})[room_id] = room
    return storage['rooms'][room_id]


def get_room(room_id, storage):
    return storage.setdefault('rooms', {}).get(room_id)
