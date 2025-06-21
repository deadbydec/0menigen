from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from database import get_db
from models.models import LandfillItem, InventoryItem, User, LandfillPickupLimit
from auth.cookie_auth import get_current_user_from_cookie

router = APIRouter(prefix="/api/landfill", tags=["landfill"])

FIXED_LIMIT = 3  # 🔒 Жесткий лимит на подбор в день

@router.get("")
@router.get("/")
async def view_landfill(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LandfillItem)
        .where(LandfillItem.quantity > 0)
        .options(joinedload(LandfillItem.product))
    )
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
        }
        for item in items
    ]

@router.post("/pickup/{landfill_id}")
async def pickup_item(
    landfill_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_from_cookie)
):
    today = date.today()

    # Проверка лимита подбора
    result = await db.execute(
        select(LandfillPickupLimit).where(
            LandfillPickupLimit.user_id == user.id,
            LandfillPickupLimit.date == today
        )
    )
    limit = result.scalar()
    used = limit.count if limit else 0

    if used >= FIXED_LIMIT:
        raise HTTPException(status_code=429, detail="Вы уже подобрали максимум предметов сегодня. Возвращайтесь завтра!")

    # Находим предмет
    result = await db.execute(
        select(LandfillItem)
        .where(LandfillItem.id == landfill_id)
        .options(joinedload(LandfillItem.product))
    )
    item = result.scalar()

    if not item or item.quantity <= 0:
        raise HTTPException(status_code=404, detail="Этот предмет уже кто-то подобрал или он исчез.")

    # Кэшируем инфу до удаления
    picked_quantity = item.quantity
    picked_name = item.product.name

    # Добавляем как уникальную ячейку в инвентарь
    db.add(InventoryItem(user_id=user.id, product_id=item.product_id, quantity=item.quantity))

    # Удаляем со свалки
    await db.delete(item)

    # Обновляем лимит
    if limit:
        limit.count += 1
    else:
        db.add(LandfillPickupLimit(user_id=user.id, date=today, count=1))

    await db.commit()

    return {"message": f"Вы подобрали {picked_quantity}x {picked_name} со свалки!"}

@router.get("/limit")
async def landfill_limit(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_from_cookie)
):
    today = date.today()

    result = await db.execute(
        select(LandfillPickupLimit).where(
            LandfillPickupLimit.user_id == user.id,
            LandfillPickupLimit.date == today
        )
    )
    limit = result.scalar()
    current = limit.count if limit else 0

    return {"used": current, "max": FIXED_LIMIT}






