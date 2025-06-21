from models.models import InventoryItem, Incubation
from typing import Optional, Dict

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
