
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



