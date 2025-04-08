from pathlib import Path
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert
import asyncio
from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BookContent(Base):
    __tablename__ = "book_content"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)

async def load_books():
    engine = create_async_engine("postgresql+asyncpg://postgres:password@localhost/omenigen", echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    book_dir = Path("data/books")
    book_files = book_dir.glob("book_*.json")

    async with async_session() as session:
        for book_file in book_files:
            with open(book_file, encoding="utf-8") as f:
                book_data = json.load(f)
            
            product_id = book_data["product_id"]
            pages = book_data["pages"]

            await session.execute(
                f"DELETE FROM book_content WHERE product_id = {product_id}"
            )

            for i, page_text in enumerate(pages, start=1):
                stmt = insert(BookContent).values(
                    product_id=product_id,
                    page_number=i,
                    text=page_text.strip()
                )
                await session.execute(stmt)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(load_books())
