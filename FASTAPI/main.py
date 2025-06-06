import os
import json
import socketio
import asyncio
from redis.asyncio import Redis  # ✅ Правильный импорт!
import uvicorn
from config import settings
from datetime import timedelta
print(f"🔑 ТЕКУЩИЙ JWT_SECRET_KEY: {settings.JWT_SECRET_KEY}")
print("🔧 База данных:", settings.SQLALCHEMY_DATABASE_URI)
print("🔧 Redis URL:", settings.REDIS_URL)
print("🔧 Secret Key:", settings.SECRET_KEY)

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_socketio import SocketManager
import logging
from fastapi.logger import logger
from models import TokenBlocklist, News, User, Product, ForumThread

from database import get_db, async_session
from sqlalchemy.future import select
from utils.last_seen import set_user_online
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
from starlette.requests import Request
from auth.cookie_auth import get_current_user_from_cookie, DebugCookieAuthMiddleware, AsyncCookieAuthMiddleware
from routes import chat_router, admin_router
from config import Config
from utils.shoputils import shop_updater_loop

app = FastAPI()

socket_manager = SocketManager(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:7177"],  # Разрешаем ВСЁ (или укажи точные домены)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AsyncCookieAuthMiddleware)


# 🛠️ Добавляем костыль для OPTIONS, чтобы избежать 400



jwt_access = JwtAccessBearer(
    secret_key=settings.JWT_SECRET_KEY,
    access_expires_delta=settings.JWT_ACCESS_TOKEN_EXPIRES,
    refresh_expires_delta=settings.JWT_REFRESH_TOKEN_EXPIRES
)


redis_client = Redis.from_url("redis://localhost", decode_responses=True)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(shop_updater_loop())

    async with async_session() as db:
        result = await db.execute(select(TokenBlocklist))
        tokens = result.scalars().all()
        for token in tokens:
            await db.delete(token)
        await db.commit()
    print("✅ Блоклист токенов очищен при старте сервера!")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

from routes.chat import socket_app, router as chat_router
app.mount("/socket.io", socket_app)
app.mount("/api/profile/avatars", StaticFiles(directory=Config.UPLOAD_FOLDER), name="avatars")
app.mount("/static", StaticFiles(directory=Config.BASE_DIR + "/static"), name="static")



# 🔥 Делаем обработчик OPTIONS-запросов, как во Flask
@app.options("/{full_path:path}")
async def preflight(full_path: str, request: Request):
    print("📌 `preflight` CORS обработан!")  # ✅ Проверяем, вызывается ли
    response = JSONResponse(content={"msg": "CORS OK"})
    response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-CSRF-TOKEN, x-csrf-token"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.status_code = 200  # 👈 Делаем 200 OK (лучше, чем 204)
    return response

# ✅ Обработчик подключения


@app.get("/")
async def root():
    return {"message": "FastAPI + Socket.IO работает!"}


from routes import auth_router, pets_router, wardrobe_router, safe_router, verifyemail_router, playershop_router, landfill_router, donateshop_router, toilet_doom_router, gift_router, shop_router, news_router, index_router, player_router, players_router, inventory_router, games_router, profile_router, friends_router, inbox_router, wall_router, achievements_router, leaderboard_router, forum_router

# Подключаем роутеры (аналог Flask Blueprint)
app.include_router(index_router)
app.include_router(players_router, prefix="/api/players")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(news_router, prefix="/api/news")
app.include_router(chat_router, prefix="/api/chat")
app.include_router(shop_router, prefix="/api/shop")
app.include_router(inventory_router)
app.include_router(forum_router, prefix="/api/forum")
app.include_router(games_router)
app.include_router(profile_router, prefix="/api/profile")
app.include_router(friends_router, prefix="/api/friends")
app.include_router(inbox_router, prefix="/api/inbox")
app.include_router(wall_router, prefix="/api/wall")
app.include_router(achievements_router, prefix="/api/achievements")
app.include_router(leaderboard_router, prefix="/api/leaderboard")
app.include_router(player_router)
app.include_router(gift_router)
app.include_router(toilet_doom_router)
app.include_router(admin_router)
app.include_router(landfill_router)
app.include_router(donateshop_router, prefix="/api/donateshop")
app.include_router(playershop_router, prefix="/api/playershop")
app.include_router(safe_router, prefix="/api/safe")
app.include_router(verifyemail_router)
app.include_router(pets_router)
app.include_router(wardrobe_router)

from routes.socketio import socket_app

app.mount("/socket.io", socket_app)

SSL_CERT_PATH = "C:/Users/cumvolk/WebProjects/omeznet/frontend/localhost+2.pem"
SSL_KEY_PATH = "C:/Users/cumvolk/WebProjects/omeznet/frontend/localhost+2-key.pem"

@app.middleware("https")
async def update_online_status(request: Request, call_next):
    try:
        user = get_current_user_from_cookie(request)  # 👈 синхронная проверка из куки
        if user:
            await set_user_online(user.id)
            print(f"✅ Пользователь {user.id} онлайн")
    except Exception as e:
        print("⚠️ Токен отсутствует, продолжаем без авторизации")

    return await call_next(request)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)
    uvicorn.run(
    
        "main:app",
        host="localhost",
        port=5002,  # HTTPS-порт
        ssl_certfile=SSL_CERT_PATH,
        ssl_keyfile=SSL_KEY_PATH,
        workers=1,  # Указываем кол-во воркеров
    )

    