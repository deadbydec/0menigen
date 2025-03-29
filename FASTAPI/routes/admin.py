from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from database import get_db
from models.models import User

router = APIRouter(prefix="/api/admin", tags=["admin"])

# 🔎 Поиск пользователей по никнейму (например, 'джипет')
@router.get("/find-users")
async def find_users(q: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.username.ilike(f"%{q}%"))
    )
    users = result.scalars().all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "usertype": user.user_type.to_russian() if user.user_type else "Неизвестен",
            "email": user.email,
            "bio": user.bio,
        }
        for user in users
    ]

# 🧨 Удаление пользователя по ID
@router.delete("/user/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()

    if not user:
        raise HTTPException(status_code=404, detail="❌ Пользователь не найден")

    await db.delete(user)
    await db.commit()

    return {"success": True, "message": f"Пользователь {user.username} удалён"}
