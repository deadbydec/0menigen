import socketio
from fastapi import APIRouter
from jose import JWTError
import json
from redis.asyncio import Redis
from sqlalchemy.future import select
from models.models import async_session, User
from auth.cookie_auth import decode_access_token

router = APIRouter()
# Создаем асинхронный сервер Socket.IO
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


# Асинхронный Redis-клиент
redis_client = Redis.from_url("redis://localhost", decode_responses=True)

def parse_cookies(cookie_str: str) -> dict:
    cookies = {}
    if cookie_str:
        parts = cookie_str.split(";")
        for part in parts:
            if "=" in part:
                name, value = part.strip().split("=", 1)
                cookies[name] = value
    return cookies

@sio.event
async def connect(sid, environ, auth):
    """
    При подключении клиента:
      - Извлекаем куки из заголовка,
      - Получаем access_token_cookie,
      - Декодируем токен с помощью decode_access_token,
      - Загружаем пользователя из БД,
      - Сохраняем данные (user_id и username) в сессии Socket.IO.
      
    Если что-то не так – отклоняем подключение.
    """
    cookie_header = environ.get("HTTP_COOKIE", "")
    cookies = parse_cookies(cookie_header)
    token = cookies.get("access_token_cookie")
    if not token:
        print("Connection rejected: no access_token_cookie found")
        return False

    try:
        payload = decode_access_token(token)
    except JWTError as e:
        print("Connection rejected: invalid token", e)
        return False

    user_id = int(payload.get("sub"))
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar()
    if not user:
        print("Connection rejected: user not found")
        return False

    # Сохраняем данные пользователя в сессии
    await sio.save_session(sid, {"user_id": user_id, "username": user.username})
    print(f"User {user.username} connected with sid {sid}")

     # Обновляем онлайн-статус для пользователя, подключившегося через WebSocket
    from utils.last_seen import set_user_online  # Импортируем здесь, если ещё не импортировано
    await set_user_online(user_id)
    
@sio.event
async def disconnect(sid):
    session = await sio.get_session(sid)
    print(f"User {session.get('username', 'unknown')} disconnected.")
    # Обновление статуса онлайн не производится здесь – online-счетчик обновляется через last_seen в вашем игровом коде.

@sio.event
async def send_message(sid, data):
    """
    Обработка отправки сообщения:
      - Извлекаем сессию (username),
      - Если передан текст, формируем сообщение,
      - Сохраняем сообщение в Redis (ограничиваем до 100 последних),
      - Рассылаем сообщение всем подключенным клиентам.
    """
    session = await sio.get_session(sid)
    username = session.get("username")
    text = data.get("text")
    if not text:
        return
    message = {"username": username, "text": text}
    await redis_client.rpush("chat_messages", json.dumps(message))
    await redis_client.ltrim("chat_messages", -100, -1)
    await sio.emit("chat_message", message)

@router.get("/messages")
async def get_messages():
    """
    Возвращает последние 100 сообщений из Redis.
    """
    messages = await redis_client.lrange("chat_messages", -100, -1)
    messages = [json.loads(msg) for msg in messages]
    return messages

@router.get("/online")
async def get_online_count():
    """
    Возвращает количество онлайн-пользователей.
    Здесь мы считаем ключи в Redis, созданные функцией set_user_online (last_seen).
    """
    online_keys = await redis_client.keys("online:*")
    online_count = len(online_keys)
    return {"online": online_count}

socket_app = socketio.ASGIApp(sio)



