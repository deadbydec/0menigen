import redis.asyncio as redis

# Подключаем асинхронный Redis
redis = redis.from_url("redis://localhost", decode_responses=True)

async def set_user_online(user_id: int):
    """Записываем игрока в онлайн на 5 минут (ASYNC)"""
    print(f"[DEBUG] set_user_online вызван для user_id={user_id}")  # DEBUG
    await redis.setex(f"online:{user_id}", 300, "1")  # EX 300 = 5 минут

async def is_user_online(user_id: int) -> bool:
    """Проверяет, онлайн ли игрок (ASYNC)"""
    return await redis.exists(f"online:{user_id}") == 1