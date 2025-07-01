# routes/auction.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, field_validator

from models.models import User, InventoryItem, Pet, AuctionLot, AuctionBid
from auth.cookie_auth import get_current_user_from_cookie
from database import get_db
from pydantic import BaseModel, Field
from typing import Literal
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from fastapi import Body

router = APIRouter(prefix="/api/auction", tags=["Auction"])

STATIC_URL = "https://localhost:5002"  # или твой хостинг

class AuctionCreateRequest(BaseModel):
    item_type: Literal["item", "pet"] = Field(..., description="Тип предмета: item или pet")
    item_id: int
    currency: Literal["coins", "nullings"] = Field(..., description="Тип валюты: coins или nullings")
    min_price: float = Field(..., gt=0, description="Минимальная цена")
    duration_hours: float = Field(..., ge=0.25, le=168, description="Длительность аукциона в часах (0.5 = 30 минут)")

    @field_validator("duration_hours", mode="before")
    @classmethod
    def round_to_15_min(cls, v):
        try:
            v = float(v)
        except:
            raise ValueError("Некорректное число часов")
        if v < 0.25:
            raise ValueError("Минимальная длительность — 15 минут (0.25 часа)")
        return round(v * 4) / 4  # ⏱️ шаг 15 минут


    @field_validator("min_price", mode="after")
    @classmethod
    def validate_min_price(cls, v, info):
        currency = info.data.get("currency")
        if currency == "coins":
            if v < 500:
                raise ValueError("Минимальная ставка за монеты — 500")
            if not float(v).is_integer():
                raise ValueError("Ставка в монетах должна быть целым числом")
            return int(v)
        elif currency == "nullings":
            if v < 0.10:
                raise ValueError("Минимальная ставка за нуллинги — 0.10")
            return round(v, 2)
        return v


from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone

@router.get("/", summary="Получить все активные лоты")
async def get_all_active_auctions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_from_cookie)  # 🆕
):
    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(AuctionLot)
        .options(
            joinedload(AuctionLot.owner),
            joinedload(AuctionLot.highest_bidder)
        )
        .where(
            AuctionLot.is_active == True,
            AuctionLot.expires_at > now
        )
        .order_by(AuctionLot.expires_at.asc())
    )
    lots = result.scalars().all()

    out = []

    for lot in lots:
        # 🔢 кол-во ставок
        count_res = await db.execute(
            select(func.count()).select_from(AuctionBid).where(AuctionBid.auction_id == lot.id)
        )
        bid_count = count_res.scalar_one()

        lot_data = {
            "id": lot.id,
            "item_type": lot.item_type,
            "item_id": lot.item_id,
            "currency": lot.currency,
            "starting_price": float(lot.starting_price),
            "current_bid": float(lot.current_bid or 0),
            "expires_at": lot.expires_at.isoformat(),
            "owner_id": lot.owner_id,
            "owner_name": lot.owner.username if lot.owner else "???",
            "highest_bidder_name": lot.highest_bidder.username if lot.highest_bidder else None,
            "bid_count": bid_count,
            "name": None,
            "image": None,
            "avatar_layers": None
        }

        if lot.item_type == "item":
            item_result = await db.execute(
                select(InventoryItem).options(joinedload(InventoryItem.product)).where(InventoryItem.id == lot.item_id)
            )
            item = item_result.scalar_one_or_none()
            if item and item.product:
                lot_data["name"] = item.product.name
                lot_data["image"] = f"/static/goods/{item.product.image}" if item.product.image else "/static/goods/noimage.png"

        elif lot.item_type == "pet":
            pet_result = await db.execute(select(Pet).where(Pet.id == lot.item_id))
            pet = pet_result.scalar_one_or_none()
            if pet:
                lot_data["name"] = pet.name or f"Питомец #{pet.id}"
                lot_data["avatar_layers"] = pet.avatar_layers or []

        out.append(lot_data)

    return {"lots": out, "user_id": user.id}



