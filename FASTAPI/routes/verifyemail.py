from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import User
from utils.confirm_email import send_confirmation_email  # Импортируем функцию

router = APIRouter(prefix="/verifyemail", tags=["Email Verification"])

@router.get("/send")
async def send_verification_email(user_id: int, db: AsyncSession = Depends(get_db)):
    """Отправить письмо для подтверждения email"""

    # Найди пользователя по ID
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Отправка email
    await send_confirmation_email(
        user=user,
        db=db,
        base_url="http://localhost:5002"  # твой URL
    )

    return {"message": "Письмо отправлено для подтверждения email"}

