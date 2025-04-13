import asyncio
from redis.asyncio import Redis

# Подключение к Redis
redis = Redis.from_url("redis://localhost", decode_responses=True)

# 🔥 Функция сброса витрины и счётчика
async def reset_shop_state():
    await redis.delete("global_shop")
    await redis.delete("global_shop_refresh_count")
    print("🧹 Магазин и счётчик очищены")

# Запуск
if __name__ == "__main__":
    asyncio.run(reset_shop_state())