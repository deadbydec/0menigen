from models.models import InventoryItem, Incubation
from typing import Optional, Dict
from fastapi import HTTPException

def build_inventory_item(item: InventoryItem) -> Dict:
    incubation: Optional[Incubation] = (
        item.incubation if item.incubation and not item.incubation.is_hatched else None
    )

    return {
        "id": item.id,
        "name": item.product.name,
        "type": item.product.product_type.value,
        "image": item.product.image,
        "rarity": item.product.rarity.value,
        "state": item.state,  # ← 💥 ДОБАВЬ ЭТУ СТРОКУ
        "quantity": item.quantity,
        "incubation": (
            {
                "started_at": incubation.started_at.isoformat(),
                "hatch_at": incubation.hatch_at.isoformat(),
                "is_hatched": incubation.is_hatched,
            } if incubation else None
        ),
        "product_id": item.product.id,  # 🔥 ВОТ ЭТА СТРОКА — ДОБАВЬ ЕЁ
        "product": {
            "name": item.product.name,
            "image": item.product.image,
            "description": item.product.description,
            "rarity": item.product.rarity.value,
            "product_type": item.product.product_type.value,
            "types": item.product.types or [],  # ✅ ВОТ ЭТО
        },
    }

# 🔒 Проверка предмета
def assert_item_unlocked(item: InventoryItem):
    if item.state in {"locked", "equipped", "safe", "auction"}:
        raise HTTPException(403, detail="Этот предмет сейчас недоступен (заблокирован).")
