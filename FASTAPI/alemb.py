import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

DSN = "postgresql+asyncpg://postgres:898939@localhost:5432/new_db"
engine = create_async_engine(DSN, echo=True, future=True)

async def test_connection():
    async with engine.connect() as conn:
        result = await conn.execute("SELECT 1")
        print(result.scalar())
    await engine.dispose()

asyncio.run(test_connection())

