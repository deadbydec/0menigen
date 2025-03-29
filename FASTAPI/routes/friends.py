from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models.models import Friendship, User
from pydantic import BaseModel
from sqlalchemy import or_, and_

router = APIRouter(prefix="/api/friends", tags=["Friends"])

jwt_access = JwtAccessBearer(secret_key="supersecretkey")

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
@router.get("/")
async def get_friends(credentials: JwtAuthorizationCredentials = Depends(jwt_access), db: AsyncSession = Depends(get_db)):
    user_id = int(credentials.subject["user_id"])
    
    result = await db.execute(
        select(Friendship).where(or_(Friendship.user_id == user_id, Friendship.friend_id == user_id))
    )
    friendships = result.scalars().all()
    
    friends_list = []
    for friendship in friendships:
        # Определяем, кто из участников – друг текущего юзера
        friend = friendship.friend if friendship.user_id == user_id else friendship.user
        friends_list.append({
            "id": friend.id,
            "username": friend.username,
            "avatar": friend.avatar or "/default-avatar.png"
        })
    
    return JSONResponse(content=friends_list, status_code=status.HTTP_200_OK)

# POST /api/friends/add - Отправить запрос в друзья
@router.post("/add")
async def send_friend_request(data: FriendRequest, credentials: JwtAuthorizationCredentials = Depends(jwt_access), db: AsyncSession = Depends(get_db)):
    user_id = int(credentials.subject["user_id"])
    friend_id = data.friend_id
    
    if user_id == friend_id:
        raise HTTPException(status_code=400, detail="Нельзя добавить себя в друзья")
    
    result = await db.execute(select(Friendship).where(Friendship.user_id == user_id, Friendship.friend_id == friend_id))
    existing_request = result.scalar()
    
    if existing_request:
        raise HTTPException(status_code=400, detail="Запрос уже отправлен")
    
    friendship = Friendship(user_id=user_id, friend_id=friend_id, status="pending")
    db.add(friendship)
    await db.commit()
    
    return JSONResponse(content={"message": "Запрос в друзья отправлен!"}, status_code=status.HTTP_200_OK)

# GET /api/friends/list - Получить список друзей (альтернативный эндпоинт)
@router.get("/list")
async def list_friends(credentials: JwtAuthorizationCredentials = Depends(jwt_access), db: AsyncSession = Depends(get_db)):
    user_id = int(credentials.subject["user_id"])
    
    result = await db.execute(
        select(Friendship).where(or_(Friendship.user_id == user_id, Friendship.friend_id == user_id))
    )
    friendships = result.scalars().all()
    
    friends_list = []
    for friendship in friendships:
        friend = friendship.friend if friendship.user_id == user_id else friendship.user
        friends_list.append({
            "id": friend.id,
            "username": friend.username,
            "avatar_url": friend.avatar
        })
    
    return JSONResponse(content=friends_list, status_code=status.HTTP_200_OK)

# POST /api/friends/remove - Удалить друга из списка
@router.post("/remove")
async def remove_friend(data: RemoveFriendRequest, credentials: JwtAuthorizationCredentials = Depends(jwt_access), db: AsyncSession = Depends(get_db)):
    user_id = int(credentials.subject["user_id"])
    friend_id = data.friend_id
    
    result = await db.execute(
        select(Friendship).where(
            or_(
                and_(Friendship.user_id == user_id, Friendship.friend_id == friend_id),
                and_(Friendship.user_id == friend_id, Friendship.friend_id == user_id)
            )
        )
    )
    friendship = result.scalar()
    
    if not friendship:
        raise HTTPException(status_code=400, detail="Вы не друзья")
    
    await db.delete(friendship)
    await db.commit()
    
    return JSONResponse(content={"success": True, "message": "Друг удален!"}, status_code=status.HTTP_200_OK)

# GET /api/friends/requests - Получить входящие запросы в друзья
@router.get("/requests")
async def get_friend_requests(credentials: JwtAuthorizationCredentials = Depends(jwt_access), db: AsyncSession = Depends(get_db)):
    user_id = int(credentials.subject["user_id"])
    
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
async def accept_friend_request(data: FriendActionRequest, credentials: JwtAuthorizationCredentials = Depends(jwt_access), db: AsyncSession = Depends(get_db)):
    user_id = int(credentials.subject["user_id"])
    request_id = data.request_id
    
    result = await db.execute(select(Friendship).where(Friendship.id == request_id))
    friendship = result.scalar()
    
    if not friendship or friendship.friend_id != user_id:
        raise HTTPException(status_code=404, detail="Запрос не найден")
    
    friendship.status = "accepted"
    await db.commit()
    
    return JSONResponse(content={"message": "Вы теперь друзья!"}, status_code=status.HTTP_200_OK)

# POST /api/friends/reject - Отклонить запрос в друзья
@router.post("/reject")
async def reject_friend_request(data: FriendActionRequest, credentials: JwtAuthorizationCredentials = Depends(jwt_access), db: AsyncSession = Depends(get_db)):
    user_id = int(credentials.subject["user_id"])
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
    friend_id: int = Query(..., description="ID другого пользователя"),
    credentials: JwtAuthorizationCredentials = Depends(jwt_access),
    db: AsyncSession = Depends(get_db)
):
    user_id = int(credentials.subject["user_id"])
    
    result = await db.execute(
        select(Friendship).where(
            or_(
                and_(Friendship.user_id == user_id, Friendship.friend_id == friend_id),
                and_(Friendship.user_id == friend_id, Friendship.friend_id == user_id)
            )
        )
    )
    friendship = result.scalar()
    
    if not friendship:
        return {"status": "none"}
    
    return {"status": friendship.status}
