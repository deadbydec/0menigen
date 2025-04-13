import os
import json
import time
from sqlalchemy.orm import selectinload
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    Request
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, Field, validator

from auth.cookie_auth import get_token_from_cookie, decode_access_token
from database import get_db, async_session
from models.models import Product, PersonalShopItem, InventoryItem, ShopTransaction, User
from config import Config
from utils.last_seen import is_user_online
from typing import List

router = APIRouter()


class ShopItemAddRequest(BaseModel):
    """
    Модель входных данных для добавления товаров в личный магазин.
    """
    product_id: int = Field(..., description="ID продукта из таблицы products")
    quantity: int = Field(..., description="Сколько штук выставляется на продажу")
    price: int = Field(..., description="Цена в монетах за одну штуку или весь лот")

    @validator('quantity', 'price')
    def must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("quantity и price должны быть > 0")
        return v


@router.get("/my")
async def get_my_shop(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Просмотр личного магазина текущего пользователя.
    Возвращает список всех товаров, выставленных в его магазине.
    """
    user = request.state.user

    # Получаем все товары пользователя
    result = await db.execute(
        select(PersonalShopItem)
        .where(PersonalShopItem.user_id == user.id)
        .options(selectinload(PersonalShopItem.product))
    )
    shop_items = result.scalars().all()

    # Формируем удобный ответ
    response_data = []
    for item in shop_items:
        response_data.append({
            "id": item.id,
            "product_id": item.product.id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "price": item.price,
            "image": item.product.image,
            "is_published": getattr(item, "is_published", False)
        })

    return {"shop_items": response_data}


from pydantic import BaseModel, Field

class ShopSaveItem(BaseModel):
    product_id: int
    quantity_in_inventory: int = 0
    price_in_shop: int = 0
    quantity_in_shop: int = 0

@router.post("/my/save")
async def save_my_shop(
    request: Request,
    items: List[ShopSaveItem],
    db: AsyncSession = Depends(get_db)
):
    """
    Принимает список товаров. Для каждого:
    - Если price_in_shop > 0, создаём/обновляем PersonalShopItem
    - Если price_in_shop == 0, удаляем из магазина
    Также синхронизируем количество инвентаря
    """
    user = request.state.user
    
    # 1. Сгрузим все сущности, чтобы не делать кучу запросов
    product_ids = [item.product_id for item in items]
    inv_result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.user_id == user.id,
            InventoryItem.product_id.in_(product_ids)
        )
    )
    inventory_map = {inv.product_id: inv for inv in inv_result.scalars().all()}

    shop_result = await db.execute(
        select(PersonalShopItem).where(
            PersonalShopItem.user_id == user.id,
            PersonalShopItem.product_id.in_(product_ids)
        )
    )
    shop_map = {sh.product_id: sh for sh in shop_result.scalars().all()}

    # Обработка каждого item
    for item in items:
        print("▶️ item:", item.dict())
        # Проверяем, существует ли нужный InventoryItem, если нет - создаём пустышку
        inv_item = inventory_map.get(item.product_id)
        if not inv_item:
            # Продукта в инвентаре не было вообще — возможно, он был только в магазине
            # Создадим пустой InventoryItem, если нужно
            inv_item = InventoryItem(
                user_id=user.id,
                product_id=item.product_id,
                quantity=0
            )
            inventory_map[item.product_id] = inv_item
            db.add(inv_item)
            await db.flush()

        # Проверяем, существует ли PersonalShopItem
        shop_item = shop_map.get(item.product_id)

        if item.price_in_shop > 0:
            # Предмет должен быть в магазине
            # quantity_in_shop не может быть > inv_item.quantity + (старое значение из shop_item, если было)
            # Но ты можешь упростить логику, делая "quantity_in_shop == inv_item.quantity" 
            # или давая игроку выбрать вручную

            # Обновляем/создаём shop_item
            if not shop_item:
                # создаём
                shop_item = PersonalShopItem(
                    user_id=user.id,
                    product_id=item.product_id
                )
                shop_map[item.product_id] = shop_item
                db.add(shop_item)

            # теперь синхронизируем количество
            shop_item.price = item.price_in_shop
            old_shop_quantity = shop_item.quantity or 0
            new_shop_quantity = item.quantity_in_shop

            # Игрок мог увеличить или уменьшить количество
            # Вычисляем, сколько прибавить/убавить из inventory
            delta = new_shop_quantity - old_shop_quantity

            # если delta > 0 => вычитаем из инвентаря
            # если delta < 0 => возвращаем в инвентарь
            inv_item.quantity -= delta

            # обнулять нельзя до минуса
            if inv_item.quantity < 0:
                raise HTTPException(status_code=400, detail=f"Недостаточно предметов для {item.product_id}")

            shop_item.quantity = new_shop_quantity

        else:
            # price_in_shop == 0 => убираем из магазина, всё возвращаем в инвентарь
            if shop_item:
                inv_item.quantity += shop_item.quantity
                await db.delete(shop_item)
                del shop_map[item.product_id]

    await db.commit()
    return {"message": "Магазин обновлён по новым параметрам!"}


@router.get("/my/all-items")
async def get_all_items(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Возвращает объединённый список:
    - Инвентарь игрока (InventoryItem)
    - Товары в магазине (PersonalShopItem)
    Если предмет частично в инвентаре, частично в магазине — показываем обе цифры.
    """
    user = request.state.user

    # 1. Берём все inventoryItem
    inv_items_result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.user_id == user.id)
        .options(selectinload(InventoryItem.product))
    )
    inv_items = inv_items_result.scalars().all()

    inv_map = {}
    for inv in inv_items:
        inv_map[inv.product_id] = {
            "product_id": inv.product_id,
            "product_name": inv.product.name,
            "image": inv.product.image,
            "quantity_in_inventory": inv.quantity,
            # Если предмет не в магазине, ниже = 0
            "price_in_shop": 0,
            "quantity_in_shop": 0
        }

    # 2. Берём товары из магазина
    shop_items_result = await db.execute(
        select(PersonalShopItem)
        .where(PersonalShopItem.user_id == user.id)
        .options(selectinload(PersonalShopItem.product))
    )
    shop_items = shop_items_result.scalars().all()

    for sh in shop_items:
        if sh.product_id in inv_map:
            inv_map[sh.product_id]["price_in_shop"] = sh.price
            inv_map[sh.product_id]["quantity_in_shop"] = sh.quantity
        else:
            # Вдруг у нас предмет чисто в магазине, а в инвентаре нет
            inv_map[sh.product_id] = {
                "product_id": sh.product_id,
                "product_name": sh.product.name,
                "image": sh.product.image,
                "quantity_in_inventory": 0,
                "price_in_shop": sh.price,
                "quantity_in_shop": sh.quantity
            }

    return {"all_items": list(inv_map.values())}



