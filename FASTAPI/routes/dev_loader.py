from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from utils.shoputils import add_products_to_db

router = APIRouter(prefix="/dev", tags=["dev"])

@router.post("/load-products")
async def load_products(db: AsyncSession = Depends(get_db)):
    await add_products_to_db(db)
    return {"status": "✅ Товары загружены в базу!"}
