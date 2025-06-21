# utils/init_db.py
async def sync_npc_json_to_db(db: AsyncSession):
    with open("data/npcs.json", "r", encoding="utf-8") as f:
        npc_list = json.load(f)

    for npc in npc_list:
        await db.execute(
            insert(QuestNPC)
            .values(id=npc["id"], name=npc["name"])
            .on_conflict_do_nothing()
        )
    await db.commit()
