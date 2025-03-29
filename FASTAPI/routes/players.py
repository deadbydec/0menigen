import redis.asyncio as redis
from fastapi import APIRouter, Query, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.models import User
from database import get_db

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
