import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import asyncio
import json
from sqlalchemy.dialects.postgresql import insert
from database import async_session
from models.models import QuestNPC

# Путь к JSON
NPC_JSON_PATH = os.path.join("data", "npcs.json")

async def sync_npc_json_to_db():
    async with async_session() as session:
        with open(NPC_JSON_PATH, "r", encoding="utf-8") as f:
            npc_list = json.load(f)

        for npc in npc_list:
            stmt = insert(QuestNPC).values(
                id=npc["id"],
                name=npc.get("name"),
                avatar=npc.get("avatar"),
                quote=npc.get("quote"),
                limit_per_day=npc.get("limit_per_day", 1),
                categories=npc.get("categories", []),
                rarity_pool=npc.get("rarity_pool", {}),
                reward_base=npc.get("reward_on_success", npc.get("reward_base", {})),
                active=True
            ).on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "name": npc.get("name"),
                    "avatar": npc.get("avatar"),
                    "quote": npc.get("quote"),
                    "limit_per_day": npc.get("limit_per_day", 1),
                    "categories": npc.get("categories", []),
                    "rarity_pool": npc.get("rarity_pool", {}),
                    "reward_base": npc.get("reward_on_success", npc.get("reward_base", {})),
                    "active": True
                }
            )
            await session.execute(stmt)

        await session.commit()
        print(f"✅ Синхронизировано {len(npc_list)} NPC")

if __name__ == "__main__":
    asyncio.run(sync_npc_json_to_db())

