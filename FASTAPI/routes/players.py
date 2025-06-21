import redis.asyncio as redis
from fastapi import APIRouter, Query, HTTPException, status, Depends
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.models import User
from database import get_db
from fastapi import Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.models import User, SystemMessage, SystemMessageType
from database import get_db
from auth.cookie_auth import get_token_from_cookie, decode_access_token
from jose import JWTError
from sqlalchemy.orm import selectinload
from utils.last_seen import is_user_online

router = APIRouter()

# Подключаемся к Redis
r = redis.from_url("redis://localhost", decode_responses=True)

@router.get("/", response_model=List[Dict])
async def get_players(
    filter: str = Query(default="all", description="'all' или 'online'"),
    search: str = Query(default="", description="Строка поиска по нику"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получает список игроков с фильтром:
    - filter: 'all' (все) или 'online' (только онлайн)
    - search: строка поиска по нику
    """
    # Строим запрос к базе пользователей
    result = await db.execute(select(User).where(User.username.ilike(f"%{search}%")) if search else select(User))
    players = result.scalars().all()

    # Оптимизированный запрос к Redis: получаем все ключи "online:*" сразу
    online_keys = await r.keys("online:*")
    online_user_ids = {int(key.split(":")[1]) for key in online_keys}

    result = [
        {
            "id": player.id,
            "username": player.username,
            "avatar_url": player.avatar,
            "status": "online" if player.id in online_user_ids else "offline"
        }
        for player in players
    ]

    # Если фильтр "online" – оставляем только онлайн-игроков
    if filter == "online":
        result = [p for p in result if p["status"] == "online"]

    return JSONResponse(content=result, status_code=status.HTTP_200_OK)


@router.get("/public/{user_id}")
async def get_public_player(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).options(selectinload(User.race)).where(User.id == user_id)
    )
    user = result.scalar()

    if not user:
        raise HTTPException(status_code=404, detail="Публичный профиль не найден")


    return {
        "id": user.id,
        "username": user.username,
        "avatar": user.avatar or "/api/profile/avatars/default_avatar.png",
        "race": {
            "id": user.race.id,
            "code": user.race.code,
            "display_name": user.race.display_name
        } if user.race else None,
        "bio": user.bio or "",
        "level": user.level,
        "coins": user.coins,
        "status": "online" if is_user_online(user.id) else "offline",
        "usertype": user.user_type.to_russian(),
        "gender": user.gender.name if user.gender else "UNKNOWN",
        "gender_label": user.gender.to_russian() if user.gender else "неизвестный",
        "registrationDate": user.registration_date.isoformat() if user.registration_date else None,
    }


