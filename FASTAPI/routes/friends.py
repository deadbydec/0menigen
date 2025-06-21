from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from auth.cookie_auth import get_current_user_from_cookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models.models import Friendship, User
from pydantic import BaseModel
from sqlalchemy import or_, and_
from utils.friendship_tools import accept_friend_request, remove_friend, get_friends, remove_friend
from sqlalchemy.orm import joinedload

router = APIRouter()

# ======================================================================
# Pydantic-модели для запросов
# ======================================================================
class FriendRequest(BaseModel):
    friend_id: int

class FriendActionRequest(BaseModel):
    request_id: int

class RemoveFriendRequest(BaseModel):
    friend_id: int

# ======================================================================
# ЭНДПОИНТЫ
# ======================================================================

# GET /api/friends/ - Получить список друзей текущего пользователя
@router.get("/list")
async def list_friends(
    current_user: User = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Friendship)
        .options(joinedload(Friendship.user), joinedload(Friendship.friend))
        .where(or_(Friendship.user_id == current_user.id, Friendship.friend_id == current_user.id))
    )
    friendships = result.scalars().all()

    friends = []
    for f in friendships:
        friend_user = f.friend if f.user_id == current_user.id else f.user
        if friend_user:
            friends.append({
                "id": friend_user.id,
                "username": friend_user.username,
                "avatar": friend_user.avatar
            })

    return friends  # 💡 FastAPI сам вернёт JSON, не надо JSONResponse


# POST /api/friends/add - Отправить запрос в друзья
@router.post("/add")
async def send_friend_request(data: FriendRequest, current_user: User = Depends(get_current_user_from_cookie)
, db: AsyncSession = Depends(get_db)):
    user_id = current_user.id
    friend_id = data.friend_id
    
    if user_id == friend_id:
        raise HTTPException(status_code=400, detail="Нельзя добавить себя в друзья")
    
    result = await db.execute(select(Friendship).where(Friendship.user_id == user_id, Friendship.friend_id == friend_id))
    existing_request = result.scalar()
    
    if existing_request:
        raise HTTPException(status_code=400, detail="Запрос уже отправлен")
    
    from utils.friendship_tools import add_friend

    await add_friend(user_id, friend_id, db)
    await db.commit()

    
    return JSONResponse(content={"message": "Запрос в друзья отправлен!"}, status_code=status.HTTP_200_OK)

# GET /api/friends/list - Получить список друзей (альтернативный эндпоинт)

# POST /api/friends/remove - Удалить друга из списка
@router.post("/remove")
async def handle_remove_friend(data: RemoveFriendRequest, current_user: User = Depends(get_current_user_from_cookie), db: AsyncSession = Depends(get_db)):
    user_id = current_user.id
    friend_id = data.friend_id

    result = await remove_friend(user_id, friend_id, db)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    await db.commit()
    return JSONResponse(content={"success": True, "message": result["message"]}, status_code=status.HTTP_200_OK)


# GET /api/friends/requests - Получить входящие запросы в друзья
@router.get("/requests")
async def get_friend_requests(current_user: User = Depends(get_current_user_from_cookie), db: AsyncSession = Depends(get_db)):
    user_id = current_user.id
    
    result = await db.execute(
        select(Friendship).where(Friendship.friend_id == user_id, Friendship.status == "pending")
    )
    requests_q = result.scalars().all()
    
    request_list = [
        {"id": req.id, "from_user": req.user.username, "user_id": req.user_id}
        for req in requests_q
    ]
    
    return JSONResponse(content=request_list, status_code=status.HTTP_200_OK)

# POST /api/friends/accept - Принять запрос в друзья
@router.post("/accept")
async def accept_request_handler(data: FriendActionRequest, current_user: User = Depends(get_current_user_from_cookie), db: AsyncSession = Depends(get_db)):
    user_id = current_user.id
    request_id = data.request_id
    
    
    result = await accept_friend_request(user_id, request_id, db)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    await db.commit()
    return JSONResponse(content={"message": result["message"]}, status_code=status.HTTP_200_OK)

# POST /api/friends/reject - Отклонить запрос в друзья
@router.post("/reject")
async def reject_friend_request(data: FriendActionRequest, current_user: User = Depends(get_current_user_from_cookie), db: AsyncSession = Depends(get_db)):
    user_id = current_user.id
    request_id = data.request_id
    
    result = await db.execute(select(Friendship).where(Friendship.id == request_id))
    friendship = result.scalar()
    
    if not friendship or friendship.friend_id != user_id:
        raise HTTPException(status_code=404, detail="Запрос не найден")
    
    await db.delete(friendship)
    await db.commit()
    
    return JSONResponse(content={"message": "Запрос отклонён!"}, status_code=status.HTTP_200_OK)

# GET /api/friends/status - Проверить статус дружбы с другим пользователем
@router.get("/status")
async def check_friend_status(
    friend_id: int = Query(...),
    current_user: User = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id

    if friend_id == user_id:
        return {"status": "none"}  # сам себе не друг

    result = await db.execute(
        select(Friendship)
        .where(
            or_(
                and_(Friendship.user_id == user_id, Friendship.friend_id == friend_id),
                and_(Friendship.user_id == friend_id, Friendship.friend_id == user_id)
            )
        )
    )
    friendship = result.scalar_one_or_none()

    if not friendship or not friendship.status:
        return {"status": "none"}

    return {"status": friendship.status}

@router.get("/public/{user_id}")
async def public_friend_list(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Friendship)
        .options(joinedload(Friendship.user), joinedload(Friendship.friend))
        .where(or_(Friendship.user_id == user_id, Friendship.friend_id == user_id))
    )
    friendships = result.scalars().all()

    friends = []
    for f in friendships:
        friend_user = f.friend if f.user_id == user_id else f.user
        if friend_user:
            friends.append({
                "id": friend_user.id,
                "username": friend_user.username,
                "avatar": friend_user.avatar
            })

    return friends







