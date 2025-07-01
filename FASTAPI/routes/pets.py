from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from pydantic import BaseModel, Field
from typing import Optional, List
from utils.wardrobe_tools import build_avatar_layers
from utils.books import get_detailed_read_books, apply_book_to_pet

import logging

from database import get_db
from models.models import Pet, PetAppearance, PetRenderConfig, Product, UserPetWardrobeItem, InventoryItem, VaultItem
from auth.cookie_auth import get_current_user_from_cookie
from utils.slot_utils import get_enum_slot

from fastapi.responses import JSONResponse
from utils.species_loader import load_all_pet_species  # ← твой готовый утиль

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


@router.get("/public/{user_id}", summary="Питомцы другого пользователя")
async def get_public_pets(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Pet).where(Pet.user_id == user_id).order_by(Pet.created_at)
    )
    pets = result.scalars().all()

    out = []
    for p in pets:
        pet_dict = await pet_to_dict(p, db)  # 💥 await обязательно
        out.append(pet_dict)

    return out

@router.get("/pet_species")
async def get_all_pet_species():
    """
    Возвращает список всех видов питомцев с метаданными.
    Формат: [{ species_code: { name, race_code, ... } }, ...]
    """
    return JSONResponse(content=load_all_pet_species())

@router.get("/{pet_id}", summary="Информация о питомце")
async def get_pet(pet_id: int, user=Depends(get_current_user_from_cookie), db: AsyncSession = Depends(get_db)):
    pet: Pet | None = await db.get(Pet, pet_id)
    if not pet or pet.user_id != user.id:
        raise HTTPException(404, "Питомец не найден")

    return await pet_to_dict(pet, db)  # ✅✅✅ вот это и надо!


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


from utils.species_loader import load_all_pet_species

async def pet_to_dict(pet: Pet, db: AsyncSession) -> dict:
    species_data = load_all_pet_species()
    species_meta = species_data.get(pet.species_code, {})

    # 🎯 Локализация trait (если в БД остался англ.)
    trait_en = pet.trait
    trait_pool_en = species_meta.get("trait_pool_en", [])
    trait_pool_ru = species_meta.get("trait_pool", [])

    try:
        index = trait_pool_en.index(trait_en)
        localized_trait = trait_pool_ru[index] if index < len(trait_pool_ru) else trait_en
    except ValueError:
        localized_trait = trait_en

    return {
        "id": pet.id,
        "name": pet.name,
        "race_code": pet.race_code,
        "image": pet.image,
        "trait": localized_trait,  # 👈 теперь уже по-русски
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
        "avatar_layers": await build_avatar_layers(pet.id, db, avatar_mode=True, race_code=pet.race_code),
        "biography": pet.biography,

        "species": {
            "code": pet.species_code,
            "name": species_meta.get("species_name"),
            "emoji": species_meta.get("emoji"),
            "race_name": species_meta.get("race_name"),
            "description": species_meta.get("description"),
            "trait": species_meta.get("trait_pool")
        },

        "favorite_items": pet.favorite_items or [],
        "read_books": pet.read_books or [],  # 👈 вот это добавили
        "companion": {
            "product_id": pet.companion_id,
            "name": pet.companion_name,
            "image": pet.companion_image,
            "description": pet.companion_description,
        } if pet.companion_id else None
    }


class BioEdit(BaseModel):
    biography: str

class CompanionAttach(BaseModel):
    product_id: int
    name: str = ""
    description: str = ""

class FavoriteItemsPayload(BaseModel):
    item_ids: list[int] = Field(default_factory=list)  # ID продуктов

@router.post("/{pet_id}/bio", summary="Изменить био питомца")
async def update_biography(pet_id: int, payload: BioEdit, db: AsyncSession = Depends(get_db), user=Depends(get_current_user_from_cookie)):
    pet = await db.get(Pet, pet_id)
    if not pet or pet.user_id != user.id:
        raise HTTPException(404, "Питомец не найден")

    pet.biography = payload.biography[:2000]  # 🔒 Защита от оверфлоу
    await db.commit()
    return {"success": True}


