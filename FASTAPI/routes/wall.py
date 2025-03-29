import json
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from database import get_db
from sqlalchemy.orm import selectinload
from auth.cookie_auth import get_current_user_from_cookie  # ✅ если не импортнул ещё
from models.models import User, WallPost

router = APIRouter()

class AddWallPostRequest(BaseModel):
    text: str
    timestamp: Optional[datetime] = None  # если захочешь ручной time-travel 🤪

class DeleteWallPostRequest(BaseModel):
    index: int
    confirm: Optional[bool] = False  # защита от случайного удаления (на будущее)


@router.get("/", response_model=list)
async def get_wall_posts(
    user: User = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User)
        .options(selectinload(User.wall_posts))  # ✅ жёсткая предзагрузка
        .where(User.id == user.id)
    )
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    posts = user.wall_posts if user.wall_posts else []

    posts_list = [
        {
            "id": post.id,
            "text": post.text,
            "created_at": post.created_at.isoformat() if post.created_at else None
        }
        for post in posts
    ]
    return JSONResponse(content=posts_list, status_code=status.HTTP_200_OK)


# POST /api/wall/add - Добавить новую запись на стену
@router.post("/add")
async def add_wall_post(
    data: AddWallPostRequest,
    user: User = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Текст записи обязателен")

    # user уже есть, никакие id из токена не нужны
    new_post = WallPost(user_id=user.id, text=data.text)
    db.add(new_post)
    await db.commit()

    return JSONResponse(
        content={"success": True, "message": "Запись добавлена!"},
        status_code=status.HTTP_200_OK
    )

# POST /api/wall/delete - Удалить запись со стены по индексу
@router.post("/delete")
async def delete_wall_post(
    data: DeleteWallPostRequest,
    user: User = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    # 🔐 Пользователь уже пришёл, не нужно вытаскивать ID из токена
    wall = user.get_wall()
    index = data.index

    if index is None or not (0 <= index < len(wall)):
        raise HTTPException(status_code=400, detail="Некорректный индекс")

    wall.pop(index)
    user.wall_posts = json.dumps(wall)
    await db.commit()

    return JSONResponse(
        content={"success": True, "message": "Запись удалена!"},
        status_code=status.HTTP_200_OK
    )
