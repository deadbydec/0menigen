import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import insert, select, and_
from database import async_session
from models.models import VipSubscription, VipStatus


async def make_vip(user_id: int, status: VipStatus = VipStatus.NULLOVERLORD, days: int = 30):
    async with async_session() as db:
        try:
            now = datetime.now(timezone.utc)
            expires = now + timedelta(days=days)

            # Проверка: уже есть активная подписка?
            result = await db.execute(
                select(VipSubscription).where(
                    and_(
                        VipSubscription.user_id == user_id,
                        VipSubscription.is_active == True,
                        VipSubscription.expires_at > now
                    )
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                print(f"⚠️ У пользователя {user_id} уже есть активная подписка до {existing.expires_at}")
                return

            # Добавление новой
            await db.execute(insert(VipSubscription).values(
                user_id=user_id,
                status=status,
                started_at=now,
                expires_at=expires,
                is_active=True,
                source="donation",
                comment=None
            ))
            await db.commit()
            print(f"✅ Пользователю {user_id} выдана подписка {status.value} до {expires}")
        except Exception as e:
            await db.rollback()
            print("❌ Ошибка:", e)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("⚠️ Укажи user_id как аргумент")
    else:
        uid = int(sys.argv[1])
        asyncio.run(make_vip(uid))