@router.post("/add")
async def add_item_to_shop(
    data: ShopItemAddRequest,  # Pydantic-модель
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Добавить предмет из инвентаря в личный магазин.
    Уменьшает quantity в инвентаре игрока.
    """
    user = request.state.user

    # Проверяем, что такой продукт существует
    product = await db.get(Product, data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Указанный продукт не найден")

    # Проверяем, есть ли у пользователя нужное кол-во предметов в инвентаре
    inventory_result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.user_id == user.id)
        .where(InventoryItem.product_id == data.product_id)
    )
    inv_item = inventory_result.scalar_one_or_none()

    if not inv_item or inv_item.quantity < data.quantity:
        raise HTTPException(status_code=400, detail="Недостаточно предметов в инвентаре")

    # Уменьшаем количество в инвентаре
    inv_item.quantity -= data.quantity
    if inv_item.quantity <= 0:
        await db.delete(inv_item)

    # Создаём запись в PersonalShopItem
    shop_item = PersonalShopItem(
        user_id=user.id,
        product_id=data.product_id,
        quantity=data.quantity,
        price=data.price,
        # Можешь добавить is_published=False, чтобы товар был не виден до publish
        is_published=False  
    )
    db.add(shop_item)
    await db.commit()
    await db.refresh(shop_item)

    return {
        "message": "Товар успешно добавлен в магазин!",
        "shop_item_id": shop_item.id,
        "remaining_in_inventory": inv_item.quantity if inv_item else 0
    }


@router.post("/return/{shop_item_id}")
async def return_from_shop(
    shop_item_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Убрать предмет из личного магазина и вернуть его обратно в инвентарь игрока.
    """
    user = request.state.user

    # Проверяем, что товар принадлежит пользователю
    shop_result = await db.execute(
        select(PersonalShopItem)
        .where(PersonalShopItem.id == shop_item_id)
        .where(PersonalShopItem.user_id == user.id)
    )
    shop_item = shop_result.scalar_one_or_none()
    if not shop_item:
        raise HTTPException(
            status_code=404,
            detail="Предмет не найден в магазине или не принадлежит текущему пользователю"
        )

    # Возвращаем в инвентарь
    inv_result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.user_id == user.id)
        .where(InventoryItem.product_id == shop_item.product_id)
    )
    inv_item = inv_result.scalar_one_or_none()
    if inv_item:
        inv_item.quantity += shop_item.quantity
    else:
        new_inv = InventoryItem(
            user_id=user.id,
            product_id=shop_item.product_id,
            quantity=shop_item.quantity
        )
        db.add(new_inv)

    # Удаляем товар из магазина
    await db.delete(shop_item)
    await db.commit()

    return {"message": "Товар возвращён в инвентарь"}


