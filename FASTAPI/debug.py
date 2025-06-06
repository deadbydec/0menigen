import asyncio
from sqlalchemy import select
from database import async_session
from models.models import Product, ProductType

async def main():
    async with async_session() as db:
        result = await db.execute(
            select(Product).where(Product.product_type == ProductType.creature.value)
        )
        eggs = result.scalars().all()
        for egg in eggs:
            print(f"[{egg.id}] {egg.name} → {egg.custom}")

if __name__ == "__main__":
    asyncio.run(main())

