from __future__ import annotations

import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from fastapi import HTTPException

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
        "accessory": "аксессуар", "face": "морда", "skin": "покров", "foreground":"передний план"
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


# ────────────────────────────────────────────────────────────
async def move_to_wardrobe(           # ← только ОДИН экземпляр
    db:   AsyncSession,
    user,                             # current user (модель User)
    item_id: int                      # InventoryItem.id
) -> None:
    """
    Перемещает ОДИН конкретный `InventoryItem`
    → создаёт НОВУЮ запись `UserPetWardrobeItem`
    с `quantity = 1` и уникальным `wardrobe_id`.
    """

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


# ────────────────────────────────────────────
async def move_from_wardrobe(
    db: AsyncSession, user, product_id: int, qty: int = 1
) -> None:
    """
    Возвращает `qty` экземпляров косметики из гардероба → инвентарь.
    Вызывается роутом  POST /wardrobe/remove, который шлёт product_id + quantity.
    """
    if qty < 1:
        raise HTTPException(400, "quantity ≥ 1")

    entry: UserPetWardrobeItem | None = (
        await db.execute(
            select(UserPetWardrobeItem).where(
                UserPetWardrobeItem.user_id == user.id,
                UserPetWardrobeItem.product_id == product_id,
            )
        )
    ).scalar_one_or_none()

    if not entry or entry.quantity < qty:
        raise HTTPException(400, "Недостаточно предметов в гардеробе")

    # — инвентарь —
    inv_item: InventoryItem | None = (
        await db.execute(
            select(InventoryItem).where(
                InventoryItem.user_id == user.id,
                InventoryItem.product_id == product_id,
            )
        )
    ).scalar_one_or_none()

    if inv_item:
        inv_item.quantity += qty
    else:
        db.add(
            InventoryItem(
                user_id=user.id,
                product_id=product_id,
                quantity=qty,
            )
        )

    # — гардероб —
    entry.quantity -= qty
    if entry.quantity == 0:
        await db.delete(entry)

    await db.commit()
    print(f"[WARDROBE] {entry.product.name} ← {qty} шт. обратно в инвентарь")


# ────────────────────────────────────────────
async def serialize_wardrobe(
    db: AsyncSession,
    user_id: int
) -> list[dict]:
    """
    Возвращает **каждую копию** предмета гардероба отдельным элементом.
    Поле `quantity` остаётся (всегда 1), но больше не влияет на фронт.
    """

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

# ────────────────────────────────────────────
async def build_avatar_layers(pet, db: AsyncSession) -> list[dict]:
    """
    Строит слои рендера для мини-аватара (pet.avatar_layers), на основе appearance.
    Используется для карточек питомцев.
    """

    inventory_ids = [l["inventory_id"] for l in pet.appearance_layers]
    order = pet.slot_order or []

    result = await db.execute(
        select(InventoryItem)
        .options(joinedload(InventoryItem.product))
        .where(InventoryItem.id.in_(inventory_ids))
    )
    inventory_map = {item.id: item for item in result.scalars().all()}

    STATIC_URL = "https://localhost:5002/static/goods"  # ❗️или подставь переменную окружения

    layers = []
    for iid in order:
        inv = inventory_map.get(iid)
        if not inv or not inv.product:
            continue

        prod = inv.product
        custom = prod.custom
        if isinstance(custom, str):
            try:
                custom = json.loads(custom)
            except json.JSONDecodeError:
                custom = {}

        layers.append({
            "src": f"{STATIC_URL}/{prod.image}",
            "z": custom.get("z", 0),
            "slot": custom.get("slot", "unknown")
        })

    return layers







