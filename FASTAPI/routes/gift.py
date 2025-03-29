from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models.models import InventoryItem, Product, ProductType, User, PendingGift, SystemMessage, SystemMessageType
from auth.cookie_auth import get_current_user_from_cookie
from pydantic import BaseModel
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/api/gift", tags=["gift"])

class GiftRequest(BaseModel):
    recipient_username: str
    quantity: int = 1  # 💥 по умолчанию дарим 1 шт

class GiftResponse(BaseModel):
    success: bool
    message: str


@router.post("/{item_id}")
async def gift_item(
    item_id: int,
    data: GiftRequest,
    user: User = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    try:
        print(f"🎁 Подарок от: {user.username}, item_id: {item_id}, получатель: {data.recipient_username}")

        result = await db.execute(
    select(InventoryItem)
    .where(InventoryItem.id == item_id)
    .options(selectinload(InventoryItem.product))
)
        item = result.scalar()
        print(f"📦 Найден предмет: {item}")

        if not item or item.user_id != user.id:
            raise HTTPException(status_code=403, detail="Этот предмет вам не принадлежит")

        result = await db.execute(select(User).where(User.username == data.recipient_username))
        recipient = result.scalar()
        print(f"🎯 Получатель найден: {recipient}")

        if not recipient:
            raise HTTPException(status_code=404, detail="Получатель не найден")

        gift = PendingGift(sender_id=user.id, recipient_id=recipient.id, item_id=item.id)
        db.add(gift)

        await db.flush()  # 👈 чтоб у gift был id
        print(f"🧾 PendingGift создан с id={gift.id}")

        system_msg = SystemMessage(
            recipient_id=recipient.id,
            message_type=SystemMessageType.GIFT.value,
            title="🎁 Вам подарок!",
            content=f"Игрок {user.username} прислал вам предмет: {item.product.name}.",
            timestamp=datetime.utcnow(),
            is_read=False,
            related_id=gift.id
        )
        db.add(system_msg)

        await db.commit()

        return {"success": True, "message": "Подарок отправлен!"}

    except Exception as e:
        print(f"❌ [GIFT ERROR]: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при отправке подарка")



@router.post("/accept/{gift_id}")
async def accept_gift(
    gift_id: int,
    user: User = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PendingGift)
        .options(
            selectinload(PendingGift.item).selectinload(InventoryItem.product)
        )
        .where(PendingGift.id == gift_id)
    )
    gift = result.scalar()

    if not gift or gift.recipient_id != user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к подарку")

    # 🔍 Проверяем, есть ли у получателя уже такой предмет
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.user_id == user.id,
            InventoryItem.product_id == gift.item.product_id
        )
    )
    existing_item = result.scalar()

    if existing_item:
        existing_item.quantity += gift.item.quantity
        await db.delete(gift.item)  # удаляем отдельный экземпляр подарка
    else:
        gift.item.user_id = user.id

    system_msg = SystemMessage(
        recipient_id=gift.sender_id,
        message_type=SystemMessageType.GIFT.value,
        title="🎁 Подарок принят",
        content=f"Игрок {user.username} принял ваш подарок: {gift.item.product.name}.",
        timestamp=datetime.utcnow(),
        is_read=False,
        related_id=gift.id
    )
    db.add(system_msg)

    await db.delete(gift)
    await db.commit()

    return {"success": True, "message": "Подарок принят!"}


@router.post("/reject/{gift_id}")
async def reject_gift(
    gift_id: int,
    user: User = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
    select(PendingGift)
    .options(
        selectinload(PendingGift.item).selectinload(InventoryItem.product)
    )
    .where(PendingGift.id == gift_id)
)

    gift = result.scalar()

    if not gift or gift.recipient_id != user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к подарку")

    # 🔍 Проверяем, есть ли у получателя уже такой предмет
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.user_id == gift.sender_id,
            InventoryItem.product_id == gift.item.product_id
        )
    )
    existing_item = result.scalar()

    if existing_item:
        existing_item.quantity += gift.item.quantity
        await db.delete(gift.item)
    else:
        gift.item.user_id = gift.sender_id

    # ✉️ Отправляем системку дарителю
    system_msg = SystemMessage(
        recipient_id=gift.sender_id,
        message_type=SystemMessageType.GIFT.value,
        title="🎁 Подарок отклонён",
        content=f"Игрок {user.username} отклонил ваш подарок: {gift.item.product.name}. Предмет возвращён вам.",
        timestamp=datetime.utcnow(),
        is_read=False,
        related_id=gift.id
    )
    db.add(system_msg)

    await db.delete(gift)
    await db.commit()

    return {"success": True, "message": "Подарок отклонён и возвращён отправителю!"}