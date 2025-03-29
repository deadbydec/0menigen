from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models.models import InventoryItem, Product, ProductType, User
from auth.cookie_auth import get_current_user_from_cookie
from sqlalchemy.orm import selectinload
from typing import Optional
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/inventory", tags=["inventory"])

from pydantic import BaseModel

class GiftPayload(BaseModel):
    recipient_id: int
    quantity: int = 1


@router.get("/")
async def get_inventory(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_from_cookie),
):
    # CORS preflight fallback
    if request.method == "OPTIONS" or not user:
        print("🔁 [INFO] Preflight или отсутствует юзер — пустой ответ")
        return JSONResponse(status_code=204, content={})
    
    if not user:
        return JSONResponse(status_code=401, content={"detail": "❌ Не авторизован"})

    print("🧠 [DEBUG] Запрашивает юзер:", user.id)
    """Возвращает инвентарь пользователя, используя куки."""
    result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.user_id == user.id)
        .options(selectinload(InventoryItem.product))
)
    inventory = result.scalars().all()

    print("📦 [DEBUG] Найдено предметов:", len(inventory))

    inventory_list = []
    for item in inventory:
        if not item.product:
            print(f"⚠️ Предмет {item.id} не имеет связанного продукта, пропускаем")
            continue
        
        inventory_list.append({
            "id": item.id,
            "name": item.product.name,
            "type": item.product.product_type.value,
            "image": item.product.image,
            "rarity": item.product.rarity.value,
            "quantity": item.quantity,
            "product": {
                "name": item.product.name,
                "image": item.product.image,
                "description": item.product.description,
                "rarity": item.product.rarity.value,
                "product_type": item.product.product_type.value,
            }
        })

    return {"inventory": inventory_list}


@router.post("/{item_id}")
async def gift_item(
    item_id: int,
    payload: GiftPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    sender: User = Depends(get_current_user_from_cookie)
):
    recipient_id = payload.recipient_id
    quantity = payload.quantity

    if not recipient_id or recipient_id == sender.id:
        raise HTTPException(status_code=400, detail="Нельзя дарить себе или неуказанному игроку.")

    # Ищем предмет у отправителя
    result = await db.execute(
    select(InventoryItem)
    .where(InventoryItem.id == item_id, InventoryItem.user_id == sender.id)
    .options(selectinload(InventoryItem.product))
)
    sender_item = result.scalar()
    if not sender_item or sender_item.quantity < quantity:
        raise HTTPException(status_code=400, detail="Недостаточно предметов для подарка.")

    # Ищем получателя
    result = await db.execute(select(User).where(User.id == recipient_id))
    recipient = result.scalar()
    if not recipient:
        raise HTTPException(status_code=404, detail="Получатель не найден.")

    # Ищем предмет у получателя
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.user_id == recipient.id,
            InventoryItem.product_id == sender_item.product_id
        )
    )
    recipient_item = result.scalar()

    if recipient_item:
        recipient_item.quantity += quantity
    else:
        new_item = InventoryItem(
            user_id=recipient.id,
            product_id=sender_item.product_id,
            quantity=quantity
        )
        db.add(new_item)

    # Уменьшаем у отправителя
    sender_item.quantity -= quantity
    if sender_item.quantity <= 0:
        await db.delete(sender_item)

    await db.commit()

    return {
        "success": True,
        "message": f"Вы подарили {quantity}x '{sender_item.product.name}' игроку {recipient.username}."
    }


# 🔥 Использование предмета
@router.post("/use/{item_id}")
async def use_item(
    item_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_from_cookie)
):
    """Использует предмет из инвентаря (через куки-авторизацию)"""
    result = await db.execute(
    select(InventoryItem)
    .where(InventoryItem.id == item_id)
    .options(selectinload(InventoryItem.product))
)
    item = result.scalar()

    if not item or item.user_id != user.id:
        raise HTTPException(status_code=403, detail="Этот предмет вам не принадлежит!")

    product = item.product
    response = {"success": True, "message": f"Вы использовали {product.name}!"}

    # Логика использования
    if product.product_type == ProductType.drink:
        xp_reward = 10
        user.add_xp(xp_reward)
        response["message"] = f"Вы выпили {product.name} и получили {xp_reward} XP!"
    elif product.product_type == ProductType.food:
        health_restore = 20
        user.health = getattr(user, 'health', 100) + health_restore
        response["message"] = f"Вы поели {product.name} и восстановили {health_restore} здоровья!"
    elif product.product_type == ProductType.artifact:
        response["message"] = f"Вы использовали артефакт {product.name} и получили бонус!"
    elif product.product_type == ProductType.collectible:
        response["message"] = f"Вы добавили {product.name} в свою коллекцию!"

    # Уменьшаем количество или удаляем
    if item.quantity > 1:
        item.quantity -= 1
    else:
        await db.delete(item)

    await db.commit()
    return response

# 🔥 Уничтожение предмета
@router.delete("/destroy/{item_id}")
async def destroy_item(
    item_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_from_cookie)
):
    """Удаляет предмет из инвентаря (через куки-авторизацию)"""
    result = await db.execute(
    select(InventoryItem)
    .where(InventoryItem.id == item_id)
    .options(selectinload(InventoryItem.product))
)
    inventory_item = result.scalar()

    if not inventory_item or inventory_item.user_id != user.id:
        raise HTTPException(status_code=403, detail="Этот предмет вам не принадлежит!")

    item_name = inventory_item.product.name
    await db.delete(inventory_item)
    await db.commit()

    return {"success": True, "message": f"Предмет {item_name} уничтожен!"}




