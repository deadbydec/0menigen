from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.models import Product, InventoryItem, User
from auth.cookie_auth import get_current_user_from_cookie
from database import get_db
from redis.asyncio import Redis
from decimal import Decimal, ROUND_DOWN
import json
from socket_config import sio

router = APIRouter(prefix="/api/donateshop", tags=["donateshop"])
redis = Redis.from_url("redis://localhost", decode_responses=True)


@router.get("/")
async def get_donate_shop(user: User = Depends(get_current_user_from_cookie)):
    """Отдаёт список донатных товаров (только за нуллинги)"""
    raw = await redis.get("donate_shop")
    if not raw:
        raise HTTPException(status_code=500, detail="🧨 Донат-шоп пуст или не сгенерирован")

    data = json.loads(raw)
    return {"products": data}


@router.post("/buy/{product_id}")
async def buy_donate_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_from_cookie)
):
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.is_nulling_only == True
        ).with_for_update()
    )
    product = result.scalar()

    if not user or not product:
        raise HTTPException(status_code=404, detail="Пользователь или донатный товар не найден!")

    # Проверка стока (если None — значит бесконечный)
    is_limited_stock = product.stock is not None
    if is_limited_stock and product.stock <= 0:
        raise HTTPException(status_code=400, detail="❌ Нет в наличии!")

    # Безопасное округление и сравнение
    user_nullings = Decimal(user.nullings).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    price = Decimal(product.nulling_price).quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    if user_nullings < price:
        raise HTTPException(status_code=400, detail="Недостаточно нуллингов!")

    user.nullings = (user_nullings - price).quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    if is_limited_stock:
        product.stock -= 1

    await user.add_xp(db, 200)

    # Добавляем в инвентарь
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.user_id == user.id,
            InventoryItem.product_id == product.id
        )
    )
    inventory_item = result.scalar()
    if inventory_item:
        inventory_item.quantity += 1
    else:
        db.add(InventoryItem(user_id=user.id, product_id=product.id, quantity=1))

    db.add(user)
    if is_limited_stock:
        db.add(product)

    await db.commit()

    # Обновляем Redis и пушим через сокет
    raw = await redis.get("donate_shop")
    if raw:
        data = json.loads(raw)
        for p in data:
            if p["id"] == product.id and is_limited_stock:
                p["stock"] = product.stock
                break
        await redis.set("donate_shop", json.dumps(data))
        await sio.emit("donate_shop_update", {"products": data}, namespace="/shop")

    return {"message": "🖤 Покупка за нуллинги прошла успешно!"}

