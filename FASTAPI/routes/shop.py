import random
import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models.models import Product, InventoryItem, ProductRarity, User
from redis.asyncio import Redis
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer

router = APIRouter()

# JWT менеджер
jwt_access = JwtAccessBearer(secret_key="supersecretkey")

redis = Redis.from_url("redis://localhost", decode_responses=True)

# 🔥 Функция загрузки товаров из JSON-файла (если нужно)
async def load_products_from_json():
    with open("data/products.json", encoding="utf-8") as file:
        return json.load(file)

# 🔥 Функция выбора случайных товаров (без особых предметов)
async def get_random_products():
    async with AsyncSession() as session:
        result = await session.execute(
            select(Product).where(Product.stock > 0, Product.rarity != ProductRarity.special)
        )
        products = result.scalars().all()

    if not products:
        print("⚠ Нет доступных товаров для обновления магазина!")
        return []

    rarity_weights = {
    ProductRarity.trash: (100, (2, 6), (5, 9)),
    ProductRarity.common: (85, (3, 5), (4, 7)),
    ProductRarity.rare: (30, (1, 2), (2, 3)),
    ProductRarity.epic: (10, (1, 1), (1, 2)),
    ProductRarity.legendary: (3, (1, 1), (1, 1)),
    ProductRarity.elder: (1, (1, 1), (1, 1)),
    }

    grouped_products = {rarity: [] for rarity in rarity_weights.keys()}
    for product in products:
        if product.rarity in grouped_products:
            grouped_products[product.rarity].append(product)

    selected_products = []
    for rarity, (chance, count_range, stock_range) in rarity_weights.items():
        if random.randint(1, 100) <= chance:
            available_items = grouped_products[rarity]
            if available_items:
                num_items = random.randint(count_range[0], min(count_range[1], len(available_items)))
                selected = random.sample(available_items, num_items)

                for item in selected:
                    random_stock = random.randint(stock_range[0], stock_range[1])
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

    print(f"🛒 Обновлённый магазин: {[p['name'] + ' (' + str(p['stock']) + ' шт.)' for p in selected_products]}")
    return selected_products

# 🔥 Асинхронный процесс обновления магазина
async def background_shop_updater():
    while True:
        await asyncio.sleep(20)
        new_products = await get_random_products()
        await redis.set("global_shop", json.dumps(new_products))
        print("🛒 Магазин обновлён в Redis!")

# 🔥 Получение магазина
@router.get("/")
async def get_shop(
    credentials: JwtAuthorizationCredentials = Depends(jwt_access),
    category: str = Query(None)
):
    """Возвращает товары из Redis с фильтрацией по категории"""
    shop_data = await redis.get("global_shop")
    if not shop_data:
        return JSONResponse(content={"error": "Магазин пуст!"}, status_code=400)

    products_data = json.loads(shop_data)

    # Маппинг категорий
    mapping = {
        "food": ["еда", "напиток", "сладости"],
    }

    if category:
        allowed_types = mapping.get(category.lower(), [category.lower()])
        filtered_products = [
            p for p in products_data if p.get("product_type", "").lower() in allowed_types
        ]
    else:
        filtered_products = products_data

    return {"products": filtered_products}

# 🔥 Покупка товара
@router.post("/buy/{product_id}")
async def buy_product(
    product_id: int,
    credentials: JwtAuthorizationCredentials = Depends(jwt_access),
    db: AsyncSession = Depends(get_db)
):
    """Позволяет игроку купить товар"""
    user_id = credentials.subject["user_id"]

    # Получаем пользователя и товар
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar()

    if not user or not product:
        raise HTTPException(status_code=404, detail="Пользователь или товар не найдены!")

    if user.coins < product.price:
        raise HTTPException(status_code=400, detail="У вас недостаточно коинов!")
    
    if product.stock <= 0:
        raise HTTPException(status_code=400, detail="Товара больше нет в наличии!")

    # Оплата и уменьшение количества
    user.coins -= product.price
    user.add_xp(200)
    product.stock -= 1

    # Добавление в инвентарь
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.user_id == user.id, InventoryItem.product_id == product.id)
    )
    inventory_item = result.scalar()
    if inventory_item:
        inventory_item.quantity += 1
    else:
        new_item = InventoryItem(user_id=user.id, product_id=product.id, quantity=1)
        db.add(new_item)

    await db.commit()
    return {"success": f"Вы купили {product.name}!"}
