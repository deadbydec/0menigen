#routes.wardrobe.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from auth.cookie_auth import get_current_user_from_cookie
from utils.wardrobe_tools import (
    move_to_wardrobe,
    move_from_wardrobe,
    serialize_wardrobe,
)

router = APIRouter(prefix="/api/wardrobe", tags=["wardrobe"])

@router.get("/", summary="Получить гардероб")
async def get_wardrobe(
    user = Depends(get_current_user_from_cookie),
    db:   AsyncSession = Depends(get_db),
):
    if not user:
        raise HTTPException(401, "Не авторизован")
    return await serialize_wardrobe(db, user.id)

@router.post("/add", summary="Убрать предмет из инвентаря в гардероб")
async def add_to_wardrobe(
    payload: dict,
    user      = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db),
):

    if not user:
        raise HTTPException(401, "Не авторизован")

    # берём либо item_id, либо inventory_id — чтобы фронт мог прислать любой из них
    item_id = payload.get("item_id") or payload.get("inventory_id")
    if item_id is None:
        raise HTTPException(400, "`item_id` обязателен")

    # 👉 сам перенос (+ commit) делает утилита
    await move_to_wardrobe(db, user, int(item_id))

    # отдаём свежее содержимое гардероба
    return await serialize_wardrobe(db, user.id)

@router.post("/remove", summary="Вернуть предмет из гардероба")
async def remove_from_wardrobe(
    payload: dict,
    user = Depends(get_current_user_from_cookie),
    db:   AsyncSession = Depends(get_db),
):
    wardrobe_id = payload.get("wardrobe_id")
    if not wardrobe_id:
        raise HTTPException(400, "`wardrobe_id` обязателен")

    await move_from_wardrobe(db, user, wardrobe_id)

    return await serialize_wardrobe(db, user.id)


#utils.wardrobe_tools.py
from __future__ import annotations
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from fastapi import HTTPException
from models.models import PetRenderConfig, Pet  # не забудь импорт
from constants.wardrobe import AVATAR_SLOTS

async def build_avatar_layers(
    pet_id: int,
    db: AsyncSession,
    avatar_mode: bool = False,
    race_code: str = ""
) -> list[dict]:

    config: PetRenderConfig | None = await db.get(PetRenderConfig, pet_id)
    pet: Pet | None = await db.get(Pet, pet_id)

    if not config or not isinstance(config.slot_order, list) or not pet:
        return []

    inventory_ids = [
        layer["rid"]
        for layer in config.slot_order
        if isinstance(layer, dict) and "rid" in layer and layer["rid"] not in (None, -1)
    ]

    result = await db.execute(
        select(UserPetWardrobeItem)
        .options(joinedload(UserPetWardrobeItem.product))
        .where(UserPetWardrobeItem.id.in_(inventory_ids))
    )
    wardrobe_map = {item.id: item for item in result.scalars().all()}

    layers = []

    # 🐾 Базовый слой питомца — всегда строго z=3
    if pet.image:
        layers.append({
            "src": f"https://localhost:5002/static/{pet.image}",
            "z": 3,
            "slot": "base"
        })

    for layer in config.slot_order:
        rid = layer.get("rid")
        slot = layer.get("slot")

        if rid in (None, -1) or not slot:
            continue

        if avatar_mode and slot not in AVATAR_SLOTS:
            continue

        wrd = wardrobe_map.get(rid)
        if not wrd or not wrd.product:
            continue

        prod = wrd.product
        custom = prod.custom

        if isinstance(custom, str):
            try:
                custom = json.loads(custom)
            except json.JSONDecodeError:
                custom = {}

        src = None
        render_variants = custom.get("render_variants", {})
        variant = render_variants.get(race_code)

        if isinstance(variant, str):
            src = f"https://localhost:5002/static/cosmetic/{variant}"
        elif f"{slot}_image" in custom:
            src = f"https://localhost:5002/static/{custom[f'{slot}_image']}"
        elif "image" in custom:
            src = f"https://localhost:5002/static/cosmetic/{custom['image']}"
        elif prod.image:
            src = f"https://localhost:5002/static/goods/{prod.image}"

        if src:
            layers.append({
                "src": src,
                "z": custom.get("z", 100),
                "slot": slot
            })

    return sorted(layers, key=lambda l: l["z"])

from utils.slot_utils import get_enum_slot
from models.models import (
    InventoryItem,
    Product,
    ProductType,
    UserPetWardrobeItem,
    WardrobeSlot,
)
async def detect_slot(product: Product) -> WardrobeSlot:
    SLOT_MAP = {
        "background": "фон", "aura": "окружение", "companion": "спутник",
        "body": "тело", "paws": "лапы", "wings": "крылья",
        "eyes": "глаза", "head": "голова", "tail": "хвост",
        "accessory": "аксессуар", "face": "морда", "skin": "покров", "foreground":"передний план", "dye":"эссенция"
    }

    try:
        custom = json.loads(product.custom) if isinstance(product.custom, str) else (product.custom or {})
    except json.JSONDecodeError:
        custom = {}

    raw = custom.get("slot")
    ru_slot = SLOT_MAP.get(raw, raw)
    try:
        return WardrobeSlot(ru_slot) if ru_slot else WardrobeSlot.accessory
    except ValueError:
        return WardrobeSlot.accessory

