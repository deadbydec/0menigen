from models.models import User, Role
from sqlalchemy.future import select
from database import async_session
import asyncio

async def give_role(user_id: int, role_name: str):
    async with async_session() as session:
        # Ищем роль
        role_result = await session.execute(select(Role).where(Role.name == role_name))
        role = role_result.scalar()
        if not role:
            print(f"❌ Роль '{role_name}' не найдена")
            return

        # Ищем пользователя
        user_result = await session.execute(select(User).where(User.id == user_id))
        user = user_result.scalar()
        if not user:
            print(f"❌ Пользователь с ID {user_id} не найден")
            return

        # Привязываем
        user.role = role
        await session.commit()
        print(f"✅ Роль '{role_name}' выдана пользователю {user.username} (ID: {user_id})")

# 🧪 Запуск вручную
if __name__ == "__main__":
    asyncio.run(give_role(user_id=1, role_name="admin"))