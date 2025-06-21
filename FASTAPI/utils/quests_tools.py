# utils/npc_utils.py
import json
import random

def pick_random_item_from_store(category: str, rarity: str) -> dict | None:
    with open("data/products.json", "r", encoding="utf-8") as f:
        products = json.load(f)

    filtered = [
        p for p in products
        if (
            # ✅ теперь проверяем category против массива types (если есть)
            category in p.get("types", [p.get("product_type")])
        )
        and p["rarity"] == rarity
    ]

    if not filtered:
        return None

    return random.choice(filtered)