async def move_to_wardrobe(           # ← только ОДИН экземпляр
    db:   AsyncSession,
    user,                             # current user (модель User)
    item_id: int                      # InventoryItem.id
) -> None:

    # 1 ▸ находим предмет в инвентаре
    item: InventoryItem | None = (
        await db.execute(
            select(InventoryItem)
            .options(joinedload(InventoryItem.product))
            .where(InventoryItem.id == item_id)
        )
    ).scalar_one_or_none()

    if not item or item.user_id != user.id:
        raise HTTPException(403, "Предмет не найден или не ваш")

    product = item.product
    if not product:
        raise HTTPException(500, "У предмета нет связанного Product")

    # 2 ▸ проверяем, что это косметика
    is_cosmetic = (
        product.product_type == ProductType.cosmetic or
        str(product.product_type) == "cosmetic"       # старые строки
    )
    if not is_cosmetic:
        raise HTTPException(400, "Это не косметика")

    slot: WardrobeSlot = await detect_slot(product)

    # 3 ▸ создаём НОВУЮ запись в гардеробе
    wardrobe_entry = UserPetWardrobeItem(
        user_id    = user.id,
        product_id = product.id,
        slot       = slot,
        quantity   = 1            # всегда 1 — каждая копия отдельно
    )
    db.add(wardrobe_entry)

    # 4 ▸ немедленно флешим, чтобы получить уникальный wardrobe_id
    await db.flush()              # ← критично, иначе SQLAlchemy
                                  #    может аггрегировать одинаковые записи

    # 5 ▸ вычитаем предмет из инвентаря
    if item.quantity > 1:
        item.quantity -= 1
    else:
        await db.delete(item)

    # 6 ▸ фиксируем транзакцию
    await db.commit()

    print(
        f"[WARDROBE] +1 «{product.name}» "
        f"(slot={slot.value}, wardrobe_id={wardrobe_entry.id})"
    )

async def move_from_wardrobe(
    db: AsyncSession,
    user,
    wardrobe_id: int
) -> None:

    entry: UserPetWardrobeItem | None = (
        await db.execute(
            select(UserPetWardrobeItem)
            .options(joinedload(UserPetWardrobeItem.product))
            .where(UserPetWardrobeItem.id == wardrobe_id, UserPetWardrobeItem.user_id == user.id)
        )
    ).scalar_one_or_none()

    if not entry:
        raise HTTPException(404, "Предмет не найден в гардеробе")

    product = entry.product
    if not product:
        raise HTTPException(500, "У гардеробного предмета нет Product")

    # 📥 Перемещаем в инвентарь
    existing: InventoryItem | None = (
        await db.execute(
            select(InventoryItem)
            .where(InventoryItem.user_id == user.id, InventoryItem.product_id == product.id)
        )
    ).scalar_one_or_none()

    if existing:
        existing.quantity += 1
    else:
        db.add(InventoryItem(user_id=user.id, product_id=product.id, quantity=1))

    await db.delete(entry)
    await db.commit()

    print(f"[WARDROBE] -1 «{product.name}» (wardrobe_id={wardrobe_id}) → инвентарь")

async def serialize_wardrobe(
    db: AsyncSession,
    user_id: int
) -> list[dict]:

    rows = (
        await db.execute(
            select(UserPetWardrobeItem)
            .options(joinedload(UserPetWardrobeItem.product))
            .where(UserPetWardrobeItem.user_id == user_id)
            .order_by(UserPetWardrobeItem.id.asc())
        )
    ).scalars().all()

    RU_TO_EN = {
        "фон": "background", "окружение": "aura",   "спутник": "companion",
        "тело": "body",      "лапы": "paws",        "крылья": "wings",
        "глаза": "eyes",     "голова": "head",      "хвост": "tail",
        "аксессуар": "accessory", "морда": "face",  "покров": "skin",
        "передний план":"foreground", "эссенция":"dye"
    }

    out: list[dict] = []

    for wrd in rows:
        prod = wrd.product

        # safe-parse custom
        custom = prod.custom
        if isinstance(custom, str):
            try:
                custom = json.loads(custom)
            except json.JSONDecodeError:
                custom = {}

        item: dict = {
            "wardrobe_id": wrd.id,          # 👈 уникальный id копии
            "product_id":  prod.id,
            "slot":        wrd.slot.value,
            "quantity":    wrd.quantity,    # всегда 1, но пусть будет
            "name":        prod.name,
            "image":       prod.image,
            "rarity":      prod.rarity.value,
            "custom":      custom or {},
        }

        # если custom имеет slot-specific изображение — кладём отдельным ключом
        en_slot = RU_TO_EN.get(wrd.slot.value)
        if en_slot:
            key = f"{en_slot}_image"
            if isinstance(custom, dict) and key in custom:
                item[key] = custom[key]

        out.append(item)

    return out
