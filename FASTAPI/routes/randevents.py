# routes/events.py
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from random import random, randint

from auth.cookie_auth import get_current_user_from_cookie
from database import get_db

router = APIRouter()

@router.post("/api/events/random")
async def random_event(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return {"message": "User not authenticated."}

    if random() > 0.35:
        return {"message": "Ничего не найдено... только баг в стене."}

    coins = randint(47, 83)
    user.coins += coins
    await db.commit()

    return {
        "message": f"✨ Ты услышал шёпот из вентиляции... +{coins} монет!",
        "coins": coins
    }
