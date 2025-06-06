from uuid import uuid4
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User  # путь адаптируй под свой проект
from config import MAIL_CONF  # заранее настрой CONF или передавай конфиг в аргументе

async def send_confirmation_email(user: User, db: AsyncSession, base_url: str):
    token = str(uuid4())
    user.email_token = token
    await db.commit()

    confirm_link = f"{base_url}/verify-email?token={token}"
    message = MessageSchema(
    subject="Подтверждение Email",
    recipients=[user.email],
    body=f"""
        <h3>Привет, {user.username}!</h3>
        <p>Чтобы завершить регистрацию, подтвердите свою почту:</p>
        <a href="{confirm_link}">Подтвердить Email</a>
    """,
    subtype="html"
)

    fm = FastMail(MAIL_CONF)
    await fm.send_message(message)

