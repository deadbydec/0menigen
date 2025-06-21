# force_shop_reset.py
import asyncio
import json
from redis.asyncio import Redis
from database import get_db
from routes.shop import smart_shop_update

async def force_shop_reset():
    redis = Redis.from_url("redis://localhost", decode_responses=True)

    # 💣 Обнуляем счётчик сброса
    await redis.set("global_shop_reset_hour", -1)
    print("💣 Час сброса установлен на -1")

    # 🧠 Корректно извлекаем сессию из async генератора
    db_gen = get_db()
    db = await db_gen.__anext__()

    try:
        await smart_shop_update(db)
        print("✅ Магазин сброшен вручную!")
    finally:
        await db_gen.aclose()

if __name__ == "__main__":
    asyncio.run(force_shop_reset())