@router.post("/publish")
async def publish_shop(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Опубликовать (сохранить) магазин, чтобы его товары стали видны другим игрокам
    (если is_published поле используется).
    """
    user = request.state.user

    result = await db.execute(
        select(PersonalShopItem)
        .where(PersonalShopItem.user_id == user.id)
    )
    shop_items = result.scalars().all()

    if not shop_items:
        return {"message": "У вас нет товаров в магазине для публикации"}

    for item in shop_items:
        item.is_published = True
    await db.commit()

    return {"message": "Магазин опубликован!"}

@router.get("/search")
async def search_items(query: str, db: AsyncSession = Depends(get_db)):
    if not query or len(query.strip()) < 2:
        return {"results": []}

    result = await db.execute(
        select(PersonalShopItem)
        .join(PersonalShopItem.product)
        .where(PersonalShopItem.is_published == True)
        .where(Product.name.ilike(f"%{query}%"))
        .order_by(PersonalShopItem.price.asc())
        .options(selectinload(PersonalShopItem.product), selectinload(PersonalShopItem.user))
    )
    items = result.scalars().all()

    return {"results": [
        {
            "id": item.id,
            "product_id": item.product.id,
            "product_name": item.product.name,
            "image": item.product.image,
            "price": item.price,
            "quantity": item.quantity,
            "seller": item.user.username,
            "seller_id": item.user.id,
        } for item in items
    ]}

@router.post("/buy")
async def buy_item(data: dict, request: Request, db: AsyncSession = Depends(get_db)):
    user = request.state.user
    shop_item_id = data.get("shop_item_id")
    quantity_to_buy = data.get("quantity", 1)

    result = await db.execute(
        select(PersonalShopItem).where(PersonalShopItem.id == shop_item_id).options(
            selectinload(PersonalShopItem.product),
            selectinload(PersonalShopItem.user)
        )
    )
    shop_item = result.scalar_one_or_none()

    if not shop_item:
        raise HTTPException(status_code=404, detail="Товар не найден")

    if shop_item.user_id == user.id:
        raise HTTPException(status_code=400, detail="Нельзя купить свой товар")

    if quantity_to_buy > shop_item.quantity:
        raise HTTPException(status_code=400, detail="Недостаточно товара в магазине")

    total_price = quantity_to_buy * shop_item.price

    if user.coins < total_price:
        raise HTTPException(status_code=400, detail="Недостаточно монет")

    # Обновляем продавца
    shop_item.quantity -= quantity_to_buy
    shop_item.user.shop_balance += total_price

    # Обновляем покупателя
    user.coins -= total_price

    # Перемещаем в инвентарь
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.user_id == user.id,
            InventoryItem.product_id == shop_item.product_id
        )
    )
    inv_item = result.scalar_one_or_none()
    if inv_item:
        inv_item.quantity += quantity_to_buy
    else:
        db.add(InventoryItem(
            user_id=user.id,
            product_id=shop_item.product_id,
            quantity=quantity_to_buy
        ))

    # Если товар закончился — удаляем из магазина
    if shop_item.quantity == 0:
        await db.delete(shop_item)

    # Записываем транзакцию
    db.add(ShopTransaction(
        seller_id=shop_item.user_id,
        buyer_id=user.id,
        product_id=shop_item.product_id,
        quantity=quantity_to_buy,
        price_per_unit=shop_item.price,
        total_price=total_price,
    ))

    await db.commit()
    return {"message": "Товар куплен успешно"}


@router.get("/my/transactions")
async def get_shop_transactions(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Возвращает список всех продаж текущего пользователя (как продавца)
    """
    user = request.state.user

    result = await db.execute(
        select(ShopTransaction)
        .where(ShopTransaction.seller_id == user.id)
        .order_by(ShopTransaction.timestamp.desc())
        .options(selectinload(ShopTransaction.product), selectinload(ShopTransaction.buyer))
    )
    transactions = result.scalars().all()

    return {
        "transactions": [
            {
                "id": t.id,
                "product_name": t.product.name,
                "product_id": t.product_id,
                "quantity": t.quantity,
                "price_per_unit": t.price_per_unit,
                "total_price": t.total_price,
                "buyer_username": t.buyer.username,
                "timestamp": t.timestamp.isoformat()
            }
            for t in transactions
        ]
    }

from sqlalchemy import select

@router.post("/withdraw")
async def withdraw_balance(request: Request, db: AsyncSession = Depends(get_db)):
    current_user = request.state.user

    # Заново подгружаем пользователя
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.shop_balance <= 0:
        raise HTTPException(status_code=400, detail="Нет заработанных монет для вывода")

    withdrawn = user.shop_balance
    user.coins += withdrawn
    user.shop_balance = 0

    await db.commit()

    return {"message": f"Вы успешно вывели {withdrawn} монет!", "amount": withdrawn}

@router.get("/my/balance")
async def get_shop_balance(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.state.user.id

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return {"shop_balance": user.shop_balance}




