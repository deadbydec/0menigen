from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from auth.cookie_auth import get_current_user_from_cookie
from sqlalchemy.future import select
from pydantic import BaseModel
from database import get_db
from datetime import datetime
from sqlalchemy.orm import joinedload

from models.models import PrivateMessage, User, SystemMessage

router = APIRouter()

class SendMessageRequest(BaseModel):
    recipient: str
    subject: str = ""
    content: str


@router.options("/send")
async def options_send():
    return JSONResponse(content={"ok": True})


@router.get("/")
async def get_inbox(
    user: User = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    # Получаем личные сообщения (PrivateMessage)
    private_result = await db.execute(
        select(PrivateMessage)
        .options(joinedload(PrivateMessage.sender))
        .where(PrivateMessage.recipient_id == user.id)
        .order_by(PrivateMessage.timestamp.desc())
    )
    private_messages = private_result.scalars().all()

    # Получаем системные сообщения (SystemMessage)
    system_result = await db.execute(
        select(SystemMessage)
        .where(SystemMessage.recipient_id == user.id)
        .order_by(SystemMessage.timestamp.desc())
    )
    system_messages = system_result.scalars().all()

    messages_list = []

    # Формируем список личных сообщений
    for msg in private_messages:
        messages_list.append({
            "id": msg.id,
            "sender": msg.sender.username if msg.sender else None,
            "subject": msg.subject,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
            "message_type": "private"
        })

    # Формируем список системных сообщений (например, подарков)
    for sysmsg in system_messages:
        messages_list.append({
            "id": sysmsg.id,
            "sender": "Система",
            "subject": sysmsg.title,
            "content": sysmsg.content,
            "timestamp": sysmsg.timestamp.isoformat() if sysmsg.timestamp else None,
            "message_type": sysmsg.message_type.lower(),  # например, "gift"
            "related_id": sysmsg.related_id
        })

    # Сортируем объединённый список по timestamp (от нового к старому)
    messages_list.sort(key=lambda x: x["timestamp"], reverse=True)

    return JSONResponse(content=messages_list, status_code=status.HTTP_200_OK)


# ======================================================================
# API Исходящих сообщений
# ======================================================================
@router.get("/sent")
async def get_sent(user: User = Depends(get_current_user_from_cookie), db: AsyncSession = Depends(get_db)):
    user_id = user.id
    
    result = await db.execute(
        select(PrivateMessage)
        .options(joinedload(PrivateMessage.recipient))
        .where(PrivateMessage.sender_id == user_id)
        .order_by(PrivateMessage.timestamp.desc())
    )
    messages = result.scalars().all()
    
    messages_list = [
        {
            "id": msg.id,
            "recipient": msg.recipient.username if msg.recipient else None,
            "subject": msg.subject,  # 🔥 ЭТО БЫЛО ПРОПУЩЕНО
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
        }
        for msg in messages
    ]
    return JSONResponse(content=messages_list, status_code=status.HTTP_200_OK)

# ======================================================================
# API Отправки сообщения
# ======================================================================
@router.post("/send")
async def send_message(
    data: SendMessageRequest,
    user: User = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    if not data.content.strip():
        raise HTTPException(status_code=400, detail="Сообщение не может быть пустым!")

    result = await db.execute(select(User).where(User.username == data.recipient))
    recipient = result.scalar()

    if not recipient:
        raise HTTPException(status_code=404, detail="Пользователь не найден!")

    new_message = PrivateMessage(
        sender_id=user.id,
        recipient_id=recipient.id,
        subject=data.subject,  # ← вот оно!
        content=data.content,
        timestamp=datetime.utcnow()
    )
    db.add(new_message)
    await db.commit()

    return JSONResponse(
        content={"success": "Сообщение отправлено!", "message_id": new_message.id},
        status_code=status.HTTP_200_OK
    )


# ======================================================================
# API Удаления сообщения
# ======================================================================
from auth.cookie_auth import get_current_user_from_cookie

@router.delete("/delete/{message_id}")
async def delete_message(
    message_id: int,
    user: User = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(PrivateMessage).where(PrivateMessage.id == message_id))
    message = result.scalar()

    if not message:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")

    # Проверяем, что текущий юзер — получатель или отправитель
    if message.recipient_id != user.id and message.sender_id != user.id:
        raise HTTPException(status_code=403, detail="Нет прав для удаления этого сообщения.")

    await db.delete(message)
    await db.commit()

    return JSONResponse(
        content={"success": "Сообщение удалено!"},
        status_code=status.HTTP_200_OK
    )

