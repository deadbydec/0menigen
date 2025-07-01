from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models.models import InventoryItem, Product, ProductType, User, LandfillItem, Incubation, Pet
from auth.cookie_auth import get_current_user_from_cookie
from sqlalchemy.orm import selectinload
from typing import Optional
from fastapi.responses import JSONResponse
from random import random, randint
from datetime import datetime, timedelta, timezone
from typing import Optional
from utils.inventory_tools import build_inventory_item
from random   import choice
from pydantic import BaseModel, constr
from fastapi import Body
from pydantic import field_validator

router = APIRouter(prefix="/api/inventory", tags=["inventory"])

from pydantic import BaseModel

class GiftPayload(BaseModel):
    recipient_id: int   
    quantity: int = 1

class HatchPayload(BaseModel):
    name: constr(strip_whitespace=True, min_length=3, max_length=15)
    incubation_id: int | None = None

    @field_validator("name")
    @classmethod
    def check_visible_length(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Имя должно содержать хотя бы 3 видимых символа.")
        return v

@router.get("/")
async def get_inventory(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_cookie: Optional[User] = Depends(get_current_user_from_cookie),
):
    # CORS preflight fallback
    
    if request.method == "OPTIONS" or not user_cookie:
        print("🔁 [INFO] Preflight или отсутствует юзер — пустой ответ")
        return JSONResponse(status_code=204, content={})
    
    # Перезагружаем юзера в текущей сессии с его расой
    result = await db.execute(
        select(User).where(User.id == user_cookie.id).options(selectinload(User.race))
    )
    user = result.scalar_one()

    print("🧠 [DEBUG] Запрашивает юзер:", user.id)

    # Загружаем инвентарь
    result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.user_id == user.id)
        .options(
            selectinload(InventoryItem.product),
            selectinload(InventoryItem.incubation),
        )
    )
    inventory = result.scalars().all()

    inventory_list = [build_inventory_item(item) for item in inventory if item.product]
    user_race = user.race.code.lower() if user.race else None

    return {
        "inventory": inventory_list,
        "user_race": user_race,
    }




@router.post("/incubate/{item_id}")
async def incubate_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_from_cookie)
):
    # Получаем предмет
    result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.id == item_id)
        .options(
            selectinload(InventoryItem.product),
            selectinload(InventoryItem.incubation)  # 👈 вот это добавь
        )
    )
    item = result.scalar()

    if not item or item.user_id != user.id:
        raise HTTPException(403, detail="Этот предмет вам не принадлежит!")

    from utils.inventory_tools import assert_item_unlocked
    assert_item_unlocked(item)


    if item.product.product_type != ProductType.creature:
        raise HTTPException(status_code=400, detail="Это не яйцо!")

    if item.incubation:
        raise HTTPException(status_code=400, detail="Это яйцо уже инкубируется")

    # Проверяем, есть ли уже активная инкубация
    active = await db.execute(
        select(Incubation).where(Incubation.user_id == user.id, Incubation.is_hatched == False)
    )
    if active.scalar():
        raise HTTPException(status_code=400, detail="У тебя уже есть активное яйцо")

    incubation_data = item.product.custom or {}
    time_range = incubation_data.get("incubation_time_range", [3, 5])
    minutes = randint(time_range[0], time_range[1])

    now = datetime.now(timezone.utc)
    hatch_at = now + timedelta(minutes=minutes)

    new_incubation = Incubation(
        user_id=user.id,
        inventory_item_id=item.id,
        started_at=now,
        hatch_at=hatch_at,
        is_hatched=False
    )

    db.add(new_incubation)
    await db.commit()

    return {
        "success": True,
        "message": f"🥚 Инкубация началась! Вылупление через {minutes} минут.",
        "hatch_at": hatch_at.isoformat()

    }


