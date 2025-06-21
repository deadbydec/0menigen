import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import async_session  # путь может отличаться у тебя
from models.models import User, Role  # путь к моделям подгони под себя

async def assign_admin_role(user_id: int):
    async with async_session() as session:
        # Ищем роль ADMIN
        result = await session.execute(select(Role).where(Role.name == "ADMIN"))
        admin_role = result.scalar_one_or_none()

        if not admin_role:
            print("❌ Роль ADMIN не найдена в базе.")
            return

        # Ищем юзера
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            print(f"❌ Пользователь с ID {user_id} не найден.")
            return

        user.role_id = admin_role.id
        user.role_assigned_at = datetime.utcnow()

        await session.commit()
        print(f"✅ Пользователь {user.username} теперь {admin_role.display_name}.")

if __name__ == "__main__":
    asyncio.run(assign_admin_role(1))
