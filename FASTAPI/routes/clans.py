from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from datetime import datetime, timezone
from auth.cookie_auth import get_current_user_from_cookie
from database import get_db
from models.models import User, VipSubscription, Clan, ClanMember
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlalchemy import func, desc
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/clans", tags=["Clans"])

# 🧠 Получить список всех кланов (позже добавим фильтры, пагинацию и т.д.)

@router.get("/")
async def list_clans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            Clan.id,
            Clan.name,
            Clan.avatar_url,
            Clan.description,
            Clan.level,
            Clan.xp,
            func.count(ClanMember.id).label("member_count")
        )
        .outerjoin(ClanMember)
        .group_by(Clan.id)
    )
    rows = result.all()

    return [
        {
            "id": r.id,
            "name": r.name,
            "avatar_url": r.avatar_url,
            "description": r.description,
            "level": r.level,
            "xp": r.xp,
            "member_count": r.member_count
        }
        for r in rows
    ]

# 👤 Получить список кланов, в которых состоит игрок
@router.get("/my")
async def my_clans(user=Depends(get_current_user_from_cookie), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Clan)
        .join(ClanMember)
        .where(ClanMember.user_id == user.id)
    )
    clans = result.scalars().all()
    return [{"id": c.id, "name": c.name, "level": c.level} for c in clans]


class ClanCreateRequest(BaseModel):
    name: str = Field(..., max_length=20)
    avatar_url: str = ""
    description: str = ""
    is_private: bool = True  # ✅ по умолчанию закрытый клан


@router.post("/create")
async def create_clan(data: ClanCreateRequest, user=Depends(get_current_user_from_cookie), db: AsyncSession = Depends(get_db)):
    # 1. Проверка: уже состоит в 2 кланах?
    result = await db.execute(
        select(ClanMember).where(ClanMember.user_id == user.id)
    )
    existing = result.scalars().all()
    if len(existing) >= 2:
        raise HTTPException(status_code=400, detail="Нельзя состоять более чем в 2 кланах")

    # 2. Проверка уровня или подписки
    now = datetime.now(timezone.utc)
    vip_q = await db.execute(
        select(VipSubscription).where(
            and_(
                VipSubscription.user_id == user.id,
                VipSubscription.is_active == True,
                VipSubscription.expires_at > now
            )
        )
    )
    vip = vip_q.scalar_one_or_none()

    if user.level < 100 and not vip:
        raise HTTPException(status_code=403, detail="Нужно 100+ уровень или VIP-подписка для создания клана")

    # 3. Создание клана
    new_clan = Clan(
        name=data.name.strip(),
        avatar_url=data.avatar_url.strip(),
        description=data.description.strip(),
        leader_id=user.id,
        is_private=data.is_private
    )
    db.add(new_clan)
    try:
        await db.flush()  # Получаем ID
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Клан с таким именем уже существует")

    # 4. Добавить в участники (автоматически)
    member = ClanMember(
        clan_id=new_clan.id,
        user_id=user.id,
        can_withdraw=True
    )
    db.add(member)
    await db.commit()

    return {"success": True, "clan_id": new_clan.id, "message": "Клан создан успешно"}

@router.get("/stats")
async def clan_stats(db: AsyncSession = Depends(get_db)):
    one_week_ago = datetime.utcnow() - timedelta(days=7)

    total = await db.scalar(select(func.count()).select_from(Clan))
    new = await db.scalar(select(func.count()).select_from(Clan).where(Clan.created_at >= one_week_ago))

    # Клан с самым высоким уровнем
    top_level_clan = (await db.execute(
        select(Clan).order_by(desc(Clan.level), desc(Clan.xp)).limit(1)
    )).scalar()

    # Клан с наибольшим XP за неделю
    top_xp_week = (await db.execute(
        select(Clan).order_by(desc(Clan.xp_this_week)).limit(1)
    )).scalar()

    # Самый массовый клан

    top_members = (await db.execute(
        select(Clan)
        .options(selectinload(Clan.members))
    )).scalars().all()
    most_members = max(top_members, key=lambda c: len(c.members)) if top_members else None

    def serialize(clan):
        return {
            "id": clan.id,
            "name": clan.name,
            "level": clan.level,
            "avatar_url": clan.avatar_url
        } if clan else None

    return {
        "total_clans": total,
        "new_this_week": new,
        "top_by_level": serialize(top_level_clan),
        "top_by_xp_week": serialize(top_xp_week),
        "most_members": {
            **serialize(most_members),
            "member_count": len(most_members.members)
        } if most_members else None
    }
