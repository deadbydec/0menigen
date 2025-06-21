from models.models import SystemMessageType
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional
from sqlalchemy import select, or_
from models.models import Friendship
from sqlalchemy.orm import joinedload


async def get_friends(user_id: int, db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Friendship)
        .options(joinedload(Friendship.user), joinedload(Friendship.friend))
        .where(
            or_(
                Friendship.user_id == user_id,
                Friendship.friend_id == user_id
            )
        )
    )

    friendships = result.scalars().all()

    return [
        {
            "id": f.friend.id if f.user_id == user_id else f.user.id,
            "username": f.friend.username if f.user_id == user_id else f.user.username,
            "avatar": f.friend.avatar if f.user_id == user_id else f.user.avatar
        }
        for f in friendships
        if (f.friend and f.user)  # 💥 гарантируем, что .user и .friend существуют
    ]

async def send_system_message(
    db: AsyncSession,
    recipient_id: int,
    message_type: SystemMessageType,
    title: str,
    content: str,
    related_id: Optional[int] = None,
    mark_unread: bool = True,
):
    
    from models.models import SystemMessage

    msg = SystemMessage(
        recipient_id=recipient_id,
        message_type=message_type,
        title=title,
        content=content,
        related_id=related_id,
        is_read=not mark_unread,
        timestamp=datetime.utcnow()
    )
    db.add(msg)
    # ВАЖНО: НЕ коммить здесь, если вызываешь изнутри бизнес-логики сессии
    # commit вызывается уже в методах `add_friend` и т.д.

async def get_friends(user_id: int, db: AsyncSession):
    result = await db.execute(
        select(Friendship).where(
            Friendship.user_id == user_id,
            Friendship.status == "accepted"
        )
    )
    return result.scalars().all()


async def add_friend(user_id: int, friend_id: int, db: AsyncSession):
    new_friendship = Friendship(user_id=user_id, friend_id=friend_id, status="pending")
    db.add(new_friendship)

    await send_system_message(
        db=db,
        recipient_id=friend_id,
        message_type=SystemMessageType.FRIEND_REQUEST,
        title="👥 Запрос в друзья",
        content=f"Пользователь с ID {user_id} хочет добавить тебя в друзья.",
        related_id=user_id
    )


async def accept_friend_request(user_id: int, friend_id: int, db: AsyncSession):
    result = await db.execute(
        select(Friendship).where(
            Friendship.user_id == friend_id,
            Friendship.friend_id == user_id,
            Friendship.status == "pending"
        )
    )
    friendship = result.scalar_one_or_none()

    if friendship:
        friendship.status = "accepted"

        await send_system_message(
            db=db,
            recipient_id=friend_id,
            message_type=SystemMessageType.FRIEND_ACCEPTED,
            title="✅ Дружба принята",
            content=f"Пользователь с ID {user_id} принял твой запрос в друзья.",
            related_id=user_id
        )

        return {"message": "Друг добавлен!"}

    return {"error": "Запрос не найден!"}


async def remove_friend(user_id: int, friend_id: int, db: AsyncSession):
    try:
        result = await db.execute(
            select(Friendship).where(
                or_(
                    (Friendship.user_id == user_id) & (Friendship.friend_id == friend_id),
                    (Friendship.user_id == friend_id) & (Friendship.friend_id == user_id)
                )
            )
        )
        friendship = result.scalar_one_or_none()

        if friendship:
            try:
                await send_system_message(
                    db=db,
                    recipient_id=friend_id,
                    message_type=SystemMessageType.FRIEND_CANCELLED,
                    title="💔 Дружба разорвана",
                    content=f"Пользователь с ID {user_id} удалил тебя из друзей.",
                    related_id=user_id
                )
            except Exception as sm_err:
                print(f"⚠️ Ошибка при отправке system message: {sm_err}")

            await db.delete(friendship)
            await db.commit()  # 🔥 обязательно

            print(f"[FRIEND_REMOVED] user {user_id} удалил друга {friend_id}")
            return {"message": "Друг удалён!"}

        return {"error": "Друг не найден!"}
    
    except Exception as e:
        print(f"🔥 Ошибка в remove_friend: {e}")
        return {"error": "Ошибка при удалении друга"}