@router.post("/hatch")
async def hatch_pet(
    payload: HatchPayload = Body(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_from_cookie),
):
    user = await db.get(User, user.id, options=[selectinload(User.race)])
    if not payload.name:
        raise HTTPException(400, "Нужно придумать имя для питомца!")

    q = (
        select(Incubation)
        .where(
            Incubation.user_id == user.id,
            Incubation.is_hatched == False,
            Incubation.hatch_at <= datetime.now(timezone.utc)
        )
        .options(
            selectinload(Incubation.inventory_item)
            .selectinload(InventoryItem.product)
        )
    )
    if payload.incubation_id:
        q = q.where(Incubation.id == payload.incubation_id)

    result = await db.execute(q)
    incubation = result.scalar_one_or_none()
    if not incubation:
        raise HTTPException(400, "Нет готовых к вылуплению яиц")

    egg_item = incubation.inventory_item
    egg_product = egg_item.product
    egg_settings = egg_product.custom or {}

    # 💎 особая логика для мистического яйца
    if egg_product.id == 511:
        from utils.pet_spawner import spawn_random_pet

        new_pet = await spawn_random_pet(user.id, db)
        new_pet.name = payload.name
        db.add(new_pet)

        incubation.is_hatched = True
        await db.delete(egg_item)
        await db.commit()
        await db.refresh(new_pet)

        return {
            "id": new_pet.id,
            "name": new_pet.name,
            "image": new_pet.image
        }


    # 🐣 обычное яйцо (по расе, как раньше)
    race_code = egg_settings.get("race_code", user.race.code if user.race else "unknown")
    image_name = choice(egg_settings.get("spawn_variants", ["noimage.png"]))
    trait_pick = choice(egg_settings.get("trait_pool", ["silent"]))

    new_pet = Pet(
        user_id=user.id,
        race_code=race_code,
        name=payload.name,
        image=f"pets/{image_name}",
        trait=trait_pick,
    )
    db.add(new_pet)

    incubation.is_hatched = True
    await db.delete(egg_item)
    await db.commit()
    await db.refresh(new_pet)

    return {
        "id": new_pet.id,
        "name": new_pet.name,
        "image": new_pet.image
    }


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
    from utils.inventory_tools import assert_item_unlocked
    

    if not sender_item or sender_item.quantity < quantity:
        raise HTTPException(status_code=400, detail="Недостаточно предметов для подарка.")
    assert_item_unlocked(sender_item)

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
        raise HTTPException(403, detail="Этот предмет вам не принадлежит!")

    from utils.inventory_tools import assert_item_unlocked
    assert_item_unlocked(item)


    product = item.product
    if not product:
        raise HTTPException(500, detail="У предмета отсутствует привязанный продукт.")
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
@router.delete("/discard/{item_id}")
async def discard_item(
    item_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_from_cookie)
):
    """Удаляет одну единицу предмета из инвентаря"""
    result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.id == item_id)
        .options(selectinload(InventoryItem.product))
    )
    inventory_item = result.scalar()

    if not inventory_item or inventory_item.user_id != user.id:
        raise HTTPException(403, detail="Этот предмет вам не принадлежит!")

    from utils.inventory_tools import assert_item_unlocked
    assert_item_unlocked(inventory_item)


    item_name = inventory_item.product.name

    # 💥 Кидаем только 1 шт.
    landfill = LandfillItem(
        product_id=inventory_item.product_id,
        quantity=1,
        thrown_by_id=user.id
    )
    db.add(landfill)

    # 💥 Уменьшаем количество в инвентаре
    if inventory_item.quantity > 1:
        inventory_item.quantity -= 1
    else:
        await db.delete(inventory_item)

    await db.commit()
    return {"success": True, "message": f"Вы выбросили 1x {item_name}!"}



@router.post("/recycle/{item_id}")
async def recycle_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_from_cookie)
):
    # Перезагружаем пользователя с опцией загрузки отношения race
    user = await db.get(User, user.id, options=[selectinload(User.race)])
    
    # Проверка расы
    user_race = user.race.display_name.strip().lower() if user.race and user.race.display_name else ""
    print(f"[DEBUG] User race: '{user_race}'")  # для отладки
    if user_race != "наллвур":
        raise HTTPException(status_code=403, detail="Только Наллвур могут перерабатывать предметы.")

    # Находим предмет
    result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.id == item_id)
        .options(selectinload(InventoryItem.product))
    )
    item = result.scalar()

    if not item or item.user_id != user.id or not item.product:
        raise HTTPException(status_code=403, detail="Этот предмет вам не принадлежит!")
    from utils.inventory_tools import assert_item_unlocked
    assert_item_unlocked(item)


    product = item.product
    result_msg = [f"Вы переработали {product.name}..."]

    roll = random() * 100

    if roll < 60:
        coins = randint(5, 20)
        user.coins += coins
        result_msg.append(f"Из хлама извлечено {coins} монет!")
    elif roll < 90:
        xp = randint(10, 50)
        await user.add_xp(db, xp)
        result_msg.append(f"Вы получили {xp} опыта, вдыхая пыль предмета.")
    elif roll < 90.35:
        user.nullings += 0.35
        result_msg.append("⚫ Из пустоты извлечено 0.35 нуллингов. Холод прошёл по коже.")
    else:
        result_msg.append("Ничего не найдено, кроме запаха разложения.")

    # Уменьшаем количество или удаляем
    if item.quantity > 1:
        item.quantity -= 1
    else:
        await db.delete(item)

    await db.commit()
    return {"message": " ".join(result_msg)}









