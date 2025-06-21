# routes/npc_quests.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import random
import json

from database import get_db
from auth.cookie_auth import get_current_user_from_cookie
from models.models import DailyQuest, InventoryItem, User  # ✅ Убедись, что User есть в models
from utils.quests_tools import pick_random_item_from_store  # ✅ это твоя утиль-функция, добавь если ещё нет

router = APIRouter(prefix="/api/npc-quests", tags=["NPC Quests"])


# ─────────────────────────────────────────────
#  POST /npc-quests/ — создать дейлики от всех NPC
# ─────────────────────────────────────────────
@router.post("/", summary="Создать дейлики от всех NPC")
async def create_npc_quests(user=Depends(get_current_user_from_cookie),
                            db: AsyncSession = Depends(get_db)):
    now = datetime.utcnow()

    with open("data/npcs.json", "r", encoding="utf-8") as f:
        npc_list = json.load(f)

    new_quests = []

    for npc in npc_list:
        result = await db.execute(
            select(DailyQuest).where(
                DailyQuest.user_id == user.id,
                DailyQuest.npc_id == npc["id"],
                DailyQuest.created_at > now - timedelta(hours=24)
            )
        )
        if result.scalar():
            continue

        category = random.choice(npc["categories"])
        rarity = random.choices(list(npc["rarity_pool"].keys()), weights=npc["rarity_pool"].values())[0]
        item = pick_random_item_from_store(category, rarity)
        if not item:
            continue

        item_payload = {
            "item_id": item["id"],
            "category": item.get("product_type", category),  # если есть product_type
            "rarity": item["rarity"],
            "name": item["name"],
            "icon": item["icon"]
        }

        quest = DailyQuest(
            user_id=user.id,
            npc_id=npc["id"],
            item_requested=item_payload,
            created_at=now,
            expires_at=now + timedelta(minutes=30),
            completed=False,
            failed=False
        )

        db.add(quest)
        new_quests.append(quest)

    await db.commit()
    return {"new_quests": [q.item_requested for q in new_quests]}


# ─────────────────────────────────────────────
#  POST /npc-quests/accept?npc_id=...
# ─────────────────────────────────────────────
@router.post("/accept", summary="Принять квест у NPC")
async def accept_npc_quest(npc_id: str = Query(...),
                           user=Depends(get_current_user_from_cookie),
                           db: AsyncSession = Depends(get_db)):
    now = datetime.utcnow()

    result = await db.execute(
        select(DailyQuest).where(
            DailyQuest.user_id == user.id,
            DailyQuest.npc_id == npc_id,
            DailyQuest.created_at > now - timedelta(hours=24)
        )
    )
    today_quests = result.scalars().all()

    with open("data/npcs.json", "r", encoding="utf-8") as f:
        npcs = {n["id"]: n for n in json.load(f)}

    npc = npcs.get(npc_id)
    if not npc:
        raise HTTPException(404, detail="Такой NPC не найден")

    limit = npc.get("limit_per_day", 5)
    if len(today_quests) >= limit:
        raise HTTPException(400, detail="Лимит квестов исчерпан")

    category = random.choice(npc["categories"])
    rarity = random.choices(list(npc["rarity_pool"].keys()), weights=npc["rarity_pool"].values())[0]
    MAX_ATTEMPTS = 10
    item = None

    for _ in range(MAX_ATTEMPTS):
        item = pick_random_item_from_store(category, rarity)
        if item:
            break

    if not item:
        raise HTTPException(400, detail="NPC завис в раздумьях, не нашёл предмет")


    expires_at = now + timedelta(minutes=30)

    quest = DailyQuest(
        user_id=user.id,
        npc_id=npc_id,
        item_requested={"item_id": item["id"], "category": category, "rarity": rarity},
        created_at=now,
        expires_at=expires_at,
        completed=False,
        failed=False
    )
    db.add(quest)
    await db.commit()

    return {
        "message": "Квест принят",
        "expires_at": expires_at.isoformat(),
        "item": item
    }


class TurnInPayload(BaseModel):
    quest_id: int

