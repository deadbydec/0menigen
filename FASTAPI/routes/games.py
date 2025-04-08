from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from datetime import datetime, date
from database import get_db
from models.models import User, Match3Score
from auth.cookie_auth import get_current_user_from_cookie
from pydantic import BaseModel

router = APIRouter(prefix="/api/games", tags=["games"])

class Match3Result(BaseModel):
    score: int
    combos: int
    coins_earned: int
    xp_earned: int

@router.post("/match3/submit")
async def submit_match3_score(
    data: Match3Result,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_from_cookie)
):
    today = date.today()

    result = await db.execute(
        select(func.count())
        .select_from(Match3Score)
        .where(
            Match3Score.user_id == user.id,
            Match3Score.is_rewarded == True,
            func.date(Match3Score.submitted_at) == today
        )
    )
    rewarded_today = result.scalar()

    is_rewarded = rewarded_today < 3

    db.add(Match3Score(
        user_id=user.id,
        score=data.score,
        combos=data.combos,
        coins_earned=data.coins_earned if is_rewarded else 0,
        xp_earned=data.xp_earned if is_rewarded else 0,
        is_rewarded=is_rewarded
    ))

    if is_rewarded:
        user.coins += data.coins_earned
        user.xp += data.xp_earned
        db.add(user)

    await db.commit()

    return {
        "message": "Награды выданы!" if is_rewarded else "Лимит наград за сегодня достигнут, но результат сохранён.",
        "xp_gained": data.xp_earned if is_rewarded else 0,
        "coins_gained": data.coins_earned if is_rewarded else 0,
        "score": data.score,
        "rewarded_today": rewarded_today + (1 if is_rewarded else 0),
        "reward_limit": 3
    }

# 🏆 Топ игроков Match-3
@router.get("/match3/leaderboard")
async def match3_leaderboard(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User.username, func.max(Match3Score.score))
        .join(Match3Score, Match3Score.user_id == User.id)
        .group_by(User.username)
        .order_by(func.max(Match3Score.score).desc())
        .limit(10)
    )
    top = result.all()
    return {
        "leaderboard": [{"username": r[0], "score": r[1]} for r in top]
    }