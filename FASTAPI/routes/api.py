from fastapi import APIRouter
from auth import router as auth_router
from chat import router as chat_router
from profile import router as profile_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(chat_router, prefix="/chat", tags=["chat"])
router.include_router(profile_router, prefix="/profile", tags=["profile"])

@router.get("/ping")
def ping():
    return {"msg": "pong"}