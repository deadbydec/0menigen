import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

router = APIRouter()

# Определяем путь к фронтенду
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))

# ✅ Если папка существует – раздаём фронт, если нет – отдаём JSON-заглушку
if os.path.exists(frontend_path):
    router.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    print(f"⚠️ Папка фронтенда '{frontend_path}' не найдена! FastAPI будет отдавать заглушку.")

@router.get("/")
async def serve_index():
    """Отдаёт заглушку, если фронтенд не найден"""
    if not os.path.exists(frontend_path):
        return JSONResponse(content={"message": "Фронтенд не найден, но API работает!"})
    
    raise HTTPException(status_code=404, detail="Фронтенд ожидается в dist/, но его нет")

