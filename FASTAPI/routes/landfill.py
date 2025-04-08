from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models.models import LandfillItem, InventoryItem, Product, User, LandfillPickupLimit, VipStatus
from auth.cookie_auth import get_current_user_from_cookie

router = APIRouter(prefix="/api/landfill", tags=["landfill"])

@router.get("/")
async def view_landfill(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LandfillItem).where(LandfillItem.quantity > 0))
    items = result.scalars().all()

    return [
        {
            "id": item.id,
            "name": item.product.name,
            "image": item.product.image,
            "description": item.product.description,
            "quantity": item.quantity,
            "rarity": item.product.rarity.value,
            "product_type": item.product.product_type.value,
            "thrown_at": item.thrown_at.isoformat(),
        } for item in items
    ]


@router.post("/pickup/{landfill_id}")
async def pickup_item(
    landfill_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_from_cookie)
):
    today = date.today()

    # 🌌 Определяем расу игрока
    user_race = (user.race.name.lower() if user.race and user.race.name else "")

# 📦 Определяем дневной лимит подбора на свалке
    if user.vip_status in [VipStatus.CRYPTOVOID, VipStatus.NULLOVERLORD]:
        daily_limit = 7  # 🛡️ VIP подписчики — элита среди мусорщиков
    elif user_race == "наллвур":
        daily_limit = 5  # 👁️ Наллвур умеют мимикрировать под гулей
    else:
        daily_limit = 3  # 🧍 Обычные смертные

# 📅 Получаем счётчик на сегодня
    result = await db.execute(
        select(LandfillPickupLimit).where(
            LandfillPickupLimit.user_id == user.id,
            LandfillPickupLimit.date == today
        )
    )
    limit = result.scalar()

# 🚫 Проверка превышения лимита
    if limit and limit.count >= daily_limit:
        if user.vip_status == VipStatus.NULLOVERLORD:
            detail = "Вы уже унизили всех бомжей сегодня. Омега-бомжи покорно отступили."
        elif user_race == "наллвур":
            detail = "Гули тоже устают. Завтра снова можете прикинуться бомжом."
        else:
            detail = "Вы слишком часто шаритесь по свалке. Омега-бомжи вас заметили и дали леща. Попробуйте завтра."

        raise HTTPException(status_code=429, detail=detail)

    result = await db.execute(select(LandfillItem).where(LandfillItem.id == landfill_id))
    item = result.scalar()

    if not item or item.quantity <= 0:
        raise HTTPException(status_code=404, detail="Этот предмет уже кто-то подобрал или он исчез.")

    # Обновим инвентарь
    result = await db.execute(select(InventoryItem).where(
        InventoryItem.user_id == user.id,
        InventoryItem.product_id == item.product_id
    ))
    inv_item = result.scalar()

    if inv_item:
        inv_item.quantity += item.quantity
    else:
        db.add(InventoryItem(user_id=user.id, product_id=item.product_id, quantity=item.quantity))

    # Удаляем со свалки
    await db.delete(item)

    # Обновим лимит
    if limit:
        limit.count += 1
    else:
        db.add(LandfillPickupLimit(user_id=user.id, date=today, count=1))

    await db.commit()

    return {"message": f"Вы подобрали {item.quantity}x {item.product.name} со свалки!"}


