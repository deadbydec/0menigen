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

router = APIRouter()

redis = AsyncRedis.from_url("redis://localhost", decode_responses=True)

# 🔥 Загрузка (при желании) из products.json
async def load_products_from_json():
    with open("data/products.json", encoding="utf-8") as file:
        return json.load(file)


# ===========================
#  Генерация витрины
# ===========================
async def get_random_products(db: AsyncSession):
    # 1) Выбираем товары из БД, исключая особые редкости
    result = await db.execute(
        select(Product).where(
            Product.stock > 0,
            ~Product.rarity.in_([
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
        ProductRarity.trash:     (100, (6, 8), (5, 7)),
        ProductRarity.common:    (85,  (4, 6), (3, 5)),
        ProductRarity.rare:      (30,  (1, 1), (1, 2)),
        ProductRarity.epic:      (7,   (1, 1), (1, 1)),
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
    return selected_products

# --------------------------------
#  Функция-обёртка c "накопительным" завозом
# --------------------------------
async def smart_shop_update(db: AsyncSession):
    """Накопительный завоз: 5 раз «добавляем», на 6-й — полный сброс."""
    count_key = "global_shop_refresh_count"
    shop_key = "global_shop"

    # Считываем счётчик из Redis
    count_raw = await redis.get(count_key)
    refresh_count = int(count_raw) if count_raw else 0

    # Генерируем новую порцию товаров
    new_products = await get_random_products(db)

    if refresh_count < 5:
        # (1) Накопительный завоз
        print(f"🔄 Завоз №{refresh_count+1} (накопительный)")

        # Получаем текущий магазин
        existing_raw = await redis.get(shop_key)
        existing = json.loads(existing_raw) if existing_raw else []

        # Добавляем только уникальные товары (по id) с накоплением стока
        existing_dict = {p["id"]: p for p in existing}
        for item in new_products:
            if item["id"] in existing_dict:
                existing_dict[item["id"]]["stock"] += item["stock"]
            else:
                existing_dict[item["id"]] = item

        final_shop = list(existing_dict.values())

        # Записываем обновлённый список в Redis (используем final_shop!)
        await redis.set(shop_key, json.dumps(final_shop))
        # Инкрементируем счётчик
        await redis.set(count_key, refresh_count + 1)

        # Шлём сокет-событие
        await sio.emit("shop_update", {"products": final_shop}, namespace="/shop")

    else:
        # (2) Полный сброс, на 6-м вызове
        print("💥 Полный сброс магазина!")
        await redis.set(shop_key, json.dumps(new_products))
        await redis.set(count_key, 0)

        # Шлём сокет-событие
        await sio.emit("shop_update", {"products": new_products}, namespace="/shop")

    print(f"✔ Завоз завершён. Текущий счётчик = {await redis.get(count_key)}")


# --------------------------------
#  Теперь используем smart_shop_update
# --------------------------------
async def background_shop_updater():
    """Раз в 20 сек вызываем smart_shop_update, который сам решает «добавлять» или «сбросить»."""
    while True:
        await asyncio.sleep(random.randint(50, 500))
        async with get_db() as db:
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
        "коллекционный": ["коллекционный", "сувенир", "игрушка", "наклейка"],

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

        "продуктовый": ["еда", "напиток", "сладость"],
        "технолайт": ["гаджет"],
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

    # 5. Добавляем в инвентарь
    existing_item = await db.execute(
        select(InventoryItem).where(
            InventoryItem.user_id == user.id,
            InventoryItem.product_id == product.id
        )
    )
    inventory_item = existing_item.scalar()
    if inventory_item:
        inventory_item.quantity += 1
    else:
        new_item = InventoryItem(user_id=user.id, product_id=product.id, quantity=1)
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





