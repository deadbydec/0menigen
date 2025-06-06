from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from sqlalchemy.orm import Session
from sqlalchemy import cast, String
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession  # импорт нужного класса
from sqlalchemy.dialects.postgresql import JSONB
from models.models import User, Race, GenderEnum, Product, InventoryItem, SystemMessage, SystemMessageType, ProductType
from sqlalchemy.future import select  # не забудь импорт!
from auth.cookie_auth import get_current_user_from_cookie, get_token_from_cookie, decode_access_token
from utils.last_seen import is_user_online, set_user_online
from pydantic import BaseModel
from sqlalchemy.orm import selectinload
from utils.random_event_loader import RANDOM_EVENTS
from random import random, choice

router = APIRouter(prefix="/api/player", tags=["player"])

class IdentityData(BaseModel):
    race: str
    gender: str
    birth_date: str

@router.get("/")
async def get_player_info(request: Request, db: Session = Depends(get_db)):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Ты не игрок. Уходи.")
    
    await set_user_online(user.id)

    # 💥 Пытаемся вызвать глюк
    event_result = await maybe_trigger_random_event(user, db)
    response = await get_player_data(user.id, db)

    if event_result:
        response["random_event"] = event_result  # 👈 фронт может ловить и показывать

    return response


async def get_player_data(user_id: int, db: AsyncSession) -> dict | None:
    result = await db.execute(
        select(User).options(selectinload(User.race)).filter_by(id=user_id)
    )
    user = result.scalar()
    
    if not user:
        return None

    return {
        "id": user.id,
        "name": user.username,
        "usertype": user.user_type.to_russian(),
        "avatar": user.avatar if user.avatar else "/api/profile/avatars/default_avatar.png",
        "coins": user.coins,
        "race": {
            "id": user.race.id,
            "code": user.race.code,
            "display_name": user.race.display_name,
            "vibe": user.race.vibe,
            "description": user.race.description,
            "image_url": f"https://localhost:8000/static/races/{user.race.code}.png" if user.race else None,
        } if user.race else None,
        "nullings": user.nullings,
        "level": user.level,
        "xp": user.xp,
        "nextLevelXp": user.get_xp_to_next_level(),
        "bio": user.bio,
        "registrationDate": user.registration_date.isoformat() if user.registration_date else None,
        "lastLogin": user.last_login.isoformat() if user.last_login else None,
        "gender": user.gender.name if user.gender else "UNKNOWN",
        "gender_label": user.gender.to_russian() if user.gender else "неизвестный",
        "playtime": round(user.total_playtime, 2),
        "layout": user.layout,
        "nicknames": user.nicknames,
        "warnings": user.warning_count,
        "lastIps": user.last_ips,
        "birthdate": user.birthdate.isoformat() if user.birthdate else None,
        "email": user.email,
        "vault_balance": user.vault_balance,
    }

@router.get("/public/{user_id}")
async def get_public_player(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()

    if not user:
        raise HTTPException(status_code=404, detail="Публичный профиль не найден")

    return {
        "id": user.id,
        "name": user.username,
        "avatar": user.avatar if user.avatar else "/api/profile/avatars/default_avatar.png",
        "race": user.race,
        "bio": user.bio,
        "level": user.level,
        "coins": user.coins,
        "status": "online" if is_user_online(user.id) else "offline",
        "usertype": user.user_type.to_russian(),
        "gender": user.gender.name if user.gender else "UNKNOWN",
        "registrationDate": user.registration_date.isoformat() if user.registration_date else None,
    }


@router.get("/races")
async def get_available_races(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Race).where(Race.is_selectable == True))
    races = result.scalars().all()

    base_url = str(request.base_url).rstrip("/")
    return [
        {
            "id": race.id,
            "code": race.code,
            "display_name": race.display_name,
            "vibe": race.vibe,
            "description": race.description,
            "is_selectable": race.is_selectable,
            "image_url": f"{base_url}{race.image_url}"  # 🔄 Автоматически по хосту
        }
        for race in races
    ]




@router.post("/choose-identity")
async def choose_identity(
    request: Request,
    data: IdentityData,
    db: AsyncSession = Depends(get_db)
):
    token = get_token_from_cookie(request)
    payload = decode_access_token(token)
    user_id = int(payload.get("sub"))

    race_code = data.race
    gender = data.gender
    birth_date = data.birth_date

    race = await db.execute(select(Race).where(Race.code == race_code))
    race = race.scalar()
    if not race:
        raise HTTPException(status_code=400, detail="Недопустимая расовая сущность.")

    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalar()
    if user.race_id:
        raise HTTPException(status_code=403, detail="Раса уже выбрана!")

    if gender not in [g.value for g in GenderEnum]:
        raise HTTPException(status_code=400, detail="Недопустимый пол.")

    try:
        birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты.")

    user.race_id = race.id
    user.gender = GenderEnum(gender)
    user.birthdate = birth_date_obj
    await db.commit()

    result = await db.execute(
        select(Product)
        .where(
            Product.product_type == ProductType.creature.value,
            Product.custom.op("->>")("race_code") == race.code
        )
    )
    egg = result.scalar()
    if not egg:
        raise HTTPException(status_code=500, detail="Яйцо для этой расы не найдено.")
    
    db.add(InventoryItem(user_id=user.id, product_id=egg.id, quantity=1))

    await db.commit()
    
    return {
        "message": f"Раса '{race.display_name}' успешно выбрана! Яйцо добавлено в инвентарь.",
        "egg": {
            "name": egg.name,
            "image": egg.image,
            "description": egg.description,
            "rarity": egg.rarity.value
        }
    }



async def maybe_trigger_random_event(user, db):
    if random() < 0.25:
        event = choice(RANDOM_EVENTS)
        reward = event.get("reward", {})

        # Применяем награду
        if "coins" in reward:
            user.coins += reward["coins"]
        if "xp" in reward:
            await user.add_xp(db, reward["xp"])
        if "item_id" in reward:
            product = await db.get(Product, reward["item_id"])
            if product:
                db.add(InventoryItem(user_id=user.id, product_id=product.id, quantity=1))

        await db.commit()

        return {
            "title": event["title"],
            "description": event["description"],
            "effect": event.get("effect", ""),
            "reward": reward
        }

    return None


