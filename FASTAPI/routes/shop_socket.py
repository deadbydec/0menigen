import socketio

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio)

@sio.event(namespace="/shop")
async def connect(sid, environ):
    print(f"🛒 [SHOP SOCKET] Подключился клиент: {sid}")

@sio.event(namespace="/shop")
async def disconnect(sid):
    print(f"🛒 [SHOP SOCKET] Отключился клиент: {sid}")