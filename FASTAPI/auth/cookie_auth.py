from fastapi import Request, HTTPException, Depends
from jose import jwt, JWTError
from sqlalchemy import select
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware, ASGIApp
from database import get_db, async_session
from models import User
from config import settings
from utils.last_seen import set_user_online
from typing import Optional

EXCLUDED_PATHS = ["/auth/login", "/auth/register", "/auth/check-auth"]
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"




def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="❌ Невалидный или повреждённый токен")

def get_token_from_cookie(request: Request) -> str:
    token = request.cookies.get("access_token_cookie")
    if not token:
        raise HTTPException(status_code=401, detail="❌ Не передан access_token_cookie")
    return token

async def get_current_user_from_cookie(request: Request) -> Optional[User]:
    if request.method == "OPTIONS":
        print("🛰️ [CORS] OPTIONS-запрос — игнорируем авторизацию")
        return None

    token = get_token_from_cookie(request)
    if not token:
        print("⚠️ [COOKIE] Токен не найден")
        return None

    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
        if not user_id:
            print("❌ [COOKIE] В токене нет user_id")
            return None

        async with async_session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                return user
            print("❌ [COOKIE] Юзер не найден в БД")
    except JWTError as e:
        print(f"❌ [COOKIE] JWTError: {e}")
    except Exception as e:
        print(f"💥 [COOKIE] Ошибка при получении юзера: {e}")

    return None


class AsyncCookieAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # ✅ Пропускаем preflight-запросы от CORS
        if request.method == "OPTIONS":
            return await call_next(request)

        request_path = request.url.path
        if any(request_path.startswith(p) for p in EXCLUDED_PATHS):
            return await call_next(request)
        
        request.state.user = None
        token = request.cookies.get("access_token_cookie")

        if token:
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = int(payload.get("sub"))
                async with async_session() as session:
                    user = await session.get(User, user_id)
                    if user:
                        request.state.user = user
                        await set_user_online(user.id)
            except JWTError as e:
                print(f"❌ Невалидный токен: {e}")

        response = await call_next(request)
        return response



class DebugCookieAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        if request.method == "OPTIONS":
            return await call_next(request)
        # Тут можно отловить куку до запроса:
        token = request.cookies.get("access_token_cookie")

        if token:
            try:
                # Просто декодируем и печатаем (без зависимостей)
                from config import settings
                SECRET_KEY = settings.JWT_SECRET_KEY
                ALGORITHM = "HS256"
                from jose import jwt
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                print(f"🔐 [COOKIE OK] Payload: {payload}")
            except JWTError as e:
                print(f"🚫 [COOKIE FAIL] JWTError: {str(e)}")
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Невалидный токен (JWTError)"},
                )
            except Exception as e:
                print(f"💥 [COOKIE CRASH] Exception: {str(e)}")
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Ошибка при проверке токена"},
                )
        else:
            print("⚠️ [COOKIE MISS] access_token_cookie не найден")

        return await call_next(request)