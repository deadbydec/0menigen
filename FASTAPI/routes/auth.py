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
    "Глитч-напиток «УГАР»",
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

        await db.commit()  # ✅ Один раз — если всё прошло успешно
        return {"message": "Регистрация успешна! Теперь можно войти."}

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
async def logout(response: Response, request: Request):
    token = request.cookies.get("access_token_cookie")  # 🧐 Проверяем, есть ли кука
    response.delete_cookie("access_token_cookie")
    response.delete_cookie("csrf_access_token")
    
    if not token:
        return {"message": "🛑 Токен уже пустой. Зачем ты здесь?"}
    
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    
    return RedirectResponse(url="/login", status_code=302)

