import asyncio
from utils.shoputils import add_products_to_db
from database import async_session
from sqlalchemy import delete, select
from models.models import Product


async def main():
    print("🚑 Очищаем таблицу товаров...")
    async with async_session() as session:
        await session.execute(delete(Product))
        await session.commit()
        print("🧼 Старые товары удалены.")

        print("🚀 Загружаем новые товары из JSON...")
        await add_products_to_db(session)
        print("✅ Готово! Все товары загружены в базу.")
        result = await session.execute(select(Product.id, Product.name))
        for row in result.all():
            print(f"🧾 {row.id}: {row.name}")

if __name__ == "__main__":
    asyncio.run(main())
