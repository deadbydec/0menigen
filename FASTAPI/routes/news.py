import json
import os
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Query, Body, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from config import Config
from auth.cookie_auth import get_current_user_from_cookie

router = APIRouter()

# 🔄 Загружаем новости через API
def load_news():
    try:
        with open(Config.NEWS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# 💾 Функция сохранения новостей
def save_news(news_list):
    with open(Config.NEWS_FILE, "w", encoding="utf-8") as file:
        json.dump(news_list, file, ensure_ascii=False, indent=4)

# 🔍 Фильтруем и сортируем новости по дате (от новых к старым)
def get_sorted_news(category: str = None):
    news_list = load_news()
    try:
        sorted_news = sorted(
            news_list,
            key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"),
            reverse=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при сортировке новостей"
        )
    
    if category and category != "Все":
        sorted_news = [news for news in sorted_news if news["category"] == category]
    
    return sorted_news

# ✅ API для получения новостей с опциональной фильтрацией по категории
@router.get("/", response_model=list)
async def get_news(
    request: Request,
    user = Depends(get_current_user_from_cookie),
    category: str = Query(default=None)
):
    if not user:
        print("🔒 Пользователь не авторизован или токен сломан")
        raise HTTPException(status_code=401, detail="Кармик Коала: доступ только с кукой")

    print(f"🔐 Авторизованный юзер: {user.username}")
    return get_sorted_news(category)



# 🔥 API для лайков
@router.post("/{news_id}/like")
def like_news(news_id: int):
    news_list = load_news()
    news_item = None
    for news in news_list:
        if news["id"] == news_id:
            news["likes"] += 1
            news_item = news
            break
    if news_item is None:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    
    save_news(news_list)
    return {"status": "success", "likes": news_item["likes"]}

# Модель для комментария
class CommentRequest(BaseModel):
    author: str = "Аноним"
    text: str

# 💬 API для добавления комментария к новости
@router.post("/{news_id}/comment")
def add_comment(news_id: int, comment: CommentRequest):
    if not comment.text.strip():
        raise HTTPException(status_code=400, detail="Пустой комментарий")
    
    news_list = load_news()
    news_item = None
    for news in news_list:
        if news["id"] == news_id:
            # Инициализируем комментарии, если их ещё нет
            if "comments" not in news:
                news["comments"] = []
            news["comments"].append({"author": comment.author, "text": comment.text})
            news_item = news
            break
    if news_item is None:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    
    save_news(news_list)
    return {"status": "success", "comments": news_item.get("comments", [])}
