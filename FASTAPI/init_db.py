import asyncio
from database import engine, Base
from database import async_session
from models.models import Role  # 💡 если модель там
from sqlalchemy import select

# 🔥 Создание ролей
async def create_roles(session):
    existing = await session.execute(select(Role.name))
    existing_names = {r[0] for r in existing.all()}
    roles = ["admin", "moderator", "bot", "npc", "tester"]

    for role_name in roles:
        if role_name not in existing_names:
            session.add(Role(name=role_name))
    await session.commit()
    print("✅ Роли обновлены")

# 🔥 Общий запуск
async def init():
    async with engine.begin() as conn:
        print(f"📌 Таблицы: {Base.metadata.tables.keys()}")
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        await create_roles(session)

if __name__ == "__main__":
    asyncio.run(init())
