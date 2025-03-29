import aioredis
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Подключаем Redis (АСИНХРОННО)
r = aioredis.from_url("redis://localhost", decode_responses=True)

@router.websocket("/chat")
async def chat_ws(websocket: WebSocket):
    await websocket.accept()

    # Создаём подписку на канал
    pubsub = r.pubsub()
    await pubsub.subscribe("chat_channel")

    async def reader():
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"])

    # Запускаем задачу прослушки Redis-канала
    reader_task = asyncio.create_task(reader())

    try:
        while True:
            data = await websocket.receive_text()
            await r.publish("chat_channel", data)  # Redis теперь асинхронный
    except WebSocketDisconnect:
        reader_task.cancel()
        await pubsub.unsubscribe("chat_channel")
        await pubsub.close()
