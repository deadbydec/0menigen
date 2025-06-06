from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from pydantic import BaseModel, Field
from typing import Optional, List
from utils.wardrobe_tools import build_avatar_layers
import logging

from database import get_db
from models.models import Pet, PetAppearance, PetRenderConfig
from auth.cookie_auth import get_current_user_from_cookie
from utils.slot_utils import get_enum_slot

router = APIRouter(prefix="/api/pets", tags=["pets"])
logger = logging.getLogger(__name__)

class Layer(BaseModel):
    pid: int
    rid: Optional[int] = None
    instance: int
    slot: Optional[str] = None

class AppearanceUpdate(BaseModel):
    appearance: dict[str, list[dict]] = Field(default_factory=dict)
    slot_order: list[Layer] = Field(default_factory=list)


@router.get("/", summary="Все питомцы игрока")
async def get_my_pets(user=Depends(get_current_user_from_cookie), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Pet).where(Pet.user_id == user.id).order_by(Pet.created_at)
    )
    pets = result.scalars().all()

    out = []
    for p in pets:
        pet_dict = await pet_to_dict(p, db)  # 💥 await обязательно!
        out.append(pet_dict)

    return out



@router.get("/{pet_id}", summary="Информация о питомце")
async def get_pet(pet_id: int, user=Depends(get_current_user_from_cookie), db: AsyncSession = Depends(get_db)):
    pet: Pet | None = await db.get(Pet, pet_id)
    if not pet or pet.user_id != user.id:
        raise HTTPException(404, "Питомец не найден")
    return pet_to_dict(pet)

@router.get("/{pet_id}/appearance")
async def get_appearance(pet_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user_from_cookie)):
    pet = await db.get(Pet, pet_id)
    if not pet or pet.user_id != user.id:
        raise HTTPException(404, "Питомец не найден")

    result = await db.execute(
        select(PetAppearance).where(PetAppearance.pet_id == pet.id).order_by(PetAppearance.slot, PetAppearance.layer_index)
    )
    app_rows = result.scalars().all()
    config = await db.get(PetRenderConfig, pet.id)

    appearance = {}
    instances = {}
    for row in app_rows:
        key = row.slot.name
        instances.setdefault(key, -1)
        instances[key] += 1
        appearance.setdefault(key, []).append({
            "rid": row.wardrobe_id,
            "pid": row.product_id,
            "instance": instances[key]
        })

    full_slot_order = []
    if config and isinstance(config.slot_order, list):
        for layer in config.slot_order:
            if isinstance(layer, dict):
                full_slot_order.append({
                    "pid": layer.get("pid", -1),
                    "rid": layer.get("rid", -1),
                    "slot": layer.get("slot", None),
                    "instance": layer.get("instance", 0),
                })

    return {"appearance": appearance, "slot_order": full_slot_order}

@router.post("/{pet_id}/appearance/bulk")
async def save_appearance(
    pet_id: int,
    payload: AppearanceUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_from_cookie),
):
    app_dict = payload.appearance or {}
    slot_order = payload.slot_order or []

    pet = await db.get(Pet, pet_id)
    if not pet or pet.user_id != user.id:
        raise HTTPException(404, "Питомец не найден")

    await db.execute(delete(PetAppearance).where(PetAppearance.pet_id == pet.id))

    for slot_str, layer_list in app_dict.items():
        try:
            slot_enum = get_enum_slot(slot_str)
        except ValueError:
            continue
        for layer_index, layer_obj in enumerate(layer_list):
            pid = layer_obj.get("pid")
            rid = layer_obj.get("rid")
            if pid == -1: pid = None
            if rid == -1: rid = None
            if pid is None and rid is None:
                continue
            db.add(PetAppearance(
                pet_id=pet.id,
                slot=slot_enum,
                wardrobe_id=rid,
                product_id=pid,
                layer_index=layer_index
            ))

    # Гарантируем, что slot_order сериализуется в JSONB
    full_slot_order = []
    for layer in slot_order:
        full_slot_order.append({
            "pid": layer.pid,
            "rid": layer.rid,
            "instance": layer.instance,
            "slot": layer.slot
        })

    existing_config = await db.get(PetRenderConfig, pet.id)
    if existing_config:
        existing_config.slot_order = full_slot_order
    else:
        db.add(PetRenderConfig(
            pet_id=pet.id,
            slot_order=full_slot_order
        ))

    await db.commit()
    return {"success": True}


async def pet_to_dict(pet: Pet, db: AsyncSession) -> dict:
    return {
        "id": pet.id,
        "name": pet.name,
        "race_code": pet.race_code,
        "image": pet.image,
        "trait": pet.trait,
        "level": pet.level,
        "intelligence": pet.intelligence,
        "fullness": pet.fullness,
        "energy": pet.energy,
        "health": pet.health,
        "mood": pet.mood,
        "bond": pet.bond,
        "anomaly_level": pet.anomaly_level,
        "birthdate": pet.birthdate.isoformat() if pet.birthdate else None,
        "created_at": pet.created_at.isoformat() if pet.created_at else None,
        "last_update": pet.last_update.isoformat() if pet.last_update else None,
        "avatar_layers": build_avatar_layers(pet.id, db),  # ← ВОТ ЭТО ДОЛЖНО БЫТЬ
    }