@router.post("/create")
async def create_auction_lot(
    data: AuctionCreateRequest,
    user: User = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)

    # ⛔ Проверка: валидный предмет и владелец
    if data.item_type == "item":
        result = await db.execute(
            select(InventoryItem)
            .options(joinedload(InventoryItem.product))  # 🩹 вот это обязательно!
            .where(
                and_(
                    InventoryItem.id == data.item_id,
                    InventoryItem.user_id == user.id,
                    or_(
                        InventoryItem.state == None,
                        InventoryItem.state.notin_(["equipped", "safe", "locked"])
            )
        )
    )
)
        

        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail="Предмет не найден или недоступен")

        FORBIDDEN_RARITIES = {"trash", "frequent", "common", "unique"}

    if item.product.non_tradeable or item.product.rarity in FORBIDDEN_RARITIES:
        raise HTTPException(status_code=400, detail="Этот предмет нельзя выставить на аукцион")


    elif data.item_type == "pet":
        result = await db.execute(
            select(Pet).where(
                and_(
                    Pet.id == data.item_id,
                    Pet.user_id == user.id,
                    or_(
    Pet.state == None,
    Pet.state == "normal"
)
                )
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail="Питомец не найден или недоступен")

        if item.non_tradeable or item.rarity == "unique":
            raise HTTPException(status_code=400, detail="Этого питомца нельзя выставить на аукцион")


    # ✅ Создание лота
    expires_at = now + timedelta(hours=data.duration_hours)

    new_lot = AuctionLot(
        owner_id=user.id,
        item_type=data.item_type,
        item_id=data.item_id,
        currency=data.currency,
        starting_price=data.min_price,
        expires_at=expires_at,
        is_active=True,
        created_at=now
    )

    db.add(new_lot)
    # 🛡️ Блокировка предмета/питомца
    item.state = "auction"
    await db.commit()

    return {
        "success": True,
        "lot_id": new_lot.id,
        "expires_at": expires_at.isoformat(),
        "message": "Лот успешно выставлен на аукцион"
    }


class BidRequest(BaseModel):
    lot_id: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)

@router.post("/bid", summary="Сделать ставку")
async def place_bid(
    data: BidRequest = Body(...),
    user: User = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    now = datetime.now(timezone.utc)

    # 1. Получаем лот с блокировкой SELECT FOR UPDATE
    result = await db.execute(
        select(AuctionLot)
        .where(
            AuctionLot.id == data.lot_id,
            AuctionLot.is_active == True,
            AuctionLot.expires_at > now
        )
        .with_for_update()
    )
    lot = result.scalar_one_or_none()
    if not lot:
        raise HTTPException(status_code=404, detail="Лот не найден или уже завершён")

    # 2. Запрет на ставку самому себе
    if lot.owner_id == user.id:
        raise HTTPException(status_code=403, detail="Нельзя делать ставку на свой лот")

    # 3. Проверка минимальной суммы
    if lot.current_bid is None:
        if data.amount < lot.starting_price:
            raise HTTPException(
                status_code=400,
                detail=f"Ставка должна быть не ниже минимальной ({lot.starting_price})"
            )
    else:
        if data.amount <= lot.current_bid:
            raise HTTPException(
                status_code=400,
                detail=f"Ставка должна быть выше текущей ({lot.current_bid})"
            )

    user = await db.merge(user)

    # 4. Проверка баланса и списание валюты у нового игрока
    if lot.currency == "coins":
        if user.coins < data.amount:
            raise HTTPException(status_code=400, detail="Недостаточно монет для ставки")
        user.coins -= int(data.amount)
    elif lot.currency == "nullings":
        if user.nullings < data.amount:
            raise HTTPException(status_code=400, detail="Недостаточно нуллингов для ставки")
        user.nullings -= round(float(data.amount), 2)

    # 5. Возврат предыдущей ставки предыдущему игроку (если был)
    if lot.highest_bidder_id and lot.highest_bidder_id != user.id:
        prev_result = await db.execute(
            select(User).where(User.id == lot.highest_bidder_id)
        )
        prev_user = prev_result.scalar_one_or_none()
        if prev_user:
            if lot.currency == "coins":
                prev_user.coins += int(lot.current_bid)
            elif lot.currency == "nullings":
                prev_user.nullings += round(float(lot.current_bid), 2)

    # 6. Создаём ставку
    bid = AuctionBid(
        auction_id=lot.id,
        bidder_id=user.id,
        amount=data.amount,
        created_at=now
    )
    db.add(bid)

    # 7. Обновляем лот
    lot.current_bid = data.amount
    lot.highest_bidder_id = user.id

    await db.commit()
    return {"success": True, "message": "Ставка принята"}

