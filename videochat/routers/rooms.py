from uuid import uuid4

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from starlette.requests import Request

import utils
import settings


router = APIRouter()


@router.get('/', tags=['rooms'], response_class=HTMLResponse)
async def get_index(request: Request):
    return request.app.templates.TemplateResponse(
        'index.jinja2', {'request': request}
    )


@router.post('/', tags=['rooms'], status_code=status.HTTP_201_CREATED)
async def create_room(request: Request):
    # use app context to store rooms
    # another storage might be use such as redis or something else
    room = utils.add_room(
        room_id=uuid4().hex,
        storage=request.app._rooms
    )

    return {'room_link': f'{settings.API_URL}/r/{room["id"]}'}


@router.get('/r/{room_id}', tags=["rooms"], response_class=HTMLResponse)
async def get_room(request: Request, room_id: str):
    if not utils.get_room(room_id, request.app._rooms):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return request.app.templates.TemplateResponse(
        'room.jinja2', {'request': request}
    )
