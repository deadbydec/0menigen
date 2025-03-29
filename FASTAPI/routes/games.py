from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models.models import User, GameScore, Leaderboard
from datetime import datetime

router = APIRouter(prefix="/api/games", tags=["Games"])

jwt_access = JwtAccessBearer(secret_key="supersecretkey")

# 🔥 Заглушка для системы мини-игр с конвертацией очков в монеты

@router.post("/save_score")
async def save_game_score(
    game_id: int,
    score: int,
    credentials: JwtAuthorizationCredentials = Depends(jwt_access),
    db: AsyncSession = Depends(get_db)
):
    """Сохраняет результаты мини-игры и конвертирует очки в монеты."""
    user_id = int(credentials.subject["user_id"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Конвертация очков в монеты (1 монета = 100 очков)
    coins_earned = score // 100
    user.coins += coins_earned
    
    # Сохраняем результат игры в таблице GameScore
    new_score = GameScore(user_id=user.id, game_id=game_id, score=score, timestamp=datetime.utcnow())
    db.add(new_score)
    
    # Проверяем глобальный рейтинг
    leaderboard_result = await db.execute(select(Leaderboard).where(Leaderboard.user_id == user_id, Leaderboard.category == "games"))
    leaderboard_entry = leaderboard_result.scalar()
    
    if leaderboard_entry:
        if score > leaderboard_entry.score:
            leaderboard_entry.score = score
            leaderboard_entry.last_updated = datetime.utcnow()
    else:
        leaderboard_entry = Leaderboard(user_id=user.id, category="games", score=score)
        db.add(leaderboard_entry)
    
    await db.commit()
    
    return JSONResponse(content={"message": "Результат сохранён!", "coins_earned": coins_earned, "total_coins": user.coins}, status_code=status.HTTP_200_OK)

@router.get("/leaderboard")
async def get_leaderboard(db: AsyncSession = Depends(get_db)):
    """Возвращает топ-10 игроков по очкам в мини-играх."""
    result = await db.execute(
        select(User.username, Leaderboard.score)
        .join(User, User.id == Leaderboard.user_id)
        .where(Leaderboard.category == "games")
        .order_by(Leaderboard.score.desc())
        .limit(10)
    )
    top_players = result.all()
    
    return JSONResponse(content={"leaderboard": [{"username": player[0], "score": player[1]} for player in top_players]}, status_code=status.HTTP_200_OK)