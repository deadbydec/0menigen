import os
import json
import time
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from auth.cookie_auth import get_token_from_cookie, decode_access_token
from sqlalchemy.future import select
from database import get_db, async_session
from models.models import User
from PIL import Image
from config import Config
from utils.last_seen import is_user_online
from pydantic import BaseModel

router = APIRouter()

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
MAX_AVATAR_SIZE = (300, 300)

class BioUpdate(BaseModel):
    bio: str

# ✅ Функция проверки допустимых файлов
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ API для загрузки аватарки
@router.post("/upload-avatar")
async def upload_avatar(
    request: Request,
    avatar: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    token = get_token_from_cookie(request)
    payload = decode_access_token(token)
    user_id = int(payload.get("sub"))

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    UPLOAD_FOLDER = Config.UPLOAD_FOLDER

    # ✅ Проверяем файл
    if not allowed_file(avatar.filename):
        raise HTTPException(status_code=400, detail="Недопустимый формат")

    # ✅ Генерируем имя файла
    ext = avatar.filename.rsplit(".", 1)[1].lower()
    filename = f"{user_id}_{int(time.time())}.{ext}"
    save_path = os.path.join(UPLOAD_FOLDER, filename)

    # ✅ Создаём папку, если её нет
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # ✅ Обрабатываем изображение
    img = Image.open(avatar.file)
    img = img.convert("RGB")  # 🔥 Фикс для PNG и GIF
    img.thumbnail(MAX_AVATAR_SIZE)  # 🔥 Уменьшаем до 300x300
    img.save(save_path)

    # ✅ Обновляем БД
    user.avatar = f"/api/profile/avatars/{filename}"
    await db.commit()

    return {"avatarUrl": user.avatar}


# ✅ API для редактирования био
@router.post("/edit_bio")
async def edit_bio(
    data: BioUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    token = get_token_from_cookie(request)
    payload = decode_access_token(token)
    user_id = int(payload.get("sub"))

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if len(data.bio.strip()) > 500:
        raise HTTPException(status_code=400, detail="Текст слишком длинный")

    user.bio = data.bio.strip()
    await db.commit()

    return {"success": True, "bio": user.bio}


