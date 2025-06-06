import asyncio
from utils.shoputils import add_or_update_products_from_json
from database import async_session
from sqlalchemy import select
from models.models import Product

async def main():
    print("🚀 Загружаем новые товары из JSON...")
    async with async_session() as session:
        await add_or_update_products_from_json(session)
        print("✅ Готово! Все товары добавлены.")
        result = await session.execute(select(Product.id, Product.name))
        for row in result.all():
            print(f"🔹 [{row.id}] {row.name}")


if __name__ == "__main__":
    asyncio.run(main())

