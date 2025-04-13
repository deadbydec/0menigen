from fastapi import APIRouter, Depends, Request, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models.models import InventoryItem, VaultItem, User
from auth.cookie_auth import get_current_user_from_cookie
from sqlalchemy.orm import joinedload
from typing import Optional
from sqlalchemy import func

router = APIRouter()

@router.get("/vault", response_model=dict)
async def get_vault(request: Request, db: AsyncSession = Depends(get_db)):
    user = request.state.user

    query = (
        select(VaultItem)
        .where(VaultItem.user_id == user.id)
        .options(joinedload(VaultItem.product))
    )
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "vault_balance": user.vault_balance,
        "vault_items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product.name,
                "rarity": item.product.rarity,
                "image": item.product.image,
                "quantity": item.quantity
            }
            for item in items
        ]
    }


@router.post("/vault/deposit-item")
async def deposit_item(
    data: dict = Body(...),
    request: Request = ...,
    db: AsyncSession = Depends(get_db)
):
    user = request.state.user

    # Принудительно загружаем race
    result = await db.execute(
        select(User).options(joinedload(User.race)).where(User.id == user.id)
    )
    user = result.scalar_one()


    item_id = data.get("item_id")  # ⬅️ берем item_id (InventoryItem.id)
    quantity = data.get("quantity", 1)

    # Находим нужный предмет в инвентаре
    result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.id == item_id, InventoryItem.user_id == user.id)
        .options(joinedload(InventoryItem.product))
    )
    inv_item = result.scalar()

    if not inv_item or inv_item.quantity < quantity:
        raise HTTPException(status_code=400, detail="Недостаточно предметов в инвентаре")

    product_id = inv_item.product_id  # получаем фактический product_id

    # Вычитаем из инвентаря
    inv_item.quantity -= quantity
    if inv_item.quantity <= 0:
        await db.delete(inv_item)

    # Проверяем, есть ли уже такой product_id в сейфе
    result = await db.execute(
        select(VaultItem).where(
            VaultItem.user_id == user.id,
            VaultItem.product_id == product_id
        )
    )
    vault_item = result.scalar()

    # Если впервые кладём этот product
    if not vault_item:
        # Проверка лимита
        vault_count_query = select(func.count()).select_from(VaultItem).where(VaultItem.user_id == user.id)
        count_result = await db.execute(vault_count_query)
        vault_unique_count = count_result.scalar()

        default_limit = 50
        drakkor_limit = 65
        limit = drakkor_limit if user.race == "драккор" else default_limit

        if vault_unique_count >= limit:
            raise HTTPException(status_code=400, detail=f"Сейф переполнен: максимум {limit} разных предметов.")

        vault_item = VaultItem(user_id=user.id, product_id=product_id, quantity=quantity)
        db.add(vault_item)
    else:
        vault_item.quantity += quantity

    await db.commit()
    return {"message": "Предмет успешно убран в сейф!"}




@router.post("/vault/withdraw-item")
async def withdraw_item(
    data: dict = Body(...),
    request: Request = ...,
    db: AsyncSession = Depends(get_db)
):
    user = request.state.user
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    # Ищем предмет в сейфе
    vault_query = select(VaultItem).where(
        VaultItem.user_id == user.id,
        VaultItem.product_id == product_id
    )
    result = await db.execute(vault_query)
    vault_item = result.scalars().first()

    if not vault_item or vault_item.quantity < quantity:
        raise HTTPException(status_code=400, detail="Недостаточно предметов в сейфе")

    # Списываем из сейфа
    vault_item.quantity -= quantity
    if vault_item.quantity <= 0:
        await db.delete(vault_item)

    # Кладем обратно в инвентарь
    inv_query = select(InventoryItem).where(
        InventoryItem.user_id == user.id,
        InventoryItem.product_id == product_id
    )
    result = await db.execute(inv_query)
    inv_item = result.scalars().first()

    if inv_item:
        inv_item.quantity += quantity
    else:
        inv_item = InventoryItem(
            user_id=user.id,
            product_id=product_id,
            quantity=quantity
        )
        db.add(inv_item)

    await db.commit()
    return {"message": "Предмет возвращён из сейфа!"}


@router.post("/vault/favorite-toggle")
async def toggle_favorite(
    data: dict = Body(...),
    request: Request = ...,
    db: AsyncSession = Depends(get_db)
):
    user = request.state.user
    product_id = data.get("product_id")

    vault_item_query = select(VaultItem).where(
        VaultItem.user_id == user.id,
        VaultItem.product_id == product_id
    )
    result = await db.execute(vault_item_query)
    vault_item = result.scalars().first()

    if not vault_item:
        raise HTTPException(status_code=404, detail="Предмет не найден в сейфе")

    vault_item.is_favorite = not vault_item.is_favorite
    await db.commit()

    return {
        "message": (
            "Предмет добавлен в избранные" if vault_item.is_favorite
            else "Предмет удалён из избранного"
        )
    }


@router.get("/vault/favorites")
async def get_favorite_items(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user = request.state.user
    query = (
        select(VaultItem)
        .where(VaultItem.user_id == user.id, VaultItem.is_favorite == True)
        .options(joinedload(VaultItem.product))
    )
    result = await db.execute(query)
    items = result.scalars().all()

    # Если у VaultItem нет метода serialize(), делаем вручную:
    favorites = []
    for item in items:
        favorites.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product.name,
            "rarity": item.product.rarity,
            "image": item.product.image,
            "quantity": item.quantity,
            "is_favorite": True
        })

    return {"favorites": favorites}

@router.post("/vault/deposit-coins")
async def deposit_coins(
    data: dict = Body(...),
    request: Request = ...,
    db: AsyncSession = Depends(get_db)
):
    raw_user = request.state.user
    user_result = await db.execute(select(User).where(User.id == raw_user.id))
    user = user_result.scalar_one()

    amount = data.get("amount", 0)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Неверное количество монет")
    if user.coins < amount:
        raise HTTPException(status_code=400, detail="Недостаточно монет для внесения")

    user.coins -= amount
    user.vault_balance += amount

    await db.commit()
    await db.refresh(user)

    return {"message": f"Вы внесли {amount} монет в сейф"}



@router.post("/vault/withdraw-coins")
async def withdraw_coins(
    data: dict = Body(...),
    request: Request = ...,
    db: AsyncSession = Depends(get_db)
):
    raw_user = request.state.user
    user_result = await db.execute(select(User).where(User.id == raw_user.id))
    user = user_result.scalar_one()
    
    amount = data.get("amount", 0)

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Неверное количество монет")

    if user.vault_balance < amount:
        raise HTTPException(status_code=400, detail="Недостаточно монет в сейфе")

    user.vault_balance -= amount
    user.coins += amount
    await db.commit()
    await db.refresh(user)  # <--- ЭТО НУЖНО

    return {"message": f"Вы вывели {amount} монет из сейфа"}




