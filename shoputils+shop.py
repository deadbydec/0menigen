#routes.shop.py
import random
import asyncio
import json
from socket_config import sio
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models.models import Product, InventoryItem, ProductRarity, User
from redis.asyncio import Redis as AsyncRedis
from auth.cookie_auth import get_current_user_from_cookie
from collections import defaultdict
from datetime import datetime

router = APIRouter()

redis = AsyncRedis.from_url("redis://localhost", decode_responses=True)

# 🔥 Загрузка (при желании) из products.json
async def load_products_from_json():
    with open("data/products.json", encoding="utf-8") as file:
        return json.load(file)

async def get_random_products(db: AsyncSession):
    # 1) Выбираем товары из БД, исключая особые редкости
    result = await db.execute(
        select(Product).where(
            Product.stock > 0,
            Product.rarity.notin_([
    ProductRarity.special, 
    ProductRarity.prize, 
    ProductRarity.unique, 
    ProductRarity.vanished, 
    ProductRarity.glitched, 
    ProductRarity.void
])
        )
    )
    products = result.scalars().all()

    if not products:
        print("⚠ Нет доступных товаров для обновления магазина!")
        return []

    # 2) Настройки редкостей: (шанс, (min_items, max_items), (min_stock, max_stock))
    rarity_weights = {
        ProductRarity.trash: (100, (8, 10), (1, 2)),
        ProductRarity.common: (85, (8, 15), (2, 3)),
        ProductRarity.rare:      (35,  (2, 4), (1, 1)),
        ProductRarity.epic:      (12,   (1, 2), (1, 1)),
        ProductRarity.legendary: (4,   (1, 1), (1, 1)),
        ProductRarity.elder:     (1,   (1, 1), (1, 1)),
    }

    # 3) Группируем товары по (product_type -> rarity -> [товары])
    # 1. Группируем товары по редкости (без product_type)
    rarity_dict = defaultdict(list)
    for p in products:
        if p.rarity in rarity_weights:
            rarity_dict[p.rarity].append(p)

    # 4) Генерируем список для витрины
    selected_products = []

    for rarity, (chance, count_range, stock_range) in rarity_weights.items():
        roll = random.randint(1, 100)
        if roll <= chance:
            available_items = rarity_dict.get(rarity, [])
            if not available_items:
                continue

                # Кол-во
            count_min, count_max = count_range
            count_max = min(count_max, len(available_items))
            if count_min > count_max:
                continue

            num_items = random.randint(count_min, count_max)
            chosen = random.sample(available_items, num_items)

                # Cток
            stock_min, stock_max = stock_range
            for item in chosen:
                if stock_min > stock_max:
                    continue
                random_stock = random.randint(stock_min, stock_max)

                # ✅ ОБНОВЛЯЕМ БД-СТОК
                item.stock = random_stock
                db.add(item)

                selected_products.append({
                        "id": item.id,
                        "name": item.name,
                        "price": item.price,
                        "rarity": item.rarity.value,
                        "image": item.image,
                        "description": item.description,
                        "stock": random_stock,
                        "product_type": item.product_type.value,
                    })

    print("🛒 Обновлённый магазин:", [f"{p['name']} ({p['stock']} шт.)" for p in selected_products])

     # 🧠 Без этого — изменения в БД не сохранятся
    await db.commit()
    
    return selected_products

# --------------------------------
#  Функция-обёртка c "накопительным" завозом
# --------------------------------
# Ключ для хранения: в какой час был последний сброс
last_reset_hour_key = "global_shop_reset_hour"

async def smart_shop_update(db: AsyncSession):
    shop_key = "global_shop"
    reset_hour_key = last_reset_hour_key

    # Считываем текущий час
    current_hour = datetime.now().hour
    last_reset_raw = await redis.get(reset_hour_key)
    last_reset_hour = int(last_reset_raw) if last_reset_raw else None

    # Проверка: пора ли сбрасывать
    full_reset_needed = (last_reset_hour != current_hour)

    # Генерируем новую порцию товаров
    new_products = await get_random_products(db)

    if full_reset_needed:
        print(f"💥 Новый час ({current_hour}) — сбрасываем магазин!")
        await redis.set(shop_key, json.dumps(new_products))
        await redis.set(reset_hour_key, current_hour)
        await sio.emit("shop_update", {"products": new_products}, namespace="/shop")
        return

    # 🟢 Иначе — накопительный завоз
    print(f"🔄 Накопительный завоз в {datetime.now().strftime('%H:%M:%S')}")
    existing_raw = await redis.get(shop_key)
    existing = json.loads(existing_raw) if existing_raw else []

    existing_dict = {p["id"]: p for p in existing}
    for item in new_products:
        if item["id"] in existing_dict:
            existing_dict[item["id"]]["stock"] += item["stock"]
        else:
            existing_dict[item["id"]] = item

    final_shop = list(existing_dict.values())
    await redis.set(shop_key, json.dumps(final_shop))
    await sio.emit("shop_update", {"products": final_shop}, namespace="/shop")

    print(f"✔ Магазин обновлён. Всего товаров: {len(final_shop)}")


