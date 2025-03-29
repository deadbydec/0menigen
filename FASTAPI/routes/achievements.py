import os
import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from pydantic import BaseModel
from models.models import User, UserAchievement
from config import Config

jwt_access = JwtAccessBearer(secret_key="supersecretkey")

# Базовая директория и файл с ачивками из конфига
BASE_DIR = Config.BASE_DIR
ACHIEVEMENTS_FILE = Config.ACHIEVEMENTS_FILE

router = APIRouter(prefix="/api/achievements", tags=["Achievements"])

# 🔥 Функция загрузки всех доступных ачивок из JSON-файла
def load_achievements():
    if os.path.exists(ACHIEVEMENTS_FILE):
        with open(ACHIEVEMENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Модель для запроса выдачи ачивки
class UnlockAchievementRequest(BaseModel):
    achievement_id: str

@router.get("/view")
async def get_achievements(credentials: JwtAuthorizationCredentials = Depends(jwt_access), db: AsyncSession = Depends(get_db)):
    user_id = credentials.subject["user_id"]
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")


    # Получаем все ачивки из БД (информация для отображения)
    all_achievements = db.session.query(UserAchievement).all()
    # Множество ID ачивок, которые уже есть у юзера
    user_achievements = {ach.achievement_id for ach in db.session.query(UserAchievement).filter_by(user_id=user_id).all()}

    achievements_data = [
        {
            "id": ach.id,
            "title": ach.title,
            "description": ach.description,
            "icon": ach.icon_url,
            "unlocked": ach.id in user_achievements,
            "date": ach.date_unlocked.isoformat() if ach.id in user_achievements and ach.date_unlocked else None
        }
        for ach in all_achievements
    ]
    return JSONResponse(content=achievements_data)

# 🔥 API: Получить список ВСЕХ ачивок из JSON
@router.get("/all")
def get_all_achievements():
    return JSONResponse(content=load_achievements())

# 🔥 API: Получить ачивки текущего пользователя (данные из JSON, сопоставленные с БД)
@router.get("/")
async def get_user_achievements(credentials: JwtAuthorizationCredentials = Depends(jwt_access), db: AsyncSession = Depends(get_db)):
    user_id = credentials.subject["user_id"]
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Загружаем ачивки юзера из БД
    result = await db.execute(select(UserAchievement).where(UserAchievement.user_id == user.id))
    user_achievements = result.scalars().all()
    achievement_ids = {ach.achievement_id for ach in user_achievements}

    # Подтягиваем полную инфу из JSON-файла
    all_achievements = load_achievements()
    user_achievements_list = [ach for ach in all_achievements if ach["id"] in achievement_ids]

    return JSONResponse(content=user_achievements_list)

# 🔥 API: Выдать ачивку пользователю
@router.post("/unlock")
async def unlock_achievement(request_data: UnlockAchievementRequest, credentials: JwtAuthorizationCredentials = Depends(jwt_access), db: AsyncSession = Depends(get_db)):
    user_id = credentials.subject["user_id"]
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    achievement_id = request_data.achievement_id
    if not achievement_id:
        raise HTTPException(status_code=400, detail="Нет ID ачивки!")

    all_achievements = load_achievements()
    achievement = next((a for a in all_achievements if a["id"] == achievement_id), None)

    if not achievement:
        raise HTTPException(status_code=404, detail="Такой ачивки не существует!")

    # Проверяем, не выдана ли уже такая ачивка
    result = await db.execute(select(UserAchievement).where(UserAchievement.user_id == user.id, UserAchievement.achievement_id == achievement_id))
    existing_achievement = result.scalar()

    if existing_achievement:
        return JSONResponse(content={"message": "Ачивка уже получена!"}, status_code=200)

    # Добавляем новую ачивку в БД
    new_achievement = UserAchievement(user_id=user.id, achievement_id=achievement_id)
    db.add(new_achievement)
    
    # Добавляем XP за ачивку
    user.xp += achievement.get("reward", 0)

    await db.commit()

    return JSONResponse(content={"success": True, "message": f"Ачивка '{achievement['name']}' получена!"})

# 🔥 Функция: Проверка ачивок пользователя (вызывается при бою, торговле, исследовании и т.д.)
async def check_achievements(user_id: int, db: AsyncSession):
    """Проверяет, какие ачивки юзеру нужно выдать"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    if not user:
        return
    
    all_achievements = load_achievements()
    result = await db.execute(select(UserAchievement).where(UserAchievement.user_id == user.id))
    user_achievements = {ach.achievement_id for ach in result.scalars().all()}
    new_achievements = []

    for ach in all_achievements:
        ach_id = ach["id"]
        # Если ачивка уже есть – пропускаем
        if ach_id in user_achievements:
            continue

        # Проверяем условия выдачи ачивки
        if ach_id == "first_blood" and user.kills >= 1:
            new_achievements.append(ach)
        elif ach_id == "rich_boi" and user.coins >= 10000:
            new_achievements.append(ach)
        elif ach_id == "chatty_omeg" and user.chat_messages >= 100:
            new_achievements.append(ach)
        elif ach_id == "explorer" and user.visited_locations >= 10:
            new_achievements.append(ach)
        elif ach_id == "omegagod" and user.level >= 100:
            new_achievements.append(ach)

    # Выдаем новые ачивки
    for ach in new_achievements:
        db.add(UserAchievement(user_id=user.id, achievement_id=ach["id"]))
        user.xp += ach.get("reward", 0)
        print(f"✅ Ачивка получена: {ach['name']} (XP: {ach['reward']})")

    await db.commit()
