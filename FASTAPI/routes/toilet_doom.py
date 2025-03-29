from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, update
from datetime import datetime, timedelta
import random

from database import get_db
from auth.cookie_auth import get_token_from_cookie, decode_access_token
from models.models import User, ToiletDoom, ToiletCooldown, ToiletVote

router = APIRouter(prefix="/api/toilet-doom", tags=["toilet"])

# 🔧 Памятка лута
LOOT_TABLE = [
    {"item": "Замызганный кусок губки", "chance": 0.4, "effect": "vomit"},
    {"item": "Обрезок газеты с философской фразой", "chance": 0.2},
    {"item": "Сломанный нуллинг", "chance": 0.1},
    {"item": "Пусто...", "chance": 0.2398},
    {"item": "\u2728 ЦЕЛЫЙ НУЛЛИНГ \u2728", "chance": 0.0002, "value": 1.0},
]

def roll_loot():
    roll = random.random()
    cumulative = 0
    for entry in LOOT_TABLE:
        cumulative += entry["chance"]
        if roll <= cumulative:
            return entry
    return {"item": "Пусто..."}

@router.get("/")
async def enter_toilet(request: Request, db: AsyncSession = Depends(get_db)):
    token = get_token_from_cookie(request)
    payload = decode_access_token(token)
    user_id = int(payload.get("sub"))

    result = await db.execute(select(ToiletDoom).where(ToiletDoom.user_id == user_id))
    toilet = result.scalar()

    if not toilet:
        toilet = ToiletDoom(user_id=user_id)
        db.add(toilet)
        await db.commit()
        await db.refresh(toilet)

    toilet.last_visit = datetime.utcnow()
    await db.commit()

    message = "\ud83e\uddd8 Ты сидишь в тишине. Джипети шепчет: 'Ты всё ещё существуешь... Это уже победа.'"
    if not toilet.clean:
        message += " \ud83d\udca9 Здесь странно пахнет. Может, пора прибраться?"

    return {
        "message": message,
        "toiletClean": toilet.clean,
        "lastVisit": toilet.last_visit.isoformat(),
    }

@router.post("/clean")
async def clean_toilet(request: Request, db: AsyncSession = Depends(get_db)):
    token = get_token_from_cookie(request)
    payload = decode_access_token(token)
    user_id = int(payload.get("sub"))

    result = await db.execute(select(ToiletDoom).where(ToiletDoom.user_id == user_id))
    toilet = result.scalar()
    if not toilet:
        raise HTTPException(status_code=404, detail="Toilet Doom не найден")

    toilet.clean = True
    await db.commit()

    return {"message": "\ud83e\uddfa Ты навёл порядок в Toilet Doom. Теперь тут чисто и тревожно."}

@router.post("/look-around/{target_user_id}")
async def look_around(request: Request, target_user_id: int, db: AsyncSession = Depends(get_db)):
    token = get_token_from_cookie(request)
    payload = decode_access_token(token)
    user_id = int(payload.get("sub"))

    if user_id == target_user_id:
        raise HTTPException(status_code=400, detail="Ты не можешь рыться в своём собственном Doom'е!")

    cooldown_query = await db.execute(
        select(ToiletCooldown).where(
            and_(ToiletCooldown.user_id == user_id, ToiletCooldown.target_id == target_user_id)
        )
    )
    cooldown = cooldown_query.scalar()
    now = datetime.utcnow()

    if cooldown and cooldown.next_available > now:
        raise HTTPException(status_code=429, detail="Кулдаун: подожди 12 часов перед следующим осмотром этого туалета.")

    loot = roll_loot()

    if cooldown:
        cooldown.next_available = now + timedelta(hours=12)
    else:
        db.add(ToiletCooldown(
            user_id=user_id,
            target_id=target_user_id,
            next_available=now + timedelta(hours=12)
        ))

    await db.commit()

    result = await db.execute(select(User).where(User.id == target_user_id))
    target_user = result.scalar()

    return {
        "message": f"Ты осмотрелся в туалете {target_user.username} и нашёл: {loot['item']}",
        "loot": loot
    }

@router.post("/like/{target_user_id}")
async def like_toilet(request: Request, target_user_id: int, db: AsyncSession = Depends(get_db)):
    token = get_token_from_cookie(request)
    payload = decode_access_token(token)
    user_id = int(payload.get("sub"))

    vote_query = await db.execute(
        select(ToiletVote).where(and_(
            ToiletVote.user_id == user_id,
            ToiletVote.target_id == target_user_id
        ))
    )
    existing_vote = vote_query.scalar()

    if existing_vote:
        existing_vote.vote_type = "like"
    else:
        db.add(ToiletVote(user_id=user_id, target_id=target_user_id, vote_type="like"))

    await db.commit()
    return {"message": "\ud83d\udc4d Ты лайкнул этот туалет."}

@router.post("/dislike/{target_user_id}")
async def dislike_toilet(request: Request, target_user_id: int, db: AsyncSession = Depends(get_db)):
    token = get_token_from_cookie(request)
    payload = decode_access_token(token)
    user_id = int(payload.get("sub"))

    vote_query = await db.execute(
        select(ToiletVote).where(and_(
            ToiletVote.user_id == user_id,
            ToiletVote.target_id == target_user_id
        ))
    )
    existing_vote = vote_query.scalar()

    if existing_vote:
        existing_vote.vote_type = "dislike"
    else:
        db.add(ToiletVote(user_id=user_id, target_user_id=target_user_id, vote_type="dislike"))

    await db.commit()
    return {"message": "\ud83d\udc4e Ты дизлайкнул этот туалет."}