# --------------------------------
#  Теперь используем smart_shop_update
# --------------------------------
async def background_shop_updater():
    print("🚀 Фоновый процесс background_shop_updater() запущен!")
    #Раз в 20 сек вызываем smart_shop_update, который сам решает «добавлять» или «сбросить».
    while True:
        await asyncio.sleep(random.randint(15, 40))
        async for db in get_db():
            await smart_shop_update(db)



# ===========================
#  Получение витрины
# ===========================
@router.get("/")
async def get_shop(
    request: Request,
    category: str = Query(None),
    user: User = Depends(get_current_user_from_cookie)
):
    """Возвращает товары из Redis с фильтрацией по category."""
    shop_data_raw = await redis.get("global_shop")
    if not shop_data_raw:
        raise HTTPException(status_code=500, detail="Не удалось получить магазин из Redis")

    products_data = json.loads(shop_data_raw)

    # Маппинг категорий
    mapping = {
        "еда": ["еда"],
        "напиток": ["напиток"],
        "сладость": ["сладость"],
        "книга": ["книга"],
        "наклейка": ["наклейка"],
        "игрушка": ["игрушка"],
        "аптека": ["аптека"],
        "гаджет": ["гаджет"],
        "туалет": ["туалет"],
        "сувенир": ["сувенир"],
        "существо": ["существо"],
        "коллекционный": ["коллекционный", "сувенир", "игрушка", "наклейка"],
        "косметический": ["косметический"],

        "cosmetic": ["косметический"],
        "cosmetic": ["cosmetic"],
        "toy": ["игрушка"],
        "tech": ["гаджет"],
        "toilet": ["туалет"],
        "слив": ["туалет"],
        "drugs": ["аптека"],
        "drug": ["аптека"],
        "books": ["книга"],
        "book": ["книга"],
        "книжник": ["книга"],
        "food": ["еда", "напиток", "сладость"],
        "существо": ["creature"],
        "creature": ["существо"],

        "cosmetic": ["косметический", "cosmetic"],
        "zoo": ["существо"],
        "вивариум": ["zoo"],
        "продуктовый": ["еда", "напиток", "сладость"],
        "технолайт": ["гаджет"],
        "КосмоШоп": ["косметический", "cosmetic"],
        "коллекционер": ["коллекционный", "сувенир", "игрушка", "наклейка"],
        "collectioner": ["коллекционный", "сувенир", "игрушка", "наклейка"],
    }

    if category:
        allowed_types = mapping.get(category.lower())
        if allowed_types is None:
            return JSONResponse(
                content={"error": f"Неизвестная категория: {category}"},
                status_code=400
            )
        filtered_products = [
            p for p in products_data
            if p.get("product_type", "").lower() in allowed_types
        ]
    else:
        filtered_products = products_data

    return {"products": filtered_products}


# ===========================
#  Покупка товара
# ===========================
@router.post("/buy/{product_id}")
async def buy_product(
    request: Request,
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_from_cookie)
):
    """Позволяет игроку купить товар, снижая его сток в Redis."""
    # 1. Получаем товар из БД под замок
    result = await db.execute(
        select(Product).where(Product.id == product_id).with_for_update()
    )
    product = result.scalar()

    if not user or not product:
        raise HTTPException(status_code=404, detail="Пользователь или товар не найдены!")

    # 2. Проверяем деньги + локальный сток (product.stock)
    if user.coins < product.price:
        raise HTTPException(status_code=400, detail="У вас недостаточно коинов!")
    if product.stock <= 0:
        raise HTTPException(status_code=400, detail="Товара больше нет в наличии (по данным БД)!")

    # 3. Списываем деньги, уменьшаем сток в БД
    user.coins -= product.price
    product.stock -= 1

    # 4. Дадим чуть XP за покупку
    await user.add_xp(db, 200)

    # 5. Всегда создаём новую запись в инвентаре (копия предмета)
    new_item = InventoryItem(
        user_id=user.id,
        product_id=product.id,
        quantity=1
    )
    db.add(new_item)

    # 6. Сохраняем изменения в БД
    db.add(user)
    db.add(product)
    await db.commit()


    # 7. Теперь обновляем Redis (уменьшаем сток в текущей витрине)
    shop_data_raw = await redis.get("global_shop")
    if shop_data_raw:
        shop_data = json.loads(shop_data_raw)

        # Ищем соответствующий item
        for item in shop_data:
            if item["id"] == product.id:
                # Уменьшаем витринный сток
                if item["stock"] > 0:
                    item["stock"] -= 1
                # Если совсем упал в 0, можно выпилить:
                if item["stock"] <= 0:
                    item["stock"] = 0
                    # Или shop_data.remove(item) — чтобы убрать из списка
                break

        # Записываем обратно в Redis
        await redis.set("global_shop", json.dumps(shop_data))
        # И шлём сокет событие
        await sio.emit("shop_update", {"products": shop_data}, namespace="/shop")

    return {"message": f"Поздравляем с покупкой {product.name}!"}


#utils.shoputils.py
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