@router.post("/{pet_id}/companion", summary="Приручить спутника питомцем")
async def tame_companion(pet_id: int, payload: CompanionAttach, db: AsyncSession = Depends(get_db), user=Depends(get_current_user_from_cookie)):
    pet = await db.get(Pet, pet_id)
    if not pet or pet.user_id != user.id:
        raise HTTPException(404, "Питомец не найден")

    product = await db.get(Product, payload.product_id)
    if not product:
        raise HTTPException(404, "Предмет не найден")

    if "companion" not in (product.types or []):
        raise HTTPException(400, "Этот предмет нельзя приручить как спутника")

    # 🧠 Проверяем, есть ли в инвентаре такой предмет
    item_to_delete = await db.scalar(
        select(InventoryItem)
        .where(
            InventoryItem.user_id == user.id,
            InventoryItem.product_id == product.id
        )
        .limit(1)
    )

    if not item_to_delete:
        raise HTTPException(400, "У тебя нет этого предмета")

    # ✅ Приручаем спутника
    pet.companion_id = product.id
    pet.companion_name = product.name
    pet.companion_description = product.description or ""
    pet.companion_image = product.image

    await db.delete(item_to_delete)
    await db.commit()

    return {"success": True}




class CompanionEdit(BaseModel):
    name: str = ""
    description: str = ""

@router.post("/{pet_id}/companion/edit", summary="Редактировать имя и описание спутника")
async def edit_companion(pet_id: int, payload: CompanionEdit, db: AsyncSession = Depends(get_db), user=Depends(get_current_user_from_cookie)):
    pet = await db.get(Pet, pet_id)
    if not pet or pet.user_id != user.id:
        raise HTTPException(404, "Питомец не найден")
    if not pet.companion_id:
        raise HTTPException(400, "У питомца нет спутника")

    pet.companion_name = payload.name[:100]
    pet.companion_description = payload.description[:2000]

    await db.commit()
    return {"success": True}



@router.post("/{pet_id}/favorite-items", summary="Добавить любимые предметы питомцу")
async def set_favorite_items(pet_id: int, payload: FavoriteItemsPayload, db: AsyncSession = Depends(get_db), user=Depends(get_current_user_from_cookie)):
    pet = await db.get(Pet, pet_id)
    if not pet or pet.user_id != user.id:
        raise HTTPException(404, "Питомец не найден")

    # Собираем все доступные игроку product_id из инвентаря, сейфа и гардероба
    result = await db.execute(
        select(Product.id)
        .join(InventoryItem, InventoryItem.product_id == Product.id, isouter=True)
        .join(VaultItem, VaultItem.product_id == Product.id, isouter=True)
        .join(UserPetWardrobeItem, UserPetWardrobeItem.product_id == Product.id, isouter=True)
        .where(
            (InventoryItem.user_id == user.id) |
            (VaultItem.user_id == user.id) |
            (UserPetWardrobeItem.user_id == user.id)
        )
    )
    allowed_ids = {row[0] for row in result.fetchall() if row[0] is not None}

    # Оставляем только те ID, которые реально есть у игрока
    filtered = [i for i in payload.item_ids if i in allowed_ids]

    pet.favorite_items = filtered[:20]  # 🔒 максимум 20 любимок
    await db.commit()
    return {"success": True, "count": len(filtered)}


class UseBookPayload(BaseModel):
    product_id: int

@router.get("/{pet_id}/read_books", summary="Прочитанные книги питомца с подробностями")
async def get_pet_read_books(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_from_cookie)
):
    pet = await db.get(Pet, pet_id)
    if not pet or pet.user_id != user.id:
        raise HTTPException(404, "Питомец не найден или не твой")

    books = await get_detailed_read_books(pet, db)
    return {"read_books": books}


@router.post("/{pet_id}/use_book")
async def use_book_on_pet(
    pet_id: int,
    payload: UseBookPayload,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_from_cookie)
):
    pet = await db.get(Pet, pet_id)
    if not pet or pet.user_id != user.id:
        raise HTTPException(404, "Питомец не найден или не твой")

    result = await apply_book_to_pet(pet, user.id, payload.product_id, db)
    await db.commit()

    return {
        "success": True,
        **result
    }


@router.post("/{pet_id}/companion/remove", summary="Убрать спутника у питомца")
async def remove_companion(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_from_cookie)
):
    pet = await db.get(Pet, pet_id)
    if not pet or pet.user_id != user.id:
        raise HTTPException(404, "Питомец не найден")

    # Сохраняем ссылку на старого компаньона до удаления
    old_companion_id = pet.companion_id

    # Очищаем компаньона у питомца
    pet.companion_id = None
    pet.companion_name = ""
    pet.companion_description = ""

    # Если был спутник — вернуть в инвентарь
    if old_companion_id:
        item = InventoryItem(
            user_id=user.id,
            product_id=old_companion_id,
            quantity=1
        )
        db.add(item)

    await db.commit()
    return {"success": True}





