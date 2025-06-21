from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.models import User, Role
from sqlalchemy.orm import selectinload
from auth.cookie_auth import get_current_user_from_cookie

router = APIRouter(prefix="/api/adminarnia", tags=["Админарния"])

async def verify_admin(db: AsyncSession = Depends(get_db), cookie_user=Depends(get_current_user_from_cookie)):
    # Перезагружаем юзера из БД с ролью
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == cookie_user.id)
    )
    user = result.scalar()

    if not user or not user.role or user.role.name != "ADMIN":
        raise HTTPException(status_code=403, detail="Ты не админ")

    return user

@router.get("/users")
async def get_all_users(db: AsyncSession = Depends(get_db), user=Depends(verify_admin)):
    result = await db.execute(select(User).options(selectinload(User.role)))
    users = result.scalars().all()
    return [
    {
        "id": u.id,
        "username": u.username,
        "role": {
            "name": u.role.name,
            "display_name": u.role.display_name
        } if u.role else None,
        "last_ips": [str(ip) for ip in u.last_ips] if u.last_ips else []
    }
    for u in users
]



@router.post("/assign-role")
async def assign_role(data: dict, db: AsyncSession = Depends(get_db), user=Depends(verify_admin)):
    target_id = data.get("user_id")
    role_name = data.get("role")

    if not target_id or not role_name:
        raise HTTPException(status_code=400, detail="user_id и role обязательны")

    role_result = await db.execute(select(Role).where(Role.name == role_name))
    role = role_result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=404, detail=f"Роль {role_name} не найдена")

    user_result = await db.execute(select(User).where(User.id == target_id))
    target = user_result.scalar_one_or_none()

    if not target:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    target.role_id = role.id
    await db.commit()

    return {"success": True, "assigned": role.display_name}


