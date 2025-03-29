from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from database import get_db
from sqlalchemy import desc

from models.models import Leaderboard, User

router = APIRouter(prefix="/api/leaderboard", tags=["Leaderboard"])

jwt_access = JwtAccessBearer(secret_key="supersecretkey")

# ======================================================================
# Pydantic-модель для обновления рекорда игрока
# ======================================================================
class UpdateScoreRequest(BaseModel):
    category: str
    score: int

# ======================================================================
# ЭНДПОИНТЫ
# ======================================================================

# Получить топ игроков по категории (по умолчанию – ТОП богачей)
@router.get("/", response_model=list)
async def get_leaderboard(
    category: str = Query(default="money", description="Категория рейтинга"),
    period: str = Query(default="all", description="Период (фильтр по времени, пока не используется)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Фильтруем по категории и сортируем по убыванию рекорда, лимит 100 записей
    """
    result = await db.execute(
        select(Leaderboard)
        .where(Leaderboard.category == category)
        .order_by(desc(Leaderboard.score))
        .limit(100)
    )
    top_players = [entry.to_dict() for entry in result.scalars().all()]
    return JSONResponse(content=top_players, status_code=status.HTTP_200_OK)

# Обновить рекорд игрока
@router.post("/update")
async def update_score(
    data: UpdateScoreRequest,
    credentials: JwtAuthorizationCredentials = Depends(jwt_access),
    db: AsyncSession = Depends(get_db)
):
    user_id = int(credentials.subject["user_id"])
    category = data.category
    new_score = data.score

    if not category or new_score is None:
        raise HTTPException(status_code=400, detail="category и score обязательны")
    
    result = await db.execute(select(Leaderboard).where(Leaderboard.user_id == user_id, Leaderboard.category == category))
    entry = result.scalar()
    
    if entry:
        if new_score > entry.score:
            entry.score = new_score
            entry.last_updated = datetime.utcnow()
    else:
        entry = Leaderboard(user_id=user_id, category=category, score=new_score)
        db.add(entry)
    
    await db.commit()
    return JSONResponse(content={"message": "Рейтинг обновлён!", "entry": entry.to_dict()}, status_code=status.HTTP_200_OK)

# Получить топ игроков по уровням
@router.get("/levels")
async def get_top_levels(db: AsyncSession = Depends(get_db)):
    """Возвращает топ-100 игроков по уровню."""
    result = await db.execute(
        select(User)
        .order_by(desc(User.level))
        .limit(100)
    )
    top_players = result.scalars().all()
    players_data = [{"id": u.id, "username": u.username, "level": u.level} for u in top_players]
    return JSONResponse(content=players_data, status_code=status.HTTP_200_OK)