import asyncio
from datetime import datetime, timezone
from sqlalchemy.future import select

from models import User, AuctionLot, InventoryItem, Pet
from database import async_session

async def auto_expire_auction_lots():
    while True:
        try:
            async with async_session() as db:
                now = datetime.now(timezone.utc)

                result = await db.execute(
                    select(AuctionLot)
                    .where(AuctionLot.expires_at < now, AuctionLot.is_active == True)
                )
                expired_lots = result.scalars().all()

                for lot in expired_lots:
                    lot.is_active = False

                    if lot.highest_bidder_id:
                        # 🎯 победитель есть — передаём и списываем
                        if lot.item_type == "item":
                            item_result = await db.execute(
                                select(InventoryItem).where(InventoryItem.id == lot.item_id)
                            )
                            item = item_result.scalar_one_or_none()
                            if item:
                                item.user_id = lot.highest_bidder_id
                                item.state = None

                        elif lot.item_type == "pet":
                            pet_result = await db.execute(
                                select(Pet).where(Pet.id == lot.item_id)
                            )
                            pet = pet_result.scalar_one_or_none()
                            if pet:
                                pet.user_id = lot.highest_bidder_id
                                pet.state = "normal"

                        # 💸 списываем валюту у победителя
                        winner_result = await db.execute(
                            select(User).where(User.id == lot.highest_bidder_id)
                        )
                        winner = winner_result.scalar_one_or_none()
                        if winner:
                            if lot.currency == "coins":
                                winner.coins -= int(lot.current_bid)
                            elif lot.currency == "nullings":
                                winner.nullings -= round(float(lot.current_bid), 2)

                        # 💰 начисляем продавцу
                        seller_result = await db.execute(
                            select(User).where(User.id == lot.owner_id)
                        )
                        seller = seller_result.scalar_one_or_none()
                        if seller:
                            if lot.currency == "coins":
                                seller.coins += int(lot.current_bid)
                            elif lot.currency == "nullings":
                                seller.nullings += round(float(lot.current_bid), 2)

                    else:
                        # ❌ никто не победил — просто вернуть предмет владельцу
                        if lot.item_type == "item":
                            item_result = await db.execute(
                                select(InventoryItem).where(InventoryItem.id == lot.item_id)
                            )
                            item = item_result.scalar_one_or_none()
                            if item:
                                item.state = "normal"

                        elif lot.item_type == "pet":
                            pet_result = await db.execute(
                                select(Pet).where(Pet.id == lot.item_id)
                            )
                            pet = pet_result.scalar_one_or_none()
                            if pet:
                                pet.state = "normal"

                await db.commit()
                print(f"[AUCT-CLEANUP] завершено: {len(expired_lots)} лотов @ {now.isoformat()}")

        except Exception as e:
            print(f"[AUCT-CLEANUP] ошибка: {e}")

        await asyncio.sleep(60 * 5)  # 🔁 каждые 5 минут
