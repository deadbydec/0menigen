# routes/socketio.py
import socketio

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio)

# ======== CHAT =========
@sio.event(namespace="/chat")
async def connect(sid, environ):
    print(f"💬 [CHAT] Подключён: {sid}")

@sio.event(namespace="/chat")
async def disconnect(sid):
    print(f"💬 [CHAT] Отключён: {sid}")

# ======== SHOP =========
@sio.event(namespace="/shop")
async def connect(sid, environ):
    print(f"🛒 [SHOP] Подключён: {sid}")

@sio.event(namespace="/shop")
async def disconnect(sid):
    print(f"🛒 [SHOP] Отключён: {sid}")
