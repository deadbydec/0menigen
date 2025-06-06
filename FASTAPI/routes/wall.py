import json
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from fastapi import Query
from sqlalchemy.exc import IntegrityError

from database import get_db
from auth.cookie_auth import get_current_user_from_cookie
from models.models import User, WallPost, Friendship, WallComment, WallLike

router = APIRouter()

class AddWallPostRequest(BaseModel):
    text: str
    target_user_id: Optional[int] = None  # если не указан — значит пишет себе


class AddCommentRequest(BaseModel):
    text: str

# ✅ Этот код уже правильный:
# просто оставляем возможность указать чью стену:
@router.get("/")
async def get_wall_posts(
    target_user_id: Optional[int] = Query(None),
    user: User = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(WallPost)
        .options(selectinload(WallPost.user), selectinload(WallPost.likes))
        .where(WallPost.user_id == target_user_id)
        .order_by(WallPost.created_at.desc())
    )
    posts = result.scalars().all()

    return [
        {
            "id": p.id,
            "text": p.text,
            "created_at": p.created_at,
            "likes": len(p.likes),
            "liked_by_me": any(l.user_id == user.id for l in p.likes),
            "author": {
                "id": p.user.id,
                "username": p.user.username
            }
        }
        for p in posts
    ]


@router.post("/add")
async def add_wall_post(
    data: AddWallPostRequest,
    user: User = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    target_id = data.target_user_id or user.id

    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Текст записи обязателен")

    # ⛔ если игрок пишет не себе — проверяем дружбу
    if target_id != user.id:
        result = await db.execute(
            select(Friendship).where(
                ((Friendship.user_id == user.id) & (Friendship.friend_id == target_id)) |
                ((Friendship.user_id == target_id) & (Friendship.friend_id == user.id)),
                Friendship.status == "accepted"
            )
        )
        if not result.scalar():
            raise HTTPException(status_code=403, detail="Можно писать только себе или друзьям")

    # ⬇ создаём запись на стене
    new_post = WallPost(user_id=target_id, text=data.text)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    await db.refresh(new_post, attribute_names=["user"])

    return {
        "id": new_post.id,
        "text": new_post.text,
        "created_at": new_post.created_at,
        "likes": 0,
        "liked_by_me": False,
        "author": {
            "id": user.id,
            "username": user.username
        }
    }


@router.post("/{post_id}/like")
async def like_post(
    post_id: int,
    user: User = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(WallPost).options(selectinload(WallPost.likes)).where(WallPost.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    existing = next((l for l in post.likes if l.user_id == user.id), None)

    if existing:
        await db.delete(existing)
        await db.commit()
        return {"likes": len(post.likes) - 1, "liked_by_me": False}

    like = WallLike(post_id=post.id, user_id=user.id)
    db.add(like)

    try:
        await db.commit()
        return {"likes": len(post.likes) + 1, "liked_by_me": True}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Вы уже лайкнули этот пост")


@router.get("/{post_id}/comments")
async def get_comments(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(WallComment)
        .options(selectinload(WallComment.user))
        .where(WallComment.post_id == post_id)
        .order_by(WallComment.created_at.desc())
    )
    comments = result.scalars().all()

    return [
        {
            "id": c.id,
            "text": c.text,
            "created_at": c.created_at,
            "author": {
                "id": c.user.id,
                "username": c.user.username
            } if c.user else None
        }
        for c in comments
    ]


