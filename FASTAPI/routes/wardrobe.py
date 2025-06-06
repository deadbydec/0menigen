"""Ωmenigen · routes/wardrobe.py — атомарная версия
====================================================
Все операции работают с УНИКАЛЬНЫМИ экземплярами.
`quantity` не используется: одна запись = один предмет.
"""

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

# ─────────────────────────────────────────────
#  GET /api/wardrobe  —  содержимое гардероба
# ─────────────────────────────────────────────
@router.get("/", summary="Получить гардероб")
async def get_wardrobe(
    user = Depends(get_current_user_from_cookie),
    db:   AsyncSession = Depends(get_db),
):
    if not user:
        raise HTTPException(401, "Не авторизован")
    return await serialize_wardrobe(db, user.id)


# ─────────────────────────────────────────────
#  POST /api/wardrobe/add  —  из инвентаря → гардероб
# { "item_id": 123 }
# ─────────────────────────────────────────────
# routes/wardrobe.py
# ................................

# ─────────────────────────────────────────────
#  POST /api/wardrobe/add   —  инвентарь → гардероб
#  payload: { "item_id": <InventoryItem.id> }
# ─────────────────────────────────────────────
@router.post("/add", summary="Убрать предмет из инвентаря в гардероб")
async def add_to_wardrobe(
    payload: dict,
    user      = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db),
):
    """
    Перемещает **конкретный экземпляр** из user_inventory в user_pet_wardrobe_items.

    * `item_id` — это **InventoryItem.id** (не wardrobe_id, не product_id!).
    """
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





# ─────────────────────────────────────────────
#  POST /api/wardrobe/remove  —  из гардероба → инвентарь
# { "wardrobe_id": 55 }
# ─────────────────────────────────────────────
@router.post("/remove", summary="Вернуть предмет из гардероба")
async def remove_from_wardrobe(
    payload: dict,
    user = Depends(get_current_user_from_cookie),
    db:   AsyncSession = Depends(get_db),
):
    product_id = payload.get("product_id")
    qty        = payload.get("quantity", 1)

    if not product_id:
        raise HTTPException(400, "`product_id` обязателен")

    await move_from_wardrobe(db, user, int(product_id), int(qty))
    return await serialize_wardrobe(db, user.id)



