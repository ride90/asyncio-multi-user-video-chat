from fastapi import APIRouter, WebSocket


router = APIRouter()


@router.websocket("/ws")
async def ws_handler(websocket: WebSocket):

    print('AAAAAAAAAAAAAAAAAA')

    await websocket.accept()

    print('[WS] New connection is created')

    while True:
        message = await websocket.receive_text()
        print('!!!!!!!!', message)
        # await websocket.send_text(f"Message text was: {data}")
