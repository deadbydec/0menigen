import json
import asyncio
import redis.asyncio as redis_async  # не перезаписывай!
from config import Config  # убираем конфликт
from socket_config import sio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.models import Product, ProductRarity, ProductType
from config import Config
from sqlalchemy import delete
from routes.shop import get_random_products
from database import async_session

# Подключение к Redis (асинхронно)
redis_client = redis_async.from_url("redis://localhost", decode_responses=True)

#async def shop_updater_loop():
#    while True:
#        try:
#            print("🔁 Обновляем магазин...")

#            async with async_session() as db:
#                new_products = await get_random_products(db)

#            await redis_client.set("global_shop", json.dumps(new_products))
#            await sio.emit("shop_updated", {"products": new_products})

#            print("✅ Магазин обновлён, ждём 15 минут...")

#        except Exception as e:
#            print(f"🔥 Ошибка обновления магазина: {e}")

#        await asyncio.sleep(1 * 60)



# 🔹 Загрузка товаров из JSON
async def load_products_from_json():
    with open(Config.PRODUCTS_FILE, encoding="utf-8") as file:
        return json.load(file)

# 🔹 Обновление товара в Redis
async def update_global_shop(new_products):
    await redis_client.set("global_shop", json.dumps(new_products), ex=120)
    print("📌 Магазин записан в Redis!")

# 🔹 Получение товаров из Redis
async def get_global_shop():
    data = await redis_client.get("global_shop")
    return json.loads(data) if data else []

# 🔹 Добавление товаров в базу
async def add_or_update_products_from_json(db: AsyncSession):
    products_data = await load_products_from_json()

    rarity_map = {
        "trash": ProductRarity.trash,
        "common": ProductRarity.common,
        "prize": ProductRarity.prize,
        "rare": ProductRarity.rare,
        "epic": ProductRarity.epic,
        "legendary": ProductRarity.legendary,
        "special": ProductRarity.special,
        "unique": ProductRarity.unique,
        "elder": ProductRarity.elder,
        "vanished": ProductRarity.vanished,
        "glitched": ProductRarity.glitched,
        "void": ProductRarity.void
    }

    # Новая карта соответствий типов
    type_map = {
        "food": ProductType.food,
        "drink": ProductType.drink,
        "sweet": ProductType.sweet,
        "drug": ProductType.drug,
        "collectible": ProductType.collectible,
        "cosmetic": ProductType.cosmetic,
        "weapon": ProductType.weapon,
        "resource": ProductType.resource,
        "toy": ProductType.toy,
        "souvenir": ProductType.souvenir,
        "artifact": ProductType.artifact,
        "creature": ProductType.creature,
        "book": ProductType.book,
        "tech": ProductType.tech,
        "sticker": ProductType.sticker,
        "toilet": ProductType.toilet,
        "companion": ProductType.companion
    }

    PROTECTED_RARITIES = {
    ProductRarity.special,
    ProductRarity.unique,
    ProductRarity.prize,
    ProductRarity.vanished,
    ProductRarity.glitched,
    ProductRarity.void
}
    # Чистим только то, что НЕ входит в защищённые
    #stmt = delete(Product).where(Product.rarity.notin_(PROTECTED_RARITIES))
    #await db.execute(stmt)
    #await db.commit()


    result = await db.execute(select(Product))
    existing_products = {p.id: p for p in result.scalars()}

    new_count = 0
    updated_count = 0

    for data in products_data:
        pid = data["id"]
        if pid in existing_products:
            # 🧼 Обновляем, если что-то изменилось
            product = existing_products[pid]
            updated = False

            if product.name != data["name"]:
                product.name = data["name"]
                updated = True
            if product.description != data["description"]:
                product.description = data["description"]
                updated = True
            if product.price != data["price"]:
                product.price = data["price"]
                updated = True
            if product.image != data["image"]:
                product.image = data["image"]
                updated = True
            if product.rarity != rarity_map[data["rarity"]]:
                product.rarity = rarity_map[data["rarity"]]
                updated = True
            if product.product_type != type_map[data["product_type"]]:
                product.product_type = type_map[data["product_type"]]
                updated = True
            if product.custom != data.get("custom", {}):
                product.custom = data.get("custom", {})
                updated = True
            if product.types != data.get("types", []):
                product.types = data.get("types", [])
                updated = True



            if updated:
                updated_count += 1
        else:              
            product = Product(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                price=data["price"],
                image=data["image"],
                rarity=rarity_map[data["rarity"]],
                product_type=type_map[data["product_type"]],
                types=data.get("types", []),
                stock=1,
                custom=data.get("custom", {})
            )
            db.add(product)
            new_count += 1

    await db.commit()
    print(f"✅ Добавлено новых товаров: {new_count}")
    print(f"🔁 Обновлено существующих товаров: {updated_count}")

# 🔹 Обновление запаса товаров
async def reset_stock(db: AsyncSession):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    for product in products:
        if product.rarity not in {
            ProductRarity.trash,
            ProductRarity.common,
            ProductRarity.rare,
            ProductRarity.epic,
            ProductRarity.legendary,
            ProductRarity.elder
        }:
            continue  # защищаем магазинные
        product.stock = 0  # или вообще пропускаем
    await db.commit()
    print("✅ (safe) Reset stock завершён")
