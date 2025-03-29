import json
import os
from fastapi import APIRouter, HTTPException, status, Body, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.models import ForumThread, ForumPost
from database import get_db
from config import Config

router = APIRouter(prefix="/api/forum", tags=["Forum"])

FORUM_THREADS_PATH = Config.FORUM_THREADS_PATH

async def load_threads_from_json(db: AsyncSession):
    """
    Загружает темы из JSON в базу при старте.
    Если файла нет – пишет в консоль об ошибке.
    """
    if not os.path.exists(FORUM_THREADS_PATH):
        print("❌ JSON-файл с темами не найден.")
        return
    
    with open(FORUM_THREADS_PATH, "r", encoding="utf-8") as file:
        threads_data = json.load(file)

    for thread_data in threads_data:
        result = await db.execute(select(ForumThread).where(ForumThread.title == thread_data["title"]))
        existing_thread = result.scalar()
        if not existing_thread:
            new_thread = ForumThread(
                title=thread_data["title"],
                description=thread_data["description"],
                views=thread_data.get("views", 0)
            )
            db.add(new_thread)
    
    await db.commit()
    print("✅ Темы из JSON загружены в базу.")

# ======================================================================
# МОДЕЛИ ДЛЯ ВХОДНЫХ ДАННЫХ
# ======================================================================
class CreateThreadRequest(BaseModel):
    title: str
    description: str
    views: int = 0

class CreatePostRequest(BaseModel):
    thread_id: int
    author: str
    content: str

# ======================================================================
# ЭНДПОИНТЫ
# ======================================================================

# ✅ Получить список всех тем форума
@router.get("/threads")
async def get_threads(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ForumThread).order_by(ForumThread.created_at.desc()))
    threads = result.scalars().all()
    threads_list = [thread.to_dict() for thread in threads]
    return JSONResponse(content=threads_list, status_code=status.HTTP_200_OK)

# ✅ Получить конкретную тему и её сообщения
@router.get("/{thread_id}")
async def get_thread(thread_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ForumThread).where(ForumThread.id == thread_id))
    thread = result.scalar()
    if not thread:
        raise HTTPException(status_code=404, detail="Тема не найдена")
    
    result = await db.execute(select(ForumPost).where(ForumPost.thread_id == thread_id).order_by(ForumPost.created_at))
    posts = result.scalars().all()
    
    response = {
        "thread": thread.to_dict(),
        "posts": [post.to_dict() for post in posts]
    }
    return JSONResponse(content=response, status_code=status.HTTP_200_OK)

# ✅ Создать новую тему (доступно всем)
@router.post("/create_thread", status_code=status.HTTP_201_CREATED)
async def create_thread(data: CreateThreadRequest, db: AsyncSession = Depends(get_db)):
    if not data.title:
        raise HTTPException(status_code=400, detail="Название темы обязательно")
    
    new_thread = ForumThread(title=data.title, description=data.description)
    db.add(new_thread)
    await db.commit()
    return JSONResponse(content=new_thread.to_dict(), status_code=status.HTTP_201_CREATED)

# ✅ Добавить пост в тему
@router.post("/post", status_code=status.HTTP_201_CREATED)
async def create_post(data: CreatePostRequest, db: AsyncSession = Depends(get_db)):
    if not (data.thread_id and data.author and data.content):
        raise HTTPException(status_code=400, detail="Заполните все поля")
    
    new_post = ForumPost(thread_id=data.thread_id, author=data.author, content=data.content)
    db.add(new_post)
    await db.commit()
    return JSONResponse(content=new_post.to_dict(), status_code=status.HTTP_201_CREATED)

# ✅ Получить статистику форума
@router.get("/stats")
async def get_forum_stats(db: AsyncSession = Depends(get_db)):
    total_threads = await db.execute(select(ForumThread))
    total_posts = await db.execute(select(ForumPost))
    
    total_threads = total_threads.scalars().count()
    total_posts = total_posts.scalars().count()
    
    top_users_result = await db.execute(
        select(ForumPost.author, db.func.count(ForumPost.id))
        .group_by(ForumPost.author)
        .order_by(db.func.count(ForumPost.id).desc())
        .limit(10)
    )
    top_users = top_users_result.all()
    
    stats = {
        "total_threads": total_threads,
        "total_posts": total_posts,
        "top_users": [{"name": user[0], "post_count": user[1]} for user in top_users]
    }
    return JSONResponse(content=stats, status_code=status.HTTP_200_OK)

# ✅ Создать новую тему (для админов)
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_threads(data: CreateThreadRequest, db: AsyncSession = Depends(get_db)):
    if not data.title or not data.description:
        raise HTTPException(status_code=400, detail="Название и описание обязательны!")
    
    new_thread = ForumThread(
        title=data.title,
        description=data.description,
        views=data.views
    )
    db.add(new_thread)
    await db.commit()
    return JSONResponse(
        content={"message": "Тема успешно создана!", "thread": new_thread.title},
        status_code=status.HTTP_201_CREATED
    )