# ─────────────────────────────────────────────
#  POST /npc-quests/turn-in — сдать квест
# ─────────────────────────────────────────────
@router.post("/turn-in", summary="Сдать квест NPC")
async def turn_in_quest(payload: TurnInPayload,
                        user=Depends(get_current_user_from_cookie),
                        db: AsyncSession = Depends(get_db)):
    quest = await db.get(DailyQuest, payload.quest_id)
    if not quest or quest.user_id != user.id:
        raise HTTPException(404, detail="Квест не найден")

    if quest.completed or quest.failed:
        raise HTTPException(400, detail="Этот квест уже завершён")

    now = datetime.utcnow()
    if now > quest.expires_at:
        quest.failed = True
        await db.commit()
        return {"status": "fail", "message": "Время вышло, квест провален"}

    # ✅ Проверка предмета в инвентаре
    item_id = quest.item_requested["item_id"]
    inv_q = await db.execute(
        select(InventoryItem).where(
            InventoryItem.user_id == user.id,
            InventoryItem.product_id == item_id
        )
    )
    inv_item = inv_q.scalar()
    if not inv_item:
        raise HTTPException(400, detail="У тебя нет нужного предмета")

    # ❌ Удаляем предмет
    await db.delete(inv_item)
    quest.completed = True

    # 📦 Награда
    with open("data/npcs.json", "r", encoding="utf-8") as f:
        npc_data = {n["id"]: n for n in json.load(f)}
    npc = npc_data.get(quest.npc_id, {})

    reward = npc.get("reward_on_success", {})
    xp = random.randint(reward.get("xp", {}).get("min", 0), reward.get("xp", {}).get("max", 0))
    coins = random.randint(reward.get("coins", {}).get("min", 0), reward.get("coins", {}).get("max", 0))

    await user.add_xp(db, xp)
    user.coins += coins

    db.add(user)  # 👈 ОБЯЗАТЕЛЬНО, иначе не сохранит изменения

    # 🎁 Шанс special-подарков
    extra = {}

    for key, chance in reward.items():
        if key.startswith("special_") and isinstance(chance, (float, int)) and chance > 0:
            category = key.replace("special_", "").replace("_chance", "")
            if random.random() < chance:
                special = pick_random_item_from_store(category, "special")
                if special:
                    db.add(InventoryItem(
                        user_id=user.id,
                        product_id=special["id"]
                    ))
                    extra[category] = {
                        "id": special["id"],
                        "name": special["name"],
                        "icon": special["icon"]
                    }

    await db.commit()
    return {
        "status": "ok",
        "xp": xp,
        "coins": coins,
        "extra": extra
    }




# ─────────────────────────────────────────────
#  GET /npc-quests/list — получить всех NPC
# ─────────────────────────────────────────────
@router.get("/list", summary="Список всех NPC-квестодателей")
async def get_npc_list():
    with open("data/npcs.json", "r", encoding="utf-8") as f:
        npc_list = json.load(f)
    return npc_list  # ❗️возвращаем весь JSON, ничего не обрезаем



# ─────────────────────────────────────────────
#  GET /npc-quests/my — получить текущие квесты игрока
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
#  GET /npc-quests/my — получить текущие квесты игрока
# ─────────────────────────────────────────────
@router.get("/my", summary="Мои активные квесты")
async def get_my_active_quests(user=Depends(get_current_user_from_cookie),
                               db: AsyncSession = Depends(get_db)):
    now = datetime.utcnow()

    result = await db.execute(
        select(DailyQuest).where(
            DailyQuest.user_id == user.id,
            DailyQuest.created_at > now - timedelta(hours=24)
        )
    )
    quests = result.scalars().all()

    # 🧨 Фейлим истёкшие
    updated = False
    for quest in quests:
        if not quest.completed and not quest.failed and quest.expires_at < now:
            quest.failed = True
            updated = True

    if updated:
        await db.commit()

    with open("data/products.json", "r", encoding="utf-8") as f:
        products = {p["id"]: p for p in json.load(f)}

    return [
        {
            "id": q.id,
            "npc_id": q.npc_id,
            "item": {
                **q.item_requested,
                **(products.get(q.item_requested["item_id"], {}))  # 🔥 добавляем name и icon
            },
            "completed": q.completed,
            "failed": q.failed,
            "expires_at": q.expires_at.isoformat()
        }
        for q in quests
    ]




