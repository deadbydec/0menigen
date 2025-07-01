#auth.cookie_auth.py
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

#config.py
import os
import redis
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from datetime import timedelta
from fastapi_mail import ConnectionConfig

# Загружаем переменные окружения
load_dotenv()

class Settings(BaseSettings):
    # Если используешь asyncpg с SQLAlchemy, можешь указать "postgresql+asyncpg://..."
    SQLALCHEMY_DATABASE_URI: str = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql+asyncpg://postgres:898939@localhost:5432/new_db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "defaultsecretkey")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    # JWT Конфигурация
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key")  
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(days=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 7)))
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 30)))
     # 🔥 ДОБАВЬ ЭТИ:
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    class Config:
        env_file = ".env"

# Загружаем конфиг
settings = Settings()

MAIL_CONF = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TIMEOUT=30  # увеличиваем таймаут
)

# 🔹 Глобальные настройки (пути и файлы)
class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # База данных (асинхронная)
    DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI
    # Пути для загрузок
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    PRODUCT_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'goods')
    PET_UPLOAD_FOLDER     = os.path.join(BASE_DIR, 'static', 'pets')
    COSMETIC_UPLOAD_FOLDER     = os.path.join(BASE_DIR, 'static', 'cosmetic')
    FORUM_THREADS_PATH = os.path.join(BASE_DIR, "data", "forum_threads.json")
    NEWS_FILE = os.path.join(BASE_DIR, "data", "news.json")
    PRODUCTS_FILE = os.path.join(BASE_DIR, "data", "products.json")
    ACHIEVEMENTS_FILE = os.path.join(BASE_DIR, "data", "achievements.json")  # ✅ Путь к ачивкам

    # Создаём папки, если их нет
    for folder in [UPLOAD_FOLDER, PRODUCT_UPLOAD_FOLDER]:
        os.makedirs(folder, exist_ok=True)

    os.makedirs(os.path.dirname(NEWS_FILE), exist_ok=True)

    if not os.path.exists(NEWS_FILE):
        with open(NEWS_FILE, "w", encoding="utf-8") as f:
            f.write("[]")

    print(f"📌 NEWS_FILE загружен: {NEWS_FILE}")

# 🔹 Подключение Redis
try:
    REDIS_CONN = redis.StrictRedis.from_url(settings.REDIS_URL, decode_responses=False)
except redis.ConnectionError as e:
    print(f"❌ Ошибка подключения к Redis: {e}")
    REDIS_CONN = None

#routes.auth.py
from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query
from typing import AsyncGenerator
from jose import jwt, JWTError
from sqlalchemy import func
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import async_session as _async_session, User, InventoryItem, Product, async_session
import json
from config import Settings, settings
from database import get_db
from utils.confirm_email import send_confirmation_email

jwt_access = JwtAccessBearer(secret_key="supersecretkey", auto_error=True)

router = APIRouter()

async def validation_exception_handler(request, exc):
    print("📌 [DEBUG] Ошибка валидации:", exc.errors())  # ЛОГИРУЕМ!
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

async def some_dependency(local_kw: str = Query("ru")):
    return local_kw

# 🔥 Pydantic-модели для валидации запросов
class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str = Field(..., alias="confirmPassword")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True  # Добавляем для корректного маппинга

class UserLogin(BaseModel):
    username: str
    password: str

# ✅ Регистрация пользователя
@router.post("/register")
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    
    print("📌 [DEBUG] Данные регистрации:", user_data.model_dump())  # Логируем, что реально приходит
    """Регистрация нового пользователя"""
    
    if user_data.password != user_data.confirm_password:
        raise HTTPException(status_code=400, detail="Пароли не совпадают!")

    user_data.username = user_data.username.strip().lower()
    existing_user = await db.execute(select(User).where(func.lower(User.username) == user_data.username.lower()))
    if existing_user.scalar():
        raise HTTPException(status_code=409, detail="Пользователь уже существует!")
    user_data.email = user_data.email.strip().lower()
    existing_email = await db.execute(select(User).where(func.lower(User.email) == user_data.email.lower()))
    if existing_email.scalar():
        raise HTTPException(status_code=409, detail="Этот email уже используется!")

    try:
        # 🌱 Создание нового юзера
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=generate_password_hash(user_data.password),
            coins=500,
            nullings=0.0,
            level=1,
            xp=0,
            avatar="/api/profile/avatars/default_avatar.png",
            gender="UNKNOWN"
        )
        db.add(new_user)
        await db.flush()  # не коммитим пока

        # 🎁 Выдача предметов
        starter_names = [
    "Ржавый ключ от реальности",
    "Энергофлекс",
    "Потрёпанная памятка новичку"
]
        result = await db.execute(select(Product).where(Product.name.in_(starter_names)))
        starter_products = result.scalars().all()

        if not starter_products:
            raise HTTPException(status_code=500, detail="Стартовые предметы не найдены в базе.")

        for product in starter_products:
            item = InventoryItem(
                user_id=new_user.id,
                product_id=product.id,
                quantity=1
            )
            db.add(item)

            # ✉️ Отправка письма с подтверждением
        #await send_confirmation_email(
            #user=new_user,
            #db=db,
            #base_url="https://localhost:5002/api"  # ← или твой внешний адрес позже
        #)

        await db.commit()  # ✅ Один раз — если всё прошло успешно
        return {"message": "Регистрация успешна! Подтвердите email перед входом."}

    except Exception as e:
        await db.rollback()  # ❌ Откат, если что-то пошло не так
        print(f"❌ Ошибка при регистрации: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при создании пользователя. Попробуйте позже.")

# ✅ Логин
# ✅ ЛОГИН (заменили AuthJWT на fastapi-jwt)
@router.post("/login")
async def login(user_data: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user_data.username))
    user = result.scalar()

    if not user or not check_password_hash(user.password, user_data.password):
        raise HTTPException(status_code=401, detail="Неправильный логин или пароль!")

    # ⛓️ СОЗДАЁМ ТОКЕН САМИ
    access_payload = {
        "sub": str(user.id),
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=60),
        "iat": datetime.utcnow(),
    }

    csrf_payload = {
        "sub": str(user.id),
        "type": "csrf",
        "exp": datetime.utcnow() + timedelta(minutes=10),
        "iat": datetime.utcnow(),
    }

    access_token = jwt.encode(access_payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    csrf_token = jwt.encode(csrf_payload, settings.JWT_SECRET_KEY, algorithm="HS256")

    response = Response(
        content=json.dumps({"msg": "Login successful"}),
        status_code=200,
        media_type="application/json"
    )

    response.set_cookie(
        key="access_token_cookie",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="None",
    )
    response.set_cookie(
        key="csrf_access_token",
        value=csrf_token,
        secure=True,
        samesite="None",
    )

    return response

# ✅ Логаут (ревокация токена)
@router.post("/logout")
async def logout():
    resp = JSONResponse({"msg": "logged out"})
    # при логине ты ставишь secure=True, samesite="None"
    resp.delete_cookie(
        "access_token_cookie",
        secure=True,
        samesite="None",
        path="/",               # такие же!
    )
    resp.delete_cookie(
        "csrf_access_token",
        secure=True,
        samesite="None",
        path="/",
    )
    return resp