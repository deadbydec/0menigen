from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Pet, Product, InventoryItem


async def get_detailed_read_books(pet: Pet, db: AsyncSession):
    read_ids = pet.read_books or []
    if not read_ids:
        return []

    result = await db.execute(
        select(Product).where(Product.custom["unique_read_id"].astext.in_(read_ids))
    )
    products = result.scalars().all()

    return [
        {
            "product_id": p.id,
            "name": p.name,
            "image": p.image,
            "description": p.description,
            "read_id": p.custom.get("unique_read_id")
        }
        for p in products
    ]


async def apply_book_to_pet(pet: Pet, user_id: int, book_id: int, db: AsyncSession):
    # проверяем инвентарь
    item = await db.scalar(
        select(InventoryItem).where(
            InventoryItem.user_id == user_id,
            InventoryItem.product_id == book_id
        )
    )
    if not item:
        raise HTTPException(400, "У тебя нет этой книги")

    # подгружаем продукт
    product = await db.get(Product, book_id)
    if not product or not product.custom:
        raise HTTPException(400, "Некорректный предмет")

    custom = product.custom
    effect = custom.get("effect")
    read_id = custom.get("unique_read_id")
    stat_bonus = custom.get("stat_bonus", {})

    if effect != "grant_stat_once" or not read_id:
        raise HTTPException(400, "Эта книга не может быть применена")

    if read_id in (pet.read_books or []):
        raise HTTPException(400, "Питомец уже читал эту книгу")

    # применяем бонусы
    for stat, value in stat_bonus.items():
        if hasattr(pet, stat):
            setattr(pet, stat, getattr(pet, stat) + value)

    # записываем
    pet.read_books.append(read_id)
    await db.delete(item)

    return {
        "message": f"Книга '{product.name}' прочитана питомцем {pet.name}.",
        "pet": {
            "id": pet.id,
            "name": pet.name,
            "new_stats": {
                stat: getattr(pet, stat) for stat in stat_bonus
            }
        }
    }

